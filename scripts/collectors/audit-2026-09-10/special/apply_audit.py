"""Apply manually reviewed 2026 official facts. No network, authentication or private data.

Input is the previously published 43-record snapshot; outputs are auditable research
JSON, not direct website edits. Raw web evidence stays in the local evidence folder.
"""
from pathlib import Path
from collections import Counter
import copy, json, re

ROOT = Path(__file__).resolve().parent
BASE = ROOT / 'baseline-special-programs.json'
OLD = ROOT
DATE = '2026-09-10'
programs = json.loads(BASE.read_text())
before = copy.deepcopy(programs)
sources = json.loads((OLD / 'baseline-sources.json').read_text())
policies = json.loads((OLD / 'baseline-policies.json').read_text())
by = {p['id'].removeprefix('strong-2026-'):p for p in programs if p['type']=='strong-foundation'}
sid = {s['id']:s for s in sources}
changes = []

def source(key, title, url, publisher, date=None, verification='已重读2026官方原文，核对本次采用字段。'):
    ident = 'audit-special-source-2026-' + key
    if ident not in sid:
        obj = dict(id=ident,title=title,url=url,publisher=publisher,platform='高校官方网站',sourceType='official',year=2026,publishedAt=date,accessedAt=DATE,verification=verification)
        sources.append(obj);sid[ident]=obj
    return ident

def attach(k, *ids):
    by[k]['sourceIds'] = list(dict.fromkeys(by[k]['sourceIds'] + list(ids)))

def finding(kind, school, summary, ids, **kw):
    changes.append(dict(id='special-audit-'+str(len(changes)+1).zfill(3),kind=kind,school=school,summary=summary,sourceIds=ids,**kw))

direct = {
 'pku':('https://bkzs.pku.edu.cn/tzgg/4dc8487f304e476786627574e8744c27.htm','2026-04-15'),
 'buaa':('https://zs.buaa.edu.cn/info/1008/3538.htm','2026-04-13'),
 'tju':('https://zs.tju.edu.cn/info/1116/3829.htm','2026-04-07'),
 'hust':('https://zsb.hust.edu.cn/info/1006/3040.htm','2026-04-08'),
 'hnu':('https://admi.hnu.edu.cn/info/1186/7295.htm',None),
 'csu':('https://zhaosheng.csu.edu.cn/info/1242/2499.htm','2026-04-08'),
 'uestc':('https://zs.uestc.edu.cn/view/2098.html','2026-04-08'),
 'nudt':('https://www.nudt.edu.cn/xwgg/tzgg/77c49bac43724c279c017f58a85a996e.htm','2026-04-10'),
 'cqu':('https://zhaosheng.cqu.edu.cn/pub/desktopend/contentpage/1181','2026-04-10'),
}
brochure={k:'special-source-2026-'+k for k in by}
for k,(url,date) in direct.items():
    brochure[k]=source(k+'-brochure',by[k]['school']+'2026年强基计划招生简章',url,by[k]['school'],date)
    attach(k,brochure[k]);by[k]['officialUrl']=url

# The original six values stay unchanged; the missing units and formulas are repaired.
formula_image = source('ustc-formula','中国科学技术大学2026年强基计划综合成绩公式（简章内原图）','https://zsb.ustc.edu.cn/_upload/article/images/67/83/78ff82204c528dbb25b3fbe50a0c/47c31005-08de-4373-9079-277dcf438334.png','中国科学技术大学','2026-04-10','已逐字目读公式原图，并与简章中校考满分270分（笔试200、面试70）核对。')
formulae={
 'ustc':(100,'高考成绩（不含加分）/该省高考满分×85+学校考核成绩/270×15','学校考核满分270分；第一类笔试200分、面试70分。',[brochure['ustc'],formula_image]),
 'xmu':(1000,'高考成绩（不含加分）/高考总分×850+学校考核成绩','综合成绩四舍五入取2位小数；校考满分150分，第一类初试与面试各占50%。',[brochure['xmu']]),
 'csu':(100,'(高考成绩（不含加分）/高考满分)×100×85%+面试成绩×15%','面试成绩满分100分。',[brochure['csu']]),
}
for k,(maximum,formula,note,ids) in formulae.items():
    for r in by[k]['scoreRecords']:
        r.update(maxScore=maximum,formula=formula,formulaStatus='verified',note=note+'这是录取综合成绩，含校考，不能与高考原始分或普通批投档线直接比较。')
        r['sourceIds']=list(dict.fromkeys(r['sourceIds']+ids))
    attach(k,*ids)
    finding('formula-repaired',by[k]['school'],f"补齐{len(by[k]['scoreRecords'])}条综合成绩公式及{maximum}分制，原数值不变。",ids,affectedScoreIds=[r['id'] for r in by[k]['scoreRecords']])

