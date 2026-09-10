#!/usr/bin/env python3
"""Rebuild the 2026 plan audit from public-only baseline and captured official sources.

No network, credentials, private workspace paths, or website mutation is used.
Run extract_tables.py first if rebuilding from freshly fetched HTML.
"""
import collections, copy, hashlib, json, pathlib, re
BASE = pathlib.Path(__file__).resolve().parent
def read(p): return json.loads((BASE/p).read_text())
def write(p,v): (BASE/p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
original=read('baseline/research-plans.json')
site=read('baseline/site-plans.json')
sources={s['id']:s for s in read('baseline/research-sources.json')+read('baseline/site-sources.json')}
new_sources={}; changes=[]; excluded=[]; differences=[]; unresolved=[]
def source(key,title,date=None):
    meta=read('raw/'+key+'.meta.json'); sid='audit-plan26-'+key
    new_sources[sid]={'id':sid,'title':title,'url':meta['url'],'publishedAt':date,
        'accessedAt':meta['accessedAt'],'sha256':meta['sha256'],'recordCount':0,
        'year':2026,'method':'官方公开页面或原图；字段级摘录与原始表格行对应；未由分数推断组码。',
        'rawFile':meta['rawFile'],'request':meta.get('request'),'requestEncoding':meta.get('requestEncoding')}
    return sid
YP=source('ylu_plan_recheck','玉林师范学院2026年招生计划','2026-06-23')
YC=source('ylu_cutoff_recheck','玉林师范学院2026年录取情况一览表（动态更新）','2026-07-11')
YT=source('ylu_charter','玉林师范学院2026年全日制普通本科招生章程','2026-06-08')
TG=source('gxtcm_groups_image','广西中医药大学2026年普通高考本专科招生院校专业组分组方案（广西）原图','2026-06-18')
TP=source('gxtcm_groups','广西中医药大学2026年专业组分组方案官方发布页','2026-06-18')
TC=source('gxtcm_charter','广西中医药大学2026年全日制普通本专科招生章程','2026-06-10')
NP=source('gxnu_plan_recheck','广西师范大学2026年广西分专业招生计划',None)
NT=source('gxnu_teacher','广西师范大学2026年地方公费师范生招生简章','2026-06-15')
MF=source('gxmu_faq','广西医科大学2026年招生常见问题解答','2026-06-24')
GC=source('guet_charter','桂林电子科技大学2026年全日制普通本科招生章程','2026-06-09')
def evidence(sid,locator,detail=None):
    e={'sourceId':sid,'locator':locator}
    if detail: e['detail']=detail
    return e
def change(r,field,value,e):
    if r.get(field)==value: return
    changes.append({'planId':r['id'],'school':r['school'],'field':field,'old':copy.deepcopy(r.get(field)),
        'new':copy.deepcopy(value),'evidence':e})
    r[field]=value
    r.setdefault('fieldSourceIds',{})[field]=list(dict.fromkeys(x['sourceId'] for x in e))
def append_note(r,text,e):
    n=r.get('note') or ''
    if text not in n: change(r,'note',(n.rstrip('；。')+'；'+text).lstrip('；'),e)
def cleanmajor(m): return re.sub(r'[（(]精准专项[）)]','',m).strip()
arts={'美术学','视觉传达设计','环境设计','服装与服饰设计','工艺美术','音乐学','舞蹈学','体育教育','社会体育指导与管理','运动康复'}
plans=[]
for row in original:
    r=copy.deepcopy(row)
    if r['schoolCode']=='10602' and r['batch']=='预科直升批':
        excluded.append({'plan':r,'reason':'预科直升批面向已完成预科的学生，不是当年高考可填报计划。',
            'evidence':[evidence(NP,'招生计划表：批次=预科直升批；按专业代码、科类、计划数定位')]}); continue
    if r['schoolCode']=='10606' and r['major'] in arts:
        excluded.append({'plan':r,'reason':'原始总计划表的师范类/普通类不是高考科类；官方录取表明确属艺术或体育，退出普通文化分计划筛选。',
            'evidence':[evidence(YP,'广西分专业计划表：该专业与历史/物理计划列'),evidence(YC,'第1—5表：艺术、体育类别录取表；按专业名称定位')]}); continue
    req=r.get('requirementText') or ''
    if re.fullmatch(r'(物理|历史)[（(]1门科目考生必须选考方可报考[）)]',req):
        change(r,'subjectRule','none',[evidence(r['sourceId'],'选科要求原文',req+'；首选科目已存入track，再选无额外要求。')])
    if r['schoolCode']=='10606' and r['major']=='人工智能':
        ev=[evidence(YP,'选考科目表：人工智能080717','原文仅列物理、化学，却注明3门均须选考，存在源内矛盾。')]
        change(r,'subjectRule','unknown',ev);change(r,'requirementStatus','source-conflict',ev)
        append_note(r,'选科原文列出物理、化学但标注3门，完整选科条件待校方核实。',ev)
    if r['schoolCode']=='10602' and '地方公费师范生' in r['note']:
        ev=[evidence(NP,'计划性质列=地方公费师范生；专业='+r['major'])]
        change(r,'category','地方公费师范生',ev)
        if not r['major'].startswith('科学教育'):
            change(r,'duration','4',[evidence(NT,'第四部分（一）：学制四年，本科层次')])
            change(r,'tuition','免费',[evidence(NT,'第五部分（三）：在校期间免除学费')])
    if r['schoolCode']=='10598':
        batch=('高职高专普通批' if '层次：高职' in r['note'] or '层次：专科' in r['note'] else
            '其他预科批' if r['major']=='免费少数民族预科班' else
            '本科提前批（小批次待核）' if r['category']=='免费医学定向生' else '本科普通批')
        ev=[evidence(MF,'Q11：2026年广西招生四个批次；结合接口层次及专业类型')]
        change(r,'batch',batch,ev)
        change(r,'note',r['note'].replace('接口未公布批次、组码与选科要求。','组码与选科要求尚未核实。'),ev)
        if '中澳学分互认' in r['major']:
            change(r,'category','学分互认联合培养项目',[evidence(r['sourceId'],'药学：专业名称和备注明确中澳学分互认联合培养项目')])
    if r['schoolCode']=='10595' and r['category']=='中外合作办学':
        change(r,'tuition','45000' if r['major'].startswith('数字媒体技术') else '60000',
               [evidence(GC,'第三十条3—4：对应中外合作专业学年学费')])
    if r['schoolCode']=='11548' and '预科' in r['major'] and r['duration']=='4':
        ev=[evidence(r['sourceId'],'专业为少数民族预科班，接口level=本科、educational_code=4；未区分预科阶段与本科阶段')]
        change(r,'sourceDuration','4',ev);change(r,'duration',None,ev)
        change(r,'durationStatus','source-stage-ambiguous',ev)
        append_note(r,'接口学制字段为4年，未区分预科阶段与本科阶段；当前阶段学制待核。',ev)
    plans.append(r)

# 玉林：直接读取包含专业组的实际录取表；不读取或利用分数字段。
yr=[]
for ti,tr in [(7,'历史'),(8,'物理')]:
    for ri,row in enumerate(read(f'raw/ylu_cutoff_expanded-{ti}.json')):
        if len(row)<8 or not re.fullmatch(r'\d{3}',str(row[0])) or '征集' in str(row[1]): continue
        yr.append({'group':str(row[0]),'major':cleanmajor(row[1]),'precise':'精准专项' in row[1],
                   'track':tr,'count':int(row[5]),'locator':f'HTML第{ti+1}表，第{ri+1}行（含表头）'})
yfees={r[0]:(r,i) for i,r in enumerate(read('raw/ylu_charter.tables.json')[0]) if len(r)==4}
yfees['无人机测绘技术']=yfees['无人机测绘技术（本科层次职业教育专业）']
for r in plans:
    if r['schoolCode']!='10606': continue
    if r['major']=='网络新媒体':
        change(r,'major','网络与新媒体',[evidence(YT,'学费表：网络与新媒体050306T'),evidence(YC,'本科普通批表：网络与新媒体')])
        ev=[evidence(YP,'第4表第15行（含表头）：网络与新媒体，不提科目要求')]
        change(r,'requirementText','不提科目要求',ev);change(r,'subjectRule','none',ev)
    candidates=[q for q in yr if q['major']==r['major'] and q['track']==r['track'] and q['precise']==(r['category']=='精准专项')]
    # 当普通/民族同专业出现多组，仅用源计划数区分；仍有歧义即不赋组。
    if len({q['group'] for q in candidates})>1:
        candidates=[q for q in candidates if q['count']==r['plannedCount']]
    if len({q['group'] for q in candidates})==1:
        q=candidates[0];ev=[evidence(YC,q['locator'],'专业、科类、类别及组码直接同一行；未采用分数值。')]
        change(r,'group',q['group'],ev)
        if q['count']!=r['plannedCount']:
            differences.append({'planId':r['id'],'school':r['school'],'major':r['major'],'track':r['track'],
                'originalPublishedCount':r['plannedCount'],'laterAdmissionTablePlanCount':q['count'],'evidence':ev})
            change(r,'laterPublishedPlanCount',q['count'],ev)
            append_note(r,f'原招生计划{r["plannedCount"]}人；后续录取公告计划栏为{q["count"]}人，保留原招生计划口径。',ev)
    else:
        unresolved.append({'planId':r['id'],'field':'group','reason':'官方后续表无法唯一匹配专业/类别/人数','candidateGroups':[q['group'] for q in candidates]})
    if r['major'] in yfees:
        q,ri=yfees[r['major']];ev=[evidence(YT,f'第二十五条学费表第{ri+1}行：{q[0]}')]
        change(r,'tuition',q[3],ev);change(r,'duration',{'四年':'4','五年':'5'}.get(q[2],q[2]),ev)

# 广西中医药：人工逐格核对官方组表图片的文字转录。严禁把组区间拆成县组。
tfees={(r[0],r[1]):(r,i) for i,r in enumerate(read('raw/gxtcm_charter.expanded-0.json')) if len(r)==5}
ttrans=[]
for r in plans:
    if r['schoolCode']!='10600':continue
    m=r['major'];tr=r['track'];cat=r['category'];base=re.split('[（(]',m)[0]
    vocational='高职高专' in r['batch'];g=None
    if '定向医学生' in m: pass
    elif '预科A类' in m:g='713' if tr=='历史' else '753'
    elif '预科B类' in m:g='712' if tr=='历史' else '752'
    elif vocational:g=('114' if tr=='历史' else '161') if base=='针灸推拿' else '163' if base=='护理' else '162'
    elif '5+3' in m:g='111' if tr=='历史' else '151'
    elif cat=='国家专项计划':g='511' if tr=='历史' else '551' if base=='中医学' else '553'
    elif cat=='地方专项计划':g='512' if tr=='历史' else '552' if base=='中医学' else '554'
    elif cat=='民族班':g='711' if tr=='历史' else '751'
    elif tr=='历史':g='113' if base=='健康服务与管理' else '112'
    elif base in ['中医学','中医康复学','中医骨伤科学','针灸推拿学','壮医学']:g='152'
    else:g={'口腔医学':'153','临床医学':'154','中西医临床医学':'155','预防医学':'156','临床药学':'157','中药学':'157','药学':'157','制药工程':'157','医学检验技术':'158','医学影像技术':'158','康复治疗学':'158','医学信息工程':'158','食品质量与安全':'158','护理学':'159','健康服务与管理':'160'}[base]
    ev=[evidence(TG,f'{tr}科类；专业={m}；'+('专业组='+g if g else '定向专业组区间')),
        evidence(TP,'2026年分组方案官方发布页（年份及原图归属）')]
    if base not in ['健康服务与管理','医学信息工程'] and '预科' not in m:
        change(r,'admissionRequirements',['不招色盲、色弱考生'],ev)
        append_note(r,'不招色盲、色弱考生。',ev)
    if '5+3' in m:
        change(r,'undergraduateDuration','5',ev)
        append_note(r,'培养总程为5+3，本科阶段5年。',ev)
    if g:
        change(r,'group',g,ev)
        ttrans.append({'planId':r['id'],'track':tr,'major':m,'group':g,'sourceId':TG})
        chem=tr=='物理' and g in ['153','154','155','156','157','158','159','162','163','553','554','752','753']
        change(r,'requiredSubjects',['化学'] if chem else [],ev)
        change(r,'subjectRule','all' if chem else 'none',ev)
        change(r,'requirementText',tr+('，化学（均须选考）' if chem else '；再选不限'),ev)
        # 已有直接专业组证据之后，仅借省考试院相同学校/科类/组码确认批次。
        matches=[c for c in read('baseline/site-cutoffs.json') if c['schoolCode']==r['schoolCode'] and c['track']==tr and c['group']==g]
        if len({c['batch'] for c in matches})==1:
            c=matches[0];change(r,'batch',c['batch'],[evidence(c['sourceId'],'学校代码10600，科类'+tr+'，专业组'+g+'；仅核定批次，不使用分数')])
    if not vocational and '预科' not in m:
        e=[evidence(r['sourceId'],'广西本科计划表备注：广西计划数包含预科直升计划')]
        change(r,'plannedCountScope','includesPreparatoryProgression',e)
        change(r,'currentGaokaoSeatsKnown',False,e)
    if '定向医学生' in m:
        change(r,'tuition','免费',[evidence(TC,'第二十一条：农村订单定向免费医学教育')])
        change(r,'note',r['note'].replace('专业组和批次未列','分组图列组码区间（历史401—414、物理451—464）；当前计划未拆地区，不能对应单组，具体批次待核'),ev)
    elif '预科A类' in m:change(r,'tuition','免费（预科阶段）',[evidence(TC,'第二十二条：免费少数民族预科班免一年学费')])
    elif '预科' not in m:
        q,ri=tfees[('高职' if vocational else '本科',base)]
        fee=q[4]
        if not vocational:fee+='（本科阶段按学分制预缴，毕业结算）'
        change(r,'tuition',fee,[evidence(TC,f'第二十八条学费表第{ri+1}行：{q[0]}{q[1]}；本科为预缴标准')])
    if g:
        change(r,'note',r['note'].replace('；专业组和批次未列','').replace('专业组和批次未列','').replace('，组码和批次未列','').replace('；图表未列批次、专业组和学费','').replace('原表未列具体批次或专业组。','专业组已由官方分组图核实；具体批次待核。'),ev)

# 玉林补充教师计划：依据原招生计划的县×专业×科类格子验证，合并录取表分列。
teachers=[copy.deepcopy(r) for r in site if r['id'].startswith('plan-major-2026-ylu')]
matrix=read('raw/ylu_teacher_plan_expanded.json')
teacher_groups=collections.defaultdict(list)
for r in teachers:teacher_groups[(r['track'],r['group'],r['major'])].append(r)
upsert=[];delete=[];teacher_evidence=[]
for key,rows in teacher_groups.items():
    old_counts=[q['plannedCount'] for q in rows]
    r=rows[0];major,qualifier=re.match(r'^(.*)[（(](.*)[）)]$',r['major']).groups()
    level,county=qualifier.split(',',1)
    county=county.replace('龙胜各族自治县','龙胜县').replace('恭城瑶族自治县','恭城县')
    ri=next(i for i,q in enumerate(matrix) if q[0]==county)
    ci={'数学与应用数学':1,'物理学':2,'生物科学':3}.get(major)
    if major=='英语':ci=4 if r['track']=='历史' else 5
    if major=='应用心理学':ci=(6 if level=='高中' else 8)+(r['track']=='物理')
    count=int(matrix[ri][ci]);ev=[evidence(YP,f'第3表：{county}×{matrix[0][ci]}×{r["track"]}，计划{count}'),evidence(YC,'本科提前批其他一类，专业组'+r['group']+'：'+r['major'])]
    assert sum(q['plannedCount'] for q in rows)==count,(r['major'],count,rows)
    change(r,'plannedCount',count,ev)
    if len(rows)>1:
        delete.extend(q['id'] for q in rows[1:])
        teacher_evidence.append({'retainedId':r['id'],'removedIds':[q['id'] for q in rows[1:]],'oldCounts':old_counts,
            'newCount':count,'evidence':ev,'reason':'原计划同一县专业科类只有一格；录取公告分列，未提供不同专业代码。征集是剩余计划，不与原计划相加。'})
    req=matrix[1][ci];subs=[s for s in ['化学','生物','政治','地理'] if s in req]
    change(r,'requiredSubjects',subs,ev);change(r,'subjectRule','all' if subs else 'none',ev);change(r,'requirementText',req,ev)
    change(r,'category','优师计划' if matrix[ri][13]=='优师计划' else '地方公费师范生',ev)
    change(r,'planBasis','2026年6月23日原招生计划（县×专业×科类），已与正投表对应',ev)
    restrictions=('不招色盲、色弱考生。' if '不招色盲、色弱' in r['note'] else '')
    if major=='英语' and '口语测试合格' in r['note']:restrictions+='英语须口语测试合格。'
    change(r,'note','定向培养，服务地区见专业名；原招生计划已核实。'+restrictions+('原录取公告分列，已按原计划合并；征集不另计计划。' if len(rows)>1 else ''),ev)
    upsert.append(r)

assert len(original)==1584 and len(excluded)==87 and len(plans)==1497
assert len(upsert)==27 and len(delete)==2
assert all(r['year']==2026 for r in plans+upsert)
assert len({r['id'] for r in plans})==len(plans)
assert all(r['group'] is None or re.fullmatch(r'\d{3}',r['group']) for r in plans)
assert not any(r['schoolCode']=='10606' and r['major'] in arts for r in plans)
assert not any(r['batch']=='预科直升批' for r in plans)
all_evidence=[e for c in changes for e in c['evidence']]+[e for c in excluded for e in c['evidence']]
assert all(e['sourceId'] in sources or e['sourceId'] in new_sources for e in all_evidence)
for sid,s in new_sources.items():
    s['recordCount']=len({c['planId'] for c in changes if any(e['sourceId']==sid for e in c['evidence'])})
    data=(BASE/s['rawFile']).read_bytes();assert hashlib.sha256(data).hexdigest()==s['sha256']
write('corrected-plans.json',plans);write('excluded-plans.json',excluded)
write('new-sources.json',list(new_sources.values()));write('field-corrections.json',changes)
write('supplemental-plan-patch.json',{'format':'id-keyed-delete-and-upsert','baseline':'baseline/site-plans.json','deleteIds':delete,'upsert':upsert,'mergeEvidence':teacher_evidence})
write('plan-count-differences.json',differences);write('gxtcm-group-transcription.json',ttrans)
baseline_by_id={r['id']:r for r in original}
base_diff=collections.Counter(f for r in plans for f in set(r)|set(baseline_by_id[r['id']]) if f!='fieldSourceIds' and r.get(f)!=baseline_by_id[r['id']].get(f))
write('audit-findings.json',{'year':2026,'scope':'基础14校全量计划深审及玉林补充29条教师计划；另2校只做结构核验',
 'baselineRows':len(original),'correctedRows':len(plans),'excludedRows':len(excluded),'fieldCorrections':len(changes),
 'changedPlanRows':len({c['planId'] for c in changes}),'beforeGroups':sum(bool(r['group']) for r in original),'afterGroups':sum(bool(r['group']) for r in plans),
 'baselineToFinalFieldDifferences':dict(base_diff),'baselineRowsChanged':sum(any(r.get(f)!=baseline_by_id[r['id']].get(f) for f in set(r)|set(baseline_by_id[r['id']]) if f!='fieldSourceIds') for r in plans),
 'exclusionReasons':dict(collections.Counter(x['reason'] for x in excluded)),
 'fieldsChanged':dict(collections.Counter(c['field'] for c in changes)),
 'schoolStats':[{'school':school,'rows':len(rs),'groupKnown':sum(bool(r['group']) for r in rs),'subjectUnknown':sum(r['subjectRule']=='unknown' for r in rs),'tuitionUnknown':sum(r['tuition'] is None for r in rs),'durationUnknown':sum(r['duration'] is None for r in rs),'batchUnknown':sum('待核' in r['batch'] for r in rs)} for school,rs in ((s,[r for r in plans if r['school']==s]) for s in sorted({r['school'] for r in plans}))],
 'unresolvedGroupMappings':unresolved,'sourceConflicts':[{'school':'玉林师范学院','major':'人工智能','rows':2,'conflict':'科目名单为物理、化学两门，括注却写三门；subjectRule保留unknown'}],
 'teacherPatch':{'inputRows':len(teachers),'outputRows':len(upsert),'removedDuplicateRows':len(delete),'originalPlanCount':sum(r['plannedCount'] for r in upsert)},
 'checks':{'baselinePreserved':True,'allYear2026':True,'uniqueIds':True,'allEvidenceSourcesResolved':True,'newSourceHashesMatch':True,'noInferredGroupCodes':True,'noScoresUsedForGroupMapping':True,'originalPublishedCountsRetained':True}})
print(json.dumps({'corrected':len(plans),'excluded':len(excluded),'changes':len(changes),'groupKnown':sum(bool(r['group']) for r in plans),'unresolvedYulin':unresolved,'teacherRows':len(upsert)},ensure_ascii=False))
