"""Offline normalization of public 2026 Guangxi initial plans; no shared-file writes."""
from pathlib import Path
import json,re,hashlib,datetime
from parse_tables import NestedTables
ROOT=Path(__file__).resolve().parent
RAW=ROOT/'raw'
OUT=ROOT/'plan-package';OUT.mkdir(exist_ok=True)
TARGETS={r['schoolCode']:r for r in json.loads((ROOT/'targets-public.json').read_text())}
NOW='2026-09-12'
plans=[];sources={};qa=[]
def read(n):return json.loads((RAW/n).read_text())
def src(n,role='plan-data'):
    sid='pilot-b-20260912-'+n.replace('.','-')
    if sid in sources:return sid
    m=read(n+'.meta.json');code=m.get('schoolCode') or n[:5]
    safe={k:m.get(k) for k in ['url','entryUrl','httpStatus','requestMethod','sha256','responseSha256'] if m.get(k) is not None}
    if not safe.get('sha256'):
        safe['sha256']=hashlib.sha256(json.dumps(m,sort_keys=True).encode()).hexdigest()
        safe['hashScope']='sanitized-request-failure-metadata'
    sources[sid]={**safe,'id':sid,'schoolCode':code,'publisher':TARGETS[code]['school'],
        'title':TARGETS[code]['school']+'：2026广西资料核查 '+n,
        'accessedAt':m.get('checkedAt'),'sourceType':'official','evidenceRole':role,
        'archiveFile':'raw/'+n,'requestParameters':m.get('data'),
        'method':'官方公开页面及前端请求；仅发布统计事实、查询参数和脱敏证据元数据，原响应与会话不公开。'}
    return sid
def subjects(text):
    text=text or ''
    subs=[s for s in ['化学','生物','政治','地理'] if s in text or s=='政治' and '思政' in text]
    if subs:return ('any' if '或' in text or '选考其中' in text else 'all'),subs
    if text and text not in ['--','-'] and re.search('不提|不限|不需要|物理|历史',text):return 'none',[]
    return 'unknown',[]
def add(c,major,track,count,n,row,batch=None,category='普通类',requirement='',duration=None,tuition=None,note='',**kw):
    assert track in ['物理','历史']
    assert str(count).isdigit()
    if re.search('预科|艺术|体育\(',category+' '+major):return
    sid=src(n);rule,subs=subjects(requirement)
    batch=batch or ('高职专科（批次待核）' if TARGETS[c]['ordinaryLevel']=='vocational' else '本科（批次待核）')
    base={'year':2026,'province':'广西','planStage':'initial','planVersion':'2026高校公开初始招生计划（本轮查询版）',
        'schoolCode':c,'school':TARGETS[c]['school'],'track':track,'sourceTrack':track+'类',
        'batch':batch,'group':None,'major':major.strip(),'majorCode':None,'plannedCount':int(count),
        'duration':duration or None,'tuition':tuition if tuition not in ['',None] else None,
        'requiredSubjects':subs,'subjectRule':rule,'requirementText':requirement,'category':category,
        'sourceCategory':category,'sourceId':sid,'sourceIds':[sid],
        'fieldSourceIds':{k:[sid] for k in ['major','track','plannedCount','batch','category']},
        'sourceRow':row,'reviewedAt':NOW,'groupMappingStatus':'unmatched',
        'coverageStatus':'已采集当前来源范围，专业组待核',
        'note':note or '来自2026广西初始招生计划，人数为计划数。未列字段保留未知，不由专业录取人数、其他轮次组线或专业名称推断。',**kw}
    for k,v in [('requiredSubjects',requirement),('duration',duration),('tuition',tuition)]:
        if v not in ['',None]:base['fieldSourceIds'][k]=[sid]
    identity='|'.join(str(base.get(k,'')) for k in ['year','schoolCode','track','batch','major','category','majorCode','includedMajors'])
    base['id']='plan26-pilot-b-'+c+'-'+hashlib.sha256(identity.encode()).hexdigest()[:12]
    assert base['id'] not in {x['id'] for x in plans},base
    plans.append(base)