# Province confirmation uses explicit Guangxi evidence, not the national school list.
scope_news = {
 'thu':('清华大学2026年高考录取通知书寄送进度（7月16日）','https://m.admissions.tsinghua.edu.cn/info/1033/2213.htm','2026-07-16','2026年7月16日录取通知书寄送公告的强基计划栏目明确列广西，确认当年广西实际录取；公告未给出人数和分数。','actual-admission'),
 'fudan':('复旦大学2026年强基计划初试安排预告','https://ao.fudan.edu.cn/ec/fa/c36331a781562/page.htm','2026-05-29','2026年A类考生初试生源表明确广西对应南宁考点，确认广西考生申请/校考范围；不据此推定具体专业、计划人数或实际录取数。','application-test-scope'),
 'tju':('天津大学关于公示2026年强基计划录取标准的通知','https://zs.tju.edu.cn/info/1116/4829.htm','2026-07-03','2026录取标准原图明确广西能源与动力工程83.88（综合成绩）。','admission-cutoff'),
 'hnu':('湖南大学2026年强基计划录取标准公布','https://admi.hnu.edu.cn/info/1150/7417.htm','2026-07-03','2026录取标准表明确广西化学82.05（综合成绩）。','admission-cutoff'),
 'hust':('华中科技大学2026年强基计划录取结果公布','https://zsb.hust.edu.cn/info/1009/3092.htm','2026-07-04','2026录取标准原图明确广西化学、生物科学、物理学（依托物理学院培养）的综合成绩线。','admission-cutoff'),
}
scope_ids={}
for k,(title,url,date,note,typ) in scope_news.items():
    ident=source(k+'-scope',title,url,by[k]['school'],date,'已重读官方公告；天津大学、华中科技大学广西行已目读官方原图。')
    scope_ids[k]=ident;attach(k,ident)
    by[k].update(guangxiStatus='confirmed',guangxiEvidence=note)
    by[k]['scopeAudit']=dict(status='reverified',evidenceType=typ,checkedAt=DATE,sourceIds=[ident],note=note)
    finding('province-confirmed',by[k]['school'],note,[ident],oldStatus='unknown',newStatus='confirmed')

csu_entry=source('csu-entry','中南大学2026年强基计划校考安排（含分省分专业入围资格线）','https://zhaosheng.csu.edu.cn/info/1288/2638.htm','中南大学','2026-06-27','已核对广西行及六专业列顺序：应用物理学601、材料科学与工程616。')
hust_entry=source('hust-entry','2026年强基计划第一类报考条件考生入围校考标准','https://zsb.hust.edu.cn/info/1009/3087.htm','华中科技大学','2026-06-26','已目读官方原图广西3条；原图明示小数点后依次为最后一名入围考生语文、数学、外语单科成绩，不能作小数分。')

def add_score(k, major, value, typ, maximum, formula, ids, note='',raw=None,code=None):
    p=by[k];r=dict(id=f'strong-2026-{k}-audit-{len(p["scoreRecords"])}',year=2026,province='广西',track='物理类',major=major,score=value,scoreType=typ,scoreLabel='录取综合成绩线' if typ=='admission-composite' else '高考原始分入围线',maxScore=maximum,formula=formula,formulaStatus='verified',sourceIds=ids,officialUrl=sid[ids[0]]['url'],verifiedAt=DATE,auditStatus='reverified',note=note)
    if raw is not None:r['rawScoreText']=raw
    if code is not None:r['tieBreakCode']=code
    if typ=='entrance-gaokao':r['scoreSemantics']='高考总成绩原始分，不含政策加分；仅为校考入围门槛，不等于录取'
    else:r['scoreSemantics']='含学校考核的录取综合成绩，不是高考原始分'
    p['scoreRecords'].append(r);attach(k,*ids)
    finding('score-added',p['school'],f'{major}：{value}，{r["scoreLabel"]}。',ids,scoreId=r['id'])

