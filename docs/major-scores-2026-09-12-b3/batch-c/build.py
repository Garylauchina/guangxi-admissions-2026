"""Build frozen 2026 Guangxi factual records from local official archives. No repository required."""
from pathlib import Path
from html import unescape
from collections import Counter
import json,csv,re,hashlib
from parse_tables import parse
BASE=Path(__file__).resolve().parent
DATE='2026-09-12'; PREFIX='major-20260912b3-c-'
def load(f):return json.loads((BASE/f).read_text())
def dump(f,v):(BASE/f).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def sha(f):return hashlib.sha256((BASE/f).read_bytes()).hexdigest()
def sid(k):return PREFIX+k
def text(k):return re.sub(r'\s+',' ',unescape(re.sub('<[^>]+>',' ',(BASE/'raw'/f'{k}.html').read_text())))
ctx=load('baseline-context.json'); req={r['key']:r for r in load('requests.json')}
info={
'mdj-score':('牡丹江师范学院2026年广西壮族自治区普通类本科批次录取公告','牡丹江师范学院','2026-07-28'),
'mdj-charter':('牡丹江师范学院2026年全日制普通本科招生章程','牡丹江师范学院','2026-05-26'),
'xync-10981':('咸阳师范学院2026年录取简报（十六）','咸阳师范学院','2026-07-25'),
'xync-11021':('咸阳师范学院2026年录取简报（十九）广西征集','咸阳师范学院','2026-07-27'),
'xync-charter':('咸阳师范学院2026年普通本科招生章程','咸阳师范学院','2026-06-08'),
'bjwl-1383':('宝鸡文理学院2026年录取快讯（九）','宝鸡文理学院','2026-07-19'),
'bjwl-charter':('宝鸡文理学院2026年普通本科招生章程','宝鸡文理学院','2026-06-03'),
'cdutcm-score':('成都中医药大学【2026】录取快讯第21期—广西普通本科批','成都中医药大学','2026-07-20'),
'cdutcm-image':('成都中医药大学2026广西普通本科批专业录取成绩原图','成都中医药大学','2026-07-20'),
'cdutcm-charter':('成都中医药大学2026年普通本科招生章程','成都中医药大学','2026-05-21'),
'cdutcm-plan-entry':('成都中医药大学公开招生计划查询及实际字段','成都中医药大学',None),
'cdutcm-plan-gx':('成都中医药大学2026广西招生计划查询回包（用于类别及名称核对）','成都中医药大学',None),
'kmmc-score':('昆明医科大学2026年录取简报（广西、山东、内蒙古、宁夏）','昆明医科大学','2026-07-20'),
'zafu-score':('浙江农林大学2026年广西本科普通批录取结束','浙江农林大学','2026-07-25'),
'gxust-home':('广西科技大学招生网2026招生录取数据入口','广西科技大学',None),
'gxust-wechat':('广西科技大学官方链接的2026招生录取数据微信页（访问验证）','广西科技大学',None),
}
sources=[]
for k,(title,pub,date) in info.items():
 r=req[k];m=load('raw/'+k+'.meta.json');f='raw/'+r['file']; digest=sha(f)
 sources.append({'id':sid(k),'title':title,'url':r['url'],'publisher':pub,'sourceType':'official','year':2026,'province':'广西','publishedAt':date,'accessedAt':DATE,'requestMethod':m['requestMethod'],'parameters':r.get('parameters',{}),'httpStatus':m['status'],'sha256':digest,'rawSha256':digest,'archiveSha256':digest,'archiveFile':f,'method':'公开页面或公开前端查询；完整原档仅本地保存，公开事实与哈希。'})
