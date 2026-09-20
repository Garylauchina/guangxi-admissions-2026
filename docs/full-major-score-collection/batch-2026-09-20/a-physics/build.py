#!/usr/bin/env python3
"""Build a bounded 30-school 2026 Guangxi evidence batch from local raw files.

No network requests and no live-site writes. Raw bodies stay local.
"""
import collections, datetime, hashlib, html, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RAW = ROOT / 'raw'
PREFIX = 'major-20260920-a-'
DATE = '2026-09-20'
targets = json.loads((ROOT / 'targets.json').read_text())
names = {r['schoolCode']: r['school'] for r in targets}

NOTES = {
 '10616': ('access-blocked', '实际访问学校招生就业处，确认本科招生链接为zs.cdut.edu.cn；正确入口普通浏览器显示ERR_CONNECTION_CLOSED，脚本亦连接失败。没有取得分专业查询菜单或2026结果；初始旧域名失败不作为未发布证据。'),
 '10145': ('entry-only-year-gap', '实际读取招生官网历年分数省份目录及其广西图片；图片标题和逐列年份均为2023—2025，未取得2026专业分。只核查该省份目录与附件，未声称全校所有渠道均无发布。'),
 '19141': ('query-unresolved', '实际读取大连理工录取分数前端脚本及浏览器页面；点击盘锦校区、广西后，年份/科类/类型仍无选项，概况和分专业表均显示暂无数据。公开年份接口返回code=200、data=[]，但未能完成明确年份的完整查询，故不能记为2026有效空表。没有用主校区分数替代独立代码19141。'),
 '10621': ('entry-only-year-gap', '从当前本科招生官网转入官方zssj历史录取数据查询；该页所示历史年份为2024，首页另列2025分省录取表、2025四川分专业统计，未取得2026广西专业结果。查询响应字符编码未正确呈现全部中文，不能将乱码行推断成当前专业分。'),
 '10657': ('entry-only-year-gap', '实际读取分省分批次分专业最低分页面及其内嵌history-score-list数据。虽然页面URL/发布日期为2026，标题和内嵌统计年份为2025，未导入旧年分数。'),
 '10425': ('collected-partial', '实际读取官方ajax_lnfs菜单并枚举广西2026物理普通生、民族班、国家专项、高校专项及历史普通生5个组合，取得41条实际具体专业最低分。逐行限定nf=2026和ssmc=广西；源字段rs分专业合计与对应学校类别汇总核对，但其公开表头没有录取人数标签，不解读为实际录取人数。组码、广西填报专业代号及首次/征集轮次均未列，保持未知。'),
 '10058': ('entry-only-year-gap', '实际读取历年录取分数目录及广西2025详情；当前目录最新统计年2025，未取得2026广西分专业表。2025公告的晚发布日期不改变统计年份。'),
 '10560': ('entry-only-year-gap', '实际读取本科招生官网分专业录取查询页，公开年份菜单为2025、2024、2023。没有2026选项；初始无省份/零行不作为2026有效空结果。'),
 '10256': ('entry-only-year-gap', '实际读取官方各省专业录取查询页及其前端，按真实JSONP回调请求nf-list.jsp，返回success=1，DTList为2025、2024、2023。先前不带回调请求返回无效请求已单独记录，不把业务失败当作空数据。'),
 '10028': ('entry-only-year-gap', '实际读取本科招生录取分数目录及2025京外分数详情，当前栏目最高统计年2025。未取得2026广西具体专业最低分。'),
 '10140': ('entry-only-year-gap', '沿辽宁大学官网确认现用zs.lnu.edu.cn，读取历年录取情况第1页40条：最新各省2025统计，含广西2025，后续已进入2024。2026年1月发布的2025录取情况仍归2025。'),
 '10274': ('entry-only-year-gap', '实际读取上海海关学院招生主页、2025本科招生日统计表及2026章程。当前主页所链接分数统计为2025日统计，2026录取通知书消息及章程不构成专业录取最低分；本轮未取得2026广西分专业统计，未宣称全站均未发布。'),
 '10617': ('entry-only-year-gap', '脚本请求招生域名被412拦截后，以普通浏览器进入真实wxfsx.aspx分数查询页；年份菜单明确为2025至2013，省份含广西，没有2026选项。未绕过验证码或安全警告。2026分批次公告入口另留作后续组线核查，不当作具体专业分。'),
 '19359': ('entry-only-year-gap', '实际读取合工大官方查询前端和有效ajax菜单，广西有宣城校区物理普通批/国家专项、历史普通批，但年份最高2025。以明确宣城校区限定代码19359，没有用合肥校区或旧年数据填补。'),
 '10632': ('entry-only-year-gap', '沿学校主页确认zsxxw本科入口并读取历年分数目录；最新为2025本科分省专业表，其后为2024及更早年份，未取得2026广西专业统计。'),
 '10749': ('collected-partial', '经招生官网真实分数链接的HTTPS最终地址，读取有效匿名ajax菜单并查询广西2026普通类物理、历史两个组合，取得12条实际专业最低分。逐行年份与省份核验，原始rs合计核对，但不把rs解释为录取人数；另读2026章程PDF确认普通类含政策加分口径。艺体历年公告不混入普通类。'),
 '10023': ('entry-only', '实际打开现用gkxc.pumc.edu.cn本科招生网，并展开招生信息—信息公开：第1页30条（全栏目56条）最新有2026章程、毕业典礼，招生计划及往年情况相关文章为2025。该已读目录未取得2026广西具体专业最低分；第二页更早公告及公众号全文未穷尽。'),
 '10110': ('entry-only-year-gap', '沿学校主页进入zbzs本科招生网并实际读取历年录取目录第1页20条，最新为2025分省分专业统计和2025各省各科类线；后续为2024及更早。未以2026录取结束消息推断分数。'),
 '10615': ('entry-only-year-gap', '沿学校考生栏目/招生就业处确认正确本科入口zsb.swpu.edu.cn/swpu，普通浏览器成功进入并点击普通类本科专业录取分数，读取专用前端majorEnrollFormForIUKGEQ.js及广西有效getMajorSelectChange菜单；年份列表最高2025。初始入口传输失败已被正确入口核查替代，不声称2026有效空表。'),
 '10151': ('entry-only-year-gap', '实际读取海事大学官方sjcx分数前端及有效匿名ajax菜单；广西最新2025，含物理提前批、普通批、国家专项、高校专项和历史普通批。2026未出现在该真实菜单。'),
 '10300': ('entry-only-year-gap', '实际读取往年分数表单，年选项最高2025；另读取2026全国分省分类型公告，广西本科/定向/国家专项有分数，但最低字段标题为投档分且未到具体专业，不作为专业实际最低分或组录取线。'),
 '11415': ('collected-partial', '实际读取官方ajax_lnfs菜单，枚举广西2026普通考生物理物化1/2/3/4、物理1及历史不限6个组合，取得28条具体专业实际最低分；逐行核验年份、省份和类别，原始rs合计核对但不解释为录取人数。2026菜单中的艺术科类排除，2025专项未改年；组名称不是广西组码。章程专业排序口径为实考总分不含政策加分。'),
 '10259': ('entry-only-year-gap', '实际读取官方enroll历年查询前端，并按其POST与X-Requested-With调用GetDropScoreLineYear，返回年份2025至2018；2026未在菜单。早先无XHR请求返回网页而非JSON已记录为解析/业务失败。另查2026进程表，仅省份/选科合并层级，未把其分数拆到专业或未知组码。'),
 '10337': ('entry-only-year-gap', '实际读取官方历年录取查询页，省份含广西，年份菜单为2025、2024、2023、2022、2021，类别含普通类、国家专项等，未提供2026选项。'),
 '11232': ('entry-only-year-gap', '沿学校本科招生页确认现用zhaosheng官网及zhaoshengcx查询，真实ajax菜单广西最高2025（物理普通类、中外合作），2026不存在。没有以北京分数公众号标题替代广西数据。'),
 '10252': ('empty-current-response', '实际读取上理工官方查询页，年份包含2026，但按前端调用2026省份菜单返回[]，2026广西科类菜单亦[]；同接口2025阳性对照返回含广西的31省份及理工/物理、文史/历史两科类。该结论仅为2026有效空菜单，不等同已完成当前分数查询或全校未招生。'),
 '11413': ('entry-only-year-gap', '沿矿大北京学校主页确认zb.cumtb.edu.cn并读取真实分数入口；HTTP匿名POST403后改用入口已重定向的HTTPS，菜单有效，广西最新2025（普通/国家/高校专项及历史普通）。未取得2026选项，传输失败和有效旧年菜单分开记录。'),
 '10655': ('collected-partial', '实际读取2026普通本科批、艺术本科批、艺术提前批三则官方公告；只采普通本科批公告广西6个专业录取线，并逐格视觉核验文/理列，已独立复核。章程普通类含政策加分，工业设计要求物理化学；两艺术批不混入750分普通类。原表文/理在广西分别归历史/物理，组码/轮次/位次未知。'),
 '10338': ('entry-only-year-gap', '实际读取官方历年录取目录及其最新2024—2025录取分数情况详情；未取得2026广西具体专业表，旧年不改年导入。'),
 '10697': ('entry-only-year-gap', '实际读取官网链接的智能答疑专业录取信息表单，并请求广西getMajorSelectChange，yearList为2025至2016，无2026。不是仅凭旧发布文章日期判断。'),
}