add_score('tju','能源与动力工程',83.88,'admission-composite',100,'(高考成绩（不含加分）/高考满分×100)×85%+(面试成绩/面试满分×100)×15%',[scope_ids['tju'],brochure['tju']],'100分制综合成绩，不能与750分高考原始分比较。',raw='83.88')
add_score('hnu','化学',82.05,'admission-composite',100,'高考成绩（不含加分，折算100分）×85%+专业综合考核成绩（折算100分）×15%',[scope_ids['hnu'],brochure['hnu']],'成绩折算均四舍五入取2位小数；含校考，不能与高考原始分比较。',raw='82.05')
hust_formula='高考成绩（不含加分）/高考满分×100×85%+面试成绩（满分100）×15%'
for major,value,raw in [('化学',82.1933,'82.1933'),('生物科学',85.44,'85.4400'),('物理学（依托物理学院培养）',85.1733,'85.1733')]:
    add_score('hust',major,value,'admission-composite',100,hust_formula,[scope_ids['hust'],brochure['hust']],'100分制录取综合成绩；此录取表小数为真实综合成绩小数，与入围表排序码不同。',raw=raw)
for major,value,raw,code in [('化学',519,'519.097109105','097109105'),('生物科学',613,'613.120119128','120119128'),('物理学（依托物理学院培养）',611,'611.113111128','113111128')]:
    add_score('hust',major,value,'entrance-gaokao',750,'高考原始总成绩，不含政策加分；小数点后9位为语文、数学、外语三项排序码，不计入分数',[hust_entry,brochure['hust']],f'原表显示{raw}，小数点后依次是末位考生语文{int(code[:3])}、数学{int(code[3:6])}、外语{int(code[6:])}分。达到原始总分仍须核对同分排序、报名资格和确认要求；不等于录取。',raw=raw,code=code)
for major,value in [('应用物理学',601),('材料科学与工程',616)]:
    add_score('csu',major,value,'entrance-gaokao',750,'高考原始总分，不含政策加分',[csu_entry,brochure['csu']],'此表为一般入围资格线；另有高考数学145分或五大学科全国决赛二等奖及以上的直接入围规则，须按简章核对资格。',raw=str(value))

# Four explicit exclusions are supported by complete 2026 province lists.
province_lists={
 'muc':{'历史学':'北京 河北 江苏 河南 重庆 陕西','哲学':'北京 辽宁 浙江 山东 湖南 四川','中国少数民族语言文学（古文字学方向：突厥文）':'北京 山西 山东','中国少数民族语言文学（古文字学方向：古藏文）':'北京 天津 河北 河南'},
 'seu':{'哲学':'北京 江苏 安徽 山东','数学类、物理学类、化学':'北京 天津 山西 上海 江苏 浙江 安徽 山东 河南 广东 四川 陕西 湖北 湖南 重庆 江西 福建 贵州 甘肃 河北 辽宁 内蒙古 云南 青海 海南'},
 'uestc':{'全部强基专业':'北京 天津 河北 山西 江苏 浙江 安徽 山东 河南 湖北 湖南 广东 重庆 四川 陕西'},
 'nudt':{'全部强基专业':'北京 辽宁 江西 山东 河南 湖南 四川 贵州 陕西'},
}
for k,groups in province_lists.items():
    p=by[k];coverage={g:v.split() for g,v in groups.items()}
    p['provinceCoverage']=coverage
    p['guangxiEvidence']='已重读2026官方简章完整招生省份范围；'+('；'.join(g+'：'+v.replace(' ','、') for g,v in groups.items()))+'。上述范围均不含广西。'
    p['scopeAudit']=dict(status='reverified',evidenceType='complete-province-list',checkedAt=DATE,sourceIds=[brochure[k]],note='完整当年省份名单不含广西；不由未见广西分数反推排除。')
    finding('exclusion-reverified',p['school'],'2026完整省份名单不含广西，维持excluded。',[brochure[k]])

# Replace a previously incorrect description of BUAA's table: it is a subject table.
by['buaa']['guangxiEvidence']='2026官方简章将可报专业和计划交由报名系统；第二节表格为专业/选科要求，并非完整省份名单。广西实际投放仍未取得可读原始证据。'
finding('evidence-description-corrected','北京航空航天大学','原“招生省份表为图片”不准确：该表为专业选科表；改为报名系统投放待核。',[brochure['buaa']])

