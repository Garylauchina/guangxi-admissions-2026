#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build the reviewed gap-only package offline from bundled summaries; dates stay frozen."""
from pathlib import Path
import json
R=Path(__file__).resolve().parent;P='major-20260912b2-a-'
def read(n):return json.loads((R/n).read_text())
def write(n,d):(R/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
sources=read('source-snapshots.json');e=read('query-evidence.json');context=read('review-context.json')
assert len(sources)==60 and context['scoreRows']==e['recordCount']==0 and len(e['schools'])==7
scope=[
('10422','山东大学','empty-current-response','no-current-year-menu-and-empty-query','http://www.bkzssys.sdu.edu.cn/static/front/sdu/basic/html_web/lnfs.html','官网当前广西菜单只列2023至2025。依据公开科类和类别字段，本轮请求2026物理普通、国家专项、高校专项、少数民族预科、专业志愿，以及历史普通、国家专项、高校专项、少数民族预科共9组合，均state=1且分专业数组为空。2025普通正对照物理24条、历史11条正常。2026各类型公告原图只有省市/科类/统计类型汇总，无专业名称列，不挪作专业分。本包查本部系统，不合并威海；旧年类别探查不证明本年各类别安排相同。'),
('10268','上海中医药大学','access-restricted','gateway-timeout','https://ygzs.shutcm.edu.cn/','本科招生入口两次请求均HTTP 504；学校主页另返回HTTP 403。本轮未取得可读前端年份/科类菜单或2026广西专业分，不能完成两科与类别请求。访问失败不等于本年没有录取或没有发布；不记录成成功空表。'),
('10590','深圳大学','previous-year-only','current-table-is-prior-year','https://zs.szu.edu.cn/info/1153/2984.htm','已读官网历年分数主入口、分省目录及广西正文。广西专业表体明确为2025年与2024年，包含历史和物理，不能因当前访问年份为2026而收录。主入口另注按第一次投档统计，这一口径也不能自动视作最终专业实际录取。本轮未在这些官方入口取得2026广西专业实际分；不把此结论扩大到所有发布渠道。'),
('10272','上海财经大学','access-restricted','captcha-required','https://zs.sufe.edu.cn/zsjh/list.htm','官网历年录取分数iframe可读，年份选项含2026/2025/2024、省市含广西；结果模板列有年份、省市、科类名称、专业名称、最高分、最低分、备注。但提交查询必须填写图形验证码。本轮未提交绕过验证的请求，未取得物理/历史及类别实际行；仅确认本年查询入口，不能宣称专业分已采集或查询为空。'),
('10559','暨南大学','previous-year-only','current-directory-is-prior-year','https://zsb.jnu.edu.cn/2026/0518/c33879a855601/page.htm','已读当前历年分数总入口、2025各省目录和广西表。标题及正文属于2025年录取分，发布时间为2026-05-18；总入口注明2025各省普通类专业录取分（含2026招生指南）。广西正文物理/历史普通及国家专项、校区、录取人数、最高平均最低分均为旧年，全部排除。本轮未在这些入口取得2026广西实际专业分，未将2026计划人数混入实际人数。'),
('10652','西南政法大学','access-restricted','http-412','https://zs.swupl.edu.cn/','学校主页可访问，但招生就业入口和本科招生官网均HTTP 412，返回访问验证内容，未取得可读分数前端。本轮没有完成2026广西物理/历史及类别查询；不执行验证挑战，不把访问失败写成空数据。'),
('10019','中国农业大学','empty-current-response','no-current-year-menu-and-empty-query','https://zb.cau.edu.cn/static/front/cau/basic/html_web/lnfs.html','学校主页链接的HTTP历年分数入口实际重定向HTTPS；初始HTTP或未完成会话请求403已保留，最终按HTTPS正常匿名Cookie及公开CSRF流程查询成功。广西菜单仅2023至2025。本轮2026物理普通、国家专项、高校专项、中外合作办学与历史普通、中外合作办学共6组合均state=1且分专业数组为空；2025普通正对照物理21、历史6条正常。本轮不合并烟台研究院类别，未将各省录取结果公告的类别/组汇总当专业分。旧年选项探查不证明本年类别安排相同。')]
notes=[]
for code,school,status,limit,entry,note in scope:
 ss=[s for s in sources if s['schoolCode']==code]
 notes.append(dict(id='major-score-audit-20260912b2-a-'+code,auditKind='major-scores',year=2026,province='广西',schoolCode=code,school=school,checkedAt=context['checkedAt'],status=status,accessLimitType=limit,entryUrl=entry,sourceIds=[s['id'] for s in ss],checkedUrls=list(dict.fromkeys(s.get('entryUrl') or s['url'] for s in ss)),note=note))
qa=dict(status='PASS',checkedAt=context['checkedAt'],reviewDate=context['reviewDate'],summary=dict(schoolsChecked=7,newMajorRows=0,sources=len(sources),schoolNotes=7,successfulCurrentEmptyQueries=15,oldYearPositiveControls=4,accessRestrictedSchools=3,previousYearOnlySchools=2,currentEmptyResponseSchools=2),scope='7校公开入口有界核查完成；没有新增满足2026广西单专业实际录取分口径的记录。',checks=['60份归档hash与来源元信息一致','山东9组和农大6组2026查询均HTTP200/state1/sszygradeList为空','4个2025正对照共62条专业行，年省科类明确，未导入','山东本部与威海、农大本部查询与烟台研究院类别分开','2026录取类别/组汇总不转为专业分','深圳/暨南表体旧年与发布时间分开','上财仅本年入口且验证码必填，未冒称查询已完成','访问失败与成功空响应分开保存','审核日期来自冻结采集元信息，不依赖运行当天','公开文件仅含最小来源元信息、查询条件、汇总证据和本包脚本'],limitations=['上海中医药、西南政法因访问失败未读分数菜单；上海财经未通过验证码提交查询','缺口结论只覆盖已列入口、字段与参数，不等于所有官方渠道均未发布','旧年分数、类别/组汇总和第一次投档口径不纳入本轮实际专业数据'])
write('major-cutoffs-upsert.json',[]);write('sources.json',sources);write('school-audit-notes.json',notes);write('QA.json',qa)
print('PASS: 0 added rows; 60 sources; 7 bounded school audits.')
