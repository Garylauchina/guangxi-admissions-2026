"""Build reviewed root scores and bounded negative evidence; raw stays local."""
import json,re,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parent
RAW=ROOT/'raw'
DATE='2026-09-10'
def read(name):return json.loads((RAW/name).read_text())
def save(name,data):(ROOT/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
sources=[]
def source(key,file,title,publisher,year=None,date=None):
    mfile=file+'.meta.json'
    if not (RAW/mfile).exists():mfile=file.removesuffix('.json')+'.meta.json'
    m=read(mfile)
    s={'id':'major-score-root-'+key,'title':title,'url':m['url'],'publisher':publisher,'publishedAt':date,'accessedAt':m['checkedAt'],'sha256':m['sha256'],'sourceDataYear':year,'method':'官方公开页面或页面原有查询接口；会话仅在内存中使用，不发布会话字段。','requestMethod':m['method'],'notes':[]}
    if m.get('requestData') is not None:s['requestData']=m['requestData']
    for k in ['archiveSha256','redactedFields']:
      if k in m:s[k]=m[k]
    sources.append(s);return s['id']
hust=source('hust-scores','hust-scores.html','华中科技大学分省分专业分数线（可选2025/2024/2023）','华中科技大学')
hit=source('hit-scores','hit-scores-entry.html','哈尔滨工业大学分省分专业录取分数查询','哈尔滨工业大学')
hit26=source('hit-query-2026','hit-scores-2026.html','哈尔滨工业大学广西2026查询探查（实际回退到2025）','哈尔滨工业大学',2025)
sysupar=source('sysu-params','sysu-score-params.json','中山大学历年分数菜单（广西最新2025）','中山大学')
sysu26=[source('sysu-2026-'+t,'sysu-scores-2026-'+t+'.json','中山大学广西2026'+t+'普通录取查询（空响应）','中山大学',2026) for t in ['物理类','历史类']]
sysu25=source('sysu-control-2025','sysu-scores-2025-物理类.json','中山大学广西2025物理普通录取查询（旧年正向对照）','中山大学',2025)
sxy=source('sxyyc-recheck','sxyyc-scores.html','重庆三峡医药高等专科学校2026录取结果复查（2条冲突未修正）','重庆三峡医药高等专科学校',2026)
zjpage=source('zjiet-page','zjiet-gx-scores.html','【广西】2026年分专业录取情况一览表','浙江经贸职业技术学院',2026,'2026-08-13')
zjimage=source('zjiet-table','zjiet-gx-scores.png','浙江经贸职业技术学院2026广西专业录取结果原图','浙江经贸职业技术学院',2026,'2026-08-13')
sources[-1]['method']='原始PNG双人独立逐单元格目视转录；分别复算历史与物理录取人数、最高和最低合计，12行均一致。'
sources[-1]['notes']=['正文日期为2026-08-13，不按URL路径0817推定发布日期。人数是录取数；图未标批次、轮次和专业组。']
# Each entry is image data row: major, history (admitted,max,min), physics (admitted,max,min).
table=[['电子商务',[1,435,435],None],['食品检验检测技术',None,[1,403,403]],['食品营养与健康',None,[1,421,421]],['市场营销',[2,435,424],None],['现代物流管理',[2,424,424],[2,427,414]],['应用英语',[3,443,424],[3,417,402]],['跨境电子商务',[1,427,427],[1,443,443]],['金融科技应用',[1,419,419],None],['会展策划与管理',None,[2,440,402]]]
rows=[]
for i,(major,history,physics) in enumerate(table,1):
 for track,cell in [('历史',history),('物理',physics)]:
  if cell is None:continue
  count,high,low=cell
  rows.append({'id':f'major26-root-zjiet-{i}-{track}','year':2026,'province':'广西','school':'浙江经贸职业技术学院','schoolCode':'12864','track':track,'batch':'高职高专（批次待核）','group':None,'major':major,'score':low,'scoreType':'专业录取最低分','sourceMaximumScore':high,'sourceAverageScore':None,'plannedCount':None,'admittedCount':count,'rank':None,'rankType':None,'requiredSubjects':[],'subjectRule':'unknown','requirementText':None,'round':'录取汇总（轮次未分）','admissionType':'普通类','sourceId':zjpage,'sourceIds':[zjimage],'sourceRow':i,'sourceTable':'广西专业录取情况图表（行号不含表头）','fieldSourceIds':{'schoolCode':['gxeea-2026-33315','gxeea-2026-33316'],'score':[zjimage],'admittedCount':[zjimage]},'note':'官方图表仅列实际录取数与最高、最低分，未列计划人数、广西专业组代码和录取轮次；批次也未单列，保持待核。加分处理未在本表单独说明，以学校录取口径为准。','reviewedAt':DATE,'evidenceStatus':'verified','scoreComparable':True,'scoreEvidenceGaps':[],'conflictFields':[]})
assert len(rows)==12
sums={t:{'rows':len([r for r in rows if r['track']==t]),'admitted':sum(r['admittedCount'] for r in rows if r['track']==t),'max':max(r['sourceMaximumScore'] for r in rows if r['track']==t),'min':min(r['score'] for r in rows if r['track']==t)} for t in ['历史','物理']}
assert sums=={'历史':{'rows':6,'admitted':10,'max':443,'min':419},'物理':{'rows':6,'admitted':10,'max':443,'min':402}}
text=(RAW/'hust-scores.html').read_text();m=re.search(r'var\s+year_listObject\s*=\s*',text);years=list(json.JSONDecoder().raw_decode(text[m.end():])[0]);assert years==['2025','2024','2023']
for t in ['物理类','历史类']:
 o=read('sysu-scores-2026-'+t+'.json');assert o['state']==1 and not o['data']['zsSsgradeList'] and not o['data']['sszygradeList']
assert read('sysu-scores-2025-物理类.json')['data']['sszygradeList']
assert hashlib.sha256((RAW/'sxyyc-scores.html').read_bytes()).hexdigest()=='cf4d40a45d9663828594cf3a8a2c399912a4ff17dc82a42da17f513ae25c36e5'
notes=[]
def note(code,name,status,ids,text,count=0):
 notes.append({'id':'major-score-review-root-'+code,'year':2026,'province':'广西','auditKind':'major-scores','title':'2026广西专业录取分复查','schoolCode':code,'school':name,'checkedAt':DATE,'status':status,'sourceIds':ids,'checkedUrls':list(dict.fromkeys(s['url'] for s in sources if s['id'] in ids)),'recordCount':count,'note':text})
note('10487','华中科技大学','not-found-current-major',[hust],'官方分省分专业分数页面的实际年份数据只有2025、2024、2023，未取得2026广西专业实际最低分；2026计划及强基分数不能补代普通专业录取分。')
note('10213','哈尔滨工业大学','not-found-current-major',[hit,hit26],'官方分数查询当前提供2025/2024；显式请求广西2026后实际页面仍显示2025广西，因此不将该返回误记为2026。未取得本轮所查2026普通专业最低分。')
note('10558','中山大学','empty-current-response',[sysupar,*sysu26,sysu25],'正常公开查询流程已跑通。广西菜单最新为2025；2026物理、历史普通录取均成功响应但学校/专业列表为空，2025物理正向对照有专业数据。只记录本轮未取得，不断言学校尚未公布；不猜补其他招生类别。')
note('14008','重庆三峡医药高等专科学校','source-conflict',[sxy],'重新取得的官网内容摘要与前轮一致，2条冲突未修正：物理医学检验技术录取1人却记最低335/最高411；物理预防医学录取1人却记最低283/最高424。保留原文并继续排除分数比较，不以专业组线猜改。')
note('12864','浙江经贸职业技术学院','collected-partial',[zjpage,zjimage],'官方广西录取图表新增12条专业分（历史6、物理6），对应20名实际录取考生。双人读图与两科合计均一致。9个专业名称按科类分列；空白格不作0分、合计行不作为专业。仍缺专业组、精确批次和轮次，以及分专业计划人数。',12)
save('major-cutoffs-upsert.json',rows);save('sources.json',sources);save('school-audit-notes.json',notes);save('zjiet-reviewed-transcription.json',table)
save('QA.json',{'status':'PASS','newRows':12,'independentImageReview':'两个代理分别逐格读取原始图，12条全部一致','zjietTotals':sums,'hustAvailableYears':years,'sysu2026EmptyQueries':2,'sysu2025PositiveControl':True,'sxyycHashUnchanged':True,'existingConflictsRetained':2,'rawPublic':False})