# National major lists are still explicitly national, not Guangxi-specific quotas.
major_updates={
 'ustc':['数学类','物理学类','化学','生物科学类','理论与应用力学','核工程类','地球物理学','量子信息科学','能源与动力工程'],
 'tju':['数学与应用数学','应用物理学','应用化学','生物科学','工程力学','合成生物学','能源与动力工程','船舶与海洋工程'],
 'csu':['数学与应用数学','应用物理学','应用化学','生物科学','材料科学与工程','信息与计算科学'],
 'hnu':['化学','应用化学','化学生物学'],
 'xmu':['数学类','物理学','化学类','生物科学类','海洋科学','药学','历史学','哲学'],
 'hust':['数学与应用数学','物理学','化学','生物科学','基础医学','汉语言文学（古文字学方向）','哲学'],
 'cqu':['数学与应用数学','物理学','储能科学与工程'],
 'uestc':['信息与计算科学','数理基础科学','应用物理学'],
}
for k,majors in major_updates.items():
    by[k]['majors']=majors;by[k]['majorsScope']='national-brochure';by[k]['majorsAudit']='2026全国简章完整专业名单；不代表广西全部投放'
    if k not in ['hust','xmu']:
        by[k]['subjectRequirements']='物理、化学均须选考';by[k]['tracks']=['物理类']
        by[k]['evidenceGaps']=[g for g in by[k]['evidenceGaps'] if g!='部分专业或选科要求待补核']
by['hust']['subjectRequirements']='数学与应用数学、物理学、化学、生物科学、基础医学须选物理+化学；汉语言文学（古文字学方向）、哲学在3+1+2省份为历史类。广西已证专业见分数记录。'
by['xmu']['subjectRequirements']='专业组1、2须物理+化学；专业组3为历史学、哲学，在3+1+2省份按历史类编制计划。'
for k in ['hust','xmu']:by[k]['evidenceGaps']=[g for g in by[k]['evidenceGaps'] if g!='部分专业或选科要求待补核']
by['xmu']['scoreRecords'][0]['major']='专业组2（化学类、生物科学类、海洋科学、药学）'
by['xmu']['scoreRecords'][0]['note']+='这是专业组共同线，不等于组内每个专业的录取最低分。'
for i,r in enumerate(by['cqu']['scoreRecords']):
    r['major']='专业组别1（数学与应用数学、物理学）' if i==0 else '专业组别2（储能科学与工程）'
    r['sourceIds'].append(brochure['cqu'])
for k in ['tju','hnu','hust','csu']:
    by[k]['guangxiMajors']=list(dict.fromkeys(r['major'] for r in by[k]['scoreRecords']))
    by[k]['guangxiMajorsEvidence']='仅列已取得2026广西分数原表的专业；不是完整计划表，不能据此排除其他专业。'

# Individual result/attachment access limitations, with exact official entrances.
buaa_notice=source('buaa-result','关于发布北京航空航天大学2026年强基计划预录取结果和预录取标准的通知','https://zs.buaa.edu.cn/info/1008/3597.htm','北京航空航天大学','2026-07-02','正文可读；所附标准PDF下载入口本轮返回验证码页面，未读取附件内容。')
attach('buaa',buaa_notice)
pku_query=source('pku-result-index','北京大学2026年强基计划结果查询官方栏目','https://bkzs.pku.edu.cn/zslb/qjjh/index.htm','北京大学',None,'栏目可读2026-06-26入围通知和2026-07-04录取通知；入围通知明确需身份证号及报名号登录个人平台。')
attach('pku',pku_query)
thu_query=source('thu-result','清华大学2026年强基计划录取结果查询通知','https://www.admissions.tsinghua.edu.cn/info/1033/2208.htm','清华大学','2026-07-04','公告要求登录本校强基报名平台查询，未附省级录取线。')
attach('thu',thu_query)
nankai_notice=source('nankai-entry','南开大学2026年强基计划入围结果查询及考核安排','https://zsb.nankai.edu.cn/2026-06-27/1815','南开大学','2026-06-27','官方检索显示2026通知及入围线图片；本轮直连HTTP403，未读取省份分数原图，不采用其未核实数值。')
attach('nankai',nankai_notice)
sjtu_index=source('sjtu-result-index','上海交通大学强基计划官方检索栏目（2026录取结果公告入口）','https://admissions.sjtu.edu.cn/search?searchKeyword=%E5%BC%BA%E5%9F%BA%E8%AE%A1%E5%88%92','上海交通大学',None,'官方栏目列2026-06-29录取结果公告；链接正文此轮仅返回页面框架，未取得广西原表。')
attach('sjtu',sjtu_index)

