"""Offline build from retained official responses. Python 3 standard library only.
Freeze audit-context.json once; subsequent builds never derive an audit date from NOW.
"""
from pathlib import Path
import json,re,hashlib,datetime
from collections import Counter
from html import unescape
R=Path(__file__).resolve().parent;RAW=R/'raw';P='major-20260912b3-b-'
SCHOOLS={'ecust':('10251','华东理工大学'),'shu':('10280','上海大学'),'ouc':('10423','中国海洋大学'),'sztu':('14655','深圳技术大学'),'dhu':('10255','东华大学'),'njupt':('10293','南京邮电大学'),'nnu':('10319','南京师范大学')}
def read(n):return (RAW/n).read_text()
def load(n):return json.loads(read(n))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,d):(R/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def plain(s):return re.sub(r'\s+',' ',unescape(re.sub('<[^>]+>','',s))).strip()
metas=[json.loads(p.read_text()) for p in sorted(RAW.glob('*.meta.json'))]
context=R/'audit-context.json'
if not context.exists():
 ts=max(datetime.datetime.fromisoformat(m['checkedAt']) for m in metas)
 save('audit-context.json',{'reviewedAt':ts.astimezone(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),'year':2026,'province':'广西','baselineCommit':'89383ef','baselineMajorRecords':1120,'baselineMajorSchools':30,'scope':list(SCHOOLS.values())})
CTX=json.loads(context.read_text());AT=CTX['reviewedAt'];checks=[]
def ck(n,b):checks.append({'name':n,'passed':bool(b)})
S=[]
for m in metas:
 key=m['id'].split('-')[0];school=SCHOOLS.get(key,('', '广西招生考试院'))[1]
 fn=m.get('archiveFile');path=RAW/fn if fn else None
 if path:ck('Archive SHA '+m['id'],path.exists() and sha(path)==m['archiveSha256'])
 count=None
 if m['id'].startswith('ouc-gx') and fn:count=len(load(fn).get('data',{}).get('sszygradeList',[]))
 method=m.get('accessMethod','按官方页面及实际前端取得公开材料；保存原响应与脱敏归档指纹，会话值仅在内存。')
 if m['id'].startswith('ouc-gx'):method+=' 使用学校实际专业统计表；另表省科类汇总不作专业分，预科汇总不纳入本批。'
 if m['id']=='gx-code-source':method='按页面声明GBK读取；本批仅核验10423对应中国海洋大学，不据组投档最低分生成实际专业分或推断组码、批次。'
 if m['id'].startswith('shu-gx'):method+=' 官方响应仅更新网格，没有再次回显所选年、省；原表单请求值与旧年广西正对照共同留证，本年菜单未配置。'
 pub={'ouc-charter':'2026-05-28','ouc-cooperation':'2026-06-04','sztu-current':'2026-09-01','dhu-gx-2025':'2026-03-30','gx-code-source':'2026-07-18'}.get(m['id'])
 S.append({'id':P+m['id'],'title':school+'官方来源核查：'+m['id'],'url':m['url'],'publisher':school,'sourceType':'official','publishedAt':pub,'accessedAt':m['checkedAt'],
           'sha256':m.get('archiveSha256'),'rawSha256':m.get('rawSha256'),'archiveSha256':m.get('archiveSha256'),'archiveFile':'raw/'+fn if fn else None,
           'httpStatus':m.get('status'),'accessOutcome':'response-received' if fn else 'access-failed','requestMethod':'POST' if 'data' in m else 'GET','requestParams':m.get('data',{}),'accessError':m.get('error'),'method':method,'recordCount':count})
rows=[];excluded=[];param=load('ouc-params.json');configured=set()
for entry in param['data']['ssmc_nf_klmc_sex_campus_zslx_list']:
 for k,v in entry.items():
  a=k.split('_')
  if a[:2]==['广西','2026']:configured.update((a[2],c) for c in v)
ck('OUC actual menu has nine 2026 Guangxi combinations',len(configured)==9)
entry=read('ouc-scores.html');charter=plain(read('ouc-charter.html'))
ck('Professional table maps direct minimum/average/maximum fields',all(t in entry for t in ['id="sszygradeList"',"out($value,'minScore'","out($value,'avgScore'","out($value,'maxScore'",'<th>专业</th>']))
ck('2026 charter permits policy bonus in actual professional allocation','2026年本科招生章程' in charter and '投档分（含政策性加分）进行专业安排' in charter)
ck('Code 10423 independently identified in official Guangxi source',bool(re.search(r'10423</td><td[^>]*>中国海洋大学</td>',read('gx-code-source.html'))))
seen=set();fieldsCompared=0
weak=['海洋科学','海洋技术','轮机工程','化学','化学工程与工艺','材料类','生物科学','生物科学类','地质学','地球信息科学与技术','环境工程','工业设计','水产养殖学','海洋资源与环境','海洋渔业科学与技术','食品科学与工程类','药学']
color=['经济学','工商管理','市场营销','会计学','财务管理','公共事业管理','行政管理']
for i in range(1,10):
 name=f'ouc-gx-2026-{i}';d=load(name+'.json');m=load(name+'.meta.json');q=m['data'];seen.add((q['klmc'],q['zslx']))
 ck('OUC query state and actual params '+str(i),d['state']==1 and q['ssmc']=='广西' and q['zsnf']=='2026' and (q['klmc'],q['zslx']) in configured)
 for j,x in enumerate(d['data']['sszygradeList'],1):
  if x['zslx']=='少数民族预科班':excluded.append({'sourceId':P+name,'sourceRow':j,'major':x['zymc'],'reason':'少数民族预科班汇总，不是具体专业实际录取分'});continue
  ck('Year/province/category '+name+'-'+str(j),x['nf']=='2026' and x['ssmc']=='广西' and x['klmc']==q['klmc'] and x['zslx']==q['zslx'])
  ck('Numeric order '+name+'-'+str(j),0<=x['minScore']<=x['avgScore']<=x['maxScore']<=750)
  major=x['zymc'];cat=x['zslx'];sid=P+name;common=[sid,P+'ouc-scores',P+'ouc-charter',P+'gx-code-source']
  requirement='首选'+x['klmc'][:2]+'；原成绩表未列再选科目。'
  req='普通类录取外语语种不作限制，学校建议英语，其他语种考生谨慎报考。'
  stem=re.split('[（(]',major)[0]
  if stem in weak:req+='章程列明本专业轻度色觉异常（色弱）或色盲原则上不予录取。'
  elif stem=='大气科学':req+='章程列明本专业色盲原则上不予录取。'
  elif stem in color:req+='章程规定不能准确识别红、黄、绿、蓝、紫任一种颜色导线、按键、信号灯、几何图形者原则上不予录取。'
  elif stem in ['计算机类','计算机科学与技术']:req+='章程规定不能准确在显示器上识别红、黄、绿、蓝、紫任一种颜色数码或字母者原则上不予录取计算机类。'
  subjects=[];rule='unknown';field={k:[sid,P+'ouc-scores'] for k in ['year','province','track','major','score','sourceMaximumScore','sourceAverageScore','admissionType']};field['schoolCode']=[P+'gx-code-source'];field['scoreBasis']=[P+'ouc-charter'];field['admissionRequirements']=[P+'ouc-charter']
  if cat=='高校专项计划':req+='须符合高校专项计划资格；章程要求投档成绩达到生源省特殊类型招生控制分数线，并按当地规定在相应批次填报。'
  if cat=='国家专项计划':req+='国家专项计划按教育部有关规定和学校招生要求录取，须核实相应资格。'
  if cat=='中外合作办学':
   req+='中外合作办学在校期间不能调整至非中外合作专业，建议非英语语种考生谨慎填报。'
   subjects=['化学'];rule='all';requirement='同时选考物理、化学方可报考。';common.append(P+'ouc-cooperation')
   field['admissionRequirements'].append(P+'ouc-cooperation');field['requiredSubjects']=[P+'ouc-cooperation'];field['subjectRule']=[P+'ouc-cooperation'];field['requirementText']=[P+'ouc-cooperation']
   if stem=='计算机科学与技术':req+='3+1培养，前三年国内学费70000元/年，第四年须赴英国赫瑞-瓦特大学学习并按当年标准缴学费，同时向海大缴注册费；核心课程全英文授课。'
   elif stem=='物理学':req+='3+1培养，前三年国内学费75000元/年，第四年须赴英国赫瑞-瓦特大学学习并按当年标准缴学费，同时向海大缴注册费。'
   elif stem=='海洋科学':req+='国内学费52000元/年，可选择4+0、2+2或3+2培养模式，境外费用依当年合作校标准。'
  batch=x.get('pcmc') or ('本科提前批（具体批次待核）' if cat=='普通类-提前批' else '本科（批次待核）')
  r={'id':P+'10423-'+str(i)+'-'+str(j),'year':2026,'province':'广西','schoolCode':'10423','school':'中国海洋大学','track':x['klmc'][:2],'sourceTrack':x['klmc'],'batch':batch,'sourceBatch':x.get('pcmc') or None,'round':'录取汇总（轮次未分）','group':None,'major':major,'majorCode':None,'sourceMajorCode':x.get('zydm') or None,'score':x['minScore'],'sourceMaximumScore':x['maxScore'],'sourceAverageScore':x['avgScore'],'rank':None,'admittedCount':None,'plannedCount':None,'sourceCategory':cat,'admissionType':'普通类（提前批）' if cat=='普通类-提前批' else cat,'scoreType':'专业录取最低分','scoreScaleMaximum':750,'scoreBasis':'学校按高考投档分（含符合规定的政策性加分）安排专业；原成绩表未拆分政策加分。','scoreComparable':True,'scoreEvidenceGaps':[],'conflictFields':[],'evidenceStatus':'verified','sourceId':sid,'sourceIds':common,'fieldSourceIds':field,'sourceTable':'sszygradeList','sourceRow':j,'sourceNote':x.get('remarks') or '', 'requiredSubjects':subjects,'subjectRule':rule,'requirementText':requirement,'admissionRequirements':req,'reviewedAt':AT,'note':'学校按具体专业或正式招生大类公布的录取结果；最低、平均及最高分均保留原表值。原表未公布录取人数、专业位次、专业组码及分轮次结果，精确批次尚待核实。政策加分未在成绩表中单列。'}
  rows.append(r);fieldsCompared+=3
ck('Configured queries fully represented',seen==configured)
ck('Only 60 actual rows; 2 prep summaries excluded',len(rows)==60 and len(excluded)==2)
ck('Expected track/category coverage',Counter(r['track'] for r in rows)=={'物理':46,'历史':14} and Counter(r['sourceCategory'] for r in rows)=={'普通类':47,'普通类-提前批':1,'高校专项计划':2,'国家专项计划':7,'中外合作办学':3})
ck('No fabricated group/code/rank/count',all(r['group'] is None and r['majorCode'] is None and r['rank'] is None and r['admittedCount'] is None and r['plannedCount'] is None for r in rows))
ck('Unique actual identities',len({(r['track'],r['major'],r['admissionType'],r['batch']) for r in rows})==60)
# Negative checks are tied to original response bodies, not assertions of non-publication.
ecust={}
for year in [2025,2026]:
 for kl in ['physics','history']:
  d=load(f'ecust-gx-{year}-{kl}.json');ck(f'ECUST valid query {year} {kl}',d.get('code')==200 and d.get('success') is True);ecust[f'{year}-{kl}']=len(d['list'])
ck('ECUST old positives and current empty',ecust=={'2025-physics':25,'2025-history':2,'2026-physics':0,'2026-history':0})
shu={}
for y,c in [(2025,'normal'),(2026,'normal'),(2026,'coop'),(2026,'national'),(2026,'special')]:
 s=read(f'shu-gx-{y}-{c}.html');m=re.search(r'"RecordCount":(\d+)',s);shu[f'{y}-{c}']=int(m.group(1)) if m else None;ck(f'SHU successful FineUI grid {y} {c}',m is not None and "F('Panel1_Grid1')" in s)
ck('SHU old positive and current empty',shu=={'2025-normal':6,'2026-normal':0,'2026-coop':0,'2026-national':0,'2026-special':0})
ck('SZTU 2026 province menu empty',read('sztu-provinces-2026.js').strip()=='')
ck('SZTU selected-province 2026 no-record message','该省份今年无录取信息' in read('sztu-gx-2026.js'))
ck('SZTU 2025 Guangxi directly identified','2025年在广西的录取情况' in plain(read('sztu-gx-2025.js')) and '智能医学工程' in read('sztu-gx-2025.js'))
ck('DHU original title is 2025 Guangxi','东华大学2025年广西本科一批录取分数一览表' in read('dhu-gx-2025.html'))
ck('NJUPT directory links 2025 workbook','南京邮电大学2025年录取情况统计表' in read('njupt-scores.html'))
ck('NNU actual HTTP and HTTPS both failed 412',load('nnu-home.meta.json')['status']==412 and load('nnu-https.meta.json')['status']==412)
N=[]
def note(key,status,limit,entry,text,summary):
 code,school=SCHOOLS[key];ss=[s for s in S if s['id'].startswith(P+key+'-')]
 N.append({'id':'review-20260912b3-b-'+code,'auditKind':'major-scores','year':2026,'province':'广西','schoolCode':code,'school':school,'checkedAt':AT,'status':status,'accessLimitType':limit,'entryUrl':entry,'sourceIds':[s['id'] for s in ss],'checkedUrls':sorted({s['url'] for s in ss}),'note':text,'resultSummary':summary,'collectedMajorRecordCount':60 if key=='ouc' else 0})
note('ouc','collected-partial','missing-group-rank-count-batch-round','https://lqcx.ouc.edu.cn/static/front/ouc/basic/html_web/lnfs.html','官方2026广西9类组合全部查询，取得60条具体专业或正式大类实际最低、最高及平均分，另2条预科汇总排除。物理46、历史14，包含普通类、提前批、国家专项、高校专项及中外合作。原表不提供人数、专业位次、专业组和精确批次，不推测。章程说明专业安排认可符合规定的政策加分；保留语种、健康、合作项目及专项资格条件。本批不代表专业计划或首轮完整分组覆盖。',{'configuredCombinations2026':9,'collected':60,'excludedPreparatorySummaries':2,'tracks':dict(Counter(r['track'] for r in rows)),'sourceCategories':dict(Counter(r['sourceCategory'] for r in rows))})
note('ecust','empty-current-response','year-unavailable-and-empty-query','https://bkzsdata.ecust.edu.cn/zsdata/lqxx/#/lnfs','已读官方新前端和筛选字段，旧、新参数配置均最高2025。按真实新接口字段查询2026广西理工类/物理类、文史类/历史类，类别、选科和批次选全部，均code=200/success=true且专业表为空；2025同条件分别25、2条。历史旧年2条属民族班，未误称普通类正对照。请求条件保存在元数据；空响应本身未再次回显筛选条件。本轮未取得本年专业分，不断言其他渠道未发布。',{'currentSuccessfulEmptyScoreQueries':2,'requestConditionEcho':False,'positiveControl2025Rows':{'物理':25,'历史':2},'configurationLatestYear':2025})
note('shu','empty-current-response','year-unavailable-and-empty-grid','https://bks.shu.edu.cn/pub/scores.aspx','专业查询菜单最高2025；通过官方FineUI表单正常会话与状态交换，2025广西一本取得6条正式大类（物理及物理化学5、历史1），2026广西一本、一本中外、国家专项、高校专项四次返回RecordCount=0。响应只更新网格而不回显年、省，查询条件和旧年正对照分别留证；本年菜单未配置，空网格不构成已发布或全面无数据的证明。另找到2026各省最低线候选，但本轮正文访问403未读；未作为专业分证据。',{'currentSuccessfulEmptyScoreQueries':4,'requestConditionEcho':False,'positiveControl2025MajorRows':6,'configurationLatestYear':2025,'currentCandidateBodyAccess':'HTTP403','currentCandidateUsedForMajorScores':False})
note('sztu','empty-current-response','year-unavailable-and-explicit-no-record','https://zs.sztu.edu.cn/bkzn/lnlq1.htm','官方年份菜单最新2025；2026省份联动返回空选项，按真实表单路径及参数查询2026广西，HTTP200显示“该省份今年无录取信息”。2025广西同路径有14条专业行（历史3、物理11）。空结果页面未再次回显所选年、省，故只据实际请求记录本轮未取得数据，不当成无招生。另核对2026年9月1日招录大数据长图，广西604等为省级录取线，不能拆为专业分。',{'currentNoRecordScoreQueries':1,'requestConditionEcho':False,'currentProvinceOptions':0,'positiveControl2025MajorRows':14,'configurationLatestYear':2025,'currentNewsAggregateExcluded':True})
note('dhu','entry-only-year-gap','latest-table-is-prior-year','https://zs.dhu.edu.cn/9564/list.htm','官方一般类、高校专项、国家专项分数目录已查，最新为2025资料；广西具体表虽2026年3月30日发布，正文明确“东华大学2025年广西本科一批录取分数一览表”。表内21条具体专业/大类与3条科类总计分别识别，均不转成2026。本轮未找到可采本年专业分，不扩大为所有渠道均未发布。',{'latestObservedScoreYear':2025,'positiveControl2025MajorRows':21,'excludedAggregateRows':3,'publicationYearDoesNotEstablishScoreYear':True})
note('njupt','entry-only-year-gap','latest-table-is-prior-year','https://zs.njupt.edu.cn/2564/listm.htm','官方往年录取目录最高2025，直接下载原Excel；广西工作表标题明确“南京邮电大学2025年各专业录取分数统计（广西）”，专业、人数、最高、最低、位次及平均分列均为旧年，不能按2026网站/访问日期改年。本轮没有取得2026广西实际专业分。',{'latestObservedScoreYear':2025,'priorWorkbookGuangxiTitle':'南京邮电大学2025年各专业录取分数统计（广西）'})
note('nnu','access-limited','http-412-entry-unavailable','http://bkzs.njnu.edu.cn','由学校公开招生章程所指本科招生网址尝试HTTP及HTTPS，均返回412；网页读取渠道同样失败。本轮未能读取真实查询菜单、年份配置或广西正对照，因此不作本年空表或尚未发布的判断，未采专业分。',{'httpAttemptStatuses':[412,412],'configurationRead':False,'currentSuccessfulEmptyScoreQueries':0})
ids={s['id'] for s in S};ck('All row/note field source references resolve',all(set(r.get('sourceIds',[])+list(z for v in r.get('fieldSourceIds',{}).values() for z in v))<=ids for r in rows+N))
ck('Seven assigned school notes',len(N)==7 and {x['schoolCode'] for x in N}=={v[0] for v in SCHOOLS.values()})
ck('No private path in public output',not re.search(r'/(?:Users|home)/[A-Za-z]',json.dumps([S,rows,N],ensure_ascii=False)))
for n,d in [('major-cutoffs-upsert.json',rows),('sources.json',S),('school-audit-notes.json',N)]:save(n,d)
q={'status':'PASS' if all(x['passed'] for x in checks) else 'FAIL','reviewedAt':AT,'summary':{'actualMajorRecords':len(rows),'actualSchools':1,'schoolNotes':len(N),'sources':len(S),'archivedSources':sum(bool(s['archiveFile']) for s in S),'failedAccessAttempts':sum(not bool(s['archiveFile']) for s in S),'numericFieldsChecked':fieldsCompared,'checks':len(checks),'passedChecks':sum(x['passed'] for x in checks),'currentSuccessfulEmptyApiOrGridQueries':6,'currentExplicitNoRecordQueries':1,'groupKnownRows':0,'rankKnownRows':0,'admittedCountKnownRows':0},'excluded':excluded,'checks':checks,'visualReview':{'sztuNews':'2026 full long infographic and province-score section inspected; school/province aggregates, no Guangxi single-major cutoff imported.'},'outputHashes':{f:sha(R/f) for f in ['major-cutoffs-upsert.json','sources.json','school-audit-notes.json']}}
save('QA.json',q);print(json.dumps({'status':q['status'],'summary':q['summary'],'failed':[c for c in checks if not c['passed']]},ensure_ascii=False,indent=2))
if q['status']!='PASS':raise SystemExit(1)
