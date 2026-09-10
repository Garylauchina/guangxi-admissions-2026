"""Build a bounded negative-search batch; never turn empty responses into zero scores."""
import collections,datetime,hashlib,json,re,sys
from pathlib import Path
R=Path(__file__).resolve().parent; RAW=R/'raw';PREFIX='ms-20260911-b-'
read=lambda f:json.loads(f.read_text())
write=lambda name,data:(R/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
schools={'12121':'南方医科大学','10486':'武汉大学','10699':'西北工业大学','10056':'天津大学','10287':'南京航空航天大学','19213':'哈尔滨工业大学(威海)','10247':'同济大学'}
checked='2026-09-11'
config={
'12121':{'status':'not-found-current-major','accessLimitType':'year-unavailable-and-empty-query','entryUrl':'https://portal.smu.edu.cn/bkzs/bkzn/wnfs.htm','sourceKeys':['smu-entry','smu-query-config','smu-gx-2025-all','smu-gx-2026-all'],'availableYears':[2025,2024,2023],'note':'官方往年分数入口提供2025/2024/2023。公开表单配置明确无需登录、无需短信验证码；按页面真实字段、广西、2026及不限定科类/类别查询，HTTP 200、业务码9999并明确“未查询到相关数据”。同样广西2025查询得到22条，仅作接口正向对照，不计入2026专业分。'},
'10486':{'status':'empty-current-response','accessLimitType':'year-unavailable-and-empty-query','entryUrl':'https://zsdata.whu.edu.cn/public/wzgl/#/fscx','sourceKeys':['whu-home','whu-entry','whu-app','whu-types-json','whu-gx-2026-物理类','whu-gx-2026-历史类','whu-gx-2026-全部'],'availableYears':[2025,2024,2023,2022,2021],'note':'从本校主页进入公开分数查询并读取当前前端。广西配置最新2025，物理/历史及普通、单设投档、国家专项等均无2026配置。按真实JSON参数查2026广西、校本部、全部类别，物理/历史/全部三个请求均成功返回空list。初次误用form的500已用前端JSON请求纠正，未把500当作未发布证据。'},
'10699':{'status':'unavailable','accessLimitType':'official-entry-http-412-and-summary-not-major-level','entryUrl':'https://zsb.nwpu.edu.cn/','sourceKeys':['nwpu-home','nwpu-2026-summary'],'availableYears':None,'note':'本科招生入口直接访问和网页读取均返回HTTP 412，未取得分专业查询配置。已读学校官网2026本科招生工作总结，虽有广西650分/1150位次，但表格按省汇总全校物理类，不是具体专业或正式招生大类最低分，未导入专业线。本次尚不能判断该校其他官方入口是否已公开2026专业分。'},
'10056':{'status':'empty-current-response','accessLimitType':'year-unavailable-and-empty-query','entryUrl':'https://zsdata.tju.edu.cn/zsdata/lqxx/#/lnfs','sourceKeys':['tju-home','tju-entry','tju-app','tju-component','tju-types','tju-gx-2026-物理类','tju-gx-2026-历史类','tju-gx-2026-全部'],'availableYears':[2025],'note':'从官方主页链接进入历年分数，前端明确实际API仍为/lqxx/s/。广西配置只有2025北洋园校区、物理/全部，类别含普通、国家专项、高校专项；没有2026。按2026广西、北洋园校区、全部类别查询物理/历史/全部，均HTTP 200且success=true，list和sumList为空。未把历史空结果推定为该校不招历史。'},
'10287':{'status':'empty-current-response','accessLimitType':'year-unavailable-and-empty-query','entryUrl':'https://zs.nuaa.edu.cn/lnlqfs/list.psp','sourceKeys':['nuaa-entry','nuaa-years','nuaa-2026-provinces','nuaa-gx-2026-物理类','nuaa-gx-2026-历史类'],'availableYears':[2025,2024,2023,2022,2021,2020,2019,2018,2017],'note':'当前录取分数页的公开年份API最新2025；2026可选省份为空。按前端真实year/sf/kl字段查询2026广西物理类及历史类、不限定类别，均成功返回空data。查询的是getAdmissionScore逐专业接口，没有把getAdmissionScoreOverview概况当成专业分。'},
'19213':{'status':'empty-current-response','accessLimitType':'year-unavailable-and-empty-query','entryUrl':'https://zsb.hitwh.edu.cn/home/query/score','sourceKeys':['hitwh-home','hitwh-entry','hitwh-gx-2025-config','hitwh-gx-2026-config','hit-summary-gx'],'availableYears':[2025,2024,2023],'note':'威海校区官方分数页及广西配置均只列2025/2024/2023；2026广西年份查询成功返回空类别、空招生类型及空list。原系统广西科类名为“综改”，未擅自拆成物理/历史。另核校本部官网广西三校区汇总表，2026列是计划，最高/平均/最低对应2025及2024，不能把2026计划表头误套到旧分。威海代码19213独立保留，不与10213本部混并。'},
'10247':{'status':'empty-current-response','accessLimitType':'year-unavailable-and-empty-query','entryUrl':'https://bkzs.tongji.edu.cn/luqu/admission','sourceKeys':['tongji-entry','tongji-js-2574580','tongji-js-373d896','tongji-js-5e0cf47','tongji-years','tongji-gx-2026'],'availableYears':[2025,2024,2023,2022,2021,2020,2019],'note':'已读取同济官方前端的公开查询流程、字段和签名算法，按正常未登录请求查询。年份API最新2025；实际专业录取接口以year=2026、provinceCode=45、pageIndex=1/pageSize=50查询，isSuccess=true但totalCount=0、items=[]。请求不限定科类及类别，故空结果不是只查某一科类；未使用个人登录令牌，也未保存会话值。'}
}
metas={f.name.removesuffix('.meta.json'):read(f) for f in RAW.glob('*.meta.json')}
sources=[]
for k,m in sorted(metas.items()):
 code=m['schoolCode'];sid=PREFIX+k
 record={'id':sid,'title':schools[code]+'官方专业分资料复查：'+k,'url':m.get('entryUrl',m['url']),'publisher':schools[code],'sourceType':'official','queryYear':2026,'publishedAt':None,'accessedAt':m['checkedAt'],'recordCount':0,'auditOnly':True,'status':m.get('status'),'method':'直接读取学校公开入口、前端声明资源或按真实参数查询；仅用于本轮缺口审阅。接口原响应哈希与脱敏后归档哈希分别记录，原始归档不公开。','request':m.get('data',m.get('queryParameters')),'requestMethod':m.get('method','POST' if 'data' in m else 'GET'),'rawSha256':m.get('rawSha256'),'archiveSha256':m.get('archiveSha256'),'sha256':m.get('archiveSha256')}
 if m.get('entryUrl'):record['queryUrl']=m['url']
 if m.get('encoding'):record['requestEncoding']=m['encoding']
 if m.get('error'):record['accessError']=m['error']
 if m.get('methodNote'):record['method']+=m['methodNote']
 if k=='nwpu-2026-summary':record.update(year=2026,publishedAt='2026-08-03',method=record['method']+'该表为全校物理类分省概况，不是专业明细。')
 if '2025' in k:record.update(year=2025,queryYear=2025,method=record['method']+'旧年结果只作接口正向对照，不纳入2026分数。')
 sources.append(record)
notes=[]
for code,c in config.items():
 keys=c['sourceKeys'];assert all(k in metas for k in keys)
 notes.append({'id':'review-major-gap-'+code,'auditKind':'major-scores','year':2026,'province':'广西','school':schools[code],'schoolCode':code,'checkedAt':checked,'status':c['status'],'recordCount':0,'majorScoreCount':0,'accessLimitType':c['accessLimitType'],'entryUrl':c['entryUrl'],'sourceIds':[PREFIX+k for k in keys],'checkedUrls':list(dict.fromkeys([c['entryUrl']]+[metas[k]['url'] for k in keys])),'availableYears':c['availableYears'],'queryConditions':[{'sourceId':PREFIX+k,'request':metas[k].get('data',metas[k].get('queryParameters')),'status':metas[k].get('status')} for k in keys if metas[k].get('data') or metas[k].get('queryParameters')],'note':c['note'],'scope':'本轮仅限列出的官方页面、配置及请求，不宣称全校全部入口均未公布。未取得实际分数不表示0分、不招生或录取尚未完成。'})
# Explicit evidence and archive checks, independent of prose interpretation.
checks=[]
def ck(name,ok):assert ok,name;checks.append({'check':name,'passed':True})
ck('SMU old positive control22/current no-result',read(RAW/'smu-gx-2025-all.json')['data']['total']==22 and read(RAW/'smu-gx-2026-all.json')['msg']=='未查询到相关数据')
for school in ['whu','tju']:
 for track in ['物理类','历史类','全部']:
  d=read(RAW/f'{school}-gx-2026-{track}.json');ck(school+' '+track+' current successful empty',d['success'] is True and d['list']==[])
 for key in read(RAW/('whu-types-json.json' if school=='whu' else 'tju-types.json'))['typeMap']:
  if key.startswith('广西_'):ck(school+' configuration no2026 '+key,key.split('_')[1]!='2026')
ck('NUAA current province empty',read(RAW/'nuaa-2026-provinces.json')['data']==[])
for track in ['物理类','历史类']:ck('NUAA '+track+' empty',read(RAW/f'nuaa-gx-2026-{track}.json')['data']==[])
ck('NUAA latest2025',read(RAW/'nuaa-years.json')['data'][0]=='2025')
ck('HIT Weihai current config empty',read(RAW/'hitwh-gx-2026-config.json')['data']=={'categories':[],'enroll_types':[],'list':[]})
ck('HIT Weihai latest2025',read(RAW/'hitwh-gx-2025-config.json')['data']['years']==[2025,2024,2023])
ck('Tongji latest2025',read(RAW/'tongji-years.json')['result'][0]==2025)
tj=read(RAW/'tongji-gx-2026.json');ck('Tongji current empty',tj['isSuccess'] and tj['result']=={'totalCount':0,'items':[]})
ck('NWPU access limitation not counted as no-publication',metas['nwpu-home']['status']==412 and metas['nwpu-2026-summary']['status']==200)
for k,m in metas.items():
 if m.get('archiveFile'):ck('archive hash '+k,hashlib.sha256((RAW/m['archiveFile']).read_bytes()).hexdigest()==m['archiveSha256'])
ck('7 distinct schools and notes',len(notes)==len({n['id'] for n in notes})==len({n['schoolCode'] for n in notes})==7)
ck('local checking date',all(n['checkedAt']=='2026-09-11' for n in notes))
ck('all note references exist',all(x in {s['id'] for s in sources} for n in notes for x in n['sourceIds']))
for name,data in [('major-cutoffs-upsert.json',[]),('sources.json',sources),('school-audit-notes.json',notes),('QA.json',{'status':'passed','checkedAt':checked,'scope':'七校官方来源实查与缺口验证；无新增2026专业最低分。','summary':{'schoolsChecked':7,'newMajorRows':0,'successfulCurrentEmptySchoolQueries':5,'businessNoDataSchoolQueries':1,'entryAccessLimitedSchools':1,'sources':len(sources),'checks':len(checks)},'checks':checks})]:write(name,data)
print(json.dumps({'rows':0,'schools':7,'sources':len(sources),'checks':len(checks)},ensure_ascii=False))
