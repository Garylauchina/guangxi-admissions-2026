#!/usr/bin/env python3
"""Build the frozen seven-school gap package offline, with no repository dependency."""
import json
from pathlib import Path
R=Path(__file__).resolve().parent
def read(n):return json.loads((R/n).read_text())
def write(n,d):(R/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
sources=read('source-snapshots.json');e=read('query-evidence.json');c=read('review-context.json');assert len(sources)==51 and len(e['schools'])==7 and e['recordCount']==0
scope=[
('10635','西南大学','access-restricted','http-412','https://bkzswu.swu.edu.cn/static/front/admission#/data-export/open-score-page2','本科招生主页可读，链接的历年分数新入口分别以HTTP和HTTPS实访均返回412访问验证页。没有取得年份、科类和类别菜单，未执行验证挑战，未完成2026广西两科专业分查询。该结论仅限已列入口；访问失败不能证明本年未发布。没有将荣昌校区或院校专业组分数代替本部专业分。'),
('10359','合肥工业大学','empty-current-response','no-current-year-menu-and-first-filing-scope','https://bkzs.hfut.edu.cn/static/front/hfut/basic/html_web/lnfs.html','公开导航与历年分数配置已读。广西菜单只有2024/2025，合肥与宣城独立。本轮仅合肥校区，2026物理普通批、物理国家专项、历史普通批3组合HTTP200/state1且分专业数组为空；2025普通正对照物理27条、历史3条，响应校区均合肥。配置原文“所有分数均为第一次投档数据”，该口径不能自动作为实际专业录取汇总；旧年正对照也全部排除。旧年类别探查不证明2026类别设置相同。'),
('10712','西北农林科技大学','empty-current-response','no-current-year-menu-and-empty-query','https://hjhfmx.nwafu.edu.cn/auth/zsdata/lqxx/#/lnfs','新公开查询前端和JSON字段已读，广西菜单止于2025。2026物理/历史普通及物理国家专项、高校专项、中外合作共5组合均HTTP200/code200/success=true且专业和汇总数组为空；2025普通正对照物理44、历史6条，表体年省科类正确。初次未携带JSON请求体的500单独保留，不计有效空表；旧入口重定向学校身份认证，但新公开接口可正常匿名访问。预科、强基及艺术不作为本包专业实际分，旧年类别不视作本年安排。'),
('11078','广州大学','no-current-records-message','explicit-no-match-with-old-year-control','https://zsjy.gzhu.edu.cn/bkzn/lnfs2.htm','公开表单配置显示不需登录、无需图形验证码，按页面给出的匿名公开请求头和字段查询。2026广西不限科类类别及分别物理/历史普通文理共3请求均HTTP200，应用层code9999并明确“未查询到相关数据”；这是无匹配提示，不计作成功空数组。2025广西同接口正对照成功取得全17条（返回total=17），表体年省及两科正确。旧年初次504与成功重试分别留证。静态年份按钮止于2025；本轮未取得2026实际专业行，未将2026配置修改时间当分数年。'),
('10079','华北电力大学(保定)','previous-year-only','public-dataset-only-2025','https://zhaosheng.ncepu.edu.cn/lqfs/index.htm','保定本科招生官网页尾与前端独立major_bd_json.json证实校区身份。完整公开专业JSON1166条的year全部为2025，广西41条：物理37（普通29、国家专项7、高校专项1），历史普通4。没有2026行；另一个aii_bd_json.json是学校类别汇总，不转专业分。本轮不合并北京10054，不把访问日期当数据年。'),
('10403','南昌大学','empty-current-response','no-current-year-menu-and-empty-query','https://zjc.ncu.edu.cn/zs/zsw/lnfs.html','按真实前端字段和正常匿名会话及公开CSRF流程查询。广西菜单仅2024/2025；2026物理普通、历史普通、物理中外合作3组合HTTP200/state1且专业数组为空，2025普通正对照物理30、历史8条，表体nf/ssmc/klmc明确。未将专业介绍2026更新时间当分数年，未把学校汇总或介绍代码当实际专业分。2026其他类别是否另行发布未由旧年菜单证明。'),
('10161','大连医科大学','previous-year-only','old-directory-and-attachment-captcha','https://recruit.dmu.edu.cn/zsdt/lqfs.htm','本科招生历年分数目录当前列“近三年（2023—2025）”及“2025年分省市区、分专业录取分数”等旧年内容，没有本年分专业表。2025公告附件下载链接实访返回验证码HTML，未取得PDF，不能声称核实了附件表体、广西科类或全部页。2026计划、指南和旧年分数分开；本轮没有取得2026广西实际专业行，未绕过附件验证码。')]
notes=[]
for code,school,status,limit,entry,note in scope:
 ss=[s for s in sources if s['schoolCode']==code]
 notes.append(dict(id='major-score-audit-20260912b3-a-'+code,auditKind='major-scores',year=2026,province='广西',schoolCode=code,school=school,checkedAt=c['checkedAt'],status=status,accessLimitType=limit,entryUrl=entry,sourceIds=[s['id'] for s in ss],checkedUrls=list(dict.fromkeys(s.get('entryUrl') or s['url'] for s in ss)),note=note))
qa=dict(status='PASS',checkedAt=c['checkedAt'],reviewDate=c['reviewDate'],summary=dict(schoolsChecked=7,newMajorRows=0,sources=51,schoolNotes=7,successfulCurrentEmptyQueries=11,explicitNoMatchMessages=3,oldYearPositiveControls=7,oldYearPositiveRows=135,priorYearFullDatasetRows=1166,priorYearFullDatasetGuangxiRows=41),checks=['51份原归档SHA与来源元信息逐一相符，原响应与脱敏归档hash分别保留','南昌3、西北农林5、合工大合肥3个本年空数组请求有效，中文参数来自前端','7个旧年正对照135条，年省科类与合肥校区表体吻合','广州3个code9999无匹配提示和有效空数组分别统计，17条旧年正对照无漏页','合工大第一次投档口径明确排除，不作为专业实际录取汇总','保定JSON全1166条只有2025，广西41条且校区独立','西南412、大连旧附件验证码HTML、初次无效请求/超时均不当成功空表','公开包不含原HTML/JS/JSON、个人名单、会话值和私有路径','审核日期冻结2026-09-12，不随离线重建时间漂移'],limitations=['缺口结论仅覆盖实际检查的入口、菜单、字段及参数，不能证明所有官方渠道均未发布','没有新增行，因此不补猜组码、位次、批次、人数或轮次；旧年及首次投档数据均不进入本年专业录取集合','大连医科旧附件表体未通过验证码读取；西南大学未完成两科及类别查询'])
write('major-cutoffs-upsert.json',[]);write('sources.json',sources);write('school-audit-notes.json',notes);write('QA.json',qa)
print('PASS: 0 new rows, 51 sources, 7 bounded school audit notes.')