special_gaps={
 'pku':('individual-login','2026入围通知明确用身份证号和报名号登录个人平台，7月4日录取通知也只提供个人查询入口；本轮未取得广西统一分数/专业计划表。',[pku_query]),
 'thu':('individual-platform','7月4日公告要求登录报名平台查询个人录取结果；寄送公告可确认广西但不含分数或人数。',[thu_query,scope_ids['thu']]),
 'buaa':('captcha-protected-attachment','7月2日预录取标准PDF下载入口本轮显示“请输入验证码下载附件”，尚未读到广西行；没有绕过验证码。',[buaa_notice]),
 'nankai':('official-image-unretrieved','已定位6月27日官方入围公告；直连HTTP403，检索可见图片入口但未取得可读原图，广西范围和分数不作推定。',[nankai_notice]),
 'sjtu':('dynamic-page-unretrieved','官方栏目存在6月29日录取结果公告；本轮该正文响应仅页面框架，未读到广西表。',[sjtu_index]),
 'dlut':('dynamic-page-unretrieved','已检索2026官方强基栏目，官网首页此轮只返回动态页面标题；未取得2026广西原始分省表。',[brochure['dlut']]),
 'jlu':('province-image-unverified','2026简章的分省范围尚未取得可读完整原表；本轮原转载直连受限，官方搜索出现的2025材料未用于2026排除判断。',[brochure['jlu']]),
 'ruc':('primary-table-not-obtained','检索到第三方转载2026分省录取表的线索，但未取得可读高校原页，未采用第三方广西分数，也未据其改变范围。',[brochure['ruc']]),
 'xjtu':('platform-publication','2026简章规定录取标准在本校强基报名系统发布；本轮未取得广西公开分省表，不能由全国报名资格推定具体投放。',[brochure['xjtu']]),
 'whu':('province-plan-not-obtained','2026简章说明面向全国；本轮未取得广西分省投放表或广西成绩公告，保留具体投放unknown。',[brochure['whu']]),
 'scu':('province-plan-not-obtained','2026简章说明面向全国；本轮未取得广西分省投放表或广西成绩公告，保留具体投放unknown。',[brochure['scu']]),
 'neu':('province-plan-in-system','2026简章的招生范围以安排计划省份为前提，分省计划见报名系统；公开专业表只有自动化及选科，不能当完整省份排除表。',[brochure['neu']]),
 'ecnu':('province-plan-in-system','2026简章的专业组表未列完整省份；分省分专业计划在报名系统。未取得广西原表，不采第三方“不招广西”推断。',[brochure['ecnu']]),
 'zju':('province-plan-in-system','已重读2026全国专业分组及选科表；分省专业和计划以报名系统为准，未取得广西分组投放表。',[brochure['zju']]),
 'nju':('province-plan-not-obtained','已核对2026简章入口并检索官方录取信息，未取得可读广西分省原表；全国专业目录不能当作广西目录。',[brochure['nju']]),
}

# Reviewed access facts replace unpublished full-page scrape logs.
plan_access=json.loads((ROOT/'reviewed-plan-access.json').read_text())