def write(name, data):
    (ROOT / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')

def source_id(s): return PREFIX + s

browser_notes = [
 ('19141-browser', '19141', 'https://zs.dlut.edu.cn/admissionScore', '普通浏览器实际点击盘锦校区、广西后：年份/科类/类型未呈现选项；录取概况、录取分专业情况均为暂无数据。校区和年份未形成完整查询。'),
 ('10617-browser', '10617', 'https://zs.cqupt.edu.cn/wxfsx.aspx', '普通浏览器读取select#ddlyear选项为2025,2024,2023,2022,2021,2020,2019,2018,2017,2016,2015,2014,2013；select#ddlsq包含广西。'),
 ('10023-browser', '10023', 'https://gkxc.pumc.edu.cn/pumc/pumcInfo', '信息公开第1页30条，全栏目56条、2页；最新2026-07-04毕业典礼、2026-06-02招生章程，后续招生计划及往年招生情况为2025；该页未列2026专业录取结果。'),
 ('10615-browser', '10615', 'https://zsb.swpu.edu.cn/page/detail/IUKGEQ/237/11586/32287/11', '由本科官网真实点击历年分数查询打开，栏目为普通类本科专业录取分数，DOM脚本指向admin.zhinengdayi.com/static/scripts/front/page/majorEnrollFormForIUKGEQ.js。'),
]
for key, code, url, text in browser_notes:
    path = RAW / (key + '.txt')
    if not path.exists(): path.write_text(text + '\n')
    metapath = RAW / (key + '.meta.json')
    if not metapath.exists():
        metapath.write_text(json.dumps(dict(id=key, schoolCode=code, url=url, checkedAt='2026-09-20', status=None, evidenceType='manual-browser-observation', archiveFile=path.name, archiveSha256=hashlib.sha256(path.read_bytes()).hexdigest()), ensure_ascii=False, indent=2)+'\n')

sources = []
metas = []
for path in sorted(RAW.glob('*.meta.json')):
    m = json.loads(path.read_text())
    code = m.get('schoolCode', m['id'][:5])
    if code not in names: continue
    metas.append(m)
    is_api = 'accessedAt' in m
    request = m.get('request') if is_api else m.get('data')
    method = m.get('method', 'POST' if 'path' in m else 'GET') if is_api else ('POST' if 'data' in m else 'GET')
    source = dict(id=source_id(m['id']), title=f"{names[code]}：公开招生资料核查（{m['id'][6:]}）", url=m['url'], publisher=names[code], year=2026 if 'gx2026' in m['id'] else None, publishedAt=None, accessedAt=m.get('accessedAt', m.get('checkedAt')), sha256=m.get('sha256',m.get('archiveSha256')), responseSha256=m.get('responseSha256',m.get('rawSha256')), requestMethod=method, requestData=request, httpStatus=m.get('httpStatus', m.get('status')), evidenceType=m.get('evidenceType','public-response'), evidenceRole='major-score' if 'gx2026' in m['id'] else 'source-review', archiveFile=m.get('archiveFile',m.get('rawFile','').removeprefix('raw/')) or None)
    error = m.get('accessError',m.get('error'))
    if error: source['accessError'] = error
    if m.get('entryUrl'): source['entryUrl'] = m['entryUrl']
    if m.get('csrf'): source['usesAnonymousCsrf'] = True
    if m['id'] == '10259-years': source['notes'] = ['此早期调用使用基础collector，实际为GET；虽清单标注POST，但未提供data，返回HTML。后续years-post-body按真实POST/XHR取得年份。']
    sources.append(source)
source_map = {s['id']:s for s in sources}

rows, evidence = [], []
basis_sources = {'10425':'10425-charter-body','10749':'10749-charter-pdf','11415':'11415-charter','10655':'10655-charter'}
bases = {
 '10425': '750分制普通高考总分（2026章程按投档成绩安排专业，含认可政策加分）',
 '10749': '750分制普通高考总分（2026章程普通类专业排序含政策性加分）',
 '11415': '750分制普通高考实考总分（2026章程专业排序不含政策性加分）',
 '10655': '750分制普通高考文化总分（2026章程普通类含政策性加分）',
}

def make_row(code, track, major, score, sid, source_row, batch='本科普通批', category='普通类'):
    code_source = 'gxeea-2026-33107' if track == '物理' else 'gxeea-2026-33106'
    basis = source_id(basis_sources[code])
    ref = [sid, basis, code_source]
    r = dict(id=f'{PREFIX}{code}-{sum(x["schoolCode"]==code for x in rows)+1:03d}', year=2026, province='广西', schoolCode=code, school=names[code], sourceSchool=names[code], track=track, sourceTrack=track+'类', batch=batch, round='录取汇总（轮次未分）', group=None, major=major, majorCode=None, score=score, scoreType='专业录取最低分', rank=None, sourceId=sid, sourceIds=ref, sourceRow=source_row, sourceTable='sszygradeList', reviewedAt=DATE, evidenceStatus='verified', scoreComparable=True, scoreBasis=bases[code], scoreScaleMaximum=750, scoreEvidenceGaps=[], conflictFields=[], admissionType=category, sourceCategory=category, requiredSubjects=[], subjectRule='unknown', requirementText=f'首选{track}；原分数表未列完整再选科目要求', fieldSourceIds={k:[sid] for k in ['year','province','track','major','score','batch','admissionType']}, sourceScoreHeader='最低分', note='学校直接公布的具体专业实际录取最低分；广西3位组码、广西填报专业代号及首次/征集轮次未列，保持未知。全国专业代码不当作广西填报专业代号。')
    r['fieldSourceIds'].update(schoolCode=[code_source],scoreBasis=[basis],note=ref)
    return r

for code in ['10425','10749','11415']:
    for path in sorted(RAW.glob(code+'-gx2026-*.json')):
        if '.meta.' in path.name: continue
        body = json.loads(path.read_text())
        assert body['state'] == 1
        ss = body['data']['sszygradeList']
        for index, item in enumerate(ss,1):
            if item.get('nf') != '2026' or item.get('ssmc') != '广西': continue
            assert item['klmc'] in ['物理类','历史类']
            sid = source_id(path.stem)
            r = make_row(code, item['klmc'].removesuffix('类'), item['zymc'], item['minScore'], sid, index, item['pcmc'], item['zslx'])
            r.update(sourceMajorCode=item.get('zydm'), sourceGroupName=item.get('zyzname') or None, sourceMaximumScore=item['maxScore'], sourceAverageScore=item['avgScore'], sourceReportedCount=item['rs'], rank=item['minOrder'], rankType='最低分位次（学校公布）')
            for key in ['sourceMaximumScore','sourceAverageScore','sourceReportedCount','rank']:r['fieldSourceIds'][key]=[sid]
            mapping_sid = source_id(code+'-params-final') if code=='10749' else source_id(code+'-query')
            r['sourceIds'].append(mapping_sid)
            for field in ['score','sourceMaximumScore','sourceAverageScore','rank']:r['fieldSourceIds'][field].append(mapping_sid)
            r['note'] += ' 接口rs只保留为sourceReportedCount；公开前端未显示录取人数列，不解释为已录取人数。'
            if r['sourceGroupName']:r['note'] += ' 原始组选项名称仅保留为文字，不能替代广西组码。'
            if code == '11415':r['note'] += ' 本校专业排序使用实考总分，不含政策性加分。'
            conflict = item['minScore'] > item['maxScore'] or not item['minScore'] <= item['avgScore'] <= item['maxScore']
            if conflict:r.update(scoreComparable=False,evidenceStatus='source-conflict',scoreEvidenceGaps=['源表最低/平均/最高分存在冲突'],conflictFields=['scoreRange']);r['note']+=' 源表分数内部存在冲突，保留但不参加筛选比较。'
            rows.append(r)
            evidence.append(dict(rowId=r['id'],sourceFile='raw/'+path.name,sourceSha256=source_map[sid]['sha256'],sourceTable='data.sszygradeList',sourceRow=index,fieldMap={'year':'nf','province':'ssmc','track':'klmc','major':'zymc','score':'minScore','rank':'minOrder','sourceReportedCount':'rs','admissionType':'zslx','batch':'pcmc','sourceMaximumScore':'maxScore','sourceAverageScore':'avgScore','sourceMajorCode':'zydm','sourceGroupName':'zyzname'},sourceFields=item))

for major, track, score, source_track in [('艺术教育','物理',516,'理'),('工业设计','物理',586,'理'),('建筑学','历史',527,'文'),('风景园林','历史',522,'文'),('艺术设计学','历史',526,'文'),('艺术史论','历史',511,'文')]:
    sid=source_id('10655-current1')
    r=make_row('10655',track,major,score,sid,'广西行/'+major+'/'+source_track,'普通本科批','普通类')
    r.update(sourceTrack=source_track,sourceTable='普通本科批各专业录取分数线图片',sourceScoreHeader='各专业录取分数线',note='普通本科批实际专业录取线，原图广西行文/理分别对应历史/物理；不是艺术类统考或校考分数。组码、广西填报专业代号、位次及轮次未列，保持未知。')
    image_sid=source_id('10655-ordinary-image2');r['sourceIds'].append(image_sid)
    for key in ['province','track','major','score']:r['fieldSourceIds'][key]=[sid,image_sid]
    r['fieldSourceIds']['note']=r['sourceIds']
    if major=='工业设计':r.update(requiredSubjects=['化学'],subjectRule='all',requirementText='首选物理，再选化学；依据2026招生章程第二十一条');r['fieldSourceIds']['requiredSubjects']=[source_id('10655-charter')]
    rows.append(r)
    evidence.append(dict(rowId=r['id'],sourceFile='raw/10655-ordinary-image2.png',sourceSha256=source_map[image_sid]['sha256'],sourceTable='普通本科批各专业录取分数线',sourceRow=r['sourceRow'],sourceFields={'province':'广西','major':major,'trackHeader':source_track,'score':score},visualVerified=True,independentVisualReview=True))

audit, observations = [], []
for target in targets:
    code=target['schoolCode'];status,note=NOTES[code]
    code_sources=[s for s in sources if s['id'].startswith(PREFIX+code+'-')]
    count=sum(r['schoolCode']==code for r in rows)
    audit.append(dict(id=PREFIX+'review-'+code,year=2026,province='广西',schoolCode=code,school=names[code],auditKind='major-scores',checkedAt=DATE,title='2026广西专业录取分来源核查',status=status,recordCount=count,sourceIds=[s['id'] for s in code_sources],checkedUrls=list(dict.fromkeys(s['url'] for s in code_sources)),note=note,scope='仅列明官方入口、附件及真实查询组合；未取得不等于未招生或所有渠道未发布。'))
    times=sorted(s['accessedAt'] for s in code_sources if s.get('accessedAt') and 'T' in s['accessedAt'])
    span=round((datetime.datetime.fromisoformat(times[-1])-datetime.datetime.fromisoformat(times[0])).total_seconds(),2) if times else None
    observations.append(dict(schoolCode=code,school=names[code],status=status,recordCount=count,observation=note,requestCount=len(code_sources),firstRecordedRequestAt=times[0] if times else None,lastRecordedRequestAt=times[-1] if times else None,observedRequestSpanSeconds=span,timingCaveat='首末请求跨度含并行与中断等待，不等同主动采集耗时；旧请求未逐次计时，不能据此直接外推总工时。',requests=[{k:s[k] for k in ['id','url','requestMethod','requestData','httpStatus','accessedAt','sha256','responseSha256','archiveFile','evidenceType']} for s in code_sources]))

counts=collections.Counter(r['schoolCode'] for r in rows)
assert len(targets)==len(audit)==len(observations)==30
assert len(rows)==87 and dict(counts)=={'10425':41,'10749':12,'11415':28,'10655':6}
assert len({r['id'] for r in rows})==len(rows)
write('major-cutoffs-upsert.json',rows)
write('sources.json',sources)
write('school-audit-notes.json',audit)
write('observations.json',observations)
write('row-evidence.json',evidence)
write('group-admission-candidates.json',[])

checks=[]
for code in ['10425','10749','11415']:
    for path in sorted(RAW.glob(code+'-gx2026-*.json')):
        if '.meta.' in path.name:continue
        data=json.loads(path.read_text())['data'];ss=data['sszygradeList'];selected=[r for r in ss if r.get('nf')=='2026' and r.get('ssmc')=='广西']
        sums=data['sszyzgradeList'] if code=='11415' else data['zsSsgradeList']
        assert len(sums)==1
        checks.append(dict(schoolCode=code,response=path.stem,majorRows=len(selected),sourceRsSum=sum(r['rs'] for r in selected),summarySourceRs=sums[0]['rs'],sourceRsMatches=sum(r['rs'] for r in selected)==sums[0]['rs']))
assert all(c['sourceRsMatches'] for c in checks)
write('QA.json',dict(year=2026,province='广西',schoolAuditCount=30,majorRowCount=len(rows),schoolCounts=dict(counts),trackCounts=dict(collections.Counter(r['track'] for r in rows)),nonComparableCount=sum(not r['scoreComparable'] for r in rows),allRowsHaveUnknownGuangxiGroupCode=all(r['group'] is None for r in rows),groupAdmissionCandidateCount=0,groupAdmissionGap='地大北京sszyzgradeList有2026实际组汇总，但只有组选项名，没有广西3位组码；其他已采表亦不能建立完整直接组证据。不从专业子集求最小值。',apiChecks=checks,scope='30个固定目标；4校可采正向结果，26校保留有界缺口；不是全站覆盖完成声明。'))
print(json.dumps({'majorRows':len(rows),'schools':dict(counts),'auditSchools':len(audit),'sources':len(sources)},ensure_ascii=False))