sources+=load('code-sources.json')
records=[];facts=[];exclusions=[]
checks=[]
def check(name,ok):checks.append({'check':name,'passed':bool(ok)})
def conditions(code,major):
 if code=='10233':
  t='章程按国家招生体检指导意见审核；师范类及体检意见列出的不宜就读情形建议慎报。'
  if major.startswith('英语') or major=='商务英语':t+='英语、商务英语专业只招英语语种考生。'
  if major=='地理科学':t+='地理科学不录取色盲考生。'
  if major in ['计算机科学与技术','软件工程','数据科学与大数据技术']:t+='不能准确在显示器上识别红、黄、绿、蓝、紫任何一种颜色的数码、字母者不予录取；非英语语种考生谨慎报考计算机类。'
  return t
 if code=='10722':
  t='章程所有专业不限制应试语种、无需口试；入学后公共外语原则上为英语。体检按国家指导意见及章程第十条。'
  if major in ['生物科学','材料化学','化学工程与工艺','特殊教育']:t+='本专业不录取色弱、色盲考生。'
  if major=='地理科学':t+='本专业不录取色盲考生。'
  if major=='财务管理':t+='不能准确识别红、黄、绿、蓝、紫任何一种颜色的导线、按键、信号灯、几何图形者不予录取。'
  if major in ['机器人工程','计算机科学与技术','智能科学与技术']:t+='不能准确在显示器上识别红、黄、绿、蓝、紫任何一种颜色的数码、字母者不予录取（章程对应专业项写“智能科学技术”）。'
  return t
 if code=='10721':
  t='章程公共外语及相关专业课程全部采用英语教学，非英语语种考生慎报；体检按国家指导意见及章程第十九条。'
  if major in ['学前教育','化学','化学工程与工艺','环境工程']:t+='本专业不录取色弱、色盲考生。'
  if major in ['人力资源管理','旅游管理']:t+='不能准确识别红、黄、绿、蓝、紫任何一种颜色的导线、按键、信号灯、几何图形者不予录取。'
  return t
 t='章程列明本专业不招色盲、色弱考生；大学英语为必修课，非英语语种考生慎报，须适应汉语教学及答卷。医学类还须结合章程第四部分及体检指导意见核查；肝功能异常、肢体功能障碍等为慎报建议，不改成绝对禁报。'
 if major=='护理学':t+='护理学建议女生身高不低于1.58米、男生不低于1.62米，属于建议。'
 if major in ['药学','智能医学工程','康复治疗学']:t+='本条在2026广西计划查询中明确为普通类，未带中高计划或中外合作后缀；未将全国章程中的同名合作项目条件混入。'
 return t

def add(code,key,table,row,major,track,low,high,count=None,avg=None,round=None,sourceHeader='最低分',extra=None):
 charter={'10233':'mdj-charter','10722':'xync-charter','10721':'bjwl-charter','10633':'cdutcm-charter'}[code]
 s=sid(key); c=sid(charter); school=ctx['schoolCodeEvidence'][code]['school']; codes=ctx['schoolCodeEvidence'][code]['sourceIds']; ss=[s,c]+codes
 batch={'10233':'普通类本科批次','10722':'本科（批次待核）','10721':'本科（批次待核）','10633':'本科普通批'}[code]
 r={'id':PREFIX+code+'-'+key+'-'+str(row),'year':2026,'province':'广西','schoolCode':code,'school':school,'track':track[:2],'sourceTrack':track,'batch':batch,'round':round or '录取汇总（轮次未分）','group':None,'major':major,'score':int(low),'scoreType':'专业录取最低分','rank':None,'rankType':None,'sourceId':s,'sourceIds':ss,'sourceTable':table,'sourceRow':row,'reviewedAt':DATE,'evidenceStatus':'verified','scoreComparable':True,'scoreBasis':'750分制普通高考总分（包含学校认可的政策加分口径）','scoreScaleMaximum':750,'scoreEvidenceGaps':[],'conflictFields':[],'admissionType':'普通类','requiredSubjects':[],'subjectRule':'unknown','requirementText':'首选'+track[:2]+'；原成绩表未列再选科目','sourceMaximumScore':int(high),'sourceScoreHeader':sourceHeader}
 if count is not None:r['admittedCount']=int(count)
 if avg is not None:r['sourceAverageScore']=float(avg)
 fields=['year','province','track','major','score','batch','round','admissionType','sourceMaximumScore','sourceScoreHeader']
 if count is not None:fields+=['admittedCount']
 if avg is not None:fields+=['sourceAverageScore']
 r['fieldSourceIds']={f:[s] for f in fields};r['fieldSourceIds'].update({'schoolCode':codes,'school':[c],'note':[s,c],'scoreBasis':[c]})
 note='原表为2026广西具体专业录取结果；学校以认可政策加分后的投档成绩录取及安排专业，原表未拆分加分值。'
 if code=='10722':note+='原字段为“投档录取最低分”，结合普通类专业录取栏目及实际录取人数采作专业录取分；“录取最低分同分排位”仅同分序号，省位次保持未知。'
 if code in ['10721','10722']:note+='本科层次由2026章程确认，快讯未明示广西精确批次，批次待核。'
 if not round:note+='原公告未明示首次或具体征集轮次，保留录取汇总。'
 else:note+='本条为原文明确的普通类征集录取，未推断第几次征集。'
 note+='组码未列不推断；实际录取人数不作为招生计划。'+conditions(code,major)
 r['note']=note
 if extra:r.update(extra)
 records.append(r);return r

