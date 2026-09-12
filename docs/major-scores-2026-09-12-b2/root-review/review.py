"""Independent read-only UIBE and six-school source audit. Needs pdfplumber.
Uses original response arrays, frontend headers and original HTML/PDF, never
imports the collector's build/freeze code. Writes only this review directory.
"""
from pathlib import Path
from collections import Counter
from urllib.parse import urlparse,parse_qs
from html import unescape
import json,re,hashlib
import pdfplumber
R=Path(__file__).resolve().parent;B=R.parent/'batch-root';RAW=B/'raw'
checks=[];compared=[];inputs={}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):inputs[str(p.relative_to(R.parent))]=sha(p);return p.read_text()
def load(p):return json.loads(read(p))
def ck(name,v):checks.append({'name':name,'passed':bool(v)})
def plain(s):return re.sub(r'\s+','',unescape(re.sub('<[^>]*>','',s)))
def rowcheck(r,e,file):
 fields=[{'field':k,'actual':r.get(k),'sourceValue':v,'passed':r.get(k)==v} for k,v in e.items()]
 compared.append({'id':r['id'],'sourceFile':file,'fields':fields,'passed':all(x['passed'] for x in fields)})
rows=load(B/'major-cutoffs-upsert.json');sources=load(B/'sources.json');notes=load(B/'school-audit-notes.json');q=load(B/'QA.json')
sourceids={s['id'] for s in sources};param=load(RAW/'uibe-params.json')['data'];configured=set()
for x in param['ssmc_nf_klmc_sex_campus_zslx_list']:
 for k,v in x.items():
  parts=k.split('_')
  if parts[:2]==['广西','2026']:
   configured.update((parts[2],category) for category in v)
ck('UIBE eleven actual 2026 Guangxi combinations',len(configured)==11)
headers={x['fieldName']:x['label'] for x in param['showField']['showField3']}
ck('Professional minimum-rank and count column semantics',headers['minOrder']=='最低分排名' and headers['rs']=='录取人数' and headers['minScore']=='最低分')
entry=read(RAW/'uibe-scores.html');ck('Professional table binds fields from actual menu','data.sszygradeList' in entry and '$value[$td.fieldName]' in entry and 'data.showField.showField3' in entry)
rawrows=[];actual_queries=set();excluded=0
for i in range(1,12):
 fn=f'uibe-gx-2026-{i}.json';d=load(RAW/fn);m=load(RAW/(fn+'.meta.json'));params=m['data'];actual_queries.add((params['klmc'],params['zslx']))
 ck('Current successful actual query '+str(i),d['state']==1 and params['ssmc']=='广西' and params['zsnf']=='2026')
 a=d['data']['sszygradeList']
 ck('Per-category admitted counts sum '+str(i),sum(x['rs'] for x in a)==sum(x['rs'] for x in d['data']['zsSsgradeList']))
 for j,x in enumerate(a,1):
  if '预科' in x['zymc']:
   excluded+=1;ck('No preparatory aggregate imported '+str(i),not any(r['sourceId'].endswith(f'-{i}-json') for r in rows));continue
  rawrows.append(x)
  matches=[r for r in rows if r['sourceId'].endswith(f'-{i}-json') and r['sourceRow']==j]
  ck('One-to-one raw record '+str(i)+'-'+str(j),len(matches)==1)
  if not matches:continue
  r=matches[0];cat={'本科批':'普通类','提前批':'普通类（提前批）'}.get(x['zslx'],x['zslx'])
  rowcheck(r,{'year':int(x['nf']),'province':x['ssmc'],'track':x['klmc'][:2],'sourceTrack':x['klmc'],'schoolCode':'10036','school':'对外经济贸易大学','major':x['zymc'],
              'majorCode':None,'sourceMajorCode':x['zydm'],'batch':x['pcmc'],'round':'录取汇总（轮次未分）','group':None,'score':x['minScore'],'sourceMaximumScore':x['maxScore'],
              'sourceAverageScore':x['avgScore'],'rank':x['minOrder'],'rankType':'专业最低分排名（学校公布）','admittedCount':x['rs'],'plannedCount':None,
              'sourceCategory':x['zslx'],'admissionType':cat,'scoreType':'专业录取最低分','subjectRule':'unknown','requiredSubjects':[],'scoreComparable':True},'batch-root/raw/'+fn)
  ck('Numerical consistency '+r['id'],0<x['minScore']<=x['avgScore']<=x['maxScore']<=750 and x['minOrder']==x['minRank'] and (x['rs']!=1 or x['minScore']==x['maxScore']))
  ck('Rank evidence includes raw and actual header '+r['id'],r['sourceId'] in r['fieldSourceIds']['rank'] and 'major-20260912b2-root-uibe-params-json' in r['fieldSourceIds']['rank'])
  ck('Source major code only '+r['id'],r['sourceId'] in r['fieldSourceIds'].get('sourceMajorCode',[]))
  req=r.get('admissionRequirements','')
  if x['zslx']=='中外合作办学':ck('Cooperation eligibility '+r['id'],'志愿' in req and '不得转入其他专业' in req and '100000' in req)
  if x['zslx']=='高校专项':ck('Special eligibility '+r['id'],'高校专项' in req and '特殊类型招生控制线' in req)
  if x['zslx']=='国家专项':ck('National special eligibility '+r['id'],'国家专项' in req and '资格' in req)
  if x['zslx']=='提前批':ck('Foreign language eligibility '+r['id'],'只招英语' in req)
  if '选拔' in x['zymc']:ck('Selection is not automatic admission '+r['id'],'不等于获得' in req)
