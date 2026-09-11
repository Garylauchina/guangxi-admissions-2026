#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build this reviewed seven-school gap-only package from public frozen summaries."""
import datetime,json
from pathlib import Path
R=Path(__file__).resolve().parent
def read(n):return json.loads((R/n).read_text())
def write(n,v):(R/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
sources=read('source-snapshots.json');e=read('query-evidence.json')
assert e['scopeYear']==2026 and e['recordCount']==0 and len(e['schools'])==7
names={'10141':'大连理工大学','10053':'中国政法大学','10004':'北京交通大学','10008':'北京科技大学','10027':'北京师范大学','10183':'吉林大学','19614':'电子科技大学(沙河校区)'}
text={
'10141':'公开分数前端及API已核查。字典确认主校区（含开发区）=1、广西=450000、物理类=20、历史类=21。主校区年份接口为空；请求2026广西两科分类和分专业接口均成功返回空数组，未取得本年专业分。未限定招生类型，不把盘锦校区数据合入本部；入口/API空结果不等于学校所有发布渠道均无数据。',
'10053':'本科招生官网本次HTTP 200，但正文仅浏览器访问验证页，未取得可读录取查询字段或分数表。未执行验证挑战或猜造查询接口；未能按两科和类别进一步核查2026广西专业分，保留访问缺口。',
'10004':'已读公开历年分数前端和参数，广西选项仅2024、2025。实际请求2026广西物理/历史普通类，并查物理国家专项、民族班，分专业数组均空；对当前字典中的6个专业组名称逐一请求本年仍空。此举只记录查询结果，不证明旧年组标签或类别适用于2026；未将威海中外单列校区合入本部。',
'10008':'已读公开历年分数前端和参数，广西选项仅2023至2025。实际请求2026广西物理类普通类、国家专项及历史类普通类，均返回state=1且sszygradeList=[]。未将学校录取概况数组替代专业分；其他本年招生类别仍无直接记录。',
'10027':'当前计划分数目录最新为2026-06-18发布的本年计划与近年分数。广西单页附件表体明确2026招生计划及2025各专业录取分数，北京/珠海校区各自表头相同；全部旧年分数排除，未取得2026广西本部专业实际录取分。保持10027与19027校区身份独立。',
'10183':'官网公开JS直接指定的历年专业分CDN整表已完整下载，total与行数均为1704；逐行年份仅2022/2023/2024/2025，没有2026。广西有旧年记录231行，也全部排除；页面一次读取整表，没有漏采分页。本年物理/历史及各类别专业分仍缺。',
'19614':'本轮重新读取电子科大公开查询前端与选项，广西沙河校区菜单年份仅2021至2025，没有2026。以学校原文xqmc=电子科技大学（沙河校区）分别请求2026广西物理类、历史类普通类，均code=200、success=true、list=[]。本部和沙河代码保持独立，不把本部查询结果当沙河证据，其他本年类别未取得。'}
checked=max(datetime.datetime.fromisoformat(s['accessedAt']) for s in sources).astimezone(datetime.timezone(datetime.timedelta(hours=8))).isoformat();assert checked.startswith('2026-09-12')
notes=[]
for code,name in names.items():
 ss=[s for s in sources if s['schoolCode']==code]
 notes.append(dict(id='major-score-audit-2026-0912-'+code,year=2026,province='广西',auditKind='major-scores',title='2026广西专业录取分核查',schoolCode=code,school=name,checkedAt=checked,status='access-restricted' if code=='10053' else 'no-current-year-records',recordCount=0,sourceIds=[s['id'] for s in ss],checkedUrls=list(dict.fromkeys(s.get('entryUrl',s['url']) for s in ss)),note=text[code]))
qa=dict(status='PASS',checkedAt=checked,scopeSchoolCount=7,scoreRows=0,sourceCount=len(sources),auditNoteCount=7,coverageClaim='7校入口及公开查询完成有界核查；本轮0条满足2026广西实际单专业分口径，数据缺口未补齐。',checks=['7校身份/代码与任务清单一致','所有来源为本轮live请求并保留原始与归档hash','北交与北科本年分专业数组为空','大工主校区/广西/科类字典有直接前端字段证据','沙河使用独立xqmc本轮重新请求，两个科类均为空','北师表体2026计划与2025分数分开，未串年','吉林1704行与total一致，逐行年份只有2022至2025','不把院校/组线、计划人数、校测或艺术体育分作为专业分','公开摘要不含访问验证值、会话或原始整表','复核时间为北京时间2026-09-12'],limitations=['中国政法大学验证页阻挡可读前端，未实查两科类别查询','菜单缺2026和查询空结果只描述这些公开入口，不断言校方所有渠道均未发布','未解析或转用旧年录取分作本年参考','原始响应保留在本地raw，不公开发布'])
write('major-cutoffs-upsert.json',[]);write('sources.json',sources);write('school-audit-notes.json',notes);write('QA.json',qa)
print('PASS: 0 score rows,',len(sources),'sources, 7 school audit notes.')