# Full official HTML tables; positions are one-based table and row, including header.
t=parse(BASE/'raw/mdj-score.html')[2];check('牡丹江表头',t['rows'][0]==['专业','科类','计划数','录取数','最高分','最低分','省线','线差'])
for row,v in enumerate(t['rows'][1:],2):
 add('10233','mdj-score',3,row,v[0],v[1],v[5],v[4],v[3]);facts.append({'sourceKey':'mdj-score','table':3,'row':row,'cells':v})
 check('牡丹江线差行'+str(row),int(v[5])-int(v[6])==int(v[7]))
for key,ix in [('xync-10981',3),('xync-11021',0)]:
 ts=parse(BASE/'raw'/f'{key}.html');t=ts[ix];check(key+'广西上下文','广西壮族自治区普通类' in t['context'])
 for j,other in enumerate(ts):
  if j!=ix:exclusions.append({'sourceKey':key,'sourceTable':j+1,'rowCount':len(other['rows'])-1,'reason':'同公告其他省份，非广西；不导入。'})
 for row,v in enumerate(t['rows'][1:],2):
  normal=key=='xync-10981';lo,hi,tie=(6,5,7) if normal else (5,4,6)
  r=add('10722',key,ix+1,row,v[0],v[1],v[lo],v[hi],v[3],round=None if normal else '征集（次数未分）',sourceHeader=t['rows'][0][lo],extra={'sourceTieBreakOrder':int(v[tie])})
  r['fieldSourceIds']['sourceTieBreakOrder']=[sid(key)]
  if normal and v[4]:r['sourceWithdrawnCount']=int(v[4]);r['fieldSourceIds']['sourceWithdrawnCount']=[sid(key)];r['note']+='本表该专业计划3人、实际录取2人、退档1人、缺额1人；另一公告的征集录取单列，未合并覆盖。'
  facts.append({'sourceKey':key,'table':ix+1,'row':row,'cells':v})
t=parse(BASE/'raw/bjwl-1383.html')[0];check('宝鸡表头含录取人数','录取人数' in t['rows'][0])
for row,v in enumerate(t['rows'][1:],2):
 if v[0]!='广西':exclusions.append({'sourceKey':'bjwl-1383','sourceTable':1,'sourceRow':row,'province':v[0],'reason':'非广西，不导入。'});continue
 r=add('10721','bjwl-1383',1,row,v[1],v[2],v[6],v[5],v[4],v[7])
 if '化学' in v[2]:r.update(requiredSubjects=['化学'],subjectRule='all',requirementText='首选物理，再选化学');r['fieldSourceIds']['requiredSubjects']=[sid('bjwl-1383')]
 facts.append({'sourceKey':'bjwl-1383','table':1,'row':row,'cells':v})