for k,p in by.items():
    if 'scopeAudit' not in p:
        p['scopeAudit']=dict(status='prior-confirmation-retained' if p['guangxiStatus']=='confirmed' else 'unresolved',checkedAt=DATE,sourceIds=p['sourceIds'][:],note=p['guangxiEvidence'])
    if p['guangxiStatus']=='excluded':
        p['planStatus']='not-applicable-province'
        p['planGapReason']='2026官方完整招生范围不含广西；这里空值表示本省不适用，不是等待补录计划人数。'
        p['planScope']='广西；不在当年公开招生范围内，未以推算数字0代替范围说明'
        p['planEvidence']=dict(status=p['planStatus'],sourceIds=[brochure[k]],checkedAt=DATE,note=p['planGapReason'])
        p['evidenceGaps']=[g for g in p['evidenceGaps'] if g not in ['广西分专业计划人数未取得','广西投放范围待核验']]
    else:
        access=plan_access[p['id']]
        platform_urls=access.get('systemUrls',[])
        plan_system=access['status']=='registration-system-no-public-count'
        if plan_system:
            p['planStatus']='registration-system-no-public-count'
            reason='2026简章明确将分省专业或计划人数放在报名系统；本轮公开简章未提供广西数字表，未进入考生账户。'
        elif access['status']=='primary-page-access-limited':
            p['planStatus']='primary-page-access-limited'
            reason='本轮访问原简章转载链接返回HTTP412；已保留原核验记录并搜索官方入口，仍未取得可读广西人数表，不将访问失败解释为未招生或未公布。'
        else:
            p['planStatus']='province-count-table-not-obtained'
            reason='本轮已检查2026简章及所列招生范围/成绩公告；取得的材料未给出可读广西人数表，无法确认完整专业名额。'
        if k in ['ustc','buaa']:
            reason+='另实际访问该校报名平台公共入口，仅见报名界面框架，未显示省份计划数据；不能据此断言原报名期也不可查。'
        p['planGapReason']=reason
        p['planEvidence']=dict(status=p['planStatus'],sourceIds=[brochure[k]],checkedAt=DATE,note=reason,systemUrls=platform_urls)
        p['planScope']='广西分省分专业名额；当前未取得官方可读数字，null不代表0'
        p['evidenceGaps']=[g for g in p['evidenceGaps'] if g!='广西分专业计划人数未取得']
        p['evidenceGaps'].append('广西计划人数缺口：'+reason)
        if p['guangxiStatus']=='confirmed':p['evidenceGaps']=[g for g in p['evidenceGaps'] if g!='广西投放范围待核验']
    if k in special_gaps:
        status,note,ids=special_gaps[k]
        p['scoreGap']=dict(status=status,note=note,sourceIds=ids,checkedAt=DATE)
        p['evidenceGaps'].append('分省证据缺口：'+note)
        if p['guangxiStatus']=='unknown':
            p['scopeAudit']['note']=note
            p['scopeAudit']['sourceIds']=list(dict.fromkeys(p['scopeAudit']['sourceIds']+ids))
    elif not p['scoreRecords'] and p['guangxiStatus']!='excluded':
        p['scoreGap']=dict(status='province-score-table-not-obtained',note='已检查所列2026官方简章/广西范围证据，本轮未取得广西入围或录取原始数值表；不以其他省份或其他年份代替。',sourceIds=p['sourceIds'][:],checkedAt=DATE)
        p['evidenceGaps'].append('广西入围或录取数值原表尚未取得')
    p['verifiedAt']=DATE

for p in programs:
    if p['type']!='strong-foundation':
        p['planStatus']='special-national-route-no-province-count'
        p['planGapReason']='此项为独立少年/英才通道，保留原2026简章资格核验；本轮未新增广西分省名额证据，不能把全国项目规模填成广西计划。'
        p['planEvidence']=dict(status=p['planStatus'],sourceIds=p['sourceIds'],checkedAt=DATE,note=p['planGapReason'])

# Baseline scores are checked record by record. CQU source has currently regressed to an empty shell.
for k,p in by.items():
    for r in p['scoreRecords']:
        if 'auditStatus' not in r:r['auditStatus']='reverified'
        if r.get('formula'):r['formulaStatus']='verified'
        if k=='cau' and r['scoreType']=='admission-composite':r['sourceIds']=list(dict.fromkeys(r['sourceIds']+[brochure[k]]))
        if r['scoreType']=='entrance-weighted' and r['maxScore'] is None:
            r['maxScoreStatus']='not-stated-in-cutoff-notice'
            r['note']+='公告未直接给出本省加权满分，本次保留null；按已列公式理解，不作750分制比较。'
        if k=='cqu':
            r['auditStatus']='prior-value-current-source-unreadable'
            r['note']+='本轮原数值链接仅返回空正文框架，原已采数值保留但无法重新读表；请核对学校原表后使用。'
            p['evidenceGaps'].append('本轮重庆大学入围原数值链接返回空正文，611/630两值沿用前次核验，尚未完成本轮重读')
    p['evidenceGaps']=list(dict.fromkeys(p['evidenceGaps']))
