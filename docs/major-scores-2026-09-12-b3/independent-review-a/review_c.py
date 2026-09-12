#!/usr/bin/env python3
"""Read-only source-value review; does not import collector/build code from batch C."""
from pathlib import Path
import argparse,collections,csv,hashlib,html,json,re
from table_reader import tables
R=Path(__file__).resolve().parent
FROZEN={'major-cutoffs-upsert.json':'2fa83371e87e139700009692a9196936e6143734dd07c9c1be1f49965bd2408e','sources.json':'0484e3705bcf944c32910f17ab0ec42e6a8b4c05cab48ff6c203634a60029be7','school-audit-notes.json':'713180dc59e298b63d4c00b05441d4cc4478d272293c2dad169fe9bc11adc63b'}
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--bundle',type=Path,default=R.parent/'batch-c');a=parser.parse_args();B=a.bundle.resolve()
 def read(n):return json.loads((B/n).read_text())
 def text(k):return (B/'raw'/(k+'.html')).read_text()
 def plain(k):return re.sub(r'\s+','',html.unescape(re.sub('<[^>]+>',' ',text(k))))
 for f,h in FROZEN.items():assert hashlib.sha256((B/f).read_bytes()).hexdigest()==h,(f,'input changed')
 rows=read('major-cutoffs-upsert.json');sources=read('sources.json');assert len(rows)==67
 expected={};comparisons=0
 def put(key,row,values):expected[key,row]=values
 # Independently expand raw HTML rowspans; no use of C evidence-rows/parser/transcription.
 m=tables(text('mdj-score'))[2];assert m[0]==['专业','科类','计划数','录取数','最高分','最低分','省线','线差'] and len(m)==23
 for row,v in enumerate(m[1:],2):put('mdj-score',row,dict(major=v[0],sourceTrack=v[1],admittedCount=int(v[3]),sourceMaximumScore=float(v[4]),score=float(v[5])))
 x=tables(text('xync-10981'))[3];assert len(x)==19 and x[0][3:]==['录取人数','退档人数','投档录取最高分','投档录取最低分','录取最低分同分排位','缺额人数']
 for row,v in enumerate(x[1:],2):put('xync-10981',row,dict(major=v[0],sourceTrack=v[1],admittedCount=int(v[3]),sourceMaximumScore=float(v[5]),score=float(v[6]),sourceTieBreakOrder=int(v[7])))
 x2=tables(text('xync-11021'))[0];assert len(x2)==2 and x2[0][4:]==['投档录取最高分','投档录取最低分','录取最低分同分排位']
 v=x2[1];put('xync-11021',2,dict(major=v[0],sourceTrack=v[1],admittedCount=int(v[3]),sourceMaximumScore=float(v[4]),score=float(v[5]),sourceTieBreakOrder=int(v[6])))
 b=tables(text('bjwl-1383'))[0];assert b[0]==['省份','专业名称','选考科目/科类','计划','录取人数','最高分','最低分','平均分','成绩项']
 for row,v in enumerate(b[1:],2):
  if v[0]=='广西':put('bjwl-1383',row,dict(major=v[1],sourceTrack=v[2],admittedCount=int(v[4]),sourceMaximumScore=float(v[5]),score=float(v[6]),sourceAverageScore=float(v[7])))
 # These 12 image values were transcribed independently by visual inspection.
 with (R/'cdutcm-independent-transcription.tsv').open() as f:
  for v in csv.DictReader(f,delimiter='\t'):put('cdutcm-image',int(v['sourceRow']),dict(sourceMajor=v['sourceMajor'],sourceTrack=v['sourceTrack'],sourceMaximumScore=float(v['maximum']),score=float(v['minimum'])))
 assert len(expected)==67
 seen=set()
 for row in rows:
  key=row['sourceId'].removeprefix('major-20260912b3-c-');keyrow=(key,row['sourceRow']);assert keyrow in expected and keyrow not in seen;seen.add(keyrow)
  for field,val in expected[keyrow].items():assert row.get(field)==val,(row['id'],field,row.get(field),val);comparisons+=1
  assert row['year']==2026 and row['province']=='广西' and row['track'] in ['物理','历史']
  assert row['group'] is None and row['rank'] is None and row['admissionType']=='普通类'
  assert row['scoreComparable'] and row['scoreType']=='专业录取最低分' and row['score']<=row['sourceMaximumScore']<=750
  if 'sourceAverageScore' in row:assert row['score']<=row['sourceAverageScore']<=row['sourceMaximumScore']
  if key=='xync-11021':assert row['round']=='征集（次数未分）'
  else:assert row['round']=='录取汇总（轮次未分）'
  if key in ['xync-10981','xync-11021']:assert row['sourceTieBreakOrder'] and '同分' in row['note']
  if key=='bjwl-1383' and '物理' in row['sourceTrack']:assert row['requiredSubjects']==['化学'] and row['subjectRule']=='all'
  if key=='cdutcm-image':assert row.get('admittedCount') is None
 assert seen==set(expected)
 # Check article period/location/actual-admission wording, and keep collections separate.
 assert '2026年广西壮族自治区普通类本科批次录取公告' in plain('mdj-score') and '实际录取61人' in plain('mdj-score')
 assert '广西壮族自治区普通类专业录取情况' in plain('xync-10981') and '完成海南省、湖北省、青海省、广西壮族自治区普通类的录取工作' in plain('xync-10981')
 assert '2026年录取简报' in plain('xync-10981') and '广西壮族自治区普通类征集录取情况' in plain('xync-11021')
 assert '2026年录取快讯（九）' in plain('bjwl-1383')
 assert '【2026】录取快讯第21期-广西普通本科批' in plain('cdutcm-score') and '实际录取43名' in plain('cdutcm-score') and '物理类39名，历史类4名' in plain('cdutcm-score')
 # Independently inspect the 2026 Guangxi plan response only to disambiguate formal name/category.
 plan=read('raw/cdutcm-plan-gx.json');assert plan['count']==len(plan['data'])==14 and all(v['year']=='2026' and v['province']=='广西' for v in plan['data'])
 for row in [v for v in rows if v['schoolCode']=='10633']:
  matches=[v for v in plan['data'] if v['majorname']==row['major'] and v['category']==row['sourceTrack']];assert len(matches)==1 and matches[0]['typeitem']=='普通类'
  assert '不招色盲、色弱' in row['note'] and '非英语语种考生慎报' in row['note']
  if row['sourceMajor']=='中医骨伤学':assert row['major']=='中医骨伤科学' and 'major-20260912b3-c-cdutcm-plan-gx' in row['fieldSourceIds']['major']
 assert len([v for v in plan['data'] if '体育' in v['category']])==2
 # Verify sourced restrictions without converting recommendations to absolute bans.
 assert '英语、商务英语、翻译（英语翻译）、法语专业招收英语语种考生' in plain('mdj-charter')
 assert '所有招生专业不限制应试语种' in plain('xync-charter')
 assert '非英语语种' in plain('bjwl-charter') and '慎报' in plain('bjwl-charter')
 assert '智能医学工程' in plain('cdutcm-charter') and '不招收色盲色弱的考生' in plain('cdutcm-charter')
 for key in ['mdj-charter','xync-charter','bjwl-charter','cdutcm-charter']:assert '2026' in plain(key) and ('加分' in plain(key) or '加、降分' in plain(key))
 for row in rows:
  if row['schoolCode']=='10233' and '英语' in row['major']:assert '只招英语语种' in row['note']
  if row['schoolCode']=='10633' and row['major']=='护理学':assert '建议' in row['note'] and '1.58' in row['note'] and '1.62' in row['note']
  if row['schoolCode']=='10722' and row['major']=='化学工程与工艺' and '11021' not in row['sourceId']:assert row['admittedCount']==2 and '退档1人' in row['note'] and '缺额1人' in row['note']
 local=0
 for src in sources:
  if src.get('archiveFile') and (B/src['archiveFile']).exists():assert hashlib.sha256((B/src['archiveFile']).read_bytes()).hexdigest()==src['archiveSha256'];local+=1
 for fn in read('PUBLIC-FILES.json')['files']:
  path=Path(fn);assert not path.is_absolute() and '..' not in path.parts and path.parts[0]!='raw'
  t=(B/fn).read_text();local_text=re.sub(r'https?://[^\s\"<>]+','',t);assert ('/'+'Users/') not in local_text and ('/'+'home/') not in local_text
  assert not re.search(r'Bearer\s+[A-Za-z0-9._-]{16,}|JSESSIONID=[A-Za-z0-9]{8,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',t)
 report=dict(status='PASS',reviewDate='2026-09-12',inputSha256=FROZEN,reviewedRows=67,independentSourceFieldComparisons=comparisons,localArchiveHashesChecked=local,imagesVisuallyReviewed=1,imageRowsIndependentlyTranscribed=12,countsBySchool=dict(collections.Counter(r['schoolCode'] for r in rows)),recordAdmittedCounts=sum(r.get('admittedCount',0) for r in rows),admittedCountsMissing=12,schoolTotalAdditional=43,materialIssues=[],scope='All 67 positive rows checked against raw HTML or independently transcribed original image; not an audit of all negative school conclusions or all official channels.')
 (R/'review-c.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False))
if __name__=='__main__':main()
