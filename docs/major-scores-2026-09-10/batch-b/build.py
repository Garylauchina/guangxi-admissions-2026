#!/usr/bin/env python3
"""Build verified 2026 Guangxi major outcomes and bounded negative-source audits."""
from pathlib import Path
from collections import Counter
import hashlib,json,re
from html_tables import NestedTables,expand
R=Path(__file__).resolve().parent
PREFIX='major-score-b-'
def read(name):return json.loads((R/name).read_text())
def write(name,obj):(R/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
metas={p.name[:-10]:json.loads(p.read_text()) for p in sorted((R/'raw').glob('*.meta.json'))}
checked=max(x['accessedAt'] for x in metas.values())
html=(R/'raw/cqnu-2026-outside-results.html').read_text()
assert '重庆师范大学2026年高考录取结果' in html and '2026年8月8日' in html
p=NestedTables();p.feed(html)
tables=[expand(t) for t in p.tables if t]
table=next(t for t in tables if t[0]==['省份','录取批次','科类','专业名称','最低分','备注'])
assert len(table)-1==370
plans=[];excluded=[];outside=Counter();gx=[]
for i,row in enumerate(table[1:],1):
 assert len(row)==6
 province,batch,track,major,score,note=row
 if province!='广西':outside[province]+=1;continue
 gx.append({'sourceRow':i,'cells':row})
 if track not in ['物理类','历史类'] or '艺术' in batch or '体育' in track:
  excluded.append({'sourceRow':i,'province':province,'batch':batch,'track':track,'major':major,'sourceScore':score,'sourceNote':note,'reason':'艺术体育口径，不是本批一般750分高考专业录取最低分'});continue
 if '等专业' in major or '、' in major:
  excluded.append({'sourceRow':i,'province':province,'batch':batch,'track':track,'major':major,'sourceScore':score,'sourceNote':note,'reason':'多个专业合并公布最低分，不能拆成各专业实际最低分'});continue
 assert batch=='本科批' and score.isdigit() and 0<int(score)<=750 and note in ['', '征集']
 sid=PREFIX+'cqnu-2026-outside-results'
 plans.append({'id':f'major26-b-cqnu-{i}','year':2026,'province':'广西','school':'重庆师范大学','schoolCode':'10637','track':track.replace('类',''),'batch':'本科普通批','sourceBatch':batch,'sourceTrack':track,'sourceCategory':'普通高考','group':None,'major':major,'majorCode':None,'score':int(score),'scoreType':'专业录取最低分','sourceScoreLabel':'最低分','plannedCount':None,'admittedCount':None,'rank':None,'rankType':None,'sourceMaximumScore':None,'sourceAverageScore':None,'requiredSubjects':[],'subjectRule':'unknown','requirementText':None,'round':'征集（次数未分）' if note=='征集' else '录取汇总（轮次未分）','admissionType':'普通类','sourceId':sid,'sourceRow':i,'sourceTable':'重庆市以外省份录取结果完整表','fieldSourceIds':{'schoolCode':[PREFIX+'cqnu-code-gxeea']},'sourceNote':note,'note':('原表备注“征集”，未列第几次征集。' if note else '截至2026年8月8日的录取结果，原行未区分首轮或其他轮次。')+'原表为单一专业或单一正式招生大类最低分；未公布专业组、最低位次、最高分、平均分、计划数和录取数。','reviewedAt':checked,'evidenceStatus':'verified','scoreComparable':True,'scoreEvidenceGaps':[],'conflictFields':[]})
assert len(gx)==19 and len(plans)==11 and len(excluded)==8
assert Counter(x['track'] for x in plans)=={'历史':5,'物理':6}
assert sum(x['round'].startswith('征集') for x in plans)==1
# Source freshness guards: changes require a new factual review, never a fake zero record.
njp=read('raw/nju-score-params-session.json');assert njp['state']==1
njopts=njp['data']['ssmc_nf_klmc_sex_campus_zslx_Map'].get('广西',[])
assert not any(x['nf']=='2026' for x in njopts)
for n in ['nju-scores-gx-2026-probe-1','nju-scores-gx-2026-probe-2']:
 q=read('raw/'+n+'.json');assert q['state']==1 and q['data']['zsSsgradeList']==[] and q['data']['sszygradeList']==[]
sjtu=read('raw/sjtu-score-news-list.json');assert sjtu['code']==0
sjtu_years=[int(re.search(r'(20\d{2})年',x['contentTitle']).group(1)) for x in sjtu['data']['list']]
assert max(sjtu_years)==2025
fudan=(R/'raw/fudan-score-list.html').read_text();assert max(map(int,re.findall(r'复旦大学(20\d{2})年分省录取分数',fudan)))==2025
zju=(R/'raw/zju-score-2026-article.html').read_text();assert '2025年浙江大学各省份普通本一批投档分数线' in zju
med=(R/'raw/sjtu-med-latest-score-article.html').read_text();assert '上海交通大学医学院2025年普通批次录取分数线' in med
code_html=(R/'raw/cqnu-code-gxeea.html').read_bytes().decode('gb18030')
code_text=re.sub('<[^>]+>','',code_html)
assert re.search(r'10637\s*重庆师范大学',code_text)
info={
'nju-score-page':('南京大学历年分数公开前端',None,None,'公开前端区分zsSsgradeList（省级汇总）与sszygradeList（分专业），不能相互替代；查询字段名及CSRF流程由此页关联脚本确认。'),
'nju-tplt-js':('南京大学官网公开请求流程脚本',None,None,'确认Cookie会话、时间戳与公开CSRF请求流程；不保存会话值。'),
'nju-score-params-session':('南京大学录取分数公开筛选条件',2025,None,'正常公开流程HTTP200/state1；广西物理/历史仅返回2025普通批次、2024一般录取、2023文理一般录取，未列2026任何类别。'),
'nju-scores-gx-2026-probe-1':('南京大学2026广西物理类普通分数空结果探查',2026,None,'字段名来自分数前端，普通批次类别来自已公开历史选项；2026是本任务指定年份，并不声称存在于当前筛选菜单。正常公开流程返回state1，省级和专业级列表均为空；空结果不等于0分或不招生。'),
'nju-scores-gx-2026-probe-2':('南京大学2026广西历史类普通分数空结果探查',2026,None,'字段名来自分数前端，普通批次类别来自已公开历史选项；2026是本任务指定年份，并不声称存在于当前筛选菜单。正常公开流程返回state1，省级和专业级列表均为空；空结果不等于0分或不招生。'),
'fudan-score-list':('复旦大学录取分数栏目（最新数据年2025）',2025,None,'本轮栏目最新标题为2025年分省录取分数，没有可核2026广西专业最低分。'),
'sjtu-med-score-list':('上海交通大学医学院历年分数栏目',2025,None,'本轮最新可读文章为2025年普通批次分数，未采旧年记录。'),
'sjtu-med-latest-score-article':('上海交通大学医学院2025年普通批次录取分数线（排除）',2025,'2025-10-01','只核查原文标题及发布时间以判定年份错误；不纳入2026专业线。'),
'zju-score-list':('浙江大学历年录取分数栏目',2025,None,'当前最新链接发布于2026，但内容年度须读取文章标题判断。'),
'zju-score-2026-article':('2025年浙江大学各省份普通本一批投档分数线（2026年发布，排除）',2025,'2026-06-17','文章发布日期2026-06-17，但标题和内容是2025年普通本一批投档线，既非2026、亦非单专业实际录取最低分。'),
'sjtu-home':('上海交通大学本科招生网',None,None,'用于官方入口定位；未将计划人数、咨询或录取查询入口当作专业分数。'),
'sjtu-score-news-list':('上海交通大学历年分数官方公开栏目API',2025,None,'公开只读newsList请求subjectsID3810062，12条文章数据年份2014至2025；未出现2026录取分数文章。'),
'cqnu-2026-outside-results':('重庆师范大学2026年高考录取结果——重庆市以外省份',2026,'2026-08-08','完整解析370行数据，广西19行：纳入11个单一专业/正式大类，排除3艺术和5多个专业合并最低分。地理科学类作为单一正式大类保留。未标轮次的10行不称首轮；食品质量与安全547注明征集但次数未分。'),
'cqnu-code-gxeea':('广西2026本科普通批物理类投档表（仅重庆师范大学校码佐证）',2026,None,'仅核对10637对应重庆师范大学，未用该组投档表补专业分或专业组。')}
sources=[]
for key,m in metas.items():
 title,year,published,method=info[key]
 s={'id':PREFIX+key,'title':title,'url':m['url'],'sourceType':'official','sourceDataYear':year,'year':year,'queryYear':2026,'publishedAt':published,'accessedAt':m['accessedAt'],'sha256':m['sha256'],'recordCount':11 if key=='cqnu-2026-outside-results' else 0,'method':method,'httpStatus':m['status'],'requestMethod':'POST' if m.get('request') is not None else 'GET','requestData':m.get('request'),'rawFile':m['rawFile']}
 if m.get('responseSha256'):s.update(responseSha256=m['responseSha256'],archiveSha256=m['archiveSha256'],redactedFields=m['redactedFields'])
 sources.append(s)
audit_specs=[
('10248','上海交通大学',['sjtu-home','sjtu-score-news-list'],'not-found-current-major','官方分数栏目最新数据年2025；未取得2026广西两科普通或明确资格类别的单专业实际最低分。仅能确认本轮未找到，不能宣称学校不招生。'),
('19248','上海交通大学医学院',['sjtu-med-score-list','sjtu-med-latest-score-article'],'not-found-current-major','官方最新可读分数文章为2025普通批次；未取得2026广西专业最低分。独立校码，不与交大本部混用。'),
('10246','复旦大学',['fudan-score-list'],'not-found-current-major','官方分数栏目最新为2025分省录取分数，未取得2026广西专业最低分；未采用搜索中的旧年参考、预测或其他省综评成绩。'),
('10335','浙江大学',['zju-score-list','zju-score-2026-article'],'not-found-current-major','2026-06-17发布文章实际是2025年分省投档线，年度和分数层级都不符合2026广西专业实际最低分；未将医学院等独立代码并入本部。'),
('10284','南京大学',['nju-score-page','nju-tplt-js','nju-score-params-session','nju-scores-gx-2026-probe-1','nju-scores-gx-2026-probe-2'],'empty-current-response','正常公开流程已跑通；分数菜单广西只有2025/2024/2023。对2026物理与历史普通批次分别作明确标注的缺年探查，两次均state1且省/专业列表为空。未见2026资格类别选项，未猜测专项参数。'),
('10637','重庆师范大学',['cqnu-2026-outside-results','cqnu-code-gxeea'],'collected-partial','本轮实际录入11条2026广西专业最低分，历史5/物理6，其中征集1。排除艺术3和多专业合计5；这是可明确到单一专业/正式大类的部分覆盖，其他专业仍有缺口。')]
audits=[]
for code,name,keys,status,note in audit_specs:
 audits.append({'schoolCode':code,'school':name,'year':2026,'province':'广西','checkedAt':checked,'status':status,'checkedUrls':[metas[k]['url'] for k in keys],'sourceIds':[PREFIX+k for k in keys],'tracksChecked':['物理','历史'],'qualificationScope':'普通高考及来源明确列出的资格类别；未取得的2026类别不猜补','recordCount':11 if code=='10637' else 0,'recordCountMeaning':'本批已采集记录数，零不表示学校不招生或录取分为零','accessRestriction':'none','evidenceGapType':None if code=='10637' else ('empty-year-query' if code=='10284' else 'no-current-major-source'),'note':note})
write('major-cutoffs-upsert.json',plans);write('sources.json',sources);write('school-audit-notes.json',audits)
write('excluded-records.json',{'sourceId':PREFIX+'cqnu-2026-outside-results','fullTableDataRows':370,'guangxiRows':19,'acceptedRows':11,'excludedGuangxiRows':excluded,'outsideGuangxiRows':sum(outside.values()),'outsideGuangxiCounts':dict(outside),'excludedSourceYearExamples':[{'sourceId':PREFIX+'zju-score-2026-article','publishedYear':2026,'dataYear':2025,'reason':'发布日期不是录取年份，且是投档分层级'},{'sourceId':PREFIX+'sjtu-med-latest-score-article','dataYear':2025,'reason':'不是2026数据'}]})
write('cqnu-guangxi-table.json',gx)
write('fetch-results.json',list(metas.values()))
print('built',len(plans),'major rows;',len(sources),'sources;',len(audits),'school audits')