def tables(n,encoding='utf8'):
    t=NestedTables();t.feed((RAW/n).read_bytes().decode(encoding));return t.tables

# The three ajax_zsjh families have separate totals; never import summary rows.
for c in ['10269','10036','10423']:
    for f in sorted(RAW.glob(c+'-zsjh-*.json')):
        if '.meta.' in f.name:continue
        data=read(f.name)['data'];rows=data['zsjhList'];meta=read(f.name+'.meta.json')
        total=sum(int(x['zsjhs']) for x in data['zsjhTotal'])
        assert total==sum(int(x['zsjhs']) for x in rows)
        qa.append({'schoolCode':c,'source':f.name,'sourceRows':len(rows),'sumPlanned':total,'sourceTotal':total,'check':'API detailed rows equal total'})
        for i,r in enumerate(rows,1):
            assert r['nf']=='2026' and r['ssmc']=='广西'
            cat=r.get('zylx') or r.get('zslx');track='物理' if '物理' in r['klmc'] else '历史'
            if '预科' in cat:continue
            kw={'sourceDisciplineCode':r.get('zydm') or None,'sourceMajorCode':r.get('zydh') or None,'campus':r.get('jdxq') or None}
            if r.get('bhzy'):kw['includedMajors']=r['bhzy']
            add(c,r.get('zydhmc') or r['zymc'],track,r['zsjhs'],f.name,i,
                batch=r.get('zycc') or None,category=cat,requirement=r.get('xkkm'),
                duration=r.get('zyxz'),tuition=r.get('zyxf'),note=r.get('remarks') or '',**kw)
            if r.get('bhzy'):plans[-1]['fieldSourceIds']['includedMajors']=[src(f.name)]

# MUC parameter 450000 is read from its province menu. 45 was a discovery error, not an empty-data conclusion.
for i,r in enumerate(read('10052-plans-valid.json')['rows'],1):
    assert r['year']==2026 and r['sfmc']=='广西'
    if '体育' in r['klmc'] or '预科' in r['zymc']:continue
    add('10052',r['zymc'],'物理' if '物理' in r['klmc'] else '历史',r['plan_count'],
        '10052-plans-valid.json',i,category=r['stuType'],requirement=r['xkkmmc'])

for f in sorted(RAW.glob('10718-zsjh-*.json')):
    if '.meta.' in f.name:continue
    d=read(f.name);rows=d.get('list',[])
    assert sum(x['jhrs'] for x in rows)==sum(x['jhrs'] for x in d.get('sumLists',[]))
    qa.append({'schoolCode':'10718','source':f.name,'sourceRows':len(rows),'sumPlanned':sum(x['jhrs'] for x in rows),'check':'API detailed rows equal total'})
    for i,r in enumerate(rows,1):
        assert r['nf']=='2026' and r['sf']=='广西'
        add('10718',r['zymc'],'物理' if '物理' in r['klmc'] else '历史',r['jhrs'],f.name,i,
            category=r['zslb'],duration=r.get('xzmc'),tuition=r.get('zyxf'),note=r.get('zybz') or '',
            sourceDisciplineCode=r.get('zydm') or None)

d=read('10633-plans-valid.json');assert len(d['data'])==d['count']==14
for i,r in enumerate(d['data'],1):
    if r['category'] not in ['物理类','历史类']:continue
    add('10633',r['majorname'],r['category'][:2],r['pnumber'],'10633-plans-valid.json',i,
        batch=r['batch'],category=r['typeitem'],duration=r['schoolyear']+'年')

# CQNU closes the recruitment-direction TD with DIV; repair that local syntax before expansion.
for n in ['10637-plans.html','10637-plans-p2.html']:
    html=(RAW/n).read_bytes().decode('gb18030')
    html=re.sub(r'(<td\b[^>]*>[^<]*)</div>',r'\1</td>',html)
    parser=NestedTables();parser.feed(html)
    for r in parser.tables[0]['rows'][1:]:
        assert len(r)==11,r
        if r[3] not in ['历史类','物理类']:continue
        assert r[1]=='2026' and r[2]=='广西壮族自治区'
        major=r[5]+('（'+r[6]+'）' if r[6] else '')
        add('10637',major,r[3][:2],r[9],n,int(r[0]),batch=r[8],category=r[4],duration=r[7],note=r[10],sourceMajorName=r[5],admissionDirection=r[6] or None)