ck('All configured categories queried',actual_queries==configured)
ck('Two prep rows excluded',excluded==2)
ck('30 actual rows and 83 admitted',len(rows)==len(rawrows)==30 and sum(x['rs'] for x in rawrows)==sum(r['admittedCount'] for r in rows)==83)
ck('Track totals',Counter(r['track'] for r in rows)=={'历史':16,'物理':14})
ck('Category totals',Counter(r['sourceCategory'] for r in rows)=={'本科批':18,'国家专项':4,'提前批':4,'中外合作办学':2,'高校专项':2})
ck('No group-reference score mixed in',all('referenceScore' not in r and not r.get('matchedGroupId') for r in rows))
ck('All source references resolve',all(set(r.get('sourceIds',[])+[r['sourceId']]+[z for v in r['fieldSourceIds'].values() for z in v])<=sourceids for r in rows))
charter=plain(read(RAW/'uibe-charter.html'))
ck('2026 charter actual score basis','2026年本科生招生' in charter and '依据考生投档成绩和专业志愿' in charter and '全国性政策加分' in charter and '最高加分不得超过20分' in charter)
ck('Charter eligibility and cooperation fee','专业只招英语考生' in charter and '入学后不得转入其他专业' in charter and '保险学（中外合作办学）专业100000元/生/学年' in charter)
ck('Charter special admission policy','特殊类型招生控制分数线' in charter and '高校专项计划根据公布的各省' in charter)
hashes=0
for s in sources:
 if not s.get('archiveFile'):continue
 f=RAW/s['archiveFile']
 if not f.exists():f=B/s['archiveFile']
 if f.exists():
  inputs[str(f.relative_to(R.parent))]=sha(f);ck('Source hash '+s['id'],sha(f)==s['sha256']);hashes+=1
ck('Six reviewed school notes',len(notes)==6 and {n['schoolCode'] for n in notes}=={'10036','10574','11845','19422','19335','10285'})
for n in notes:
 ck('Note references '+n['schoolCode'],bool(n['sourceIds']) and set(n['sourceIds'])<=sourceids)
 ck('Local date and audit kind '+n['schoolCode'],n['checkedAt'].startswith('2026-09-12') and n['auditKind']=='major-scores')
