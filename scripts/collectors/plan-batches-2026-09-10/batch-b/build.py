"""Batch B: only official explicitly Guangxi initial plan counts. Python stdlib."""
import collections,datetime,hashlib,json,re
from pathlib import Path
from html_tables import NestedTables,expand
ROOT=Path(__file__).resolve().parent
NOW=datetime.datetime.now(datetime.timezone.utc).isoformat()
def read(n):return json.loads((ROOT/n).read_text())
def write(n,v):(ROOT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def tables(sid):
    h=(ROOT/'raw'/f'{sid}.html').read_text();p=NestedTables();p.feed(h)
    return [expand(t) for t in p.tables],h
def row(sid,school,code,track,major,count,n):
    return {'id':f'plan26-b-{sid}-{n}-{track}','year':2026,'province':'广西','planStage':'initial',
            'school':school,'schoolCode':code,'track':track,'batch':'本科普通批','group':None,
            'major':major,'majorCode':None,'plannedCount':int(count),'duration':None,'tuition':None,
            'requiredSubjects':[],'subjectRule':'unknown','requirementText':None,'category':'普通类',
            'sourceId':'batch-b-'+sid,'sourceRow':n,'note':'','reviewedAt':NOW}
def main():
    plans=[];sources=[];catalog=[];excluded=[];checks=[]
    def source(sid,school,count,title,published=None,method='',parent=None):
        m=read('raw/'+sid+'.meta.json');s={'id':'batch-b-'+sid,'title':title,'url':m['url'],'publisher':school,
            'year':2026,'publishedAt':published,'accessedAt':m['accessedAt'],'sha256':m.get('sha256'),
            'recordCount':count,'method':method,'rawPath':m.get('rawFile'),'request':m.get('request'),
            'requestEncoding':m.get('requestEncoding'),'status':m['status']}
        if parent:s['parentSourceId']='batch-b-'+parent
        sources.append(s)
    def cat(school,code,status,sids,note,entry,coverage='partial'):
        catalog.append({'schoolCode':code,'school':school,'year':2026,'status':status,
                        'sourceIds':['batch-b-'+s for s in sids],'checkedAt':NOW,'note':note,
                        'entryUrl':entry,'coverage':coverage,'recordCount':sum(r['schoolCode']==code for r in plans)})
    sid='guat-plan';ts,h=tables(sid);tab=[t for t in ts if t[0]==['专业组','科类名称','专业名称','计划']][0]
    assert '2026年招生计划统计表（广西）' in h
    group_totals=collections.defaultdict(int)
    for i,c in enumerate(tab[1:],2):
        group_totals[c[0]]+=int(c[3])
        if '艺术' in c[1] or '预科' in c[2]:excluded.append({'sourceId':'batch-b-'+sid,'sourceRow':i,'sourceCells':c,'reason':'艺术或预科不纳入普通类本科计划'});continue
        track='历史' if '历史' in c[1] else '物理';r=row(sid,'桂林航天工业学院','11825',track,c[2],c[3],i)
        r['group']=re.match(r'(\d+)组',c[0])[1];r['requirementText']=c[1]
        if '化学' in c[1]:r.update(requiredSubjects=['化学'],subjectRule='all')
        elif '不限' in c[1] or '不提科目要求' in c[1]:r['subjectRule']='none'
        for term in ['精准专项','民族班','中外合作办学']:
            if term in c[2]:r['category']=term
        r['note']='2026年广西招生计划表直接列明专业、专业组及计划数；学制和学费未列。'
        plans.append(r)
    for name,total in group_totals.items():
        expected=re.search(r'（(\d+)人）',name)
        if expected:assert total==int(expected[1]),(name,total)
    guat=[r for r in plans if r['schoolCode']=='11825'];assert len(guat)==58
    checks.append({'school':'桂林航天工业学院','records':58,'plannedCount':sum(r['plannedCount'] for r in guat),
                   'allGroups':dict(group_totals),'publishedGroupTotalChecks':'PASS','selectedGroups':len({r['group'] for r in guat}),
                   'samples':[guat[0],guat[len(guat)//2],guat[-1]]})
    source(sid,'桂林航天工业学院',58,'2026年招生计划统计表（广西）','2026-06-20',
           '直接解析官方HTML合并单元格；逐组专业人数与所有公布组总核对；剔除艺术和预科。')
    cat('桂林航天工业学院','11825','collected',[sid],'已采集原表全部58条普通类本科计划，含按原名标识的民族班、精准专项、合作；全部12个组码直接取原表。','https://zsw.guat.edu.cn/info/1020/1990.htm','complete-for-source-ordinary-plans')
    sid='ymun-plan';ts,h=tables(sid);tab=[t for t in ts if t[0][:2]==['序号','专业名称']][0]
    assert '2026年普通高等教育分省分专业招生计划表' in h
    assert tab[1][7:11]==['广西招生总数','物理类','历史类','民族班']
    new=[]
    for i,c in enumerate(tab[2:],3):
        if not c[0].isdigit():continue
        assert int(c[7])==sum(int(x or 0) for x in c[8:11])
        if '定向' in c[1]:
            excluded.append({'sourceId':'batch-b-'+sid,'sourceRow':i,'sourceCells':c[:12],'reason':'免费医学定向43人，子计划地区/组码/批次未核对，另留缺口'});continue
        if c[10]:excluded.append({'sourceId':'batch-b-'+sid,'sourceRow':i,'major':c[1],'plannedCount':int(c[10]),'reason':'民族班单列人数未拆物理/历史，不按学科常识推定科类'})
        for track,j in [('物理',8),('历史',9)]:
            if not c[j]:continue
            r=row(sid,'右江民族医学院','10599',track,c[1],c[j],i)
            r.update(duration=c[3],tuition=c[5],category='未注明招生类别',batch='本科（批次待核）');r['note']='直接采用2026分省表广西'+track+'类人数；专业组和再选科目未列，批次与资格范围尚待核实。'
            if c[1]=='生物医药数据科学':
                r['tuition']=None;r['sourceTuition']=c[5];r['note']+='源表学费列列5400元，但注释称正在申报、以最终批复为准，因此学费保留未确认。'
            new.append(r)
    assert len(new)==31 and sum(r['plannedCount'] for r in new)==2818
    plans.extend(new)
    source(sid,'右江民族医学院',31,'右江民族医学院2026年招生计划表','2026-06-23',
           '直接读取广西物理/历史列，未按总数分配；民族班30人科类未分、定向43人缺子计划证据均不入本批。新专业学费以注释优先标待批。')
    checks.append({'school':'右江民族医学院','records':31,'plannedCount':2818,'sourceGuangxiTotal':2891,'excludedMinoritySeats':30,'excludedDirectedSeats':43,'totalReconciliation':'PASS','samples':[new[0],new[len(new)//2],new[-1]]})
    cat('右江民族医学院','10599','collected',[sid],'采集直接广西物理/历史31条2818人；组码未列，批次和资格范围待核，未标为普通批普通类。原广西2891人中的民族班30人科类未拆、定向43人地区子计划未核，本批排除。','https://yyzs.ymun.edu.cn/info/1046/1537.htm')
    # Only catalog the other three: do not turn national totals into Guangxi allocations.
    for s,school,title in [('gxust_plan','广西科技大学','2026年普通本科分省分专业招生计划'),('gxust_groups','广西科技大学','2026年区内普通本科招生专业组设置'),('gxust_plan_pdf','广西科技大学','2026年分省计划原PDF'),('gxust_groups_pdf','广西科技大学','2026年专业组原PDF'),('gxust_query_data','广西科技大学','2026广西计划公开查询返回')]:
        source(s,school,0,title,method='本轮已取得2026原始资料；分省人数未完整拆科类/资格，查询2026广西返回空，不拼接推定普通组人数。')
    cat('广西科技大学','10594','source-found',['gxust_plan','gxust_groups','gxust_plan_pdf','gxust_groups_pdf','gxust_query_data'],'已取得本年分省专业人数与专业组设置，但人数未拆历史/物理及资格类别，不能硬拼到普通组；公开2026广西查询返回空。','https://www.gxust.edu.cn/zsw/info/1018/2194.htm')
    for s,title in [('gxvnu-plan','2026年普通高考招生计划总表'),('gxvnu-plan-outside','2026年外省招生计划'),('gxvnu-charter','2026年普通高考招生章程（校码直证）')]:
        source(s,'广西职业师范学院',0,title,'2026-06-25',method='全国总表和六省表是有效本年来源，但非直接广西逐专业计划列；本批不以减法推导进入计划表。')
    cat('广西职业师范学院','14684','source-found',['gxvnu-plan','gxvnu-plan-outside','gxvnu-charter'],'本年官方章程明确学校标识码4145014684；末五位14684与本项目已核验考试院学校表一致。已取得全国总表及六省160人外省表，未取得直接广西逐专业逐科类表。本批不采纳总表减外省的推导人数。','https://zsb.gxvnu.edu.cn/info/1093/2331.htm')
    for s in ['glmu-zs-home','glmu-plan-index','glmu-plan-list']:
        source(s,'桂林医科大学',0,'桂林医科大学本专科计划入口及公开列表',method='通过官方前端及其文章列表公开POST检查2026计划。')
    cat('桂林医科大学','10601','entry-only',['glmu-zs-home','glmu-plan-index','glmu-plan-list'],'已连通官方新域名本专科招生入口和动态计划列表，具体2026计划正文尚待解析。','https://jyw.glmu.edu.cn/zhaosheng/school!articleList.htm?recruitArticle.searchArticleType=1')
    # Optional later extension must retain all earlier rows and IDs.
    if (ROOT/'glmu-extension.json').exists():
        extension=read('glmu-extension.json');plans.extend(extension['plans']);sources.extend(extension['sources'])
        excluded.extend(extension.get('excluded',[]));checks.extend(extension.get('checks',[]))
        catalog=[c for c in catalog if c['schoolCode']!='10601']+[extension['catalog']]
    ids={s['id'] for s in sources};assert len(ids)==len(sources)
    assert len({r['id'] for r in plans})==len(plans)
    assert all(r['sourceId'] in ids and r['province']=='广西' and r['planStage']=='initial' and r['year']==2026 and r['plannedCount']>0 for r in plans)
    write('plans-upsert.json',plans);write('sources.json',sources);write('source-catalog.json',catalog)
    write('QA.json',{'checkedAt':NOW,'result':'PASS','records':len(plans),'plannedCount':sum(r['plannedCount'] for r in plans),'bySchool':dict(collections.Counter(r['school'] for r in plans)),
                    'withExplicitGroup':sum(r['group'] is not None for r in plans),'checks':checks,'excluded':excluded,
                    'limitations':['只入直接广西列且明确初始计划；无征集混入。','未公布组码不推断；未拆科类人数不按学科常识分配。']})
    print(json.dumps({'records':len(plans),'plannedCount':sum(r['plannedCount'] for r in plans),'bySchool':dict(collections.Counter(r['school'] for r in plans))},ensure_ascii=False))
if __name__=='__main__':main()
