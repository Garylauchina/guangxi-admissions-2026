"""Read-only bounded check of sibling A/B packages; never sends network requests."""
from pathlib import Path
from collections import Counter
import hashlib,json,re
ROOT=Path(__file__).resolve().parent
PARENT=ROOT.parent
checks=[];evidence=[]
def check(name,ok,detail=None):checks.append({'id':name,'pass':bool(ok),**({'detail':detail} if detail is not None else {})})
def load(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
packages={};queries=[];privacy=[]
def scan(obj,where):
 if isinstance(obj,dict):
  for k,v in obj.items():
   if re.fullmatch(r'(cookie|set-cookie|csrf-token|csrfToken|access[_-]?token|jessionid|jsessionid|sessionid|authorization)',k,re.I) and v not in [None,'',True,False]:privacy.append(where+'.'+k)
   scan(v,where+'.'+k)
 elif isinstance(obj,list):
  for i,v in enumerate(obj):scan(v,where+f'[{i}]')
for name in ['batch-a','batch-b']:
 p=PARENT/name;sources=load(p/'sources.json');notes=load(p/'school-audit-notes.json');manifest=load(p/'PUBLIC-FILES.json');files=manifest.get('files',manifest.get('publicFiles'))
 check(name+'-no-new-score',load(p/'major-cutoffs-upsert.json')==[])
 check(name+'-seven-distinct-schools',len(notes)==len({n['schoolCode'] for n in notes})==7)
 for n in notes:
  check(name+'-'+n['schoolCode']+'-identity-date',n['year']==2026 and n['province']=='广西' and n['auditKind']=='major-scores' and n['checkedAt'].startswith('2026-09-12'))
  check(name+'-'+n['schoolCode']+'-source-closure',all(i in {s['id'] for s in sources} for i in n['sourceIds']))
 for f in files:
  fp=p/f;check(name+'-public-file-'+f,fp.exists() and 'raw/' not in f and not f.startswith('/') and '..' not in Path(f).parts)
  if not fp.exists():continue
  text=fp.read_text();check(name+'-'+f+'-no-private-path',('/'+'Users/') not in text and ('/'+'home/') not in text)
  if fp.suffix=='.json':scan(load(fp),name+'/'+f)
 count=0;failed_body=0
 for s in sources:
  key=s['id'].split('-'+name[-1]+'-',1)[1];meta=load(p/'raw'/(key+'.meta.json'))
  qp=s.get('queryParameters') if name=='batch-a' else s.get('requestParams')
  mq=meta.get('request') if name=='batch-a' else meta.get('data',{})
  status=meta.get('httpStatus') if name=='batch-a' else meta.get('status')
  check(s['id']+'-metadata-parameters',s['url']==meta['url'] and s.get('httpStatus')==status and (qp==mq or (not qp and not mq)))
  f=s.get('archiveFile');archivehash=s.get('archiveSha256') or s.get('sha256')
  if f and archivehash:
   fp=p/f;check(s['id']+'-archive-hash',fp.exists() and sha(fp)==archivehash and s.get('sha256')==archivehash);count+=1
   if s.get('httpStatus')!=200:failed_body+=1
  else:check(s['id']+'-failed-no-body',s.get('httpStatus')!=200 and bool(s.get('accessError')))
  if s.get('httpStatus')!=200 or not f or not f.endswith('.json'):continue
  params=s.get('queryParameters') or s.get('requestParams') or {};year=params.get('zsnf',params.get('year'))
  if year not in ['2026','2025',2026,2025]:continue
  d=load(p/f)
  if isinstance(d,dict) and isinstance(d.get('data'),dict) and 'sszygradeList' in d['data']:
   major=d['data']['sszygradeList'];summary=d['data']['zsSsgradeList'];check(s['id']+'-business-success',d.get('state')==1)
   check(s['id']+'-guangxi-track-parameters',params.get('ssmc')=='广西' and params.get('klmc') in ['物理类','历史类'])
   if str(year)=='2026':check(s['id']+'-successful-empty',major==[] and summary==[])
   else:
    check(s['id']+'-positive-control',len(major)>0)
    check(s['id']+'-old-row-provenance',all(str(r.get('nf'))=='2025' and r.get('ssmc')=='广西' and r.get('klmc')==params['klmc'] for r in major))
   queries.append({'sourceId':s['id'],'package':name,'parameters':params,'queryYear':int(year),'businessCode':d['state'],'majorRows':len(major),'summaryRows':len(summary),'archiveSha256':archivehash})
  elif isinstance(d,dict) and isinstance(d.get('data'),dict) and 'provinceSpecializedSubjectScoreVOS' in d['data']:
   major=d['data']['provinceSpecializedSubjectScoreVOS'];summary=d['data']['provinceScoreVOS'];check(s['id']+'-business-success',str(d.get('code'))=='1000000')
   check(s['id']+'-guangxi-track-parameters',params.get('provinceId')==20 and params.get('subjectId') in [2,3] and s.get('parameterConfigurationYear')==2025)
   check(s['id']+'-result-shape',(major==[] and summary==[]) if str(year)=='2026' else len(major)>0)
   queries.append({'sourceId':s['id'],'package':name,'parameters':params,'queryYear':int(year),'businessCode':d['code'],'majorRows':len(major),'summaryRows':len(summary),'archiveSha256':archivehash,'parameterConfigurationYear':2025})
 packages[name]={'schoolCount':len(notes),'sourceCount':len(sources),'archivesChecked':count,'non200ArchivesIncluded':failed_body,'failuresWithoutBody':len(sources)-count,'publicFileCount':len(files),'reviewedFileHashes':{f:sha(p/f) for f in ['sources.json','school-audit-notes.json','QA.json','PUBLIC-FILES.json']}}
check('public-json-no-secret-values',not privacy,{'suspectKeys':privacy})
# Match all requested combinations; initial failed CAU requests are excluded by HTTP status.
expected={'sdu':(9,[11,24]),'cau':(6,[6,21]),'cuc':(4,[15]),'buct':(2,[2,16]),'cufe':(4,[8,13]),'jnu':(6,[1,9])}
for pre,(n,oldcounts) in expected.items():
 marker=('-a-' if pre in ['sdu','cau'] else '-b-')+pre+'-gx-'
 qs=[q for q in queries if marker in q['sourceId']]
 check(pre+'-current-query-count',len([q for q in qs if q['queryYear']==2026])==n)
 check(pre+'-old-controls-count',sorted(q['majorRows'] for q in qs if q['queryYear']==2025)==oldcounts)
# Direct JNU configuration IDs and configuration-year boundary.
b=PARENT/'batch-b/raw'
check('jiangnan-province-id',{'id':20,'name':'广西'} in load(b/'jnu-provinces-2025.json')['data'])
subjects=load(b/'jnu-subjects-json-2025.json')['data'];check('jiangnan-subject-ids',{x['id']:x['name'] for x in subjects}=={2:'历史类',3:'物理类'})
for f in ['jnu-provinces-2026.json','jnu-subjects-json-2026.json']:
 d=load(b/f);check(f+'-successful-config-empty',str(d['code'])=='1000000' and d['data']==[])
# Direct access classifications.
a=PARENT/'batch-a';am={s['id'].replace('major-20260912b2-a-',''):s for s in load(a/'sources.json')}
for key,status in [('shutcm-home',504),('shutcm-home-retry',504),('shutcm-school',403),('swupl-admissions',412),('swupl-entry',412)]:check(key+'-actual-http-status',am[key]['httpStatus']==status)
shufe=(a/am['shufe-query-entry']['archiveFile']).read_text();check('shufe-year-province-template',all(s in shufe for s in ['2026','2025','2024','广西','专业名称','最低分']))
check('shufe-captcha-submit-required','请输入四位数字验证码' in shufe and 'return false' in shufe and 'validateCode' in shufe)
szu=(a/am['szu-gx-old']['archiveFile']).read_text();check('szu-old-table-years','2025年' in szu and '2024年' in szu)
jnu=(a/am['jnu-gx-old']['archiveFile']).read_text();check('jinan-old-year-new-publication','2025年在广西录取分数线' in jnu and '2026-05-18' in jnu)
bm={s['id'].replace('major-20260912b2-b-',''):s for s in load(PARENT/'batch-b/sources.json')}
for key in ['lzu-entry','lzu-entry-http','lzu-entry-curl','lzu-charter']:check(key+'-access-error-no-success',bm[key]['httpStatus'] is None and bool(bm[key].get('accessError')))
check('citydg-independent-school-id','4144014851' in (PARENT/'batch-b'/bm['citydg-charter']['archiveFile']).read_text())
check('citydg-faq-2025','2025年' in (PARENT/'batch-b'/bm['citydg-faq']['archiveFile']).read_text())
result={'reviewedAt':'2026-09-12','status':'PASS' if all(x['pass'] for x in checks) else 'FAIL','scope':'仅兄弟A/B包原归档、已声明查询范围、关键原文、公开白名单；不联网、不扩展渠道、不逐行复核旧年专业分值。','packages':packages,'summary':{'schools':14,'newActualRows':0,'currentSuccessfulEmptyQueries':sum(q['queryYear']==2026 for q in queries),'oldYearPositiveQueries':sum(q['queryYear']==2025 for q in queries),'oldYearPositiveRows':sum(q['majorRows'] for q in queries if q['queryYear']==2025),'checks':len(checks),'passed':sum(c['pass'] for c in checks),'failed':sum(not c['pass'] for c in checks)},'queries':queries,'checks':checks,'manualReview':['山东大学2026汇总长图已目视，只有省市/科类/统计类型，无专业名称列。','广州医科大学外省长图已目视：标题2025，广西本科物理临床医学614、临床药学596，属于旧年。','深圳/暨南原HTML表体与发布时间分开核对；深圳当前入口标第一次投档统计。','上财前端直接要求图形验证码；未把未提交查询说成成功空表。','兰大web工具412和无浏览器仅核对补充尝试记录，本复核没有重新调用外部工具验证该次工具状态。','采集脚本会话Cookie和CSRF仅内存使用；公开JSON未发现具体会话值或私人路径。'],'issues':[]}
(ROOT/'QA.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(result['summary'],ensure_ascii=False));print([c for c in checks if not c['pass']])
assert result['status']=='PASS'
