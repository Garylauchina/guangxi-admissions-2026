#!/usr/bin/env python3
"""Bounded batch A. Initial plans and later remaining plans are separate by construction."""
import pathlib,json,copy,re,hashlib,datetime,collections
ROOT=pathlib.Path(__file__).resolve().parent
NOW=datetime.datetime.now(datetime.timezone.utc).isoformat()
def read(f):return json.loads((ROOT/f).read_text())
def write(f,v):(ROOT/f).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
base=read('baseline-plans.json');old_sources={s['id']:s for s in read('baseline-sources.json')}
schools={'10593':'广西大学','10602':'广西师范大学','10603':'南宁师范大学','10608':'广西民族大学','10598':'广西医科大学','10595':'桂林电子科技大学','10596':'桂林理工大学','11548':'广西财经学院'}
sources={};changes=[];upsert=[];checks=[];supp=[]
def new_source(key,title,**extra):
    meta=read('raw/'+key+'.meta.json');sid='batch-a-'+key
    raw=(ROOT/meta['rawFile']).read_bytes();assert hashlib.sha256(raw).hexdigest()==meta['sha256']
    sources[sid]={'id':sid,'year':2026,'title':title,'url':meta['url'],'publishedAt':None,
      'accessedAt':meta['accessedAt'],'sha256':meta['sha256'],'recordCount':0,
      'method':'公开官方原始来源；按字段核验。','rawFile':meta['rawFile'],
      'request':meta.get('request'),'requestEncoding':meta.get('requestEncoding'),**extra}
    return sid
for meta in read('fetch-initial-results.json'):
    assert not meta.get('error')
    key=meta['id'];old=old_sources['plan26-'+key]
    sid=new_source(key,old['title'],method='本批重新请求已有2026初始计划公开源；不将major_num猜作省编代码，不由其他轮次推初始组码。')
    f=ROOT/meta['rawFile']
    if f.suffix=='.json':
        data=read(meta['rawFile']);rs=data.get('data',{}).get('dataSource')
        if rs is not None:
            assert all(str(r['year'])=='2026' and r['province_name']=='广西' and str(r['province'])=='45' for r in rs)
            assert sum(int(r['jhsgf']) for r in rs)==sum(int(r['jhsgf']) for r in data['data']['overview'])
            group_values=collections.Counter(str(r.get('major_group')) for r in rs)
            checks.append({'sourceId':sid,'rows':len(rs),'allYear2026Guangxi':True,'overviewCountMatches':True,'rawGroupValues':dict(group_values)})
        elif key=='nnnu_plan_all':
            rs=data['list'];assert all(r['nf']=='2026' and r['sf']=='广西' for r in rs)
            checks.append({'sourceId':sid,'rows':len(rs),'allYear2026Guangxi':True,'rawGroupValues':dict(collections.Counter(str(r.get('zygroup')) for r in rs))})
    sources[sid]['recordCount']=sum(r['sourceId']=='plan26-'+key for r in base)

# Initial-plan-only correction: explicitly named credit-transfer programs had generic category.
for r in base:
    if r['schoolCode']!='10608' or '中澳' not in r['major']:continue
    key=r['sourceId'].removeprefix('plan26-');rs=read('raw/'+key+'.json')['data']['dataSource']
    def full_name(q):return q['major']+('（'+q['exam_direction']+'）' if q['exam_direction'] else '')
    qs=[q for q in rs if full_name(q)==r['major'] and q['subjects'].replace('类','')==r['track'] and int(q['jhsgf'])==r['plannedCount']]
    assert len(qs)==1,(r['id'],qs)
    q=qs[0];n=copy.deepcopy(r);sid='batch-a-'+key
    n['category']='学分互认联合培养项目';n.setdefault('fieldSourceIds',{})['category']=[sid]
    n['province']='广西';n['planStage']='initial'
    n['evidenceRound']='初始招生计划';n['initialPlanGroupVerified']=bool(r['group'])
    changes.append({'planId':r['id'],'field':'category','old':r['category'],'new':n['category'],
       'sourceId':sid,'sourceRowId':q['id'],'sourceCells':{'year':q['year'],'province_name':q['province_name'],'major':q['major'],'exam_direction':q['exam_direction'],'subjects':q['subjects'],'jhsgf':q['jhsgf']}})
    upsert.append(n)