sid['special-score-source-2026-cqu-entry']['verification']='前次已采广西组1=611、组2=630；本轮HTTP200但正文为空框架，无法重读原表。维持原值并显式标记复核缺口。'
for key,date in [('special-source-2026-neu','2026-04-08'),('special-source-2026-seu','2026-04-08')]:
    sid[key]['publishedAt']=date;sid[key]['verification']='本轮已重读2026学校官方简章和页面发布日期。'

policies.append(dict(id='special-policy-2026-score-audit',year=2026,title='强基分数须保留分制、录取阶段和同分排序码',summary='中科大、中南、湖南大学、天津大学、华中科技大学本次综合线为100分制；厦门大学为1000分制。华科入围表小数点后9位是语文、数学、外语排序码，原始总分和排序码须分别读取。强基综合线或加权入围线不能与普通批750分投档线混比。',sourceIds=[formula_image,brochure['xmu'],brochure['csu'],hust_entry,brochure['hust'],brochure['hnu'],brochure['tju']]))

score_audit=[]
for old in before:
    new=next(p for p in programs if p['id']==old['id'])
    for r in old.get('scoreRecords',[]):
        now=next(v for v in new['scoreRecords'] if v['id']==r['id'])
        score_audit.append(dict(id=r['id'],school=old['school'],oldScore=r['score'],newScore=now['score'],unchanged=r['score']==now['score'],status=now['auditStatus'],sourceIds=now['sourceIds'],formulaRepaired=r.get('formula') is None and now.get('formula') is not None))
unknown=[p['school'] for p in by.values() if p['guangxiStatus']=='unknown']
findings=dict(auditDate=DATE,scope='2026特殊通道，39强基高校及4独立通道',recordCount=len(programs),strongSchoolCount=len(by),beforeProvinceCounts=dict(Counter(p['guangxiStatus'] for p in before if p['type']=='strong-foundation')),afterProvinceCounts=dict(Counter(p['guangxiStatus'] for p in by.values())),originalScoreCount=len(score_audit),originalNumericChanges=sum(not x['unchanged'] for x in score_audit),originalScoresReverified=sum(x['status']=='reverified' for x in score_audit),originalScoresCurrentSourceUnreadable=sum(x['status']!='reverified' for x in score_audit),formulaRepairs=sum(x['formulaRepaired'] for x in score_audit),addedScoreCount=sum(len(p['scoreRecords']) for p in programs)-len(score_audit),totalScoreCount=sum(len(p['scoreRecords']) for p in programs),unknownStrongSchools=unknown,planCountsAdded=0,sourceCount=len(sources),findings=changes,originalScoreAudit=score_audit,unresolved=[dict(id=p['id'],school=p['school'],guangxiStatus=p['guangxiStatus'],planStatus=p['planStatus'],planGapReason=p['planGapReason'],scoreGap=p.get('scoreGap'),evidenceGaps=p['evidenceGaps']) for p in programs],publicationNote='只发布结构化事实、来源链接、研究说明和核验脚本；evidence原网页文本/图片只作本地审计资料，不上传。')

allids=set(sid)
assert len(programs)==43 and len(by)==39
assert len({p['id'] for p in programs})==43
assert all(p['year']==2026 for p in programs)
for p in programs:
    assert all(x in allids for x in p['sourceIds']),(p['id'],'program source')
    if p['guangxiStatus']=='excluded':assert not p['scoreRecords']
    for r in p['scoreRecords']:
        assert all(x in allids for x in r['sourceIds']),(r['id'],'score source')
        assert r['year']==2026 and r['province']=='广西' and r.get('formula')
        if r['scoreType']=='admission-composite':assert r['maxScore'] in [100,750,1000]
        if 'tieBreakCode' in r:assert r['score']==int(r['rawScoreText'].split('.')[0]) and len(r['tieBreakCode'])==9
assert all(x in allids for p in policies for x in p['sourceIds'])
assert findings['formulaRepairs']==6 and findings['addedScoreCount']==10
assert findings['originalNumericChanges']==0
for name,value in [('corrected-special-programs.json',programs),('sources.json',sources),('policies.json',policies),('findings.json',findings)]:
    (ROOT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in findings.items() if k not in ['findings','originalScoreAudit','unresolved']},ensure_ascii=False,indent=2))
