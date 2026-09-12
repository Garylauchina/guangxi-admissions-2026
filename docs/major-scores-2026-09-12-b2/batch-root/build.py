"""Offline rebuild from frozen statistical facts and source metadata, no session or private path."""
from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parent;DATE='2026-09-12'
def load(n):return json.loads((ROOT/n).read_text())
def save(n,x):(ROOT/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def sid(n):return 'major-20260912b2-root-'+n.replace('.','-')
review=load('review-evidence.json');checks=list(review['checks'])
def check(n,c):
 assert c,n
 checks.append({'check':n,'passed':True})
definitions={
 'scnu':('10574','华南师范大学','entry-only-year-gap','读取招生官网、往年分数栏目、2026录取公告及外省计划页。2026计划附件不能充当录取分；当前外省专业分公告及11页PDF实为2025，已核对PDF第一页年份和第7页广西13个专业（历史6、物理7，合计行另计）。发布于2026并不改变统计年。所读公开页未提供2026广西专业分，未遍查全部公众号。'),
 'gdut':('11845','广东工业大学','entry-only-year-gap','当前历年分数导航最高为2025，进入2025广西专页并目视核对图片，内容为专业录取数、最高/平均/最低分和最低排名，仍属于2025。图片自身未列年份，依据其官方上级页面保持旧年；本轮所读官网栏目未取得2026广西专业分。'),
 'sduwh':('19422','山东大学威海分校','empty-current-response','按当前官网真实查询路由，2026广西普通类、国家专项的物理/历史四组GET均成功且显示无数据；2025普通类物理4、历史3条专业表作正对照。最初POST的中文省份/类型/科类被服务端转成问号，已明确弃用，不能算有效空表。菜单最高2025。威海按独立代码19422审查，不套用山东大学主校表；未覆盖类别不据此断言未公布。'),
 'zju':('19335','浙江大学医学院','entry-only-year-gap','沿浙江大学官网历年分数栏目检查，最新条目发布于2026-06-17，标题与正文实际为2025各省普通本一批投档线，表含ZJU-UoE及其他列。旧年院校汇总不能填成2026医学院具体专业分。保留独立代码19335；本轮仅核实共享招生栏目，不据此认定医学院所有渠道均未发布。'),
 'suda':('10285','苏州大学','empty-current-response','官网专业分目录最高2025；依据真实详情路由和广西省份选项aid=20查询，2025取得38个专业行，2026同路由没有专业表。标题由aa参数形成，不能仅凭页面2026标题认定存在本年数据；结合ay=2026与空表记录此入口缺口，不推断全校未发布。'),
 'uibe':('10036','对外经济贸易大学','collected-partial','现招生官网导航到公开历年分数查询，广西2026两科11个实际类别组合全部成功，专业数组共32行，其中2行少数民族预科汇总排除，纳入30条具体专业/正式大类，83人。含本科批18、提前批4、国家专项4、高校专项2、中外合作2。学校直接公布专业最低分排名，字段minOrder与表头“最低分排名”对应；不使用省/科类汇总数组。组码与再选科目未列，轮次未分；原名称中的项目选拔和分流说明保留。')}
labels={'home':'招生官网','scores':'历年分数查询入口','years':'往年分数栏目','prior-scores':'2025外省专业分','gx-2025':'2025广西专业分','current':'2026录取公告栏目','plan':'2026外省计划页','notice':'2026录取公告','latest':'最新栏目条目（实际2025）','charter':'2026本科招生章程','params':'公开查询菜单及字段表头','admissions':'当前招生导航','query':'官网实际查询路由','public-query':'公开录取查询前端（未查询个人信息）','guide':'招生报考指南'}
sources=[]
for m in load('source-manifest.json'):
 filename=m['name'];prefix=filename.split('-')[0];school=definitions[prefix][1];key=filename[len(prefix)+1:].rsplit('.',1)[0]
 label=labels.get(key,key.replace('gx-','广西 ').replace('get-','有效GET ').replace('history','历史').replace('physics','物理').replace('national','国家专项'))
 actual=filename.startswith('uibe-gx-2026-');year=2025 if '2025' in filename or 'prior-scores' in filename or filename=='zju-latest.html' else (2026 if actual or filename=='uibe-charter.html' else None)
 role='actual-major-score-response' if actual else 'source-review'
 if filename in ['uibe-gx-2026-4.json','uibe-gx-2026-9.json']:role='excluded-preparatory-summary'
 if filename.startswith('sduwh-gx-'):role='excluded-malformed-query-response'
 s={'id':sid(filename),'title':school+'：'+label,'url':m['url'],'publisher':school,'year':year,'publishedAt':'2026-06-05' if filename=='uibe-charter.html' else None,'accessedAt':m['checkedAt'],'sha256':m.get('sha256'),'responseSha256':m.get('responseSha256'),'requestMethod':m['requestMethod'],'requestData':m.get('data'),'httpStatus':m.get('httpStatus'),'evidenceRole':role,'archiveFile':filename,'method':'读取当前官方入口和真实公开查询参数；匿名会话仅用于官网正常防伪流程，不保存Cookie或CSRF值。','notes':[definitions[prefix][3]]}
 if m.get('error'):s['accessError']=m['error']
 sources.append(s)
codeSources=load('code-sources.json');sources.extend(codeSources);codeSource='gxeea-2026-33106';check('UIBE official code source retained',codeSource in {x['id'] for x in codeSources})
records=[];excluded=[];charter=sid('uibe-charter.html');param=sid('uibe-params.json')
for e in load('evidence-rows.json'):
 if not e['included']:excluded.append(e);continue
 r=e['fields'];src=sid(e['file']);track=r['klmc'].replace('类','');category=r['zslx'];typ='普通类' if category=='本科批' else ('普通类（提前批）' if category=='提前批' else category)
 check(e['file']+str(e['sourceRow'])+' score bounds/count/rank',0<=r['minScore']<=r['avgScore']<=r['maxScore']<=750 and r['rs']>0 and isinstance(r['minOrder'],int) and r['minOrder']>0 and (r['rs']!=1 or r['minScore']==r['maxScore']))
 req=[]
 if category=='提前批' or '外国语言文学类' in r['zymc']:req.append('章程列明的外语语言类专业只招英语考生，外国语言文学类的具体分流及语种要求请核对当年计划。')
 if '项目' in r['zymc'] or '选拔' in r['zymc']:req.append('原专业名称包含项目选拔或分流说明；达到本专业录取分不等于获得双学士、实验班等选拔项目资格。')
 if category=='国家专项':req.append('须满足国家专项报考资格，并按当年专项计划规定报考。')
 if category=='高校专项':req.append('须满足高校专项报考资格；章程要求投档成绩达到当地特殊类型招生控制线，按专项计划择优录取。')
 if category=='中外合作办学':req.append('只录取填报该专业志愿考生，入学后不得转入其他专业；保险学中外合作学费100000元/生/学年（在本校四年期间）。')
 field={k:[src] for k in ['year','province','track','major','score','batch','admittedCount','admissionType','sourceMaximumScore','sourceAverageScore','sourceMajorCode']}
 field.update(rank=[src,param],schoolCode=[codeSource],scoreBasis=[charter],note=[src,charter],admissionRequirements=[charter,src])
 note='学校按具体专业或正式招生大类公布的录取结果。最低分与排名均为学校直接公布；依章程按投档成绩录取至专业并认可规定的全国性政策加分，不称裸分。专业组码、再选科目及首次/征集轮次未列，保持未知。录取人数不转换为计划数。学校返回的专业代码另存原值，广西填报专业代号待核。'
 rec={'id':f"major-20260912b2-root-10036-{e['file'].split('-')[-1].split('.')[0]}-{e['sourceRow']}",
  'year':2026,
  'province':'广西',
  'schoolCode':'10036',
  'school':'对外经济贸易大学',
  'sourceSchool':'对外经济贸易大学',
  'track':track,
  'sourceTrack':r['klmc'],
  'batch':r['pcmc'],
  'round':'录取汇总（轮次未分）',
  'group':None,
  'major':r['zymc'],
  'majorCode':None,
  'sourceMajorCode':r['zydm'] or None,
  'score':r['minScore'],
  'scoreType':'专业录取最低分',
  'rank':r['minOrder'],
  'rankType':'专业最低分排名（学校公布）',
  'sourceId':src,
  'sourceIds':[src,param,charter,codeSource],
  'sourceRow':e['sourceRow'],
  'sourceTable':'sszygradeList',
  'reviewedAt':DATE,
  'evidenceStatus':'verified',
  'scoreComparable':True,
  'scoreBasis':'750分制普通高考总分（含学校认可的全国性政策加分）',
  'scoreScaleMaximum':750,
  'scoreEvidenceGaps':[],
  'conflictFields':[],
  'admissionType':typ,
  'sourceCategory':category,
  'requiredSubjects':[],
  'subjectRule':'unknown',
  'requirementText':'首选'+track+'；原成绩表未列再选科目',
  'fieldSourceIds':field,
  'admittedCount':r['rs'],
  'sourceMaximumScore':r['maxScore'],
  'sourceAverageScore':r['avgScore'],
  'sourceScoreHeader':'最低分',
  'sourceRankHeader':'最低分排名',
  'admissionRequirements':' '.join(req),
  'note':note}
 records.append(rec)
notes=[]
for prefix,(code,school,status,note) in definitions.items():
 ss=[s for s in sources if s['id'].startswith(sid(prefix+'-'))]
 notes.append({'id':'review-major-20260912b2-root-'+code,'year':2026,'province':'广西','schoolCode':code,'school':school,'auditKind':'major-scores','checkedAt':DATE,'title':'2026广西专业录取分来源核查','status':status,'recordCount':30 if code=='10036' else 0,'sourceIds':[s['id'] for s in ss],'checkedUrls':list(dict.fromkeys(s['url'] for s in ss)),'note':note,'scope':'仅限列明官方页面、附件和真实查询组合；未取得不等于未招生或所有渠道未发布。'})
check('six schools and30ranked actual rows',len(notes)==6 and len(records)==30 and all(r['rank'] for r in records))
check('83admitted and2prep excluded',sum(r['admittedCount'] for r in records)==83 and len(excluded)==2)
for fn,data in [('major-cutoffs-upsert.json',records),('sources.json',sources),('school-audit-notes.json',notes),('excluded-records.json',excluded)]:save(fn,data)
save('QA.json',{'status':'passed','reviewedAt':DATE,'newScoreRecords':30,'admittedCount':83,'reviewedSchools':6,'sources':len(sources),'checks':checks,'manualReview':review['manualReview'],'limits':['旧年正对照不导入','问题POST不视为有效广西查询','两个预科汇总排除','专业组和轮次未知','排名是专业表直接公布口径']})
print('PASS',len(checks),'checks;',len(records),'scores;',len(sources),'sources')
