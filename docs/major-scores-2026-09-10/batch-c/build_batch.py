"""Build 2026 Guangxi actual major admission scores; never import filing thresholds."""
from pathlib import Path
from collections import Counter
import json,re,hashlib,html,argparse
from parse_tables import parse
R=Path(__file__).resolve().parent;RAW=R/'raw';DATE='2026-09-10';P='mscore-c-2026-'
SCHOOLS={'gxu':('10593','广西大学'),'gxnu':('10602','广西师范大学'),'gxmzu':('10608','广西民族大学'),'nnnu':('10603','南宁师范大学'),'glmu':('10601','桂林医科大学'),'ymun':('10599','右江民族医学院')}
def write(name,d):(R/name).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def read(name):return json.loads((RAW/name).read_text())
def plain(name):return re.sub(r'\s+',' ',html.unescape(re.sub('<[^>]+>',' ',(RAW/name).read_text())))
checks=[]
def check(name,ok,detail=None):
 checks.append({'check':name,'passed':bool(ok),'detail':detail});assert ok,(name,detail)
meta={f.name[:-10]:json.loads(f.read_text()) for f in RAW.glob('*.meta.json')}
# Figure out school identity from the site's audited 2026 filing directory, never from abbreviations.
workspace=R.parents[2];defaultSite=workspace/'guangxi-admissions-2026/site/data'
parser=argparse.ArgumentParser();parser.add_argument('--site-data',type=Path,default=defaultSite if defaultSite.exists() else Path.cwd()/'site/data');args=parser.parse_args();site=args.site_data;cutoffs=json.loads((site/'cutoffs.json').read_text())
for code,name in SCHOOLS.values():check('院校身份 '+name,any(x['schoolCode']==code and x['school']==name for x in cutoffs))
charter=plain('glmu-charter.html');check('桂林医科大学当前名称及标识码',all(s in charter for s in ['桂林医科大学','4145010601','2026']))
projectArticle=charter.split('第十一条',1)[1].split('第四章',1)[0]
check('章程第十一条中澳五专业属于中高计划',all(x in projectArticle for x in ['中高计划','康复治疗学','食品卫生与营养学','药学','医学检验技术','智能医学工程']))
check('章程第二十条英语90分或满分60%',all(x in charter.split('第二十条',1)[1].split('第二十一条',1)[0] for x in ['英语成绩要求不低于90分','150分制','60%']))
# The entire current public result has seven pages; compare its multiset with every group query.
allnames=['glmu-2026-all']+['glmu-all-p'+str(i) for i in range(2,8)]
allrows=[r for name in allnames for r in parse(RAW/(name+'.html'))[0]['rows'][1:]]
check('官方完整分页62行',len(allrows)==62)
cfg=read('glmu-2026-select.json')['data'];seen={};rows=[];excluded=[];bySource=Counter();rawGroupRows=[]
for g in cfg['tddwList']:
 key=(g['batchNo'],g['tddw'],g['kldm'])
 if key in seen:
  check('配置重复单位语义一致',g['tddwName']==seen[key]['tddwName']);continue
 seen[key]=g
 check('配置明确2026广西科类',g['year']==2026 and g['provinceId']==20 and g['provinceName']=='广西' and g['kldmCNName'] in ['物理类','历史类'])
 name='glmu-g-'+'-'.join(key);f=RAW/(name+'.html');table=parse(f)[0]['rows'];check('专业分数表表头 '+name,table[0]==['年份','专业名称','批次','投档单位','控制线','最高分','平均分','最低分'])
 pages=re.findall(r'class="maxPage"[^>]+value="([^"]+)"',f.read_text());check('逐组无未抓分页 '+name,not pages or all(x=='1' for x in pages))
 for ri,r in enumerate(table[1:],2):
  rawGroupRows.append(r);check('年批次类型逐行对应 '+name+':'+str(ri),r[0]=='2026' and r[2]==g['batchCNName'] and r[3]==g['tddwName'])
  if '预科' in r[1] or '预科' in r[3]:
   excluded.append({'sourceId':P+name,'sourceRow':ri,'group':g['tddw'],'track':g['kldmCNName'],'rawRow':r,'reason':'预科班阶段录取，不是确定本科专业的实际录取最低分；单独留证，不计入专业覆盖。'});continue
  score=int(r[7]);mx=int(r[5]);avg=float(r[6]);check('最低平均最高有序 '+name+':'+str(ri),0<=score<=avg<=mx<=750)
  admission='普通类'
  if '国家免费医学生' in r[3]:admission='农村订单定向免费医学生'
  elif '民族班' in r[3]:admission='民族班'
  elif '中澳学分互认' in r[1]:admission='中澳学分互认联合培养项目'
  note='官方历年录取分数查询逐专业结果；表头“投档单位”是类别筛选字段，本行最低分属于对应专业录取统计。未分首轮与征集，按录取汇总保留。学校按高考投档总分（含政策性加分）进行专业录取，非校测或艺体综合分。'
  if admission=='农村订单定向免费医学生':note+='定向服务地区见专业名；须签订培养及定向就业协议，承诺毕业后在相关基层医疗卫生机构服务6年。'
  if admission=='民族班':note+='民族班仅招少数民族考生。'
  if admission=='中澳学分互认联合培养项目':note+='为中澳学分互认联合培养项目，属2026章程第十一条所列“中高计划”；依据第二十条，招生录取要求英语单科不低于90分（150分制），英语单科满分非150分时须达到满分的60%。不能与普通非联合培养专业合并比较；收费及出国培养条件须另看项目简章。'
  if r[1]=='助产学':note+='2026章程规定助产学限招女生，建议身高低于155cm的女生慎重报考。'
  row={'id':'major-2026-c-glmu-'+hashlib.sha256('|'.join([*key,r[1]]).encode()).hexdigest()[:16],'year':2026,'province':'广西','school':'桂林医科大学','schoolCode':'10601','track':g['kldmCNName'].replace('类',''),'batch':r[2],'round':'录取汇总（轮次未分）','group':g['tddw'],'major':r[1],'score':score,'scoreType':'专业录取最低分','sourceMaximumScore':mx,'sourceAverageScore':avg,'rank':None,'rankType':None,'sourceId':P+name,'sourceTable':1,'sourceRow':ri,'note':note,'admissionType':admission,'rawAdmissionType':r[3],'reviewedAt':meta[name]['checkedAt'],'evidenceStatus':'verified','scoreComparable':True,'scoreBasis':'750分制高考投档总分（含政策性加分）','scoreScaleMaximum':750,'scoreEvidenceGaps':[],'conflictFields':[],'requiredSubjects':[],'subjectRule':'unknown','requirementText':None,'fieldSourceIds':{'schoolCode':[P+'glmu-charter'],'school':[P+'glmu-charter'],'track':[P+'glmu-2026-select'],'group':[P+'glmu-2026-select',P+name],'admissionType':[P+'glmu-2026-select',P+name],'scoreBasis':[P+'glmu-charter',P+'gx-scale-policy'],'scoreComparable':[P+'glmu-charter',P+'gx-scale-policy']}}
  if admission in ['农村订单定向免费医学生','民族班','中澳学分互认联合培养项目'] or r[1]=='助产学':row['fieldSourceIds']['note']=[P+'glmu-charter']
  if admission=='中澳学分互认联合培养项目':
   row['foreignLanguageRequirement']={'language':'英语','minimumScore':90,'scoreScaleMaximum':150,'minimumRatio':0.6,'appliesAt':'招生录取','note':'英语单科满分非150分时按满分60%折算；依据2026章程第十一条和第二十条。'}
   row['fieldSourceIds']['foreignLanguageRequirement']=[P+'glmu-charter']
  rows.append(row);bySource[name]+=1
