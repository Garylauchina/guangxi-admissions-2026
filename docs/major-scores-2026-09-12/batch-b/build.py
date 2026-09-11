"""Build the reviewed 2026 GX major score batch from public raw sources; no network or repo writes."""
from pathlib import Path
import json,hashlib,datetime,re
from collections import Counter
# Replay the approved dated review; future collection belongs in a new review package.
R=Path(__file__).resolve().parent;RAW=R/'raw';NOW='2026-09-12T07:27:13.345295+08:00';PREFIX='major-20260912-b-'
def read(name):return json.loads((RAW/(name+'.json')).read_text())
def write(name,data):(R/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
def sid(key):return PREFIX+key
schools={'xmu':('10384','厦门大学'),'bnu':('19027','北京师范大学(珠海校区)'),'njust':('10288','南京理工大学'),'hnu':('10532','湖南大学'),'hrbeu':('10217','哈尔滨工程大学'),'ecnu':('10269','华东师范大学'),'whut':('10497','武汉理工大学')}
checks=[]
def ck(label,ok,detail=None):
 checks.append({'check':label,'pass':bool(ok),**({'detail':detail} if detail is not None else {})})
 if not ok:raise AssertionError(label)
meta={p.stem.removesuffix('.meta'):json.loads(p.read_text()) for p in sorted(RAW.glob('*.meta.json'))}
sources=[]
for key,m in meta.items():
 school=schools[key.split('-')[0]]
 ext=Path(m.get('archiveFile','')).suffix
 content=None
 if ext=='.json':content=read(key)
 count=0
 if isinstance(content,dict):
  if isinstance(content.get('data'),dict) and 'sszygradeList' in content['data']:count=len(content['data']['sszygradeList'])
  elif isinstance(content.get('ext'),dict):count=len(content['ext'].get('recruitByMajorList',[]))
  elif isinstance(content.get('list'),list):count=len(content['list'])
  elif key=='njust-lines':count=len(content['data']['list'])
 year=2026 if '-2026' in key or key in ['ecnu-charter','bnu-gx-brochure','bnu-guide','xmu-guide'] else (2025 if '-2025' in key else None)
 desc='公开查询配置或前端页面'
 if 'gx-2026' in key:desc='2026广西公开分数查询响应'
 if 'gx-2025' in key:desc='2025广西正向对照（不纳入2026）'
 if key=='ecnu-charter':desc='2026年本科招生章程'
 if key=='bnu-gx-brochure':desc='2026广西计划与2025专业录取分数折页'
 if key=='njust-lines':desc='广西2023至2025各专业历年分数'
 source={'id':sid(key),'schoolCode':school[0],'title':school[1]+'：'+desc+' ['+key+']','url':m['url'],'entryUrl':m.get('entryUrl'), 'year':year,'publishedAt':'2026-05-28' if key=='ecnu-charter' else None,'accessedAt':datetime.datetime.fromisoformat(m['checkedAt']).astimezone(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),'httpStatus':m.get('status'),'sha256':m.get('archiveSha256'),'archiveSha256':m.get('archiveSha256'),'responseSha256':m.get('rawSha256'),'archiveFile':'raw/'+m['archiveFile'] if m.get('archiveFile') else None,'recordCount':count,'queryParameters':m.get('data'),'method':m.get('accessMethod','公开 GET/POST，实际 URL 与请求参数按官方页面/前端读取；完整原文仅作本地复核，不公开。')}
 if key.startswith('ecnu-gx-2026'):source['method']+=' 仅采 data.sszygradeList；同响应 sszyzgradeList 是组汇总，位次不挪至专业。zyzname 为选科文字。'
 if key=='hnu-gx-2025-control':source['note']='返回10条类别汇总，仅作为服务响应正向对照；当前响应无专业名称与人数，类别/科类文字为问号，不能当作专业数据。'
 if key=='bnu-gx-brochure':source['note']='单页主标题和北京/珠海两块表头均明确2026招生计划、2025录取分数；珠海数据没有与本部代码混用。'
 sources.append(source)
 if m.get('archiveFile'):ck('archive-hash:'+key,hashlib.sha256((RAW/m['archiveFile']).read_bytes()).hexdigest()==m['archiveSha256'])
# Official pre-existing filing sources are included as school-code evidence only.
base_sources=json.loads((R/'code-sources.json').read_text())
code_sources=[s for s in base_sources if s['id'] in ['gxeea-2026-33106','gxeea-2026-33107']]
ck('two-official-school-code-sources',len(code_sources)==2);sources.extend(code_sources)
rows=[];groups=[]
configs=read('ecnu-params')['data']['ssmc_nf_klmc_zyz_sex_campus_zslx_list']
expected={(k.split('_')[2],k.split('_')[3],c) for x in configs for k,v in x.items() if k.startswith('广西_2026_') and k.split('_')[2] in ['历史类','物理类'] for c in v}
seen=set()
charter=(RAW/'ecnu-charter.html').read_text()
ck('charter-policy-bonus', '最高不超过20分' in charter and '安排专业时均适用' in charter)
for i in range(1,9):
 key=f'ecnu-gx-2026-{i}';data=read(key);q=meta[key]['data'];ck('ecnu-query-success:'+key,data['state']==1)
 seen.add((q['klmc'],q['zyz'],q['zslx']))
 group=data['data']['sszyzgradeList'];rawrows=data['data']['sszygradeList']
 ck('ecnu-group-sum:'+key,len(group)==1 and sum(x['rs'] for x in rawrows)==group[0]['rs'])
 groups.append({'sourceId':sid(key),'category':q['zslx'],'track':q['klmc'],'subjectText':q['zyz'],'majorRows':len(rawrows),'admitted':sum(x['rs'] for x in rawrows),'groupSummaryExcluded':len(group)})
 for ri,x in enumerate(rawrows,1):
  ck(f'year-province-track:{key}:{ri}',x['nf']=='2026' and x['ssmc']=='广西' and x['ssdm']=='45' and x['klmc']==q['klmc'] and x['zslx']==q['zslx'] and x['zyzname']==q['zyz'])
  mn=float(x['minScore']);mx=float(x['maxScore']);avg=float(x['avgScore']);n=x['rs'];major=x['zymc']
  ck(f'positive-enrollment:{key}:{ri}',isinstance(n,int) and n>0)
  conflict=[]
  if not mn<=avg<=mx:conflict=['score','sourceMaximumScore','sourceAverageScore']
  if n==1 and mn!=mx:conflict+=['admittedCount']
  ck(f'score-range:{key}:{ri}',all(0<v<=750 for v in [mn,mx,avg]))
  rawcat=x['zslx'];cat='公费师范生' if '公费师范' in major else ('普通类' if rawcat=='普通类(本科批)' else rawcat)
  batch='本科普通批' if rawcat=='普通类(本科批)' else ('本科提前批（细分类待核）' if rawcat=='普通类(提前批)' else '本科（批次待核）')
  core=sid(key);char=sid('ecnu-charter');head=sid('ecnu-entry');cfg=sid('ecnu-params');code='gxeea-2026-33107' if x['klmc']=='物理类' else 'gxeea-2026-33106'
  field={f:[core] for f in ['year','province','track','major','score','sourceMaximumScore','sourceAverageScore','admittedCount','admissionType','sourceCategory','sourceTrack','sourceSubjectRequirement','requiredSubjects','subjectRule']}
  field.update({'school':[char],'schoolCode':[code],'batch':[core],'round':[core],'scoreBasis':[char],'requirementText':[core,char]})
  requirements=['首选'+x['klmc'][:2]+'，再选'+('化学' if x['zyzname']=='化学' else '不限')+'。']
  if '公费师范' in major:requirements.append('国家公费师范生须在入学前签订《本研衔接师范生公费教育协议书》，否则取消录取资格。')
  if rawcat=='国家专项':requirements.append('须符合国家专项计划报考资格，按教育部及学校专项招生规定执行。')
  if rawcat=='高校专项':requirements.append('须符合高校专项计划报考资格；投档成绩应达到生源省特殊类型招生控制分数线。')
  if major.startswith('英语') or major.startswith('翻译'):requirements.append('只招收英语语种考生。')
  base=major.split('（')[0]
  if base in ['化学','心理学类','生物科学类','生物科学','生态学','药学']:requirements.append('色弱、色盲不能录取；详见章程体检要求。')
  elif base in ['地理科学']:requirements.append('色盲不能录取；详见章程体检要求。')
  if base in ['经济学','工商管理类','行政管理','大数据管理与应用']:requirements.append('不能准确识别章程列明颜色的导线、按键、信号灯、几何图形者不能录取。')
  if base=='计算机科学与技术':requirements.append('不能准确识别显示器上章程列明颜色的数码、字母者不能录取。')
  identity='|'.join(['2026','10269',x['klmc'],rawcat,major]);rid='major26-'+hashlib.sha256(identity.encode()).hexdigest()[:20]
  note='官网分专业表原值。原表未分首轮或征集，保留录取汇总；未公布本专业最低分位次，未使用组汇总位次。专业组列为选科组合文字，不是广西组码。录取人数不作为招生计划数。'
  if rawcat in ['国家专项','高校专项']:note+=' 本条'+rawcat+'；原表未列精确批次。'
  if '公费师范' in major:note+=' 本条公费师范生，提前批细分类未列。'
  if conflict:note+=' 原始最低、最高、平均或人数存在数值矛盾，保留原值且不参与分数比较。'
  row={'id':rid,'year':2026,'province':'广西','schoolCode':'10269','school':'华东师范大学','track':x['klmc'][:2],'batch':batch,'group':None,'major':major,'majorCode':None,'score':int(mn) if mn.is_integer() else mn,'sourceMaximumScore':mx,'sourceAverageScore':avg,'admittedCount':n,'plannedCount':None,'scoreType':'专业录取最低分','scoreBasis':'普通高考750分制投档成绩；学校认可政策性加分最高一项且最高不超过20分，安排专业时亦适用；分数表未单列加分值。','scoreScaleMaximum':750,'round':'录取汇总（轮次未分）','sourceRound':None,'sourceCategory':rawcat,'sourceTrack':x['klmc'],'sourceSubjectRequirement':x['zyzname'],'sourceCampus':x.get('campus') or None,'admissionType':cat,'requiredSubjects':['化学'] if x['zyzname']=='化学' else [],'subjectRule':'all' if x['zyzname']=='化学' else 'none','requirementText':' '.join(requirements),'rank':None,'scoreComparable':not conflict,'evidenceStatus':'source-conflict' if conflict else 'verified','scoreEvidenceGaps':['原始分数或人数存在矛盾'] if conflict else [],'conflictFields':sorted(set(conflict)),'sourceId':core,'sourceIds':[core,head,cfg,char,code],'fieldSourceIds':field,'sourceRow':ri,'sourceTable':'data.sszygradeList','reviewedAt':NOW,'note':note}
  if major.endswith('类'):row['majorType']='正式招生大类'
  rows.append(row)
ck('all-eight-configured-non-art-tracks-categories',seen==expected)
ck('32-unique-rows-88-admitted',len(rows)==32 and len({x['id'] for x in rows})==32 and sum(x['admittedCount'] for x in rows)==88)
# Negative checks: distinguish actual returned empty payloads from transport failures.
for tr in ['全部','物理类','历史类']:ck('xmu-2026-empty-'+tr,read('xmu-gx-2026-'+tr).get('success') is True and read('xmu-gx-2026-'+tr)['list']==[])
ck('xmu-2025-positive',len(read('xmu-gx-2025-全部')['list'])==50)
ck('whut-2026-empty',read('whut-gx-2026-all')['success'] is True and read('whut-gx-2026-all')['ext']=={'recruitByMajorList':[],'recruitStatisticsList':[]})
ck('whut-2025-positive',len(read('whut-gx-2025-control')['ext']['recruitByMajorList'])==37)
ck('hnu-2026-empty-null-summary',read('hnu-gx-2026')==[None,[]])
ck('hnu-2025-response-positive-summary-only',len(read('hnu-gx-2025-control')[1])==10 and all('zymc' not in x for x in read('hnu-gx-2025-control')[1]))
for key in ['hrbeu-gx-2026-物理类-普通类','hrbeu-gx-2026-历史类-普通类','hrbeu-gx-2026-物理类-国家专项']:
 d=read(key);ck(key+':empty',d['state']==1 and d['data']['sszygradeList']==[] and d['data']['zsSsgradeList']==[])
ck('hrbeu-2025-positive',len(read('hrbeu-gx-2025-物理类-普通类')['data']['sszygradeList'])==16)
ck('njust-columns-2023-2025',all(f'title : "{y}年"' in (RAW/'njust-entry.html').read_text() for y in [2023,2024,2025]) and read('njust-lines')['total']==21)
summary={
 'xmu':('empty-current-response','year-unavailable-and-empty-query','官方分数查询广西配置最新2025。按真实前端参数查询2026广西、全部类别，物理类/历史类/全部均success=true且list为空；2025同口径正对照50条。2026广西报考指南另表列的是2026计划和2025/2024录取分，未挪作本年实际分。查询包含官方类别中的马来西亚分校，当前无2026结果，未产生本部/分校混码。'),
 'bnu':('not-found-current-major','only-prior-year-scores','官方计划分数目录当前有2026招生计划及近年分数、2025及更旧实际分数入口。本年广西折页已核对主标题与珠海校区表头：2026为计划年，最低/最高分属2025；未找到本次可核实的2026珠海校区单专业实际分。珠海19027独立记账，未使用北京本部10027数据。'),
 'njust':('not-found-current-major','only-prior-year-scores','官方2026招生计划及近三年分数入口中的分数表，year1/year2/year3前端表头分别为2023/2024/2025。广西接口成功返回21条旧年专业记录，未提供2026分数列；未将招生计划年份套到旧分数上。本次未取得可确认的2026专业实际分。'),
 'hnu':('empty-current-response','empty-query','官方前端年份选项包含2026；按year=2026、sf=广西壮族自治区正常GET，HTTP200返回[null,[]]。同样2025返回汇总及10条类别行，当前原响应不含专业名称/录取人数、类别文字为问号，仅证明接口响应。前端按月份在类别/专业表头间切换，本次未将类别汇总冒充专业分。'),
 'hrbeu':('empty-current-response','year-unavailable-and-empty-query','依官方Cookie与公开CSRF流程读取配置，广西分数年份最新2025，校区/性别筛选未启用。2026广西物理普通类、历史普通类、物理国家专项均state=1但专业与总表为空；2025广西物理普通类正对照16条专业记录。未把配置缺少年份等同于所有渠道均未发布。'),
 'ecnu':('collected','none','已采官方配置中2026广西物理/历史8种类别与选科组合，共32条、88名实际录取：普通本科18条、公费师范提前6条、国家专项6条、高校专项2条。已排除体育配置及8条组汇总。原专业行未公布省编组码/专业位次/校区/轮次；国家专项与高校专项精确批次待核。范围仅为当前官方查询配置，不宣称全校全部招生渠道完备。'),
 'whut':('empty-current-response','year-unavailable-and-empty-query','官方分专业查询广西年份最新2025，2026科类配置仅返回“全部”；按2026广西全部科类实际查询success=true，专业表和省份汇总表均为空。2025同口径正对照37条专业记录（含艺术旧分，仅作对照，不纳入）。本次空返回未当作0分或不招生。')}
notes=[]
for prefix,(code,school) in schools.items():
 status,limit,note=summary[prefix];keys=[k for k in meta if k.startswith(prefix+'-')];sids=[sid(k) for k in keys]
 entry={'xmu':'https://zsdata.xmu.edu.cn/public/zsdata/lqxx/#/lnfs','bnu':'https://admission.bnu.edu.cn/zsjhlnfs/index.html','njust':'https://zsb.njust.edu.cn/lqjh_fsx','hnu':'https://admi2.hnu.edu.cn/lnlqqk','hrbeu':'https://zsb.hrbeu.edu.cn/static/front/hrbeu/basic/html_web/lnfs.html','ecnu':'https://zsbcx.ecnu.edu.cn/static/front/ecnu/basic/html_web/lnfs.html','whut':'https://zs.whut.edu.cn/bkcx/bklqqk/'}[prefix]
 notes.append({'id':'review-major-gap-'+code,'auditKind':'major-scores','year':2026,'province':'广西','schoolCode':code,'school':school,'checkedAt':NOW,'status':status,'accessLimitType':limit,'entryUrl':entry,'sourceIds':sids,'checkedUrls':sorted({meta[k]['url'] for k in keys}),'note':note})
refs={s['id'] for s in sources}
ck('references-closed',all(set(r['sourceIds']+[s for ids in r['fieldSourceIds'].values() for s in ids])<=refs for r in rows) and all(set(n['sourceIds'])<=refs for n in notes))
ck('seven-local-date-notes',len(notes)==7 and all(n['checkedAt'].startswith('2026-09-12') for n in notes))
for name,data in [('major-cutoffs-upsert.json',rows),('sources.json',sources),('school-audit-notes.json',notes)]:write(name,data)
write('QA.json',{'status':'PASS','checkedAt':NOW,'summary':{'schoolsChecked':7,'newMajorRows':32,'newAdmittedCount':88,'collectedSchools':1,'successfulCurrentEmptySchoolQueries':4,'priorYearOnlySchools':2,'transportFailedSchools':0,'sources':len(sources),'checks':len(checks),'scoreComparableRows':sum(x['scoreComparable'] for x in rows),'tracks':dict(Counter(r['track'] for r in rows)),'categories':dict(Counter(r['admissionType'] for r in rows))},'queryGroups':groups,'excluded':[{'sourceId':sid('ecnu-params'),'reason':'2026广西体育科类配置不在普通高考专业分范围，未采录取分。'},{'sourceIds':[g['sourceId'] for g in groups],'count':8,'reason':'data.sszyzgradeList是类别/选科组汇总，含组位次；不并入专业，不给专业补位次。'},{'sourceId':sid('bnu-gx-brochure'),'reason':'珠海表头实际分数属于2025。'},{'sourceId':sid('njust-lines'),'count':21,'reason':'2023至2025旧分表。'}],'checks':checks})
print(json.dumps({'rows':len(rows),'admitted':sum(r['admittedCount'] for r in rows),'sources':len(sources),'checks':len(checks)},ensure_ascii=False))
