#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Independent read-only ECNU review. Usage: python3 review_b.py PATH_TO_BATCH_B"""
import collections,datetime,hashlib,html,json,re,sys
from pathlib import Path
R=Path(__file__).resolve().parent;B=Path(sys.argv[1])
def read(n):return json.loads((B/n).read_text())
rows=read('major-cutoffs-upsert.json');sources=read('sources.json');ss={s['id']:s for s in sources}
assert len(rows)==32 and len({r['id'] for r in rows})==32
assert all(r['schoolCode']=='10269' and r['school']=='华东师范大学' for r in rows)
params=read('raw/ecnu-params.json')['data'];scope=[]
for r in params['ssmc_nf_klmc_zyz_sex_campus_zslx_list']:
 for k,cats in r.items():
  if k.startswith('广西_2026_') and not '体育' in k:
   _,year,track,subject,_,_=k.split('_')
   scope.extend((track,subject,c) for c in cats)
assert len(scope)==8
seen=[];groups=[];field_checks=0;raw_count=0
fields={'year':('nf',int),'province':('ssmc',str),'sourceTrack':('klmc',str),'sourceCategory':('zylx',str),'sourceSubjectRequirement':('zyzname',str),'major':('zymc',str),'score':('minScore',float),'sourceMaximumScore':('maxScore',float),'sourceAverageScore':('avgScore',float),'admittedCount':('rs',int)}
for i in range(1,9):
 sid=f'major-20260912-b-ecnu-gx-2026-{i}';f=f'raw/ecnu-gx-2026-{i}.json';raw=read(f)
 assert raw['state']==1 and len(raw['data']['sszyzgradeList'])==1
 aa=raw['data']['sszygradeList'];raw_count+=len(aa);rr=[r for r in rows if r['sourceId']==sid]
 assert len(rr)==len(aa)
 for r in rr:
  a=aa[r['sourceRow']-1]
  for out,(key,cast) in fields.items():assert r[out]==cast(a[key]),(r['id'],out);field_checks+=1
  assert r['year']==2026 and r['province']=='广西' and r['track']==r['sourceTrack'].removesuffix('类')
  assert r['group'] is None and r['rank'] is None and r['plannedCount'] is None
  assert r['round']=='录取汇总（轮次未分）' and r['sourceRound'] is None
  assert r['score']<=r['sourceAverageScore']<=r['sourceMaximumScore']<=750 and r['admittedCount']>0
  if r['admittedCount']==1:assert r['score']==r['sourceMaximumScore']
  assert r['scoreType']=='专业录取最低分' and r['scoreComparable'] and not r['scoreEvidenceGaps'] and not r['conflictFields']
  cat=r['sourceCategory'];require=r['requirementText']
  if cat=='普通类(提前批)':
   assert '公费师范' in r['major'] and r['admissionType']=='公费师范生' and r['batch']=='本科提前批（细分类待核）'
   assert '本研衔接师范生公费教育协议书' in require
  elif cat=='普通类(本科批)':assert r['admissionType']=='普通类' and r['batch']=='本科普通批'
  else:
   assert cat in ['国家专项','高校专项'] and r['admissionType']==cat and r['batch']=='本科（批次待核）' and '报考资格' in require
   if cat=='高校专项':assert '特殊类型招生控制分数线' in require
  if r['track']=='物理':assert r['requiredSubjects']==['化学'] and r['subjectRule']=='all'
  else:assert r['requiredSubjects']==[] and r['subjectRule']=='none'
  if r['major'].startswith('英语'):assert '只招收英语语种考生' in require
  refs=set(r['sourceIds'])
  for v in r['fieldSourceIds'].values():refs.update(v)
  assert refs<=ss.keys()
  seen.append((r['sourceId'],r['sourceRow']))
 a=aa[0];seen_scope=(a['klmc'],a['zyzname'],a['zylx']);assert seen_scope in scope
 count=sum(int(r['rs']) for r in aa);assert count==raw['data']['sszyzgradeList'][0]['rs']
 groups.append(dict(sourceId=sid,track=a['klmc'],category=a['zylx'],subject=a['zyzname'],majorRows=len(aa),admittedCount=count))
assert raw_count==32 and len(set(seen))==32 and sum(g['admittedCount'] for g in groups)==88
assert {(g['track'],g['subject'],g['category']) for g in groups}==set(scope)
assert [g['majorRows'] for g in groups]==[3,11,4,1,3,7,2,1]
charter=html.unescape(re.sub('<[^>]*>',' ',(B/'raw/ecnu-charter.html').read_text()));charter=re.sub(r'\s+',' ',charter)
for term in ['2026年本科招生章程','最高不超过20分','该加分在投档、安排专业时均适用','本研衔接师范生公费教育协议书','特殊类型招生控制分数线','英语、翻译（双学位）专业只招收英语语种考生','色弱','色盲']:assert term in charter,term
entry=(B/'raw/ecnu-entry.html').read_text();table=entry.split('id="sszygradeList"',1)[1].split('</script>',1)[0]
for term in ['最高分','平均分','最低分',"out($value,'maxScore'","out($value,'avgScore'","out($value,'minScore'"]:assert term in table
assert 'minRank' not in table and 'minOrder' not in table
hashes=[]
for s in sources:
 if not s['id'].startswith('major-20260912-b-ecnu-'):continue
 path=B/s['archiveFile'];digest=hashlib.sha256(path.read_bytes()).hexdigest();assert digest==s['sha256']==s['archiveSha256']
 hashes.append(dict(sourceId=s['id'],sha256=digest))
public=read('PUBLIC-FILES.json')['files']
for fn in public:
 p=Path(fn);assert not p.is_absolute() and '..' not in p.parts and p.parts[0] not in ['raw','__pycache__']
 t=(B/fn).read_text();assert ('/'+ 'Users/') not in t and ('/'+ 'home/') not in t
 assert not re.search(r'Bearer\s+[A-Za-z0-9._-]{16,}|JSESSIONID=[A-Za-z0-9]{8,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',t)
result=dict(status='PASS',reviewedAt=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),scope='独立只读复核华东师范32条；未修改B包、网站或已有记录。',inputSha256=hashlib.sha256((B/'major-cutoffs-upsert.json').read_bytes()).hexdigest(),rows=32,sourceFieldComparisons=field_checks,admittedCount=88,tracks=dict(collections.Counter(r['track'] for r in rows)),categories=dict(collections.Counter(r['admissionType'] for r in rows)),queryGroups=groups,archiveHashChecks=len(hashes),archiveHashes=hashes,publicFilesChecked=len(public),blockingFindings=[],limitations=['针对本轮归档与转换作独立全量复核，没有另行重新在线请求','未独立复核B包其余六校缺口','组/校汇总8条及其位次未使用；完整专业招生覆盖仍限本次官方公开配置','API rs与同类别录取统计一致；不等于计划人数，保持plannedCount空','原始响应hash来自采集元数据；独立重算验证的是当前脱敏归档hash'])
(R/'independent-review-b.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print('PASS:',field_checks,'source-field comparisons;',len(hashes),'ECNU hashes; 32 rows, 88 admitted.')