check('逐组与完整分页多重集完全相同',Counter(map(tuple,rawGroupRows))==Counter(map(tuple,allrows)))
check('57专业行与5预科排除闭合',len(rows)==57 and len(excluded)==5 and len(rows)+len(excluded)==len(allrows))
check('同一组不同专业确有不同最低分',len({x['score'] for x in rows if x['group']=='155'})>1)
check('无计划或录取人数写入',all('plannedCount' not in r and 'admittedCount' not in r for r in rows))
check('未知轮次未标首轮',all(r['round']=='录取汇总（轮次未分）' for r in rows))
check('当前数据ID唯一',len({r['id'] for r in rows})==len(rows))
existing={r['id']:r for r in json.loads((site/'major-cutoffs.json').read_text())}
check('现站同ID无不同数值',all(r['id'] not in existing or all(existing[r['id']].get(k)==r[k] for k in ['schoolCode','year','group','major','score']) for r in rows))
# Sources also preserve unsuccessful attempts; their recordCount is zero and not scored evidence.
sources=[]
for key,m in meta.items():
 prefix=key.split('-')[0]
 if prefix not in SCHOOLS:continue
 code,school=SCHOOLS[prefix]
 title=school+'2026广西专业录取分数核验：'+key
 if key.startswith('glmu-g-'):title='桂林医科大学2026广西分专业录取分数（'+key.removeprefix('glmu-g-')+'）'
 s={'id':P+key,'title':title,'url':m['url'],'publisher':school,'sourceType':'official','year':2026,'publishedAt':'2026-06-10' if key=='glmu-charter' else None,'accessedAt':m['checkedAt'],'recordCount':bySource[key],'status':m.get('status'),'request':m.get('request'),'requestEncoding':m.get('requestEncoding'),'rawSha256':m.get('rawSha256'),'archiveSha256':m.get('archiveSha256'),'sha256':m.get('archiveSha256'),'method':'读取官方公开页面或按前端声明字段查询；查询条件与响应哈希逐项保存。','auditOnly':bySource[key]==0}
 if key.startswith('glmu-g-'):
  s['queryUrl']=m['url'];s['url']='https://jyw.glmu.edu.cn/zhaosheng/school!admissionScore.htm';s['method']='官方录取分数入口，固定2026年/广西省ID20及本批次投档单位/科类；返回逐专业最高、平均、最低分。此单位查询无后续分页。'
 if m.get('error'):s['accessError']=m['error']
 sources.append(s)
