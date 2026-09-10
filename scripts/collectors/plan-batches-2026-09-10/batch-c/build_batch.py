"""Create batch C initial plans from public official tables. No website writes."""
from pathlib import Path
from collections import Counter,defaultdict
import json,re,hashlib
from parse_tables import parse

R=Path(__file__).resolve().parent
ROOT=R.parents[2]
DATE='2026-09-10'
plans=[];sources=[];catalog=[]

def source(k,title,url,publisher,date=None,method=None,**kwargs):
    sid='batch-c-2026-'+k
    sources.append(dict(id=sid,title=title,url=url,publisher=publisher,sourceType='official',year=2026,publishedAt=date,accessedAt=DATE,method=method or '2026高校官方公开初始招生计划；逐行核对，不含征集和实际录取人数。',**kwargs))
    return sid
def row(school,code,group,track,major,count,sid,**kw):
    ident='plan26-batch-c-'+hashlib.sha256('|'.join([code,group,track,major]).encode()).hexdigest()[:16]
    d=dict(id=ident,year=2026,province='广西',schoolCode=code,school=school,track=track,batch='本科普通批',group=group,major=major,majorCode=None,requiredSubjects=[],subjectRule='unknown',plannedCount=count,tuition=None,duration=None,note='',sourceId=sid,category='普通类',requirementText=None,planStage='initial',planVersion='2026高校公开初始计划（以省招办公布及后续正式调整为准）',currentGaokaoSeatsKnown=True,checkedAt=DATE)
    d.update(kw);plans.append(d);return d
def cat(code,school,status,ids,note,url):
    catalog.append(dict(schoolCode=code,school=school,year=2026,province='广西',status=status,sourceIds=ids,checkedAt=DATE,note=note,entryUrl=url))

jnu_url='https://zsb.jnu.edu.cn/2026/0622/c4288a857512/page.htm'
jnu=source('jnu','暨南大学2026年在广西招生计划（共113人）',jnu_url,'暨南大学','2026-06-22')
table=parse(R/'evidence/jnu.html')[0]['rows']
jnu_totals={};excluded=[]
for i,c in enumerate(table,1):
    if len(c)!=10 or '合计' in c[0] or not re.fullmatch(r'\d+',c[8]):continue
    if c[1] not in ['历史类','物理类'] or '艺术' in c[0]:
        if '艺术' in c[0]:excluded.append(dict(school='暨南大学',sourceRow=i,major=c[3],count=int(c[8]),reason='艺术类'))
        continue
    assert c[0].startswith('本科普通批')
    g=re.search(r'专业组(\d{3})',c[2]);assert g,c
    req=c[2].split('选科要求：')[-1]
    category='国家专项计划' if '国家专项' in c[0] else '普通类'
    reqsub=['化学'] if '化学' in req else []
    note='；'.join(x for x in [category if category!='普通类' else '',c[9],'办学地点：'+c[5],'学院：'+c[4]] if x)
    row('暨南大学','10559',g.group(1),c[1].replace('类',''),c[3],int(c[8]),jnu,requiredSubjects=reqsub,subjectRule='all' if reqsub else 'none',tuition=int(c[6]),duration=c[7],requirementText=req,category=category,note=note,sourceRow=i,campus=c[5],college=c[4])
assert sum(x['plannedCount'] for x in plans)==109
assert sum(x['count'] for x in excluded)==4
cat('10559','暨南大学','collected',[jnu],'已采集普通类97人及国家专项12人，共109人；剔除艺术3条共4人。专业组代码、选科、学费、学制、校区、原备注均直接来自当年计划表。',jnu_url)

jx_url='https://zsw.jxpu.edu.cn/info/1187/17992.htm'
jx=source('jxpu','江西职业技术大学2026年分专业计划汇总表（外省本科）',jx_url,'江西职业技术大学','2026-06-17')
tables=parse(R/'evidence/jxpu.html')
t=next(t for t in tables if '2026年广西本科招生计划' in t['rows'][0][0])
heading=t['rows'][1][0]
assert '11785' in heading and '历史类专业组代码：101' in heading and '物理类专业组代码：151' in heading
for i,c in enumerate(t['rows'],1):
    if len(c)!=7 or c[0] not in ['物理','历史'] or not re.fullmatch(r'\d{6}',c[1]):continue
    row('江西职业技术大学','11785','101' if c[0]=='历史' else '151',c[0],c[2],int(c[5]),jx,majorCode=c[1],majorCodeType='专业目录代码（非广西志愿专业代号）',tuition=int(c[6]),duration=c[4],sourceRow=i,sourceTable='广西本科招生计划',note='当年初始本科计划；原表给出科类和广西组码，未列再选科目要求，不能推定不限。专业代码为六位专业目录代码。')
assert sum(x['plannedCount'] for x in plans if x['schoolCode']=='11785')==75
cat('11785','江西职业技术大学','collected',[jx],'已采集广西本科17条75人。原文标题明确广西且列院校代码11785，历史101组、物理151组；未列再选科目，保持unknown。',jx_url)