plans=load('raw/cdutcm-plan-gx.json');check('成中医计划查询成功完整14行',plans['code']==0 and plans['count']==len(plans['data'])==14)
for v in csv.DictReader((BASE/'image-transcription.tsv').open(),delimiter='\t'):
 original=v['sourceMajor'];major='中医骨伤科学' if original=='中医骨伤学' else original
 matches=[p for p in plans['data'] if p['year']=='2026' and p['province']=='广西' and p['majorname']==major and p['category']==v['sourceTrack'] and p['typeitem']=='普通类' and p['batch']=='本科普通批']
 check('成中医计划名称类别一对一'+v['sourceRow'],len(matches)==1)
 r=add('10633','cdutcm-image',1,int(v['sourceRow']),major,v['sourceTrack'],v['score'],v['sourceMaximumScore'],sourceHeader='最低分',extra={'sourceMajor':original})
 r['sourceIds']+=[sid('cdutcm-score'),sid('cdutcm-plan-entry'),sid('cdutcm-plan-gx')]
 for f in ['year','province','batch','round']:r['fieldSourceIds'][f]=[sid('cdutcm-score')]
 r['fieldSourceIds']['admissionType']=[sid('cdutcm-plan-entry'),sid('cdutcm-plan-gx')]
 r['fieldSourceIds']['sourceMajor']=[sid('cdutcm-image')]
 r['fieldSourceIds']['note']+=[sid('cdutcm-plan-gx')]
 if major!=original:r['fieldSourceIds']['major']+=[sid('cdutcm-plan-gx')];r['note']+='成绩图原名称“中医骨伤学”，同期广西官方计划为“中医骨伤科学”，保留sourceMajor原词，并按唯一对应计划正式名称展示。'
 r['note']+='正文只给本科普通批合计43人（物理39、历史4），图中未给各专业实际人数，逐专业admittedCount不填；未由计划人数推定。'
 facts.append({'sourceKey':'cdutcm-image','table':1,'row':int(v['sourceRow']),'cells':[original,v['sourceMaximumScore'],v['score'],v['sourceTrack']]})

for key,reason in [('kmmc-score','2026广西仅学校本科普通批汇总30人及最高587、最低421，无具体专业表。'),('zafu-score','2026广西仅物理/历史/国家专项科类投档汇总，不据计划拆专业。'),('gxust-wechat','官方招生主页链接2026数据微信页；HTTP200响应为访问环境验证，正文未读取，不能声称成功空数据。')]:exclusions.append({'sourceKey':key,'reason':reason})
notes=[]
counts=Counter(r['schoolCode'] for r in records)
for code in counts:
 rr=[r for r in records if r['schoolCode']==code];ss=list(dict.fromkeys(s for r in rr for s in r['sourceIds'] if s.startswith(PREFIX)))
 n={'10233':'完整普通类本科公告22行，历史8、物理14，实际61人；英语语种和体检限制已逐项备注。', '10722':'普通类专业表18行、实际66人，征集另1行1人；原“投档录取最低分”和同分排位保留。精确本科批次未在快讯明示，不推首轮；征集未指明次数。', '10721':'第九期快讯广西完整14行、实际28人；化学再选由原表直接保留，其他省5行排除。精确本科批次及首次轮次未明示。', '10633':'广西普通本科批完整原图12行，正文总录取43人但各专业人数未公开；同期计划核对为普通类，不把人数当实际录取。中医骨伤学按同年同省唯一计划名称中医骨伤科学规范并保留原词。'}[code]
 notes.append({'id':'major-audit-20260912b3-c-'+code,'auditKind':'major-scores','year':2026,'province':'广西','schoolCode':code,'school':rr[0]['school'],'checkedAt':DATE,'status':'collected','recordCount':len(rr),'note':n,'scope':'仅列明2026广西官方公告及配套章程；完整公告不代表全部招生通道。未列组码/位次/精确轮次保持未知。','sourceIds':ss,'checkedUrls':[s['url'] for s in sources if s['id'] in ss]})