for i,r in enumerate(tables('10120-plans.html')[0]['rows'][1:],1):
    if r[0]!='广西' or r[4] not in ['历史类','物理类']:continue
    add('10120',r[1],r[4][:2],r[7],'10120-plans.html',i,duration=r[2],category=r[5],requirement=r[6],note=r[3])

for i,r in enumerate(tables('11510-planquery.html')[0]['rows'][1:],1):
    assert r[7]=='2026' and r[8]=='广西'
    if r[1] not in ['历史类','物理类']:continue
    add('11510',r[4],r[1][:2],r[6],'11510-planquery.html',i,batch=r[5],category=r[2],schoolDepartment=r[3])

for i,r in enumerate(read('11552-plans.json')['data'],1):
    if r['sf']!='广西' or r['nf']!='2026' or r['kl'] not in ['历史类','物理类']:continue
    cat='中外合作办学' if '中外合作' in r['zy'] else '普通类'
    add('11552',r['zy'],r['kl'][:2],r['zsjh'],'11552-plans.json',i,
        batch=r['pc'],category=cat,duration=r['xz'],tuition=r['sfbz'],campus=r['xq'])

for i,r in enumerate(tables('12789-plans.html','gb18030')[0]['rows'][1:],1):
    assert r[0]=='2026' and r[1]=='广西'
    add('12789',r[2],r[3][:2],r[4],'12789-plans.html',i,duration=r[5],note=r[6])
for i,r in enumerate(tables('12864-plans.html')[0]['rows'][2:-1],3):
    for track,col in [('历史',2),('物理',3)]:
        if r[col]:add('12864',r[1],track,r[col],'12864-plans.html',i,tuition=r[4],schoolDepartment=r[0])

# FJBU grid cells retain blank numerical cells; only explicit merged descriptor fields are carried down.
for page,t in enumerate(json.loads((ROOT/'fjbu-tables.json').read_text()),1):
    prev={}
    for i,r in enumerate(t[2:],3):
        if r[3] not in ['历史','物理']:continue
        for col in [0,1,2,4,24]:
            if r[col] is not None:prev[col]=r[col]
        if page==1 and i==len(t):
            # A merged major cell spans the printed page break; page 2 repeats its identity.
            prev.update({0:'020402',1:'贸易经济',2:'55',4:'不提科目要求',24:'马尾'})
        if not r[15]:continue
        add('11313',prev[1].replace('\n',''),r[3],r[15],'11313-plans.pdf',f'p{page}:r{i}',
            requirement=prev[4],sourceDisciplineCode=prev[0],campus=prev[24])

# SXY initial-plan image, Guangxi is the final two columns in the upper table.
sxy=[('临床医学',None,6),('口腔医学',None,2),('中医学',4,5),('针灸推拿',4,5),
 ('中医骨伤',2,4),('医学美容技术',2,4),('护理',4,4),('医学检验技术',None,4),
 ('医学影像技术',None,2),('口腔医学技术',4,4),('眼视光技术',None,4),
 ('智能医疗装备技术',None,4),('预防医学',None,4),('食品营养与健康',2,None),('食品检验检测技术',3,None),('药学',None,3)]
for i,(major,hist,phys) in enumerate(sxy,1):
    for track,count in [('历史',hist),('物理',phys)]:
        if count is not None:add('14008',major,track,count,'14008-planimage-4.jpg',i)