# Successful web read on 09:23 followed by transport timeouts: policy text is verified, raw bytes unavailable.
sources.append({'id':P+'gx-scale-policy','title':'广西2026年普通高校招生考试和录取工作方案（右江民族医学院官方转载）','url':'https://yyzs.ymun.edu.cn/info/1062/1527.htm','publisher':'右江民族医学院（转载广西招生考试工作方案）','sourceType':'official','year':2026,'publishedAt':'2026-06-03','accessedAt':DATE,'recordCount':0,'rawSha256':None,'archiveSha256':None,'method':'网页读取工具成功读取全文：第一部分（三）明确满分750分；二（三）说明普通类投档基准为高考总分（总成绩+政策性加分）。后续程序抓取发生TLS/超时，未取得原HTML归档，不伪造原文哈希。','auditOnly':True,'accessLimitType':'web-read-verified-raw-archive-unavailable'})
notes=[]
settings={
'gxu':('not-found-in-checked-index','已重读官方录取分数栏目；最新普通本科结果标题为2025年，发布于2026年的条目是2025少数民族预科。未得到2026专业实际录取分。',['gxu-lines']),
'gxnu':('year-unavailable','已读官方分数栏目及当前查询页JS；年份接口仅2025/2024/2023。2026广西不限专业类别的JSON查询返回空数组。最初form请求415已用前端JSON编码纠正；不把415作为未发布证据。',['gxnu-index','gxnu-query','gxnu-years','gxnu-lines-all','gxnu-lines-json']),
'gxmzu':('not-found-in-checked-index','已从首页进入历年分数完整当前列表；普通、国家专项、地方专项、民族班、公费师范、中外合作和学分互认等最新表均为2025，未取得2026专业实际最低分。',['gxmzu-home','gxmzu-lines']),
'nnnu':('year-unavailable-and-empty-query','当前官网链接的前端位于/zsdata/lqxx/，但其JS明确API仍为/lqxx/s/；因此不能将先前API空结果归因于路径错误。当前lnfs/getType仅含2025等既有年份，无2026；按真实字段查询2026/广西/物理类、历史类、全部及类别全部，均成功空列表。',['nnnu-old-home','nnnu-current-entry','nnnu-app','nnnu-component','nnnu-types','nnnu-2026-物理类','nnnu-2026-历史类','nnnu-2026-全部','nnnu-home','nnnu-query']),
'ymun':('not-found-in-checked-index','已核对校部代码10599并重读官网及历年分数栏目；最新广西专业、区外专业、定向医学生录取分统计均为2025。首页2026征集公告是余额，不用于专业实录分。',['ymun-home','ymun-lines']),
'glmu':('collected','取得2026广西全部7页62行；31个唯一批次/投档单位筛选合计62行与分页多重集一致。收录57条具体专业实录分，5条预科班单独排除。当前官方查询没有区分首轮/征集，标录取汇总；排名和选科要求未列，保留未知。',['glmu-home','glmu-score','glmu-2026-select','glmu-charter']+[k for k in meta if k.startswith('glmu-g-') or k in allnames])}
for prefix,(code,school) in SCHOOLS.items():
 status,note,keys=settings[prefix];notes.append({'schoolCode':code,'school':school,'year':2026,'province':'广西','status':'collected' if prefix=='glmu' else 'unavailable','accessLimitType':status,'recordCount':57 if prefix=='glmu' else 0,'excludedRecordCount':5 if prefix=='glmu' else 0,'checkedAt':DATE,'sourceIds':[P+k for k in keys],'checkedUrls':list(dict.fromkeys(meta[k]['url'] for k in keys)),'queryConditions':[{'sourceId':P+k,'request':meta[k].get('request'),'requestEncoding':meta[k].get('requestEncoding'),'status':meta[k].get('status'),'error':meta[k].get('error')} for k in keys],'note':note,'scope':'仅限明确列出的官方页面、查询配置与参数；不宣称全校或全部公众号均未发布。'})