hz_url='https://zsw.zjhu.edu.cn/2026/0618/c3208a252607/page.htm'
hz=source('hznu','湖州师范大学2026年分省分专业招生计划安排（省外）',hz_url,'湖州师范大学','2026-06-18',method='官方网页检索正文的完整广西段逐行转录；当年计划列和分组三位代码可读。本轮直接TLS请求失败，记录此访问限制；非第三方转载。')
identity=source('hznu-identity','广西2026本科普通批首轮官方院校名称与代码（湖州师范大学身份核对）','https://www.gxeea.cn/view/content_624_33106.htm','广西招生考试院','2026-07-18',method='仅核对院校代码10347和学校名称；计划人数及专业组组成来自高校2026计划表，未用投档人数/分数推计划。')
cat('10347','湖州师范大学','source-found',[hz,identity],'官方单条搜索结果返回连续完整广西段16条70人及101/102/103组；原站本轮TLS直连失败，web open也失败，仅保留候选，不导入计划。除临床医学原备注明确5年外，其他专业学制未在该计划段列出，保持null。',hz_url)

# Prioritized schools with genuine current-year plans but no explicit Guangxi code mapping.
hnu_url='https://admi.hnu.edu.cn/info/1315/7353.htm'
hnu=source('hnu-entry','湖南大学广西2026招生计划（2025年各专业录取分数线）',hnu_url,'湖南大学','2026-06-08',method='重读当年计划入口及PDF；2026计划列与2025参考分数列分开。该表使用校编专业组1至5，未据此猜测广西三位代码。')
hnu_pdf=source('hnu-pdf','湖南大学2026年在广西招生情况及往年录取分数（官方PDF）','https://admi.hnu.edu.cn/__local/5/79/44/994F87C32D11E75CED0E1DDF164_97B38535_741CE.pdf','湖南大学',None,method='本轮可下载官方PDF，SHA256与2026-09-05原已读PDF一致。只列校编组号，三位广西代码映射未取得；本批不导入。',sha256='77f7c011a632172ee2156974dfc76d68fafa980e3dcf9cea5aba01968b337ced')
cat('10532','湖南大学','source-found',[hnu,hnu_pdf],'已取得2026广西初始计划，含普通/专项等，2025列为历史录取线；学校PDF用专业组1至5，未取得广西101等正式代码对应原文，不能自行加100。本批暂不导入。',hnu_url)
scut_url='https://admission.scut.edu.cn/30820/list.htm'
scut=source('scut-entry','华南理工大学2026招生计划官方查询入口',scut_url,'华南理工大学',None,method='原已采2026广西查询表为校编组1至4；本轮GET返回405，改用官方查询的空体POST后200可读。未证实与广西151至154的代码映射。')
cat('10561','华南理工大学','source-found',[scut],'已定位2026广西计划查询，原公开查询表为校内组1至4；本轮官方空体POST查询成功，仍未获三位广西组码映射，不将组序号转填为正式组码。',scut_url)
csu_url='https://zhaosheng.csu.edu.cn/a26jhyl/jh_bk.htm'
csu=source('csu-entry','中南大学本科招生在线—招生计划查询入口',csu_url,'中南大学',None,method='官网招生计划链接所用公开查询接口本轮可读2026广西物理类计划，使用物化1组等校内名称，未列三位广西组码。')
cat('10533','中南大学','source-found',[csu],'本轮公开查询接口返回2026广西物理类计划，名称为物化1组/物化生1组等；非广西103等正式代码，未取得对应关系原文，不推组码。本批暂不导入。',csu_url)
zju_url='https://bgptzdzsc.zju.edu.cn/zjuzsxj/xjjh-detail/2026?id=450000'
zju=source('zju-entry','浙江大学2026广西招生信息入口',zju_url,'浙江大学',None,method='本轮公共入口可访问但返回动态框架；原目录有招生联系信息，未在本轮取得带广西正式组码的完整初始专业计划表。')
cat('10335','浙江大学','entry-only',[zju],'入口可访问，不能等同已获取本年专业计划。当前未读到带广西正式组码与人数的原始完整表，本批未导入。',zju_url)
cpu_url='https://zb.cpu.edu.cn/2d/1d/c12765a208157/pagem.htm'
cpu=source('cpu-entry','中国药科大学2026年广西招生计划',cpu_url,'中国药科大学','2026-06-19',method='已读官方普通批计划原图，合计90人，图列专业组1至5；未取得广西三位正式组码对应原文。本批未导入。')
cat('10316','中国药科大学','source-found',[cpu],'当年计划官方原图可读，普通批90人；仅列校编专业组1至5，不猜测广西专业组代码。',cpu_url)

# Search-result-only evidence is staged separately, never admitted to production plans.
hz_candidates=[x for x in plans if x['schoolCode']=='10347']
plans=[x for x in plans if x['schoolCode']!='10347']
for s in sources:
    s['recordCount']=sum(x['sourceId']==s['id'] for x in plans)
fetchlog=json.loads((R/'evidence/fetch-log.json').read_text())
for k,sid in [('jnu',jnu),('jxpu',jx)]:
    sha=next(x for x in fetchlog if x['id']==k).get('sha256')
    next(x for x in sources if x['id']==sid)['sha256']=sha
for name,obj in [('plans-upsert.json',plans),('sources.json',sources),('source-catalog.json',catalog),('excluded-rows.json',excluded),('pending-hznu-plans.json',hz_candidates)]:
    (R/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
stats={school:{'rows':sum(x['school']==school for x in plans),'seats':sum(x['plannedCount'] for x in plans if x['school']==school)} for school in sorted({x['school'] for x in plans})}
print(json.dumps({'rows':len(plans),'seats':sum(x['plannedCount'] for x in plans),'schools':stats,'sources':len(sources),'catalog':len(catalog)},ensure_ascii=False,indent=2))