# Evidence-only materials that cannot be safely split into subject-specific initial plans.
extra={
 '10025':['10025-planform.html','10025-plan-js.js','10025-plan-dic-city.json','10025-plans-2026.json','10025-plans-2025.json'],
 '10043':['10043-planindex.html','10043-planhome.html'],
 '11319':['11319-planentry-11.html','11319-plan-http.html','11319-entry-0.html'],
 '16302':['16302-entry-2.html','16302-entry-1.html'],
 '11765':['11765-plan-3.html','11765-entry-1.html'],
 '12758':['12758-plan-4.html','12758-plan-5.html'],
 '10052':['10052-plan-0.pdf','10052-planentry-extra.html'],
 '10718':['10718-plan-types.json','10718-view.js','10718-score-types.json'],
 '10269':['10269-planentry-5.html','10269-session-params.json'],
 '10036':['10036-planentry-1.html','10036-session-params.json'],
 '10423':['10423-planentry-6.html','10423-params.json'],
 '10633':['10633-planentry-7.html'],
 '14008':['14008-plan-16.html','14008-entry-1.html']}
for c,files in extra.items():
    for n in files:src(n,'scope-review')

notes={
 '10025':'官方广西计划年份菜单仅2021至2025，2026精确条件返回0条；2025同条件取得6条作为阳性对照。2026实际专业录取分仍有6条，不能用录取人数替代初始计划。',
 '10043':'本轮招生计划官方栏目未呈现计划条目；查到的体育单招与体育实验班计划不属于广西普通物理/历史专业计划。保留现有11条实际专业分，未取得初始专业计划。',
 '11319':'官网指向envo2.juwp.edu.cn招生计划系统，本轮HTTPS证书过期，HTTP同路径404；现有公告无法建立2026广西初始专业计划。访问失败不等于无计划。',
 '16302':'官网2026广西录取汇总表有3个招生大类及计划数，但未说明为录取前初始计划还是调整后计划。保留其作为后期计划统计线索，暂不导入initial；未把计划数转作新增专业录取分。',
 '11765':'已取得2026招生来源计划表广西95人，其中设计学类3人、动画4人；其余88人为16个专业/方向合计。原表未分物理/历史，不能按录取结果或专业名称拆分初始计划。原录取分冲突仍待学校澄清。',
 '12758':'已取得2026统一高考专科广西5个专业合计20人；原计划未分历史/物理，不能按录取结果拆分。另查本科分省计划只列重庆、四川，不据此添加广西本科计划。'}
catalog=[]
for c,t in TARGETS.items():
    rows=[r for r in plans if r['schoolCode']==c];ss=[s for s in sources.values() if s['schoolCode']==c]
    status='collected' if rows else ('source-found' if c in ['16302','11765','12758'] else 'entry-only')
    note=notes.get(c,f'已取得本轮官方2026广西初始专业计划{len(rows)}条、{sum(r["plannedCount"] for r in rows)}人，逐科类/类别及分页核对。此状态只表示本轮来源范围采集，不宣称全校所有渠道或所有专业组完整。')
    catalog.append({'schoolCode':c,'school':t['school'],'year':2026,'province':'广西','auditKind':'plans',
        'status':status,'checkedAt':NOW,'note':note,'sourceIds':[s['id'] for s in ss],
        'checkedUrls':list(dict.fromkeys(s['url'] for s in ss)),'entryUrl':ss[0]['url'],
        'recordCount':len(rows),'plannedCount':sum(r['plannedCount'] for r in rows),
        'groupCoverage':'unmatched','scopeComplete':False,'remainingGaps':['广西专业组代码','完整官方计划分母与全部招生渠道核对']})
for name,obj in [('plans-upsert',plans),('sources',list(sources.values())),('source-catalog',catalog)]:
    (OUT/(name+'.json')).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
(ROOT/'plan-qa.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2)+'\n')
summary={'schoolReviews':len(catalog),'planRows':len(plans),'planSchools':len({r['schoolCode'] for r in plans}),
 'sumPlanned':sum(r['plannedCount'] for r in plans),'sources':len(sources),
 'bySchool':[{'schoolCode':r['schoolCode'],'school':r['school'],'rows':r['recordCount'],'planned':r['plannedCount'],'status':r['status']} for r in catalog]}
(ROOT/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(summary,ensure_ascii=False,indent=2))
