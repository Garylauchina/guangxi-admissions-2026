"""Reproduce bounded source-gap evidence. No old-year rows enter live major scores."""
from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parent;RAW=ROOT/'raw';DATE='2026-09-11'
def read(name):return json.loads((RAW/name).read_text())
def save(name,data):(ROOT/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
checks=[]
def check(name,condition):
 assert condition,name
 checks.append({'check':name,'passed':True})
# A successful old-year control distinguishes an empty current-year query from a broken collector.
for t in ['物理类','历史类']:
 check('scut2026-empty-'+t,'没有您想要的查询结果' in (RAW/('scut-gx-2026-'+t+'.html')).read_text())
 check('scut2025-positive-'+t,len((RAW/('scut-gx-2025-'+t+'.html')).read_bytes())>10000)
 o=read('uestc-gx-2026-'+t+'.json');check('uestc2026-empty-'+t,o['code']==200 and o['list']==[])
 o=read('nankai-gx-2026-'+t+'.json');check('nankai2026-empty-'+t,o['state']==1 and o['data']['sszygradeList']==[] and o['data']['zsSsgradeList']==[])
check('uestc2025-positive',bool(read('uestc-gx-2025-物理类.json')['list']))
check('nankai2025-positive',bool(read('nankai-gx-2025-物理类.json')['data']['sszygradeList']))
check('cpu2026-empty',read('cpu-gx-2026.json')['total']==0 and read('cpu-gx-2026.json')['data']==[])
check('cpu2025-positive',read('cpu-gx-2025.json')['total']>0)
check('cqu2026-no-config',read('cqu-config-2026.json')=={'msg':'','code':500})
check('cqu2025-positive-config',read('cqu-config-2025.json')['code']==0 and read('cqu-config-2025.json')['msg']['queryRemark']=='2025录取分数线查询')
for name,count,gxcount in [('ncepu-major-data.json',1308,43),('ncepu-all-data.json',114,5)]:
 rows=read(name)['data'];check(name+'-all-records',len(rows)==count and {r['properties']['year'] for r in rows}=={'2025'} and sum(r['properties']['province']=='广西' for r in rows)==gxcount)
u=read('uestc-score-types.json')['typeMap'];uy=sorted(set(k.split('_')[1] for k in u if k.startswith('广西_')))
check('uestc-menu-no2026','2026' not in uy and '2025' in uy)
n=read('nankai-score-params.json')['data']['ssmc_nf_klmc_sex_campus_zslx_list'];ny=sorted(set(k.split('_')[1] for d in n for k in d if k.startswith('广西_')))
check('nankai-menu-no2026',ny==['2024','2025'])
FILES={
 '10561':('华南理工大学',['scut-score-entry.html','scut-query.html','scut-current-min.html','scut-gx-2026-物理类.html','scut-gx-2026-历史类.html','scut-gx-2025-物理类.html','scut-gx-2025-历史类.html'],'empty-current-response','官方年份菜单为2025/2024/2023；按页面实际字段分别查询2026广西普通类物理、历史，均返回“没有您想要的查询结果”，2025两科正向对照有记录。另一个最新分数公告栏目发布于2026的广西文章，实际数据年为2025。不将计划、旧年分或空结果用作2026专业最低分。'),
 '10614':('电子科技大学',['uestc-home.html','uestc-query.html','uestc-app.js','uestc-lnfs.js','uestc-score-types.json','uestc-gx-2026-物理类.json','uestc-gx-2026-历史类.json','uestc-gx-2025-物理类.json'],'empty-current-response','当前官方公开分数菜单广西年份最高2025。按前端实际JSON字段查询2026广西普通类、本部、物理及历史，两次code200且专业列表空；2025物理正向对照有结果。校区字段已限定本部，不将沙河校区或旧年分数混入。其他资格类别的2026记录本轮未取得。'),
 '10611':('重庆大学',['cqu-score-entry.html','cqu-query.js','cqu-config-2026.json','cqu-config-2025.json'],'entry-only-year-gap','官方年份菜单只有2025/2024/2023。按页面实际接口请求2026查询配置，返回应用code500且msg为空，不能建立本年专业查询；2025同接口code0且字段/广西选项完整。属于本年配置不可用的证据，不冒称2026查询成功但零录取，也不以强基综合分或全校最低分替代。'),
 '10054':('华北电力大学(北京)',['ncepu-home.html','ncepu-score-entry.html','ncepu-query.js','ncepu-major-data.json','ncepu-all-data.json'],'not-found-current-major','官网分数页直接读取公开JSON，全量1308条专业记录和114条院校汇总记录的数据年均为2025，其中广西分别43条和5条。JSON生成时间为2026不改变其表内年份；本轮未取得2026广西专业线。北京与保定使用独立入口及院校代码，不混用。'),
 '10055':('南开大学',['nankai-home.html','nankai-score-entry.html','nankai-score-query.html','nankai-score-params.json','nankai-gx-2026-物理类.json','nankai-gx-2026-历史类.json','nankai-gx-2025-物理类.json'],'empty-current-response','招生主站直接读取403；通过官网导航的独立录取查询站正常公开会话流程已成功读取年份菜单及分数接口。广西菜单只有2025/2024，本科普通批2026物理、历史均state1且学校/专业列表为空，2025物理有正向对照。访问限制与查询结果分别记录，不用2024招生宣传附件补充2026分数。'),
 '10316':('中国药科大学',['cpu-score-page.html','cpu-score-query.js','cpu-gx-2026.json','cpu-gx-2025.json'],'empty-current-response','官方年份选项最新2025；按页面查询脚本的省份f8=广西、年份f7=2026请求，成功响应但total0/data空，2025广西正向对照有结果。默认分数表未展示年份和省份，不能因页面导航写2026招生计划而将默认表中的专业分误标为2026广西。')}
sources=[];notes=[]
for code,(school,names,status,note) in FILES.items():
 ids=[];urls=[];conditions=[]
 for filename in names:
  meta=RAW/(filename+'.meta.json')
  if not meta.exists():meta=RAW/(filename.removesuffix('.json')+'.meta.json')
  m=json.loads(meta.read_text());sid='mscore-20260911-root-'+filename.replace('.','-');ids.append(sid);urls.append(m['url'])
  if (RAW/filename).exists():
   observed=hashlib.sha256((RAW/filename).read_bytes()).hexdigest();expected=m.get('archiveSha256') or m.get('sha256');check(filename+'-hash',observed==expected)
  label=filename.replace('.html','').replace('.json','').replace('.js','').replace('scut-','').replace('uestc-','').replace('cqu-','').replace('ncepu-','').replace('nankai-','').replace('cpu-','')
  label=label.replace('gx-','广西 ').replace('score-params','分数查询年份菜单').replace('score-types','分数查询年份及类别').replace('score-query','官方分数查询').replace('score-entry','录取分数查询入口').replace('score-page','录取分数查询入口').replace('current-min','最新录取分数公告目录').replace('major-data','分专业录取数据（2025）').replace('all-data','录取汇总数据（2025）').replace('config-','查询配置 ').replace('home','招生官网').replace('query','公开查询字段与菜单').replace('app','查询页面脚本').replace('lnfs','分数查询页面脚本')
  source={'id':sid,'title':school+'：'+label,'url':m['url'],'publisher':school,'publishedAt':None,'accessedAt':m['checkedAt'],'sha256':m.get('sha256'),'method':'直接读取学校公开页面、配置及对应查询接口；记录实际请求与正向对照，旧年记录仅用于验证入口。','evidenceRole':'source-review-not-admission-records','notes':[note]}
  for k in ['archiveSha256','redactedFields','requestEncoding']:
   if k in m:source[k]=m[k]
  source['requestMethod']=m['method'];source['requestData']=m.get('requestData');source['httpStatus']=m.get('status')
  if m.get('error'):source['accessError']=m['error']
  sources.append(source);conditions.append({'sourceId':sid,'request':m.get('requestData'),'httpStatus':m.get('status'),'accessError':m.get('error')})
 notes.append({'id':'review-major-20260911-root-'+code,'year':2026,'province':'广西','schoolCode':code,'school':school,'auditKind':'major-scores','title':'2026广西专业录取分来源复查','checkedAt':DATE,'status':status,'recordCount':0,'sourceIds':ids,'checkedUrls':list(dict.fromkeys(urls)),'queryConditions':conditions,'note':note,'scope':'仅对本轮实际读取的官方页面和明确参数负责；未取得不表示学校未招生或所有渠道均未公布。'})
save('major-cutoffs-upsert.json',[]);save('sources.json',sources);save('school-audit-notes.json',notes)
save('QA.json',{'status':'passed','checkedAt':DATE,'reviewedSchools':6,'newRecords':0,'checks':checks,'uestcGuangxiMenuYears':uy,'nankaiGuangxiMenuYears':ny,'ncepuMajor2025Rows':1308,'ncepuGuangxi2025MajorRows':43,'rawPublished':False})
print('PASS',len(checks),'checks',len(sources),'sources')