# Supplementary rows are exact official remaining plans, never initial plan upserts.
for key,track,round_name in [('gxeea-first-history','历史','第一次征集'),('gxeea-first-physics','物理','第一次征集'),('gxeea-second-history','历史','第二次征集'),('gxeea-second-physics','物理','第二次征集')]:
    title=f'2026年普通高校招生本科普通批{round_name}计划信息表（首选{track}科目组）'
    sid=new_source(key,title,publisher='广西招生考试院',round=round_name,track=track,batch='本科普通批',method='GB18030官方HTML计划表，展开合并单元格；仅该轮剩余计划，不进入初始计划或首轮匹配。')
    text=(ROOT/'raw'/(key+'.html')).read_bytes().decode('gb18030')
    assert title in re.sub('<[^>]*>','',text)
    dates=re.findall(r'2026[-年]\d{1,2}[-月]\d{1,2}',text)
    if dates:sources[sid]['publishedAt']=dates[0]
    rows=read('raw/'+key+'.expanded.json')
    for ri,q in enumerate(rows):
        if q[0] not in schools:continue
        assert q[1]==schools[q[0]] and q[7]==track and len(q)==12
        cat=q[9]
        if '中外合作办学' in q[5]:cat='中外合作办学'
        elif '学分互认' in q[5]:cat='学分互认联合培养项目'
        req=q[3];subjects=[s for s in ['化学','生物','地理','政治'] if s in req]
        item={'id':f'supp26-{key}-r{ri+1}','year':2026,'schoolCode':q[0],'school':q[1],'track':track,
          'batch':'本科普通批','group':q[2],'major':q[5],'majorCode':q[4],'majorCodeType':'该轮省编专业代码',
          'requiredSubjects':subjects,'subjectRule':'none' if req=='不限' else 'all' if '+' in req or len(subjects)==1 else 'unknown',
          'requirementText':req,'plannedCount':int(q[6]),'remainingCount':int(q[6]),'plannedCountScope':'remaining-supplementary-plan',
          'tuition':q[10],'duration':None,'category':cat,'sourceCategory':q[9],'planNature':q[8],
          'note':q[11] or '', 'sourceId':sid,'sourceRow':ri+1,'evidenceRound':round_name,'round':round_name,
          'initialPlanEligible':False,'initialPlanGroupVerified':False,'firstRoundMatchAllowed':False}
        supp.append(item)
    sources[sid]['recordCount']=sum(r['sourceId']==sid for r in supp)

conflict_plan=next(r for r in base if r['id']=='plan26-5c1242de79eaeb6b')
later=next(r for r in supp if r['schoolCode']=='10596' and r['major']=='材料化冶金应用技术')
assert conflict_plan['group']=='181' and later['group']=='182'
glut_tables=read('raw/glut_plan.tables.json')
raw_initial=[q for t in glut_tables for q in t if '材料化冶金应用技术' in q]
assert len(raw_initial)==1
conflicts=[{'type':'cross-round-group-disagreement','planId':conflict_plan['id'],'schoolCode':'10596','school':'桂林理工大学','major':'材料化冶金应用技术','track':'物理',
 'initial':{'group':'181','plannedCount':150,'sourceId':'batch-a-glut_plan','sourceCells':raw_initial[0]},
 'supplementary':{'group':'182','remainingCount':later['remainingCount'],'majorCode':later['majorCode'],'evidenceRound':later['evidenceRound'],'sourceId':later['sourceId'],'sourceRow':later['sourceRow']},
 'resolution':'不覆盖初始组码，不匹配首轮；两份官方源发生阶段/内容差异，原因尚未确认。该专业不是仅凭同名可安全跨轮次关联的证明。'}]
