#!/usr/bin/env python3
"""Freeze reviewed public snapshots. Raw pages stay local; no session values are copied."""
import datetime, hashlib, html, json, re, shutil
from pathlib import Path

R=Path(__file__).resolve().parent
E=R/'evidence'; E.mkdir(exist_ok=True)
def read(n): return json.loads((R/n).read_text())
def write(n,v): (R/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def plain(s): return html.unescape(re.sub('<[^>]*>',' ',s))

# code, title, data year, publication date, direct observed conclusion
D={
'scu-home-zs':('10610','四川大学本科招生网',None,None,'HTTP 412，未取得招生正文。'),
'scu-college-score-list':('10610','四川大学化学工程学院：历年招生数据',2025,None,'可读链接标为本科录取历年分数统计（截止2025年），发布日期2026-06-25。'),
'scu-score-index-current':('10610','四川大学本科录取历年分数统计（截止2025年）',2025,'2026-06-25','学院官网直接链接，访问HTTP 412。'),
'scu-score-spa':('10610','四川大学公开录取分数查询入口',None,None,'HTTP 483，正文显示访问策略禁止访问、错误403。'),
'xjtu-score-entry':('10698','西安交通大学历年录取查询入口',None,None,'HTTP 200返回网站正在加载中访问验证页，未取得专业表格；未执行验证挑战。'),
'hitsz-home':('18213','哈尔滨工业大学（深圳）报考指南',None,None,'官方入口加载历年分数页面。'),
'hitsz-score-entry':('18213','哈尔滨工业大学（深圳）历年分数查询前端',None,None,'已读公开年份、省份和专业分接口及分页字段。'),
'hitsz-score-years':('18213','哈尔滨工业大学（深圳）历年分数年份选项',None,None,'公开年份列表仅2025、2024；没有2026对应的年份ID，未猜测ID或跨年查询。'),
'seu-gx-list':('10286','东南大学广西壮族自治区招生资料目录',None,None,'目录共5项；本年招生计划与2025年专业分数并列，不能混年。'),
'seu-score-2025':('10286','东南大学2025年广西壮族自治区各专业分数线',2025,'2026-01-13','发布日期2026年，正文数据为2025年；全部排除。'),
'seu-progress-2026':('10286','东南大学2026本科招生录取进度表（截至2026年7月28日）',2026,'2026-07-14','招生进度说明，不含广西单专业最低录取分。'),
'csu-score-entry':('10533','中南大学本科普通类历年分数查询',None,None,'公开JS直接配置学校21393、表2614、API主机及过滤字段。'),
'csu-score-config':('10533','中南大学本科普通类录取结果公示：公开查询配置',None,None,'年份配置仅2020至2025；A年份、B省份、C科类。'),
'csu-score-2026-history':('10533','中南大学2026广西历史类普通本科专业分查询',2026,None,'公开接口成功，list为空且total=0；未将line_data汇总替代专业。'),
'csu-score-2026-physics':('10533','中南大学2026广西物理类普通本科专业分查询',2026,None,'公开接口成功，list为空且total=0；未将line_data汇总替代专业。'),
'bupt-home':('10013','北京邮电大学本科招生网',None,None,'HTTP 412，未取得可读正文。'),
'bupt-score-2024-entry':('10013','北京邮电大学2024年各省录取时间及分数线入口',2024,None,'检索发现的旧年入口访问仍HTTP 412；不作2026数据来源。'),
'fudan-score-list':('19246','复旦大学分省录取分数目录',None,None,'当前目录最新可读分数链接为2025年，2026-01-21发布。'),
'fudan-score-2025':('19246','复旦大学2025年分省录取分数（含医学院列）',2025,'2026-01-21','年份为2025；医学院列主要为院校科类汇总，不作2026专业录取线。'),
'fudan-med-charter-2026':('19246','复旦大学2026年本科招生章程',2026,'2026-05-28','确认校本部与医学院分别编制计划和招生，仅用于身份核对。'),
'muc-score-entry':('10052','中央民族大学录取分数查询',None,None,'前端2026、广西选项以及分专业最低分/最低分排名字段可读；说明小数向下取整。'),
'muc-tracks-2026-gx':('10052','中央民族大学2026广西录取科类选项',2026,None,'返回历史类6、物理类7、体育类12；本包只采6、7。'),
'muc-types-2026-gx-6':('10052','中央民族大学2026广西历史类招生类型选项',2026,None,'返回普通本科01、民族班36。'),
'muc-types-2026-gx-7':('10052','中央民族大学2026广西物理类招生类型选项',2026,None,'返回普通本科01、国家专项04、合作办学16、民族班36。'),
'muc-charter-2026':('10052','中央民族大学2026年本、预科招生章程',2026,'2026-05-28','第12/13条专业录取和加分、第15至17条语种/转专业、第20条民族班、第21条国家专项。'),
'xjtlu-score-2026':('16302','西交利物浦大学2026年分省录取数据',2026,None,'正文h1明确2026；广西3个正式招生大类，分别列计划数与实际录取数；URL的2023不是本次数据年。'),
'xjtlu-policy-index':('16302','西交利物浦大学招生政策',2026,None,'官方页面直接链接2026年中国内地本科招生章程。'),
'xjtlu-charter-2026':('16302','西交利物浦大学2026年中国内地本科招生章程',2026,None,'第3、8、10、11、15条核实本科批次原则、高考招生、大类含义、分数排序及英文教学。PDF第1、2页已目视核对。'),
}
for kl in ('6','7'):
 for t in read(f'raw/muc-types-2026-gx-{kl}.json')['rows']:
  key=f"muc-majors-2026-gx-{kl}-{t['lxdm']}"
  D[key]=('10052',f"中央民族大学2026广西{'历史' if kl=='6' else '物理'}类{t['lxmc']}分专业录取情况",2026,None,'公开分专业接口；未采录取概况接口。响应总数与rows长度一致。')

sources=[]; manifest=[]
for key,(code,title,year,pub,note) in D.items():
 m=read(f'raw/{key}.meta.json')
 assert m.get('sha256') and hashlib.sha256((R/m['rawFile']).read_bytes()).hexdigest()==m['sha256']
 s=dict(id='major-20260911-a-'+key,title=title,url=m['url'],schoolCode=code,year=year,publishedAt=pub,accessedAt=m['accessedAt'],sha256=m['sha256'],responseSha256=m['responseSha256'],httpStatus=m['httpStatus'],recordCount=0,method='正常匿名公开POST查询' if m.get('path') else '公开GET页面/查询',note=note)
 s['accessedAt']=datetime.datetime.fromisoformat(m['accessedAt']).astimezone(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
 if m.get('entryUrl'):s['entryUrl']=m['entryUrl']
 if m.get('request'):s['queryParameters']=m['request']
 if key.startswith('csu-score-2026'):
  from urllib.parse import parse_qs,urlparse
  s['queryParameters']={k:v[0] for k,v in parse_qs(urlparse(m['url']).query).items()}
 if key.startswith('muc-majors'):
  response=read(m['rawFile']); assert response['success'] and response['total']==len(response['rows'])
  s['recordCount']=response['total'];s['archiveFile']=f'evidence/{key}.json';shutil.copyfile(R/m['rawFile'],R/s['archiveFile'])
 elif key in ('hitsz-score-years','csu-score-2026-history','csu-score-2026-physics','muc-tracks-2026-gx','muc-types-2026-gx-6','muc-types-2026-gx-7'):
  s['archiveFile']=f'evidence/{key}.json';shutil.copyfile(R/m['rawFile'],R/s['archiveFile'])
 if key=='xjtlu-score-2026':s['recordCount']=3
 sources.append(s)
 j={k:v for k,v in m.items() if k in ('id','url','ext','host','path','entryUrl','request','csrf')}
 j.update(expectedArchiveSha256=m['sha256'],expectedHttpStatus=m['httpStatus']);manifest.append(j)

# Extract exactly the table under Guangxi, independent of changing navigation IDs.
t=(R/'raw/xjtlu-score-2026.html').read_text()
assert re.search(r'<h1[^>]*>\s*2026年分省录取数据\s*</h1>',t)
section=t.split('<h4>广西壮族自治区',1)[1].split('</table>',1)[0]
rows=[[plain(c).strip() for c in re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>',r,re.S)] for r in re.findall(r'<tr[^>]*>(.*?)</tr>',section,re.S)]
assert rows==[['科类','招生专业组','大类','计划数','录取数','最高分','最低分'],['历史','历史+不限','工商管理类','21','21','567','501'],['物理','物理+不限','金融学类','27','27','632','532'],['物理','物理+化学','电子信息类','62','62','605','531']]
write('evidence/xjtlu-guangxi-table.json',dict(year=2026,province='广西',sourceTitle='2026年分省录取数据',section='广西壮族自治区',headers=rows[0],rows=rows[1:],sourceId='major-20260911-a-xjtlu-score-2026',note='原网页表头招生专业组实际填写选科组合，不是三位省编专业组码。'))
write('evidence/source-snapshots.json',sources)
write('public-fetch-manifest.json',manifest)

# No challenge body or page/session data is copied into these conclusions.
config=read('raw/csu-score-config.json')['data']
write('evidence/query-observations.json',{
 'hitsz':{'exposedYears':[r['nj'] for r in read('raw/hitsz-score-years.json')],'requested2026Majors':False,'reason':'前端没有2026所需年份ID，不猜测。','sourceIds':['major-20260911-a-hitsz-score-entry','major-20260911-a-hitsz-score-years']},
 'csu':{'exposedYears':sorted(config['filter']['A']),'filterColumns':json.loads(config['detail']['filter_column']),'queries':[{'year':2026,'province':'广西','track':tr,'total':0} for tr in ['历史类','物理类']],'sourceIds':['major-20260911-a-csu-score-config','major-20260911-a-csu-score-2026-history','major-20260911-a-csu-score-2026-physics']},
 'muc':{'year':2026,'province':'广西','trackCodes':['6','7'],'excludedTrack':{'code':'12','label':'体育类（物理类）','queriedMajors':False},'pagination':'前端无分页参数；六个响应total均等于rows长度。','sourceIds':['major-20260911-a-muc-score-entry','major-20260911-a-muc-tracks-2026-gx']},
 'yearBoundary':{'seu':{'publicationYear':2026,'scoreYear':2025},'fudan':{'publicationYear':2026,'scoreYear':2025},'xjtlu':{'urlContains':'2023','pageTitleYear':2026}},
})
print('Frozen',len(sources),'sources; 35 MUC rows and 3 XJTLU rows.')
