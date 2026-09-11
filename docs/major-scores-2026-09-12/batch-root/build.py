"""Verify the bounded official-source review; no historical score is imported."""
from pathlib import Path
import json, hashlib, re
import pdfplumber
ROOT=Path(__file__).resolve().parent
RAW=ROOT/'raw'
DATE='2026-09-12'
checks=[]
def load(name):return json.loads((RAW/name).read_text())
def check(label,condition):
    assert condition,label
    checks.append({'check':label,'passed':True})
def save(name,obj):(ROOT/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
def text(name):return (RAW/name).read_text()

check('FYUST current plan and Guangxi visible','2026年本科招生计划' in text('fyust-plan.html') and '广西' in text('fyust-plan.html'))
check('FYUST examined pages do not contain cutoff table headings',all('录取分数' not in text(n) and '最低分' not in text(n) for n in ['fyust-home.html','fyust-news.html','fyust-plan.html']))
check('GBU charter current 2026 with Guangxi','2026年' in text('gbu-charter.html') and '广西' in text('gbu-charter.html'))
check('GBU undergraduate page does not supply professional score headings','录取分数' not in text('gbu-home.html'))
check('BUCM school fixed ID and type mapping shown by public page',"name: '历史类'" in text('bucm-query-https.html') and "name: '物理类'" in text('bucm-query-https.html'))
check('BUCM year menu 2025-2022',load('bucm-years.json')['success'] and load('bucm-years.json')['list']==[2025,2024,2023,2022])
check('BUCM Guangxi province code450000',{r['code'] for r in load('bucm-provinces-2025.json')['list'] if r['name']=='广西'}=={450000})
for name in ['bucm-provinces-2026.json','bucm-types-code-2026.json']:
    d=load(name);check(name+' successful empty config',d['success'] and d['list']==[])
for kind,count in [(11,4),(12,22)]:
    d=load(f'bucm-gx-2025-{kind}.json')
    check(f'BUCM 2025 type{kind} positive',d['success'] and len(d['list'])==count and d['startYear']==2025 and d['endYear']==2025 and d['planYear']==2026)
d=load('bucm-gx-2026-11.json')
check('BUCM 2026 history is unsuccessful business response not successful empty',d['success'] is False and d['list'] is None and d['startYear']==0)
for name in ['bucm-gx-2026-12.json','bucm-gx-2026-12-retry.json','bucm-gx-2026-12-http.json']:
    m=load(name+'.meta.json');check(name+' transport failure preserved',bool(m.get('error')) and not m.get('httpStatus'))
check('TMU current article actually 2023-2025','天津医科大学2023-2025年各省市各专业录取分数' in text('tmu-latest.html'))
with pdfplumber.open(RAW/'tmu-old-scores.pdf') as pdf:
    gx=pdf.pages[6].extract_text()
    check('TMU PDF page7 title 2023-2025 Guangxi','天津医科大学2023—2025年广西壮族自治区录取分数统计' in gx)
    check('TMU PDF page7 explicit 2025/2024/2023 columns',all(str(y)+'年' in gx for y in [2025,2024,2023]) and '2026年' not in gx)
    check('TMU PDF caveats retained','含征集' in gx and '位次数据来源于互联网' in gx)
check('SWJTU actual frontend Guangxi filename mapping','ANXIZHUANGZUZIZHIOU' in text('swjtu-query.js'))
check('SWJTU menu latest2025',"selected='selected'>2025" in text('swjtu-query.html') and '>2026</option>' not in text('swjtu-query.html'))
check('SWJTU 2026 expected file404',load('swjtu-gx-2026.html.meta.json')['httpStatus']==404)
check('SWJTU 2025 Guangxi file is positive',load('swjtu-gx-2025.html.meta.json')['httpStatus']==200 and '广西壮族自治区' in text('swjtu-gx-2025.html') and len(re.findall('<tr>',text('swjtu-gx-2025.html')))>20)
xd=load('xidian-types.json')['typeMap']
check('Xidian Guangxi menu latest2025',set(k.split('_')[1] for k in xd if k.startswith('广西_'))=={'2025','2024','2023','2022'})
for kind in ['物理类','历史类','全部']:
    d=load(f'xidian-gx-2026-{kind}.json');check('Xidian current '+kind+' empty',d['code']==200 and d['success'] and d['list']==[])
check('Xidian 2025 physical allcategories positive17',len(load('xidian-gx-2025-物理类.json')['list'])==17)

definitions={
 'fyust':('14896','福建福耀科技大学','not-found-current-major','读取本科招生首页、招生政策栏目及2026本科计划正文，明确广西9人、按智能制造工程招生，但所读页面没有2026广西专业实际录取最低分。计划数和入学后可选专业不作为录取分；本轮未覆盖全部官方公众号历史文章，不据此认定学校全渠道未发布。'),
 'gbu':('14942','大湾区大学','not-found-current-major','本科招生页和2026章程明确面向广西，以计算机科学与技术统一招生、后续可选专业；所读页面没有2026广西专业实际最低分。未把其他培养方向分别赋予院校专业组分数，未访问考生个人录取查询，也不宣称遍查了全部官方渠道。'),
 'bucm':('10026','北京中医药大学','entry-only-year-gap','现官网链接的公开分数系统菜单最高2025；2026省份和广西科类配置成功返回空列表。按真实省码450000及历史11/物理12查询：历史返回success=false且list=null，物理HTTPS两次及官网原HTTP路径均连接关闭/协议失败，不能说两科专业查询成功为空。2025同接口历史4、物理22条正向对照；响应中的planYear=2026只是计划年份，成绩字段仍为2025。旧静态栏目为2022—2024。'),
 'tmu':('10062','天津医科大学','entry-only-year-gap','录取分数栏目最新文章发布于2026-05-27，标题及PDF实际为2023—2025。已渲染目视核对附件第7页（印刷页6）的广西表，年份列为2025、2024、2023，没有2026。原脚注明普通批含征集，位次来自互联网仅供参考；不把发布时间或旧位次改作2026专业证据。'),
 'swjtu':('10613','西南交通大学','entry-only-year-gap','官网导航的历史录取查询菜单只有2025、2024、2023、2022；按真实脚本省份映射构造的2026广西公开文件返回404，2025同格式广西文件可读取具体专业记录。没有把默认安徽表或旧年广西分数转成年份2026；404不等于录取0人，也不证明其他渠道没有公布。'),
 'xidian':('10701','西安电子科技大学','empty-current-response','通过主站招生菜单和本科招生页找到当前公开分数前端。广西菜单最高2025；限定长安校区、全部招生类别，2026物理类、历史类、全部科类三次均code200/success=true且list空，2025物理同接口取得17条正向对照。本轮没有将旧年分数、计划年份或汇总投档线改成2026专业最低分。')
}
labels={'home':'招生官网','news':'招生政策栏目','plan':'2026招生计划','charter':'2026招生章程','scores':'历年分数栏目','query':'当前公开分数查询页','query-https':'公开分数查询页（HTTPS）','old-gx':'广西2022至2024分数页','latest':'最新分数公告（2023至2025）','old-scores':'2023至2025分数附件','admissions-menu':'主站招生导航','zs':'本科招生官网','current-summary':'2026计划与近三年分数栏目','app':'公开查询配置脚本','score':'公开查询字段脚本','types':'年份与类别配置','years':'年份菜单'}
def label(filename,prefix):
    key=filename[len(prefix)+1:].rsplit('.',1)[0]
    if key in labels:return labels[key]
    return key.replace('gx-','广西 ').replace('types-code-','广西科类配置 ').replace('types-','初始科类查询（后已更正省码） ').replace('provinces-','省份配置 ').replace('-11',' 历史类').replace('-12',' 物理类').replace('-retry','（HTTPS重试）').replace('-http','（官网HTTP路径重试）')
sources=[];notes=[]
for prefix,(code,school,status,note) in definitions.items():
    metas=sorted(RAW.glob(prefix+'-*.meta.json'))
    ids=[];urls=[]
    for path in metas:
        m=json.loads(path.read_text());filename=m['name'];sid='major-20260912-root-'+filename.replace('.','-');ids.append(sid);urls.append(m['url'])
        if m.get('sha256'):check(filename+' archive hash',hashlib.sha256((RAW/filename).read_bytes()).hexdigest()==m['sha256'])
        source={'id':sid,'title':school+'：'+label(filename,prefix),'url':m['url'],'publisher':school,'publishedAt':None,'accessedAt':m['checkedAt'],'sha256':m.get('sha256'),'responseSha256':m.get('responseSha256'),'requestMethod':m['requestMethod'],'requestData':m.get('data'),'requestEncoding':m.get('encoding','form'),'httpStatus':m.get('httpStatus'),'evidenceRole':'source-review-not-admission-records','method':'按当前官网导航及前端真实公开参数读取；保存本轮状态、归档摘要及明示范围内的正向对照。','notes':[note]}
        if m.get('error'):source['accessError']=m['error']
        if m.get('archiveMethod'):source['archiveMethod']=m['archiveMethod']
        sources.append(source)
    notes.append({'id':'review-major-20260912-root-'+code,'year':2026,'province':'广西','schoolCode':code,'school':school,'auditKind':'major-scores','checkedAt':DATE,'title':'2026广西专业录取分来源复查','status':status,'recordCount':0,'sourceIds':ids,'checkedUrls':list(dict.fromkeys(urls)),'note':note,'scope':'仅针对本轮列明的公开入口、栏目和实际参数；未取得不表示未招生或全部渠道没有公布。'})
check('six distinct reviewed identities',len(notes)==6 and len({n['schoolCode'] for n in notes})==6)
save('major-cutoffs-upsert.json',[]);save('sources.json',sources);save('school-audit-notes.json',notes)
save('QA.json',{'status':'passed','checkedAt':DATE,'reviewedSchools':6,'newScoreRecords':0,'sourceRecords':len(sources),'checks':checks,'manualReview':{'file':'tmu-old-scores.pdf','physicalPage':7,'printedPage':6,'sha256':hashlib.sha256((RAW/'tmu-old-scores.pdf').read_bytes()).hexdigest(),'review':'Rendered page visually confirms Guangxi and 2023-2025 headings, ordinary batch including supplementary rounds, Internet-sourced rank caveat.'},'limits':['BUCM 2026 history business failure and physics transport failure are not successful empty professional queries','Only Xidian has successful current professional empty responses; others retain each response meaning','Full original PDFs, pages, screenshots and sessions are not published']})
print('PASS',len(checks),'checks, sources',len(sources))
