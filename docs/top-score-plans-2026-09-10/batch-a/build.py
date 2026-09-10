#!/usr/bin/env python3
"""Build a bounded negative-result package from public-source access evidence.

No rows are manufactured from national major catalogues, old-year plans, or
group filing scores. Run fetch_public.py first to refresh the declared URLs.
"""
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
def read(name):
    return json.loads((ROOT / name).read_text())
def write(name, value):
    (ROOT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')

results = {}
for file in sorted(ROOT.glob('phase*-results.json')):
    for row in read(file.name):
        results[row['id']] = row
if (ROOT / 'request-manifest-results.json').exists():
    for row in read('request-manifest-results.json'):
        results[row['id']] = row

now = datetime.now(timezone.utc).isoformat()
targets = read('targets.json')
assert len(targets) == 7
assert {x['schoolCode'] for x in targets} == {'10001', '19001', '10003'}
assert all(x['year'] == 2026 and x['round'] == '首轮' for x in targets)
assert sorted(x['group'] for x in targets if x['schoolCode'] == '10003') == ['103','104','601','602']

# All assertions are about inspected public snapshots, not the absence of
# unpublished plans elsewhere. Refreshed changed pages require renewed review.
med_raw = (ROOT / 'raw/med-gx-2025.html').read_text()
assert '2025' in med_raw and '广西' in med_raw and '2026' not in med_raw
legacy = (ROOT / 'raw/thu-plan-legacy.html').read_bytes().decode('gb18030')
assert 'var nf="2014"' in legacy and 'queryByCon' in legacy
query_ids = [f'thu-query-2026-{track}-{category}' for track in ['physics','history'] for category in ['general','special']]
assert all(read(f'raw/{key}.json') == [] for key in query_ids)
control = read('raw/thu-query-control-2014-gx.json')
assert control and all(x['nf'] == '2014' and x['sf'] == '广西' for x in control)
assert '/Login.aspx' in results['gx-plan-login']['finalUrl']

# The title/year below describes each actual source, never relabels old data.
definitions = [
 ('pku-ordinary-alias','北京大学本科招生网：普通高考栏目',None,None,'官方招生入口；未取得2026广西分专业计划。'),
 ('pku-brochures-alias','北京大学本科招生网：招生简章目录',None,None,'目录直链2026年招生简章，未列广西分省计划。'),
 ('pku-brochure-2026','北京大学2026年招生简章暨报考指南',2026,'2026-06-12','核验目录及印刷页199–202：全国专业一览与2023–2025省级录取分数；不是2026广西分省计划。'),
 ('pku-contact','北京大学2026年招生咨询联系方式',2026,'2026-06-22','2026广西咨询入口，未载分专业计划；原页说明联系方式有效至2026-07-31。'),
 ('med-plans','北京大学医学部：历年招生计划栏目',None,None,'年选项仅2025、2024、2023，不能视作2026计划。'),
 ('med-gx-2025','北京大学医学部2025年广西招生计划（旧年排除证据）',2025,None,'面包屑及年选项明确2025；仅用作排除旧年数据的证据，不导入2026。'),
 ('med-notices','北京大学医学部本科招生通知公告',None,None,'存在2026年招生咨询公告链接，未取得2026广西分专业计划。'),
 ('thu-general','清华大学本科招生网：高考统招栏目',None,None,'当前2026条目为入校选拔方案，未取得广西分专业计划。'),
 ('thu-self','清华大学本科招生网：自强计划栏目',None,None,'栏目最新简章为2025年；不能用2025规则或专业名单填充2026高校专项组。'),
 ('thu-plan-legacy','清华大学官方历年招生计划查询（旧版入口）',2014,None,'界面年份2010–2014，公开前端查询参数可读；2026广西四项查询为空。'),
 ('thu-info-disclosure','清华大学信息公开：招生考试',None,None,'分批次、分科类招生计划链接到阳光高考首页，未直链2026广西表。'),
 ('thu-contact-2026','清华大学2026年招生咨询组联系方式及提示',2026,'2026-06-22','广西图片经目视核验，仅咨询教师、电话、地点与项目联系人，没有专业或计划数。'),
 ('gx-plan-login','广西官方招生计划查询：登录要求实测',None,None,'公开访问计划入口重定向到登录页；未登录、未绕过验证，不能据此声称计划不存在。'),
]
for key in query_ids:
    q = results[key]['query']
    definitions.append((key,f"清华旧版公开计划接口：2026广西{q['track']}{q['category']}查询",2026,None,'只读POST，按公开前端m/nf/sf/kl/jhlx字段查询；返回空数组，非零招生人数。'))

sources = []
for key,title,source_year,published,note in definitions:
    r = results[key]
    assert r.get('status') == 200 and r.get('sha256'), key
    assert hashlib.sha256((ROOT / r['file']).read_bytes()).hexdigest() == r['sha256']
    sources.append(dict(id='top-a-'+key,title=title,url=r['url'],publishedAt=published,accessedAt=r['checkedAt'],sha256=r['sha256'],recordCount=0,method=note,sourceYear=source_year,sourceKind='entry-or-gap-evidence',usable2026GuangxiPlan=False))
write('sources.json',sources)
source_map = {x['id']: x for x in sources}

notes = {
 '10001':'已取得北大2026全国招生指南和官方招生入口，但指南未提供广西分省分专业计划；未取得本组专业、人数及直接省编组码关系，不能用全国专业目录或旧年计划填充。',
 '19001':'医学部官方计划栏目目前仅列2025、2024、2023；广西可读计划页明确属于2025，已排除。2026咨询微信入口返回环境验证，未绕过。尚未取得2026广西本组计划。医学部19001与北大本部10001分别记录。',
 '10003':'清华官方旧计划查询仅列2010–2014；2026广西文理科的统招与专项查询均为空，2014广西同编码阳性对照可返回数据。现有2026专业类介绍和咨询公告不是广西分省计划；尚未取得本组专业、人数及直接组码关系。',
}
school_sources = {
 '10001':['pku-ordinary-alias','pku-brochures-alias','pku-brochure-2026','pku-contact','gx-plan-login'],
 '19001':['med-plans','med-gx-2025','med-notices','gx-plan-login'],
 '10003':['thu-general','thu-self','thu-plan-legacy','thu-info-disclosure','thu-contact-2026','gx-plan-login']+query_ids,
}
catalog=[]
for code,name,entry in [('10001','北京大学',None),('19001','北京大学医学部','https://bkzs.bjmu.edu.cn/zsxx/zsjh/index.htm'),('10003','清华大学','https://bk.join-tsinghua.edu.cn/student.bz_bzw_zsjh.do')]:
    row=dict(schoolCode=code,school=name,year=2026,status='entry-only',sourceKind='仅官方入口或全国资料，未取得2026广西初始计划',sourceIds=['top-a-'+key for key in school_sources[code]],checkedAt=now,note=notes[code])
    if entry: row['entryUrl']=entry
    catalog.append(row)
write('source-catalog.json',catalog)

target_results=[]
for t in targets:
    ids=school_sources[t['schoolCode']]
    if t['schoolCode']=='10003':
        track='physics' if t['track']=='物理' else 'history'
        category='special' if t['group'] in ['601','602'] else 'general'
        ids=[x for x in ids if not x.startswith('thu-query-2026-')] + [f'thu-query-2026-{track}-{category}']
    target_results.append(dict(cutoffId=t['id'],year=2026,province='广西',schoolCode=t['schoolCode'],school=t['school'],track=t['track'],batch=t['batch'],group=t['group'],score=t['score'],status='entry-only',note=notes[t['schoolCode']],sourceIds=['top-a-'+key for key in ids],checkedAt=now,addedPlanCount=0,matchedPlanCount=0,missingFields=['本组专业组成','初始计划人数','直接省编组码与专业对应','再选科目要求','学费','学制','培养与报考限制'],checkedUrls=[source_map['top-a-'+key]['url'] for key in ids]))
write('target-results.json',target_results)
write('plans-upsert.json',[])

attempts=[]
for r in results.values():
    out={k:r[k] for k in ['id','url','query','purpose','checkedAt','status','contentType','sha256','bytes','error'] if k in r}
    if r.get('finalUrl') and r['finalUrl'] != r['url']:
        out['redirectedToLogin']='/Login.aspx' in r['finalUrl']
    if r['id']=='med-consult-wechat': out['contentResult']='环境异常，要求完成验证；没有获取正文，未绕过。'
    if r['id'] in query_ids: out['contentResult']='[]；仅说明该旧接口未返回所查2026数据。'
    if r['id']=='thu-query-control-2014-gx': out['contentResult']=f'{len(control)}条2014广西记录；阳性对照，不导入。'
    attempts.append(out)
write('access-evidence.json',attempts)
assert len({x['cutoffId'] for x in target_results}) == 7
assert all(x['status']=='entry-only' for x in target_results)
assert all(set(x['sourceIds']) <= set(source_map) for x in target_results+catalog)
qa=dict(status='passed-with-explicit-gaps',checkedAt=now,targets=7,schools=3,newPlans=0,matchedTargets=0,partialTargets=0,entryOnlyTargets=7,sources=len(sources),attempts=len(attempts),sourceChecks=['北大2026指南页首及目录目视核年，全国专业目录不当作广西计划。','医学部可读广西表的2025年份经过正文与导航双检，未改年。','清华2026四个查询为空，2014同字段同编码查询返回旧年记录作阳性对照。','广西计划页直接跳转登录，未登录或绕验证。'],limits=['没有采到可录入的2026广西初始专业计划；本批仅补来源入口与逐组缺口。','没有取得七组的完整专业名单、分组计划总人数、选科、学费学制及培养限制，均不推定。','搜索范围为公开官网、官网指向的查询系统及省级入口；不是不存在公开资料的证明。','清华旧版“专项计划”标签未细分高校专项，不凭此标签定义2026类别。'])
write('QA.json',qa)
print(json.dumps(qa,ensure_ascii=False,indent=2))