for key,title in [('gxmzu-bkguide','广西民族大学2026年报考指南'),('gxmzu-zsguide','广西民族大学2026年招生指南')]:
    new_source(key,title,publisher='广西民族大学（官网链接的电子指南）',method='官网首页直接链接；2026标题可核。报考指南经公开浏览器查看为6页，未采作初始组码证据。',sourceKind='本年官方电子指南入口')
entries={
 '10593':'https://zhaolu.zjzw.cn/release-page/plan?key=502eaa9010f49a5b1ca78afc',
 '10602':'https://bkzs.gxnu.edu.cn/pg/jh/index.php?SSDM=45&NF=2026',
 '10603':'https://zsw.nnnu.edu.cn/zsdata/lqxx/#/',
 '10608':'https://zhaolu.zjzw.cn/release-page/Plan?key=15f4609edee13b448a3a3224',
 '10598':'https://zhaolu.zjzw.cn/release-page/plan?key=338bb03bdb48ee76c2fc176b',
 '10596':'https://zscx.glut.edu.cn/f/listPlan',
 '11548':'https://www.gxufe.edu.cn/www/subWebSites/zsxx/index.html'}
catalog=[]
for code,school in schools.items():
    rs=[r for r in base if r['schoolCode']==code];ids=sorted({'batch-a-'+r['sourceId'].removeprefix('plan26-') for r in rs})
    item={'schoolCode':code,'school':school,'year':2026,'status':'collected','sourceKind':'本年初始招生计划','sourceIds':ids,'checkedAt':NOW,
      'planRowsInCurrentSite':len(rs),'initialGroupsKnown':sum(bool(r['group']) for r in rs),
      'note':f'2026年广西公开初始计划已采集并重新读取，共{len(rs)}条已采集记录。'+('学校原公开计划已列专业组；初始组码与后续征集独立保存。' if code in ['10595','10596'] else '已采集计划来源没有可用的广西三位专业组字段；初始组码仍缺直接证据。')}
    if code in entries:item['entryUrl']=entries[code]
    if code=='10608':
        item['sourceIds']+=['batch-a-gxmzu-bkguide','batch-a-gxmzu-zsguide']
        item['note']+='官网另链接2026报考指南和招生指南；报考指南计划总表含预科直升口径，未用于补组。11条中澳学分互认项目由初始API修类别。'
    if code=='10596':item['note']+='材料化冶金应用技术初始181与第一次征集182存在差异，禁止自动跨轮次匹配。'
    catalog.append(item)

assert len(upsert)==11 and len(supp)==84
assert all(r['plannedCount']==next(q['plannedCount'] for q in base if q['id']==r['id']) for r in upsert)
assert all(r['group']==next(q['group'] for q in base if q['id']==r['id']) for r in upsert)
assert not any(r['firstRoundMatchAllowed'] for r in supp)
assert all(sid in sources or sid in old_sources for r in upsert for sids in r.get('fieldSourceIds',{}).values() for sid in sids)
write('plans-upsert.json',upsert);write('supplementary-plans.json',supp);write('sources.json',list(sources.values()))
write('source-catalog.json',catalog);write('field-changes.json',changes);write('cross-round-conflicts.json',conflicts)
write('QA.json',{'year':2026,'initialPlanUpserts':len(upsert),'initialGroupAdditions':0,'supplementaryRows':len(supp),
 'supplementaryCountsBySchool':dict(collections.Counter(r['school'] for r in supp)),
 'initialApiChecks':checks,'noInitialPlanCountsChanged':True,'noInitialGroupsOverwritten':True,
 'supplementaryNeverFirstRoundMatched':True,'crossRoundConflictRegressionPassed':True,'allSourceHashesPassed':True})
print(json.dumps({'upserts':len(upsert),'supplementary':len(supp),'catalogSchools':len(catalog),'initialGroupAdditions':0},ensure_ascii=False))