check('六校都有实际核验记录',len(notes)==6 and all(n['sourceIds'] and n['checkedUrls'] for n in notes))
ids={s['id'] for s in sources};check('所有来源引用可解析',all(i in ids for r in rows for i in [r['sourceId']]+[x for v in r['fieldSourceIds'].values() for x in v]) and all(i in ids for n in notes for i in n['sourceIds']))
for k,m in meta.items():
 if m.get('archiveFile'):check('归档哈希 '+k,hashlib.sha256((RAW/m['archiveFile']).read_bytes()).hexdigest()==m['archiveSha256'])
for r in rows:check('省份年分数口径 '+r['id'],r['year']==2026 and r['province']=='广西' and r['scoreType']=='专业录取最低分' and r['rank'] is None)
for name,d in [('major-cutoffs-upsert.json',rows),('sources.json',sources),('school-audit-notes.json',notes),('excluded-records.json',excluded),('QA.json',{'passed':True,'checkedAt':DATE,'checks':checks,'summary':{'reviewedSchools':6,'collectedSchools':1,'rows':len(rows),'excludedPreparatoryRows':len(excluded),'byTrack':dict(Counter(r['track'] for r in rows)),'byAdmissionType':dict(Counter(r['admissionType'] for r in rows)),'byBatch':dict(Counter(r['batch'] for r in rows))}})]:write(name,d)
print(json.dumps({'rows':len(rows),'excluded':len(excluded),'sources':len(sources),'checks':len(checks),'byType':dict(Counter(r['admissionType'] for r in rows))},ensure_ascii=False))
