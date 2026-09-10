"""Bounded negative evidence: report only pages and query conditions actually checked."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
SPECS=[
 ('广西师范大学','10602',['gxnu-index','gxnu-years','gxnu-lines-all'],'year-unavailable','本轮官方专业分数列表及公开查询年份配置最高为2025；查询2026返回空。本轮未取得2026专业录取最低分，不能推断所有发布渠道均无数据。'),
 ('桂林电子科技大学','10595',['guet-index','guet-query'],'year-unavailable','本轮官方分数查询表单年份选项为2020至2025，没有2026选项；尚无本轮可核验2026专业最低线。'),
 ('广西大学','10593',['gxu-lines-entry'],'not-found-in-checked-index','已检查的官方历年分数列表最新专业录取结果为2025年，2026年发布项仍指2025预科；未取得2026实际专业录取线。'),
 ('广西民族大学','10608',['gxmzu-index'],'not-found-in-checked-index','本轮招生首页可见分数结果为2025年；未取得2026实际专业录取线。仅为所查官方首页结果。'),
 ('广西民族师范学院','10604',['gxnun-lines-index'],'not-found-in-checked-index','已查官方分数栏目最新相关标题为2026招生计划及2025专业录取分数，并非2026实际专业分数。'),
 ('南宁师范大学','10603',['nnnu-lines-物理类','nnnu-lines-历史类'],'empty-for-checked-query','2026、广西、普通类、历史类/物理类、空校区的公开lnfs接口返回success=true及空列表；这是限定参数检索结果，不能据此声称全校2026未发布。'),
 ('西安电子科技大学','10701',['xidian-lines-物理类'],'empty-for-checked-query','公开lnfs接口按2026、广西、普通类、物理类及长安校区返回成功空列表；限该参数组合，未核实全校所有批次。'),
 ('天津大学','10056',['tju-lines-物理类'],'empty-for-checked-query','公开lnfs接口按2026、广西、普通类、物理类及北洋园校区返回成功空列表；限该参数组合。'),
 ('电子科技大学','10614',['uestc-lines-物理类'],'empty-for-checked-query','公开lnfs接口按2026、广西、普通类、物理类及电子科技大学校区返回成功空列表；限该参数组合。'),
 ('广西财经学院','11548',['gxufe-home'],'dynamic-query-not-completed','已访问学校自建招生主页，内容由动态列表加载；本轮尚未完成其2026专业录取结果查询，不作未发布判断。'),
 ('北部湾大学','11607',['bbgu-home'],'landing-page-only','已访问招生根入口，原页为图片导航并指向sy.htm；本轮未完成下级历年分数栏目复查，不作未发布判断。'),
 ('广西中医药大学','10600',['gxtcm-home','gxtcm-advance','gxtcm-vocational'],'image-transcription-pending','已找到2026提前批和高职高专录取进程公告及图片；本轮未完成所有图片中专业与组线口径的逐行转录核对，未纳入实际专业分。应显示已找到证据待解析，不能标成未发布。'),
 ('广西工程职业学院','14127',['gxgc-lines-physics','gxgc-lines-history'],'filing-only','已核实81条2026逐专业投档最低分并另存major-filing-cutoffs.json；官方表未据此确认最终实际专业录取最低分，不计实际录取覆盖。'),
]
rows=[]
for school,code,ids,limit,result in SPECS:
    meta=[json.loads((ROOT/'raw'/f'{sid}.meta.json').read_text()) for sid in ids]
    rows.append({'school':school,'schoolCode':code,'checkedAt':max(m['accessedAt'] for m in meta),
                 'checkedUrls':[m['url'] for m in meta],'sourceIds':ids,'result':result,
                 'accessLimitType':limit,'scope':'本轮已列明页面或参数；非全校全站穷尽检索'})
(ROOT/'negative-findings.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