for track in ['physics','history']:
 for suffix in ['', '-national']:
  fn=f'sduwh-get-2026-{track}{suffix}.html';s=read(RAW/fn);m=load(RAW/(fn+'.meta.json'));u=parse_qs(urlparse(m['url']).query)
  ck('SDUWH valid Chinese parameters '+track+suffix,u['nf']==['2026'] and u['sf']==['广西壮族自治区'] and u['kl']==[{'physics':'物理类','history':'历史类'}[track]])
  ck('SDUWH valid empty response '+track+suffix,'该项选择无数据，请重新选择查询' in s and '<tr class="tr1">' not in s)
 fn=f'sduwh-get-2025-{track}.html';s=read(RAW/fn)
 ck('SDUWH valid positive '+track,'2025年广西壮族自治区普通类'+{'physics':'物理类','history':'历史类'}[track]+'专业录取情况统计表' in s and len(re.findall(r'<tr\s+class="tr1">',s))=={'physics':4,'history':3}[track])
s=read(RAW/'suda-gx-2026.html');old=read(RAW/'suda-gx-2025.html')
ck('SUDA no current table; generated title alone not evidence','ctl00_ContentPlaceHolder1_GridView1' not in s and 'ctl00_ContentPlaceHolder1_GridView1' in old)
ck('SUDA 38 old positive rows',len(re.findall(r'id="ctl00_ContentPlaceHolder1_GridView1_ctl\d+_HyperLink1"',old))==38)
ck('SUDA current query exact aid and year',parse_qs(urlparse(load(RAW/'suda-gx-2026.html.meta.json')['url']).query)['ay']==['2026'] and parse_qs(urlparse(load(RAW/'suda-gx-2026.html.meta.json')['url']).query)['aid']==['20'])
z=plain(read(RAW/'zju-latest.html'));ck('ZJU medical shared latest page is 2025 filing data','2025年浙江大学各省份普通本一批投档分数线' in z)
g=plain(read(RAW/'gdut-gx-2025.html'));ck('GDUT upstream page establishes 2025','2025' in g and '广西' in g)
scnu=plain(read(RAW/'scnu-prior-scores.html'));ck('SCNU article year is 2025 despite release in 2026','2025年华南师范大学外省录取情况一览表' in scnu and '2026-03-09' in scnu)
pdf=RAW/'scnu-prior-scores.pdf';inputs[str(pdf.relative_to(R.parent))]=sha(pdf)
with pdfplumber.open(pdf) as d:
 ck('SCNU PDF first page title year and length',len(d.pages)==11 and '华南师范大学2025年外省' in d.pages[0].extract_text())
 ck('SCNU PDF Guangxi page distinct from Hunan','广西区' in plain(d.pages[6].extract_text()) and '湖南省' in plain(d.pages[6].extract_text()))
passed=all(x['passed'] for x in checks) and all(x['passed'] for x in compared)
result={'status':'PASS' if passed else 'FAIL','reviewedAt':q['reviewedAt'],'summary':{'rows':30,'admitted':83,'fieldComparisons':sum(len(r['fields']) for r in compared),'passedFieldComparisons':sum(x['passed'] for r in compared for x in r['fields']),'checks':len(checks),'passedChecks':sum(x['passed'] for x in checks),'sourceArchiveHashes':hashes,'reviewedSchoolNotes':6},
        'findings':[{'id':'uibe-major-code-semantics','status':'closed' if all(r.get('majorCode') is None and r.get('sourceMajorCode') for r in rows) else 'open','description':'Original zydm is retained as sourceMajorCode; it does not establish the Guangxi application major code.'}],
        'visualReview':{'gdut':'Full Guangxi image checked; its own image has no year, upstream official page is 2025.','scnu':'PDF first-page title 2025 read directly; page7 image Guangxi rows visually distinct from preceding Hunan; 6 history plus7 physics actual major rows, totals excluded.'},
        'checks':checks,'rows':compared,'inputs':inputs}
(R/'QA.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'status':result['status'],'summary':result['summary'],'failedChecks':[x for x in checks if not x['passed']],'failedFields':[{'id':r['id'],'fields':[x for x in r['fields'] if not x['passed']]} for r in compared if not r['passed']]},ensure_ascii=False,indent=2))
raise SystemExit(0 if passed else 1)
