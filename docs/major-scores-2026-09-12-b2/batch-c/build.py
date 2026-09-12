"""Rebuild only this additive batch from archived public HTML and inspected image facts."""
from pathlib import Path
from collections import Counter
import json,csv,hashlib
from parse_tables import NestedTables
BASE=Path(__file__).resolve().parent
DATE='2026-09-12'
def read(name):return json.loads((BASE/name).read_text())
def write(name,data):(BASE/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def sid(k):return 'major-20260912b2-c-'+k
def txt(k):return (BASE/'raw'/next(q['file'] for q in requests if q['key']==k)).read_text()
requests=read('requests.json');context=read('baseline-context.json')
SCHOOL={'cqc':('12758','重庆城市管理职业大学'),'tlu':('10383','铜陵学院'),'wnu':('10723','渭南师范学院'),'jy':('13283','浙江农林大学暨阳学院')}
sources=[];checks=[]
def check(name,ok,detail=None):checks.append({'id':name,'pass':bool(ok),**({'detail':detail} if detail is not None else {})})
for q in requests:
 key=q['key'];pre=key.split('-')[0];meta=read('raw/'+key+'.meta.json');file=BASE/'raw'/q['file']
 check(key+'-archive',meta['status']==200 and sha(file)==meta['sha256'])
 charter='charter' in key
 title=SCHOOL[pre][1]+'：'+({'cqc-gx':'2026广西普通高校招生高职专科批次普通类录取情况','tlu-gx':'2026广西普通本科批次录取工作完成','tlu-table':'2026高考录取进程广西专业分原图','wnu-gx':'2026年7月21日各省录取快讯','wnu-13':'2026录取快讯广西普通类专业原图','jy-gx':'2026广西首轮录取结果及征求计划','jy-table':'2026广西首轮科类汇总分原图'}.get(key,'2026招生章程' if charter else '2026录取信息相关页面或原图'))
 date={'cqc':'2026-08-08','tlu':'2026-07-25','wnu':'2026-07-21','jy':'2026-07-21'}[pre]
 if charter:date={'cqc':'2026-06-15','tlu':'2026-06-01','wnu':'2026-06-08'}[pre]
 if key=='cqc-index':date=None
 sources.append({'id':sid(key),'title':title,'url':q['url'],'publisher':SCHOOL[pre][1],'sourceType':'official','year':2026,'province':'广西' if key in ['cqc-gx','tlu-gx','tlu-table','wnu-13','jy-gx','jy-table'] else None,'publishedAt':date,'accessedAt':meta['checkedAt'],'requestMethod':'GET','httpStatus':meta['status'],'sha256':meta['sha256'],'rawSha256':meta['sha256'],'archiveSha256':meta['sha256'],'archiveFile':'raw/'+q['file'],'method':'官方公开GET；原HTML/原图本地存档；不公开响应头、原网页或图片。'})
sources+=read('code-sources.json')
rows=[];evidence=[]
code_source={'12758':'gxeea-2026-33315','10383':'gxeea-2026-33107','10723':'gxeea-2026-33106'}
def base(pre,key,n,track,major,score,batch):
 code,school=SCHOOL[pre];charter=sid(pre+'-charter');source=sid(key);ids=[source,charter,code_source[code]]
 r={'id':f'major-20260912b2-c-{code}-{key}-{n}','year':2026,'province':'广西','schoolCode':code,'school':school,'sourceSchool':school,'track':track,'sourceTrack':track+'类','batch':batch,'round':'录取汇总（轮次未分）','group':None,'major':major,'score':score,'scoreType':'专业录取最低分','rank':None,'rankType':None,'sourceId':source,'sourceIds':ids,'sourceTable':1,'sourceRow':n,'reviewedAt':DATE,'evidenceStatus':'verified','scoreComparable':True,'scoreBasis':'750分制普通高考总分（包含学校认可的政策加分口径）','scoreScaleMaximum':750,'scoreEvidenceGaps':[],'conflictFields':[],'admissionType':'普通类','requiredSubjects':[],'subjectRule':'unknown','requirementText':'首选'+track+'；原成绩表未列再选科目','fieldSourceIds':{k:[source] for k in ['year','province','track','major','score','batch','round','admittedCount','admissionType']}}
 r['fieldSourceIds'].update(schoolCode=[code_source[code]],school=[charter],scoreBasis=[charter],note=[source,charter])
 return r
p=NestedTables();p.feed(txt('cqc-gx'));t=p.tables[0]['rows'];check('cqc-header',t[0]==['科类','录取专业','录取最低分数','录取数'])
for i,c in enumerate(t[1:],1):
 r=base('cqc','cqc-gx',i,c[0].replace('类',''),c[1],int(c[2]),'高职专科批次');r['admittedCount']=int(c[3]);r['sourceScoreHeader']='录取最低分数'
 r['sourceRow']=i+1
 r['note']='2026广西高职专科批次普通类录取快讯，完整9条实际专业最低分；原公告未区分首次与征集，轮次保留汇总。学校按分数优先确定专业、认可生源省加降分政策，原表未单列加分数值。外语语种不限，公共外语统一英语；普通专业大一在荣昌校区，后续年级回大学城校区。具体组码和选科细项未列，保持未知。录取人数不作为初始计划。'
 if r['major']=='婴幼儿托育服务与管理':r['note']+='该专业不招收色盲、色弱考生（2026章程第八条第5项）。';r['eligibility']={'colorBlindnessExcluded':True,'colorWeaknessExcluded':True,'sourceIds':[sid('cqc-charter')]}
 rows.append(r);evidence.append({'id':r['id'],'sourceId':sid('cqc-gx'),'sourceTable':1,'sourceRow':i+1,'cells':c})
trans=list(csv.DictReader((BASE/'image-transcription.tsv').open(),delimiter='\t'))
for c in trans:
 key=c['key'];pre=key.split('-')[0];n=int(c['row']);r=base(pre,key,n,c['track'],c['major'],int(c['minimum']),'本科批' if pre=='tlu' else '本科（批次待核）')
 r.update(admittedCount=int(c['admitted']),sourceMaximumScore=int(c['maximum']))
 r['fieldSourceIds']['sourceMaximumScore']=[sid(key)]
 parent=sid(pre+'-gx');r['sourceIds'].append(parent);r['fieldSourceIds']['year']=[parent,sid(key)] if pre=='tlu' else [parent];r['fieldSourceIds']['round']=[parent];r['fieldSourceIds']['note'].append(parent)
 if pre=='tlu':
  r['sourceAverageScore']=float(c['average']);r['fieldSourceIds']['sourceAverageScore']=[sid(key)];r['sourceScoreHeader']='最高分 / 最低分 / 平均分';r['sourceAdmissionDate']='2026-07-25';r['requiredSubjects']=['化学'];r['subjectRule']='all';r['requirementText']='物理-化学（原图类别）';r['fieldSourceIds']['requiredSubjects']=[sid(key)];r['fieldSourceIds']['requirementText']=[sid(key)]
  r['note']='官方2026高考录取进程广西本科批原图，明示录取人数与最高/最低/平均分；原图未用投档分表头。7月25日是录取日期，未以此推断首轮，保留轮次汇总。原类别明确物理-化学。学校录取以投档分为准，政策加分按生源省规定执行；教学第一外语为英语，非英语语种考生须留意。录取人数不作为初始计划。'
 else:
  r['sourceIds'].append(sid('wnu-charter-mirror'));r['fieldSourceIds']['scoreBasis'].append(sid('wnu-charter-mirror'));r['sourceScoreHeader']='文化分投档 录取最高/最低分';r['sourceScoreNote']='文化分录取';r['fieldSourceIds']['batch']=[parent,sid('wnu-charter')]
  r['note']='2026录取快讯的完整广西普通类专业表；原表头为“文化分投档 录取最高/最低分”，说明列为“文化分录取”，另列实际录取数。本字段据该录取快讯保存实际专业录取最低分，完整保留混合措辞；它未标“首次投档最低分”，也不解释成不含加分的裸分。章程按政策加降分后的成绩排序录取。具体本科批次、首轮/征集、组码及再选科目未列，保留未知/汇总。非外语专业外语语种不限，公共课程开大学英语，可选修日语、朝鲜语、俄语。录取人数不作为招生计划。'
  if c['major']=='旅游管理':r['note']+='原图计划4人、实际录取3人；这个差异不用于认定征集轮次。'
 rows.append(r);evidence.append({'id':r['id'],'sourceId':sid(key),'sourceTable':1,'sourceRow':n,'cells':c})
notes=[]
for pre,status,note,keys in [
 ('cqc','collected','取得2026广西高职专科普通类完整9条，历史4、物理5，录取20人。校名与广西当年表均为重庆城市管理职业大学，五位码12758；章程学校标识码4150012758，不因域名或升格推断新代码。轮次/组码/再选科目未列。',['cqc-gx','cqc-charter']),
 ('tlu','collected','取得2026广西普通本科批次完整2条专业成绩、共录取10人。原图录取日期7月25日，最高最低平均分，物理-化学类别明确；未据日期认定首轮。',['tlu-gx','tlu-table','tlu-charter']),
 ('wnu','collected','取得2026快讯完整广西普通类原图21条，历史7、物理14，共录取66人；其中旅游管理计划4、录取3。原表文化分投档录取最高/最低分与文化分录取说明完整保留，不改为裸分，也不以人数差推定征集。具体本科批次/轮次/组码未明。',['wnu-gx','wnu-13','wnu-charter','wnu-charter-mirror']),
 ('jy','not-found-current-major','2026广西首轮录取公告只给物理/历史两个科类最高最低分，没有具体专业，后附征求计划；科类汇总不拆成专业分，征求余额不当初始计划。',['jy-gx','jy-table'])]:
 code,school=SCHOOL[pre];notes.append({'id':'major-audit-20260912b2-c-'+code,'year':2026,'province':'广西','schoolCode':code,'school':school,'auditKind':'major-scores','checkedAt':DATE,'status':status,'recordCount':sum(r['schoolCode']==code for r in rows),'note':note,'scope':'仅本轮列明的官方页面及图表，不等同全校全渠道完整公开；未采不代表零录取。','sourceIds':[sid(k) for k in keys],'checkedUrls':[q['url'] for q in requests if q['key'] in keys]})
excluded=[{'schoolCode':'13283','school':'浙江农林大学暨阳学院','sourceIds':[sid('jy-gx'),sid('jy-table')],'rowCount':2,'reason':'只有历史/物理科类汇总，无专业字段；后续征求计划亦不入实际专业分或初始计划。'}, {'schoolCode':'10723','school':'渭南师范学院','sourceIds':[sid('wnu-'+str(i)) for i in [10,11,12,14,15,16]],'reason':'同快讯另外6图为山东/福建/黑龙江艺术或广东/内蒙古，不能迁至广西；本包仅采第4张广西普通类图。'}]
check('new-schools-only',not ({r['schoolCode'] for r in rows}&{r['schoolCode'] for r in context['baselineSchools']}))
check('not-in-current-20-targets',not ({r['schoolCode'] for r in rows}&set(context['excludedTargetSchoolCodes'])))
check('row-count',len(rows)==32)
check('cqc-count',sum(r['admittedCount'] for r in rows if r['schoolCode']=='12758')==20)
check('tlu-count',sum(r['admittedCount'] for r in rows if r['schoolCode']=='10383')==10)
check('wnu-count',sum(r['admittedCount'] for r in rows if r['schoolCode']=='10723')==66)
check('distinct-ids',len({r['id'] for r in rows})==len(rows))
check('wnu-tourism-keeps-admitted3',any(r['schoolCode']=='10723' and r['major']=='旅游管理' and r['admittedCount']==3 for r in rows))
sourceids={s['id'] for s in sources}
for r in rows:
 check(r['id']+'-source-closure',all(x in sourceids for x in r['sourceIds']) and all(x in sourceids for v in r['fieldSourceIds'].values() for x in v))
 check(r['id']+'-score-range',0<=r['score']<=r.get('sourceMaximumScore',750)<=750)
 check(r['id']+'-average-range','sourceAverageScore' not in r or r['score']<=r['sourceAverageScore']<=r['sourceMaximumScore'])
 check(r['id']+'-rank-group-unknown',r['rank'] is None and r['group'] is None)
 check(r['id']+'-no-plan-substitution','plannedCount' not in r)
check('historical-baseline-context',context['baselineRowCount']==1058 and len(context['baselineSchools'])==26)
check('wnu-explicit-current-title','2026年录取快讯' in txt('wnu-gx'))
check('cqc-identity-charter','4150012758' in txt('cqc-charter') and '重庆城市管理职业大学' in txt('cqc-charter'))
check('wnu-identity-charter','4161010723' in txt('wnu-charter'))
qa={'checkedAt':DATE,'summary':{'newSchools':3,'newActualRows':len(rows),'bySchool':dict(Counter(r['school'] for r in rows)),'byTrack':dict(Counter(r['track'] for r in rows)),'admittedCount':sum(r['admittedCount'] for r in rows),'checks':len(checks),'passed':sum(c['pass'] for c in checks),'failed':sum(not c['pass'] for c in checks)},'checks':checks,'limits':['无PDF；铜陵2行和渭南21行图片已逐行目视，待另人独审后冻结。','全部未知组码和位次保持null；未转换排名。','渭南表含投档录取混合表述，按录取快讯及实际录取数保留，原表头与文化分录取说明逐行可见。','不以实际录取人数更新计划。','本科/专科批次和轮次只以直接来源明示，不从录取日期推断首轮。']}
for name,data in [('major-cutoffs-upsert.json',rows),('sources.json',sources),('school-audit-notes.json',notes),('evidence-rows.json',evidence),('excluded-records.json',excluded),('QA.json',qa)]:write(name,data)
public=['major-cutoffs-upsert.json','sources.json','school-audit-notes.json','evidence-rows.json','excluded-records.json','QA.json','README.md','PUBLIC-FILES.json','collect.py','build.py','parse_tables.py','requests.json','image-transcription.tsv','baseline-context.json','code-sources.json','importer-preflight.json']
write('PUBLIC-FILES.json',{'publicFiles':public,'excluded':['raw/**','__pycache__/**'],'note':'原网页/图片/响应元数据仅本地；公开结构化统计事实、哈希和相对路径脚本。'})
print(json.dumps(qa['summary'],ensure_ascii=False));assert all(c['pass'] for c in checks),[c for c in checks if not c['pass']]
