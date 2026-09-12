"""Deterministic build of a bounded negative-search package, no website writes."""
from pathlib import Path
import json,hashlib,datetime,re
R=Path(__file__).resolve().parent;RAW=R/'raw';PREFIX='major-20260912b2-b-'
def read(n):return json.loads((RAW/(n+'.json')).read_text())
def write(n,v):(R/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def check(name,v):checks.append({'name':name,'passed':bool(v)})
checks=[];ctx=json.loads((R/'audit-context.json').read_text());checked=ctx['checkedAt']
schools=[('10033','中国传媒大学','cuc'),('10295','江南大学','jnu'),('10730','兰州大学','lzu'),('14851','香港城市大学(东莞)','citydg'),('10010','北京化工大学','buct'),('10034','中央财经大学','cufe'),('10570','广州医科大学','gzhmu')]
lookup={slug:(code,name) for code,name,slug in schools}
sources=[]
for f in sorted(RAW.glob('*.meta.json')):
 m=json.loads(f.read_text());stem=m['id'];slug=stem.split('-')[0];code,school=lookup[slug]
 archived=m.get('archiveFile');path=RAW/archived if archived else None
 if path:check('archive hash '+stem,path.is_file() and digest(path)==m['archiveSha256'])
 s={'id':PREFIX+stem,'title':school+'官方来源核查：'+stem,'url':m['url'],'publisher':school,'sourceType':'official','accessedAt':m['checkedAt'],
    'publishedAt':None,'sha256':m.get('archiveSha256'),'rawSha256':m.get('rawSha256'),'archiveSha256':m.get('archiveSha256'),
    'archiveFile':('raw/'+archived) if archived else None,'httpStatus':m.get('status'),'accessOutcome':'response-received' if archived else 'access-failed',
    'requestMethod':'POST' if 'data' in m else 'GET','requestParams':m.get('data',{}),'method':m.get('accessMethod','按官方入口及实际前端 URL 读取公开页面/接口；不保存会话值。')}
 if m.get('encoding'):s['requestEncoding']=m['encoding']
 if m.get('entryUrl'):s['entryUrl']=m['entryUrl']
 if m.get('referer'):s['entryUrl']=m['referer']
 if m.get('error'):s['accessError']=m['error']
 if m.get('sourceYearOfCategoryConfiguration'):s['parameterConfigurationYear']=m['sourceYearOfCategoryConfiguration']
 if archived and archived.endswith('.json'):
  v=read(stem);s['businessCode']=v.get('state',v.get('code'));s['businessMessage']=v.get('msg')
  if isinstance(v.get('data'),dict):s['responseListLengths']={k:len(x) for k,x in v['data'].items() if isinstance(x,list)}
 sources.append(s)

summaries={}
for slug in ['cuc','buct','cufe']:
 config=read(slug+'-param')['data'];records=config['ssmc_nf_klmc_sex_campus_zslx_list']
 gx=[x for x in records if any(k.startswith('广西_') for k in x)]
 years=sorted({int(k.split('_')[1]) for x in gx for k in x},reverse=True)
 check(slug+' current menu latest year',years[0]==2025)
 files=sorted(f for f in RAW.glob(slug+'-gx-2026-*.json') if not f.name.endswith('.meta.json'))
 for f in files:
  v=json.loads(f.read_text());check(slug+' empty current '+f.stem,v['state']==1 and v['data']['sszygradeList']==[] and v['data']['zsSsgradeList']==[])
 positives={}
 for track in ['物理类','历史类']:
  f=RAW/f'{slug}-gx-2025-{track}.json'
  if not f.exists():continue
  v=json.loads(f.read_text());n=len(v['data']['sszygradeList']);check(slug+' positive old '+track,v['state']==1 and n>0);positives[track]=n
 summaries[slug]={'configurationYearsGuangxi':years,'currentSuccessfulEmptyScoreQueries':len(files),'positiveControl2025MajorRows':positives}
check('JNU public request header logic read','headers["csrf"]' in (RAW/'jnu-app.js').read_text() and 'application/json' in (RAW/'jnu-app.js').read_text())
check('JNU menu latest 2025',read('jnu-years-csrf')['data']['years'][0]['id']==2025)
check('JNU 2026 empty province list',read('jnu-provinces-2026')['code']=='1000000' and read('jnu-provinces-2026')['data']==[])
check('JNU direct Guangxi ID',{'id':20,'name':'广西'} in read('jnu-provinces-2025')['data'])
check('JNU 2026 empty subject list',read('jnu-subjects-json-2026')['code']=='1000000' and read('jnu-subjects-json-2026')['data']==[])
jfiles=sorted(f for f in RAW.glob('jnu-gx-2026-*.json') if not f.name.endswith('.meta.json'))
for f in jfiles:
 v=json.loads(f.read_text());check('JNU actual query empty '+f.stem,v['code']=='1000000' and v['data']['provinceScoreVOS']==[] and v['data']['provinceSpecializedSubjectScoreVOS']==[])
jpositive={}
for sid,track,n in [(3,'物理类',9),(2,'历史类',1)]:
 v=read(f'jnu-gx-2025-{sid}-1');jpositive[track]=len(v['data']['provinceSpecializedSubjectScoreVOS']);check('JNU positive '+track,v['code']=='1000000' and jpositive[track]==n)
summaries['jnu']={'configurationYears':[2025,2024,2023],'currentSuccessfulEmptyScoreQueries':len(jfiles),'positiveControl2025MajorRows':jpositive,'parameterUse':'2026菜单为空；广西/科类/类别ID从2025菜单明确读取，再发送年份2026作有边界空结果检验。'}
check('GZHMU external menu title 2025','2025年-广州医科大学本科招生网' in (RAW/'gzhmu-external.html').read_text())
check('CityDG independent school code','14851' in (RAW/'citydg-charter.html').read_text())
check('CityDG FAQ old achievement year','2025年在十三个省' in (RAW/'citydg-faq.html').read_text())
check('LZU successful official home still points to failed score entry','https://zsdata.lzu.edu.cn/zsdata/lqxx/#/lnfs' in (RAW/'lzu-home.html').read_text())

entries={'cuc':'https://zszx.cuc.edu.cn/static/front/cuc/basic/html_web/lnfs.html','jnu':'http://admission1.jiangnan.edu.cn/pc/historyScore/nonArt','lzu':'https://zsdata.lzu.edu.cn/zsdata/lqxx/#/lnfs','citydg':'https://uga.cityu-dg.edu.cn/public-information','buct':'https://goto.buct.edu.cn/static/front/buct/basic/html_web/lnfs.html','cufe':'https://zs.cufe.edu.cn/static/front/cufe/basic/html_web/lnfs.html','gzhmu':'https://zs.gzhmu.edu.cn/wnlqfs/lnfs_ws_/a2025n.htm'}
texts={
'cuc':'官方分数查询广西年份配置最新2025。2026物理类、历史类普通类查询以及省份/科类固定而招生类别留空的查询，均state=1且专业、学校汇总表为空；2025物理普通类正对照15条。未把艺术校考位次、2025专业分或海南办学条目当成2026本部广西专业分。本轮没有取得本年实际专业分，不断言其他渠道均未发布。',
'buct':'官方分数查询广西年份配置最新2025。2026广西物理、历史普通类均state=1且专业、学校汇总表为空；2025物理16条、历史2条专业记录作为正常查询正对照。年份未挪用，预科不作为实际普通专业分。',
'cufe':'官方分数查询广西配置最新2025。2026两科统招及招生类别留空查询均state=1且专业、学校汇总表为空；2025物理统招13条、历史统招8条为正对照。统招、国家专项、高校专项、中外合作和预科配置均保留于来源，未猜2026类别结果。',
'jnu':'先读取官网分数前端及其公开RSA-CSRF封装，正常请求成功后年份菜单只有2025/2024/2023；2026省份、广西科类菜单均成功空列表。广西ID=20、物理类=3、历史类=2均来自官方2025菜单。按这些已知分类发送2026普通/专项及预科诊断请求，六种组合均业务code=1000000且专业、学校汇总列表为空；2025普通类正对照物理9条、历史1条。预科只作入口诊断，不能进入实际专业库。早期缺CSRF及不合适Content-Type所致业务错误另存，未计为空数据。',
'lzu':'官网首页可正常读取并明确链接zsdata分数入口；该入口本轮HTTPS与HTTP读取失败，curl复核同样TLS失败，网页读取工具返回412。未能读取菜单、2026广西结果或旧年正对照；浏览器备用工具无可用浏览器。此结论属于查询入口访问限制，不等于学校没有发布或本年没有录取。招生章程抓取另有IncompleteRead，亦不当成成功原文。',
'citydg':'独立校码14851在本年夏季高考招生章程核实。已读学校官网、本科招生首页、招生政策、公开信息和常见问题；公开目录有2026章程与2025各省录取名单标题，常见问题里的分数描述明确是2025成绩概述，未提供2026广西单专业最低分。未读取含考生个人信息的录取名单，也未混用香港本校代码或成绩。仅说明这些已查入口未取得所需本年专业分。',
'gzhmu':'已读官网首页、招生动态、广东及外省历年分数目录，当前最新栏目为2025。原始外省成绩长图表头明确“广州医科大学2025年外省各专业录取情况汇总表”，广西只有物理临床医学614、临床药学596两行，是旧年资料，未入2026专业库。2026广东录取报道和个人录取查询入口不能代替广西专业统计；本轮没有取得2026广西实际专业分。'}
notes=[]
for code,name,slug in schools:
 ss=[s for s in sources if s['id'].startswith(PREFIX+slug+'-')]
 status='empty-current-response' if slug in ['cuc','buct','cufe','jnu'] else ('access-limited' if slug=='lzu' else 'old-year-material-only')
 notes.append({'id':'review-major-20260912b2-b-'+code,'auditKind':'major-scores','year':2026,'province':'广西','schoolCode':code,'school':name,'checkedAt':checked,'status':status,
               'accessLimitType':'year-unavailable-and-empty-query' if status=='empty-current-response' else ('score-entry-transport-failed' if slug=='lzu' else 'no-current-major-table-in-checked-material'),
               'entryUrl':entries[slug],'sourceIds':[s['id'] for s in ss],'checkedUrls':sorted({s['url'] for s in ss}), 'note':texts[slug], 'resultSummary':summaries.get(slug,{}), 'collectedMajorRecordCount':0})
ids={s['id'] for s in sources};check('7 exact target school notes',len(notes)==7 and len({n['schoolCode'] for n in notes})==7)
check('All note sources resolve',all(set(n['sourceIds'])<=ids for n in notes))
check('Frozen local audit date',checked.startswith('2026-09-12') and ('+08:00' in checked))
check('Source IDs unique',len(ids)==len(sources))
write('major-cutoffs-upsert.json',[]);write('sources.json',sources);write('school-audit-notes.json',notes)
write('QA.json',{'checkedAt':checked,'status':'PASS' if all(x['passed'] for x in checks) else 'FAIL','baseline':ctx['baseline'],
                'summary':{'schoolsChecked':7,'newMajorRows':0,'successfulCurrentEmptySchoolQueries':4,'oldYearMaterialOnlySchools':2,'scoreEntryAccessLimitedSchools':1,'sources':len(sources),'sourceArchivesHashChecked':sum(bool(s['archiveFile']) for s in sources),'checks':len(checks),'passedChecks':sum(x['passed'] for x in checks)},
                'schoolQuerySummaries':summaries,'imageReview':{'file':'raw/gzhmu-external-image.jpg','titleYear':2025,'guangxiRows':2,'track':'物理类','rowsRead':[{'major':'临床医学','minimum':614},{'major':'临床药学','minimum':596}],'disposition':'Old-year positive material only; zero rows imported'},'checks':checks})
print(json.dumps({'sources':len(sources),'notes':len(notes),'newMajorRows':0,'checks':len(checks),'failed':[x for x in checks if not x['passed']]},ensure_ascii=False))
assert all(x['passed'] for x in checks)
