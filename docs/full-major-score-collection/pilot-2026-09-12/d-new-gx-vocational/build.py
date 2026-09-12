"""Build the manually reviewed D pilot. No score is inferred from a gap."""
from pathlib import Path
import json, hashlib
ROOT=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text())
write=lambda name,obj:(ROOT/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
targets=read(ROOT/'targets.json')
# Each observation is bounded to the actual sources below, not the whole Internet.
decisions=[
('10605','access-limited',['10605-guide'], '河池招生网报考指南的公开检索结果列出2026计划及2025录取分、2025本科专业分统计。直接读取HTTPS指南、首页及HTTP指南均超时。本次没有获得2026实际专业录取表；访问失败不能证明学校尚未发布。'),
('11354','prior-year-only',['11354-zs','11354-scores','11354-gx-round2'], '历年分数查询经浏览器正常加载，年份下拉仅2015—2025，无2026。另读2026年7月28日广西第二次征集公告，仅物理类2人及最高/最低/平均投档成绩，未列专业。'),
('11546','prior-year-only',['11546-zs','11546-scores'], '历年分数栏目最新专业统计为2025年广西本科、分县公费师范生等，发布日期2026年1月15日。已读首页及统计目录，本次未取得2026广西实际专业录取分。'),
('11547','reviewed-gap',['11547-zs','11547-notice'], '由学校官网进入招生信息网，检查通知公告及导航。2026公安招生公告为报考、面试体检等安排；原lnfsx地址实际栏目名称为招生监督投诉电话及邮箱，不是历年分数。所查入口未取得2026实际专业录取表。'),
('11671','prior-year-only',['11671-home','11671-notice','11671-2025-score','11671-2026-progress'], '招生公告首屏覆盖2026通知书进程、计划和2025投档分，2026年6月4日公布附件标题明确为2025广西区内普通高考投档分。2026通知书进程不构成专业分统计；本次未取得2026专业录取最低分。'),
('11355','other-route-only',['11355-zs','11355-scores2026'], '2026年录取分数线栏目共1条，为2026年6月8日广西职教高考招生分专业分类统计；涉及对口免试等类型，不能纳入普通高考物理/历史专业分。'),
('12104','group-only',['12104-zs-new','12104-scores-new','12104-2026-result'], '沿旧招生就业入口跳转到新的zsxx招生站。历年分数栏目最新为2025本科专业及2023—2025专科统计。2026年8月27日录取收官公告列广西本科151/104及专科116/156组投档成绩，未列实际专业分。'),
('11773','other-route-only',['11773-zs','11773-scores','11773-queryjs','11773-menu2026','11773-menu2025','11773-ordinary-menu2025','11773-2025-ordinary-物理组','11773-2025-ordinary-历史组','11773-2026-ordinary-物理组','11773-2026-ordinary-历史组'], '依据页面实际脚本调用年份菜单接口。2026菜单result=1、errno=0，仅广西/职教高考/单招与对口类型；2025对照菜单含普通批、艺术提前批及精准专项。进一步按实际菜单值广西壮族自治区/普通批/物理组或历史组查询，2026均正常返回norecords=y及0条；同参数2025对照分别37条、26条，验证接口和筛选有效。当前查询未取得2026普通高考专业分，不能把职教成绩代入。'),
('11837','prior-year-only',['11837-zs'], '通过学校官网进入zsbgs招生站，首页历年录取栏目最新为2026年3月17日公布的2025广西等省统计。本次公开入口未取得2026广西专业录取分。'),
('16205','prior-year-only',['16205-zs','16205-scores'], '历年录取分数栏目最新普通高考表为2025广西本科、专科、精准专项及区外表。已核栏目，未将2025分数或专升本/对口统计作为2026普通高考专业分。'),
('10867','reviewed-gap',['10867-zs','10867-notice'], '检查招生首页、普通高考导航及招生公告。2026现有内容为章程、计划与自治区控制线；公告中的录取名单及征集计划多为2025。未取得2026普通高考实际专业分表，省控线不作学校专业分。'),
('11608','prior-year-only',['11608-zs','11608-scores'], '历年分数目录最新为2025区内物理、历史和区外统计，另列对口/单招。未取得2026广西普通高考分专业录取结果。'),
('12356','prior-year-only',['12356-zs','12356-scores'], '招生官网及历年分数目录列2026年6月15日发布的2025广西普高各专业分数及排位、6月23日发布的2025区外分数。2026普通高考通知为计划与通知书寄送，不能替代专业成绩。'),
('12392','prior-year-only',['12392-zs','12392-2025'], '实际打开首页所链2025年全国普高统招录取分数一览表；2026导航内容为章程、专业一览及职教录取名单。所查入口未取得2026广西普通高考实际专业录取分。'),
('14313','outcome-without-scores',['14313-browser-list','14313-browser-history'], '通过浏览器正常访问招生服务栏目。2026广西历史类录取名单表头为序号、考生号、姓名、性别、录取专业，没有分数字段；栏目另有物理类名单。本次不从名单推算专业分，不公开个人信息。'),
('14358','group-only',['14358-browser-2026','14358-browser-menu'], '浏览器读取2026各省录取分数线公告，广西部分明确列101—106专业组分数，没有实际专业明细。历年分数查询年份最高2025，选择广西后返回2025物理/历史组投档线；不把组线转为专业分。'),
('12301','group-only',['12301-zs','12301-2026'], '2026年8月18日公告为各省普通类平行志愿投档线，广西历史与物理各列组分。附注虽说明部分组名称对应医学专业，原统计仍是专业组投档线，不转为实际专业录取分。'),
('12040','prior-year-only',['12040-zs','12040-scores'], '由学校官网招生信息链接进入zsw站并读取历年分数栏目，所见最新为2021各省普通高考统计，其余更早。仅能报告该栏目缺2026广西专业分，不能据此断言其他渠道未发布。'),
('14592','prior-year-only',['14592-zs','14592-scores'], '历年计划及分数栏目有2026夏季省内外计划、春季及三二分段计划；专业分数表最新标题为2024，不能把计划或2024专业分当2026录取结果。'),
('14012','prior-year-only',['14012-home','14012-zs','14012-scores'], '学校官网所链jysd招生平台历年数据查询年份原值为25、2020、2019、2018、2017，省份含广西；未提供2026选项。不擅自把25解释或改写为2026。'),
('10861','group-only',['10861-zs','10861-2026','10861-2026-img'], '视觉核对8月21日录取动态所附图，表头为2026普通高考最低投档分数线，广西仅历史431、物理408两条科类汇总，未分专业。省外科类统计不能拆到各专业。'),
('10870','prior-year-only',['10870-home','10870-zs'], '从学校主页进入招生信息网，普通高考外省、四川、重庆、定培军士分数标题均为2025，发布日期2026年4月28日；未取得2026广西实际专业分。'),
('13713','reviewed-gap',['13713-zs','13713-pg'], '普高招生栏目最新2026内容为外省/广东计划；分数资料为2025广东各专业和2022省外最低分。本次未取得2026广西实际专业分，广东专业表不跨省移用。'),
('13943','prior-year-only',['13943-zs','13943-scores'], '历年录取分数栏目最新为2024广东省分专业与2024各省第一志愿出档分，随后为2023资料。已读正式栏目，未取得2026广西实际专业分。'),
('12055','prior-year-only',['12055-zs','12055-guide'], '实际打开官网多少分可报考文章及历年分数查询导航，年份最高2025。2026文章为报考说明，要求参考近3年，不能将预期波动或单招分数代入广西统招专业分。'),
('12942','schedule-only',['12942-zs','12942-2026'], '2026普通专科批次录取安排表仅省市、计划数、录取时间三列，广西为5个计划和8月6—7日安排，不含录取分数。官网2026分专业计划不作为录取成绩。'),
('13036','other-route-only',['13036-zs','13036-scores'], '往年分数目录2026条目是单招专业分，普通统招表最新2025，旧年标题及正文又涉及在湘统计。未取得2026广西普通高考实际专业分。'),
('12572','access-limited',['12572-zs','12572-score2026','12572-scoreold'], '招生首页链到2026普通高考录取情况及历年分数微信公众号原文，两页本次均返回环境异常、需验证，未得到可复核正文。不据搜索标题填分，不把验证页当空数据。'),
('12573','other-route-only',['12573-zs','12573-scores2026'], '浏览器加载2026年录取分数栏目后，正文为2026春季学考、3+证书第一次投档录取数据，发布2026年6月11日。该统计不属于广西普通高考实际专业录取分。'),
('12791','prior-year-only',['12791-scores'], '历年录取栏目最新为2025浙江普高、艺术、单独考试及省外普高分数，随后2024、2023等；不把浙江专业明细或2025省外统计移用为2026广西专业分。'),
]
browser_sources={
 '14313-browser-list':('https://www.gxwzy.edu.cn/jy/ptzs','招生服务栏目'),
 '14313-browser-history':('https://www.gxwzy.edu.cn/jy/ptzs/ptgk/content_28330','2026广西历史类录取名单的表头核查'),
 '14358-browser-2026':('https://zsw.cswszy.com/details/article?id=735187','2026各省录取分数线公告'),
 '14358-browser-menu':('https://zsw.cswszy.com/listPage?uuid1=221c91d3-88d9-4862-b54d-26b791f44819&uuid2=ce96a145-d3c1-4ef5-9907-35481d822847','历年分数查询菜单及2025广西对照'),
}
assert {x[0] for x in decisions}=={x['schoolCode'] for x in targets}
notes=[];sources={};observations=[]
for code,status,keys,note in decisions:
 t=next(x for x in targets if x['schoolCode']==code)
 ids=[];urls=[]
 for key in keys:
  sid='pilot100-d-'+key;ids.append(sid)
  s={'id':sid,'publisher':t['school'],'year':None,'publishedAt':None,
     'accessedAt':'2026-09-12','evidenceRole':'source-review'}
  if key in browser_sources:
   url,title=browser_sources[key]
   s.update(url=url,title=t['school']+'：'+title,captureMethod='browser-visible-content',notes=['仅记录公开栏目与表头的核查结论，不收录个人名单。'])
  else:
   meta=read(ROOT/'raw'/(key+'.meta.json'))
   s.update(url=meta['url'],title=t['school']+'：'+key,accessedAt=meta['checkedAt'],httpStatus=meta.get('httpStatus'),requestMethod='POST' if 'data' in meta else 'GET')
   if meta.get('sha256'):s['responseSha256']=meta['sha256'];s['sha256']=meta['sha256']
   if meta.get('archiveFile'):s['archiveFile']=meta['archiveFile']
   if meta.get('error'):s['accessError']=meta['error']
   if 'data' in meta:s['requestData']=meta['data']
  sources[sid]=s;urls.append(s['url'])
 notes.append({'id':'review-major-pilot100-d-'+code,'year':2026,'province':'广西','schoolCode':code,
  'school':t['school'],'auditKind':'major-scores','checkedAt':'2026-09-12',
  'title':'2026广西专业录取分首次核查','status':status,'recordCount':0,
  'sourceIds':ids,'checkedUrls':urls,'note':note,
  'scope':'核查范围仅为列明的官网栏目、原文与查询菜单；未取得不等于未招生或所有渠道均未发布。'})
 observations.append({'taskId':t['taskId'],'schoolCode':code,'school':t['school'],
  'outcome':status,'actualMajorRows':0,'sourceIds':ids,'finding':note,
  'nextAction':'继续追踪2026广西普通高考实际分专业统计；有有效新原文后再重查本校。'})
write('major-cutoffs-upsert.json',[]);write('sources.json',list(sources.values()))
write('school-audit-notes.json',notes);write('observations.json',observations)
write('PUBLIC-FILES.json',['build.py','fetch.py','targets.json','observations.json','sources.json','school-audit-notes.json','major-cutoffs-upsert.json','README.md']+[f.name for f in sorted(ROOT.glob('requests-*.json'))])
(ROOT/'README.md').write_text('# 广西及高职首次核查：30校\n\n2026-09-12完成冻结清单中的30校公开来源核查。实际专业录取分新增0条；逐校缺口、来源及后续入口见 observations.json。\n\n浏览器额外核对梧州年份菜单、长沙卫生2026组线及2025广西对照、广西卫生名单表头、广东食品药品2026栏目正文。广东交通附图已视觉核对。登录/验证页不算空表，旧年、其他考试及组线均未入专业录取分表。\n\n原始响应保存在本地 raw，不公开整页、名单或会话信息。PUBLIC-FILES.json为发布白名单。fetch.py仅请求明确的公开URL；build.py从逐校人工结论构建审计记录，不推测分数。\n')
print(json.dumps({'reviewedSchools':len(notes),'newActualMajorRows':0,'sources':len(sources)}))