for code,school,key,status in [('10678','昆明医科大学','kmmc-score','source-found'),('10341','浙江农林大学','zafu-score','source-found'),('10594','广西科技大学','gxust-wechat','entry-only')]:
 notes.append({'id':'major-audit-20260912b3-c-'+code,'auditKind':'major-scores','year':2026,'province':'广西','schoolCode':code,'school':school,'checkedAt':DATE,'status':status,'recordCount':0,'note':next(x['reason'] for x in exclusions if x.get('sourceKey')==key),'scope':'仅列明实际读取页面，不证明该校未发布其他数据或零录取。','sourceIds':[sid(key)]+([sid('gxust-home')] if code=='10594' else []),'checkedUrls':[req[key]['url']]})
# Conditions and actual rows: independent checks over exclusions, bounds, table sums and source IDs.
check('总数67/4校',len(records)==67 and len(counts)==4)
check('基线无覆盖交叉',not set(counts)&set(ctx['baselineSchools']))
check('目标无交叉',not set(counts)&set(ctx['excludedTargetSchools']))
check('牡丹江实际61',sum(r.get('admittedCount',0) for r in records if r['schoolCode']=='10233')==61)
check('咸阳前表实际66',sum(r.get('admittedCount',0) for r in records if r['sourceId']==sid('xync-10981'))==66)
check('咸阳征集1',sum(r.get('admittedCount',0) for r in records if r['sourceId']==sid('xync-11021'))==1)
check('宝鸡实际28',sum(r.get('admittedCount',0) for r in records if r['schoolCode']=='10721')==28)
check('成都不推实际人数',all('admittedCount' not in r for r in records if r['schoolCode']=='10633'))
source_ids={s['id'] for s in sources}
for r in records:
 check(r['id']+'上下界',0<=r['score']<=r['sourceMaximumScore']<=750)
 check(r['id']+'来源闭合',set(r['sourceIds'])<=source_ids and all(set(v)<=set(r['sourceIds']) for v in r['fieldSourceIds'].values()))
 if 'sourceAverageScore' in r:check(r['id']+'均值区间',r['score']<=r['sourceAverageScore']<=r['sourceMaximumScore'])
 check(r['id']+'非伪位次与组码',r['rank'] is None and r['group'] is None)
check('稳定id不重复',len({r['id'] for r in records})==len(records))
for s in sources:
 if s['id'].startswith(PREFIX):check('原档哈希 '+s['id'],sha(s['archiveFile'])==s['archiveSha256'])
for f,v in [('major-cutoffs-upsert.json',records),('sources.json',sources),('school-audit-notes.json',notes),('evidence-rows.json',facts),('excluded-records.json',exclusions)]:dump(f,v)
qa={'status':'PASS' if all(c['passed'] for c in checks) else 'FAIL','checkedAt':DATE,'recordCount':len(records),'schoolCount':len(counts),'recordsBySchool':dict(counts),'actualAdmissionsWithPerMajorCounts':sum(r.get('admittedCount',0) for r in records),'missingPerMajorCounts':sum('admittedCount' not in r for r in records),'sourceArchivesChecked':len(info),'sourceTableNotes':{'mdj':'Nested HTML content table #3','xync':'#4 Guangxi table in issue16; issue19 #1 is explicit solicited admission','bjwl':'#1 rowspan-expanded Guangxi rows7–20','cdutcm':'image rows2–13, read visually; year/province from enclosing official2026GX page'},'imageVisualReview':{'file':'raw/cdutcm-image.png','rows':12,'yearProvinceVerifiedFrom':'cdutcm-score official page containing exact linked image','header':'录取专业/最高分/最低分/类别','status':'人工目视转录完成；外部独审另报'},'checks':checks,'passed':sum(c['passed'] for c in checks),'failed':sum(not c['passed'] for c in checks),'recordSha256':sha('major-cutoffs-upsert.json'),'scope':'冻结于2026-09-12；原始全文/图和会话不公开，仅PUBLIC-FILES白名单可公开。'}
dump('QA.json',qa)
print(json.dumps({k:qa[k] for k in ['status','recordCount','schoolCount','passed','failed','recordSha256']},ensure_ascii=False))
if qa['failed']:raise SystemExit(1)
