#!/usr/bin/env python3
"""Build reviewed facts and bounded gap notes from this batch's local evidence."""
import collections, datetime, hashlib, html, json, pathlib, re
ROOT = pathlib.Path(__file__).resolve().parent
def read(name): return json.loads((ROOT/name).read_text())
def write(name,value): (ROOT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
def plain(value): return html.unescape(re.sub('<[^>]+>',' ',value))
manifest = read('fetch-manifest.json')
targets = read('targets.json')
byid = {m['id']:m for m in manifest}
review_date = '2026-09-12'

notes = {
 '10593': ('not-found-current-major', '官网录取分数目录最新本科结果为2025年；2026年发布的预科表也标明数据年2025。另查招生动态首页，未发现2026广西专业实际最低分。'),
 '10595': ('year-unavailable', '当前专业分查询配置提供2020至2025，无2026；另查官网历史文章目录，首页仍为2023分省结果。未把旧年数据或查询表单视为本年分数。'),
 '10602': ('current-year-query-empty', '当前查询年份为2025、2024、2023；2026广西全部类别JSON查询成功返回空数组，2025同条件对照有记录。另找到2026生源质量公告中的14条专业投档最高/最低分，另列为投档证据，不能替代专业实际录取分。'),
 '10599': ('access-limited', '官网首页可读，2026普通批第一次征集和新生通知入口可定位；历年分数与招生动态列表本轮多次TLS连接失败，不能据此判断未发布。搜索及已访问首页未取得2026广西专业实际最低分，历史审计中的2025年份结论未冒充本轮成功读表。'),
 '10603': ('current-year-query-empty', '当前菜单广西最新2025。按页面实际API的JSON字段查询2026广西物理、历史和全部科类，类别全部，3次均成功空列表；对应2025对照有记录。新旧官网入口均核查，不能将部分入口403或404等同于接口无数据。'),
 '11607': ('year-unavailable', '从旧首页图像导航进入真实招生首页sy.htm，再进入历年分数lqxx.htm、招生公告及下载中心。广西区内各专业录取表最新2025；下载栏目未取得2026专业录取结果。'),
 '10608': ('year-unavailable', '官网首页和历年分数目录最新普通、国家专项、地方专项、民族班、公费师范及合作类型专业分均为2025；2026录取查询为个人结果入口，未使用考生身份数据。未取得2026广西专业实际分。'),
 '11548': ('source-conflict', '已解析新版官网公开栏目API：历年分数18篇、1页，最新标题2025；招生动态包含2026录取收官公告，正文只有总招生规模，无广西各专业最低分。沿官网链接进入招就网历年系统，配置标题和菜单只2025，但显式查询2026广西本科物理/历史返回117条逐行year=2026专业统计，2025对照108条。年份标题与接口冲突，全部先留待核，不能直接比较；不把2025正投说明套给2026。'),
 '10604': ('year-unavailable', '官网招生分数目录和首页最新广西资料标题明确为“广西2026年招生计划及2025年各专业录取分数”。已核对该混合年文章的表头；不能把其2025分数按2026计划年导入。'),
 '14127': ('filing-only', '官网2026两科首批专业分页面明确为投档最低分，本站原有81条保持原口径。本轮另发现第一次征集专业投档表41条（物理20、历史21），独立输出投档候选；仍未取得实际专业录取最低分。'),
 '10248': ('year-unavailable', '已重读官网首页及历年分数公开newsList栏目；返回12篇文章，数据年2014至2025，无2026。最初对POST接口误作GET返回404，已按原前端JSON请求纠正，不用404证明缺年。'),
 '19248': ('year-unavailable', '独立院校代码19248核查阳光招生历年分数列表、最新文章及医学院信息公开招生栏目，最新普通批次结果均标明2025。未与交大本部代码混用，未取得2026广西专业实际分。'),
 '10007': ('current-year-query-empty', '公开广西菜单最新2025；2026物理/历史统招缺年探查均state=1且学校/专业列表空。2025物理对照非空，但其sszygradeList的“物理组”是组汇总，不能因位于专业列表便作为单专业结果。另查官网首页公告。'),
 '10006': ('current-year-query-empty', '公开广西菜单最新2025；按其已列类别作2026物理/历史及统招、合作、国家/高校专项等5组缺年探查，均成功空列表；2025对照学校汇总非空。另核2026本科录取信息公告，其历年分数仍指向同一查询，不提供新的本年专业统计。'),
 '10213': ('year-unavailable', '官方分数页仅2025/2024；显式请求广西2026后返回页面filter-info仍为2025广西，属于回退旧年，不能当作2026。另核招生首页及官方检索结果，强基入围/综合成绩未混入普通分数。'),
 '10558': ('current-year-query-empty', '公开广西菜单最新2025；根据菜单普通、国家专项、高校专项、民族班等已列两科类别，8组2026缺年探查均成功空列表；2025物理普通对照有实际专业记录。另查官网新闻，所见综合评价公告为广东或第二学位，不能补广西普通专业分。'),
 '10284': ('current-year-query-empty', '公开广西菜单2025/2024/2023；2026物理、历史普通批次2次明确缺年探查均state=1双列表空。2025对照院校汇总非空、专业列表空；另查官网首页和官方定向检索，未取得本年广西专业分。'),
 '10358': ('current-year-query-empty', '广西菜单为2025/2024；2026物理普通本科缺年探查成功双列表空，2025对照有专业记录，说明接口可返回专业统计。前端展示配置与接口隐藏记录不能混同；2026强基公告是综合成绩，已排除。另查招生首页和信息公开栏目。'),
 '10487': ('year-unavailable', '分省分专业分数页面实际嵌入年份只有2025、2024、2023；另查录取情况、通知公告和官网首页，未取得2026广西专业实际最低分。2026计划、强基和其他申请类别结果均不能替代。'),
 '10002': ('current-year-query-empty', '公开广西菜单只有2025；按其物理/历史本科一批、国家专项、新路引航等6组菜单类别作2026缺年探查，均成功双列表空；2025对照有旧年专业记录。另查官网首页和官方定向检索，未取得本年广西专业最低分。'),
}

sources = []
for m in manifest:
    if not m.get('rawFile'): continue
    raw = ROOT/m['rawFile']
    assert raw.exists() and hashlib.sha256(raw.read_bytes()).hexdigest() == m['sha256'], m['id']
    source = {'id':m['id'],'title':m['school']+'2026广西专业录取分核查证据：'+m['id'],
              'publisher':m['school'],'sourceType':'official','year':2026,'auditOnly':True,
              'url':m['url'],'publishedAt':None,'accessedAt':m['finishedAt'],
              'sha256':m['sha256'],'httpStatus':m.get('httpStatus'),'recordCount':0,
              'method':'读取官方公开页面或按其前端声明字段查询；统计年、省份和成绩口径独立核对。原始网页、API和会话资料不公开。'}
    for k in ['request','requestEncoding','entryUrl','responseSha256','redactedFields','missingYearProbe']:
        if k in m: source[k]=m[k]
    if m.get('error'):source['accessError']=m['error']
    sources.append(source)

filing=[]
for suffix,track,expected in [('recruit-physics','物理',20),('recruit-history','历史',21)]:
    sid='p100a-14127-'+suffix
    text=(ROOT/byid[sid]['rawFile']).read_text()
    assert '2026年广西高考普通批'+track+'类第一次征集最低投档分数线' in text
    rows=[]
    for i,tr in enumerate(re.findall(r'<tr\b[^>]*>(.*?)</tr>',text,re.S|re.I),1):
        values=[re.sub(r'\s+','',plain(cell)) for cell in re.findall(r'<t[dh]\b[^>]*>(.*?)</t[dh]>',tr,re.S|re.I)]
        if i==1:
            assert values==['专业代码','专业名称','批次名称','科类','计划类别','投档最低分']
            continue
        assert len(values)==6 and values[3]==track+'类' and re.fullmatch(r'\d{6}',values[0])
        rows.append({'id':sid+'-row'+str(i),'year':2026,'province':'广西',
          'school':'广西工程职业学院','schoolCode':'14127','track':track,
          'batch':values[2],'group':None,'major':values[1],'majorCode':None,
          'sourceMajorCode':values[0],'score':int(values[5]),'scoreType':'专业投档最低分',
          'plannedCount':None,'admittedCount':None,'rank':None,'rankType':None,
          'requiredSubjects':[],'subjectRule':'unknown','requirementText':None,
          'sourceId':sid,'sourceRow':i,'round':'第一次征集','admissionType':values[4],
          'sourceCategory':values[4],'reviewedAt':review_date,'evidenceStatus':'verified',
          'scoreComparable':True,'scoreEvidenceGaps':[],'conflictFields':[],
          'note':'原文为第一次征集各专业最低投档分；不能替代实际专业录取最低分。六位代码保留为来源专业代码，广西志愿填报码未核定。',
          'fieldSources':{'year':{'sourceId':sid,'sourceField':'文章标题2026年'},
            'province':{'sourceId':sid,'sourceField':'文章标题广西'},
            'round':{'sourceId':sid,'sourceField':'文章标题第一次征集'},
            'major':{'sourceId':sid,'sourceRow':i,'sourceField':'专业名称'},
            'score':{'sourceId':sid,'sourceRow':i,'sourceField':'投档最低分'},
            'batch':{'sourceId':sid,'sourceRow':i,'sourceField':'批次名称'},
            'track':{'sourceId':sid,'sourceRow':i,'sourceField':'科类'},
            'sourceMajorCode':{'sourceId':sid,'sourceRow':i,'sourceField':'专业代码'}}})
    assert len(rows)==expected
    filing.extend(rows)
    next(s for s in sources if s['id']==sid).update(auditOnly=False,recordCount=len(rows),publishedAt='2026-08-10')

sid='p100a-10602-quality2026'
content=plain((ROOT/byid[sid]['rawFile']).read_text())
content=re.sub(r'\s+','',content)
for track,start,end in [('物理','物理类：出档2637人','历史类：出档1187人'),('历史','历史类：出档1187人','今年我校生源质量实现')]:
    section=content.split(start,1)[1].split(end,1)[0].split('其中，',1)[1]
    pairs=re.findall(r'([^；。]+?)投档最高分(\d+)分，最低分(\d+)分',section)
    assert len(pairs)==7
    for i,(major,maxscore,minscore) in enumerate(pairs,1):
        conflict=major=='政治与行政学'
        reason='原文专业名称“政治与行政学”与常见规范名称存在差异，保留原称，待学校或完整计划核定。'
        filing.append({'id':sid+'-'+track+'-'+str(i),'year':2026,'province':'广西',
          'school':'广西师范大学','schoolCode':'10602','track':track,'batch':'本科普通批',
          'group':None,'major':major,'majorCode':None,'score':int(minscore),'maxScore':int(maxscore),
          'scoreType':'专业投档最低分','plannedCount':None,'admittedCount':None,'rank':None,'rankType':None,
          'requiredSubjects':[],'subjectRule':'unknown','requirementText':None,
          'sourceId':sid,'sourceRow':i,'round':'录取汇总（轮次未分）','admissionType':'普通类',
          'sourceCategory':'普通类','reviewedAt':review_date,
          'evidenceStatus':'source-conflict' if conflict else 'verified','scoreComparable':not conflict,
          'scoreEvidenceGaps':[reason] if conflict else [],'conflictFields':['major'] if conflict else [],
          'note':'学校生源质量公告称专业投档最高、最低分，未称实际专业录取最低分；没有独立轮次和广西组码证据。'+(reason if conflict else ''),
          'sourceLocator':track+'类区内普通批段落，第'+str(i)+'项',
          'fieldSources':{'year':{'sourceId':sid,'sourceField':'标题2026年'},
            'province':{'sourceId':sid,'sourceField':'广西区内普通批'},
            'batch':{'sourceId':sid,'sourceField':'广西区内普通批'},
            'track':{'sourceId':sid,'sourceField':track+'类段落'},
            'major':{'sourceId':sid,'sourceField':major+'投档最高分'},
            'score':{'sourceId':sid,'sourceField':major+'投档最高分'+maxscore+'分，最低分'+minscore+'分'},
            'maxScore':{'sourceId':sid,'sourceField':'投档最高分'}}})
next(s for s in sources if s['id']==sid).update(auditOnly=False,recordCount=14,publishedAt='2026-08-14')
assert len(filing)==55 and len({r['id'] for r in filing})==55
write('supplementary-major-filing.json',filing)

majors=[]
config_id='p100a-11548-history-config-post'
cfg=read(byid[config_id]['rawFile'])['data']
assert cfg['title']=='广西财经学院2025年招生录取分数'
assert [x['code'] for x in cfg['years']]==['2025']
year_conflict='官方页面标题和年份菜单仍标2025，公开接口逐行返回2026；统计年度存在来源冲突，待学校确认，暂不参与分数比较。'
for track,expected in [('物理',71),('历史',46)]:
    sid='p100a-11548-history-2026-'+track+'类'
    response=read(byid[sid]['rawFile'])
    assert response['code']==0
    data=response['data']
    columns={x['dataIndex']:x['title'] for x in data['major_columns']}
    assert columns['min_score']=='最低分' and columns['lowest_position']=='最低分位次'
    assert columns['major']=='专业名称' and columns['max_score']=='最高分' and columns['average']=='平均分'
    assert len(data['major_data_source'])==expected
    for i,r in enumerate(data['major_data_source'],1):
        assert r['year']=='2026' and r['province']=='45' and r['province_name']=='广西'
        assert r['level']=='本科' and r['subjects']==track+'类' and r['major_group']==''
        assert float(r['min_score'])<=float(r['average'])<=float(r['max_score'])
        sourceids=[sid,config_id,'p100a-11548-score-list','p100a-11548-history-component']
        majors.append({'id':sid+'-row'+str(i),'year':2026,'province':'广西',
            'schoolCode':'11548','school':'广西财经学院','track':track,'sourceTrack':r['subjects'],
            'batch':r['batch'],'sourceBatch':r['batch'],'round':'录取汇总（轮次未分）',
            'group':None,'major':r['major'],'majorCode':None,
            'score':float(r['min_score']),'scoreType':'专业录取最低分',
            'rank':int(r['lowest_position']),'rankType':'专业最低分位次',
            'sourceId':sid,'sourceIds':sourceids,'sourceRow':i,
            'sourceTable':'major_data_source（不含dataSource类别汇总）',
            'sourceMaximumScore':float(r['max_score']),'sourceAverageScore':float(r['average']),
            'sourceScoreHeader':columns['min_score'],'sourceRankHeader':columns['lowest_position'],
            'reviewedAt':review_date,'evidenceStatus':'source-conflict','scoreComparable':False,
            'scoreEvidenceGaps':[year_conflict],'conflictFields':['year','sourceTitle'],
            'scoreBasis':'公开历年录取统计的专业最低分；来源统计年度冲突待核',
            'admissionType':r['enroll_type'],'sourceCategory':r['enroll_type'],
            'requiredSubjects':[],'subjectRule':'unknown','requirementText':r['xkyq'],
            'sourceYear':r['year'],'sourceTitleYear':2025,
            'fieldSourceIds':{**{k:[sid] for k in ['year','province','track','major','score','rank','batch','admissionType','sourceMaximumScore','sourceAverageScore']},
                'scoreComparable':[sid,config_id],'conflictFields':[sid,config_id]},
            'fieldSources':{'year':{'sourceId':sid,'sourceField':'year','sourceRow':i},
                'score':{'sourceId':sid,'sourceField':'major_data_source.min_score','sourceRow':i},
                'rank':{'sourceId':sid,'sourceField':'major_data_source.lowest_position','sourceRow':i},
                'sourceTitleYear':{'sourceId':config_id,'sourceField':'title和years'}},
            'note':year_conflict+' 保存接口原专业名称及类别；2025配置中的正投、不含征集说明不外推本年，轮次和省编组码保持待核。'})
    next(s for s in sources if s['id']==sid).update(auditOnly=False,recordCount=expected,
        sourceDataYear=2026,sourceTitleYear=2025,sourceStatus='year-conflict',
        method='官网历年栏目链接的公开查询API；逐行year=2026、province=45、本科及科类，major_data_source为专业统计，dataSource类别汇总排除。配置标题和年份菜单2025与接口2026冲突，全部标记待核不比较。')
assert len(majors)==117

observations=[];audits=[]
for t in targets:
    code=t['schoolCode'];rows=[m for m in manifest if m['schoolCode']==code]
    successful=[m for m in rows if m.get('httpStatus')==200 and not m.get('error')]
    assert successful,code
    status,note=notes[code]
    sourceids=[s['id'] for s in sources if s['id'].startswith('p100a-'+code+'-')]
    queryresults=[]
    for row in rows:
        if 'request' not in row or row.get('httpStatus')!=200 or not row.get('rawFile'):continue
        try:
            data=read(row['rawFile'])
            if isinstance(data,str):data=json.loads(data)
        except (ValueError,TypeError):continue
        result={'sourceId':row['id'],'request':row['request'],'httpStatus':200}
        if isinstance(data,list): result['responseRowCount']=len(data)
        if isinstance(data,dict):
            result.update({k:data[k] for k in ['state','code','success'] if k in data})
            d=data.get('data')
            if isinstance(d,dict):
                for key in ['sszygradeList','zsSsgradeList','dataSource','major_data_source','content']:
                    if isinstance(d.get(key),list):result[key+'Count']=len(d[key])
            if isinstance(data.get('list'),list):result['listCount']=len(data['list'])
        queryresults.append(result)
    evidence_gaps=['2026广西分专业实际最低录取分未取得','完整本年专业分目录和轮次未核定','专业组、最低位次及完整计划匹配仍缺证据']
    obs={'taskId':t['taskId'],'schoolCode':code,'school':t['school'],
         'startedAt':min(m['startedAt'] for m in rows),'finishedAt':max(m['finishedAt'] for m in rows),
         'reviewedAt':review_date,'status':status,'actualMajorScoreRowsAdded':0,
         'pendingMajorScoreRows':sum(r['schoolCode']==code for r in majors),
         'supplementaryFilingRows':sum(r['schoolCode']==code for r in filing),
         'requestsAttempted':len(rows),'http200Responses':len(successful),
         'queryResults':queryresults,'note':note,'remainingGaps':evidence_gaps,
         'sourceIds':sourceids,'failureEvidence':[{'url':m['url'],'httpStatus':m.get('httpStatus'),'error':m.get('error')} for m in rows if m.get('error')],
         'scope':'本轮明确列出的官方目录、网页、前端配置和查询条件；不是全站及公众号穷尽搜索结论。',
         'sourceEvidence':[{'sourceId':m['id'],'sha256':m['sha256'],'rawFile':m.get('rawFile'),'startedAt':m['startedAt'],'finishedAt':m['finishedAt']} for m in rows]}
    observations.append(obs)
    audits.append({'id':'major-score-review-p100a-'+code,'year':2026,'province':'广西',
          'schoolCode':code,'school':t['school'],'auditKind':'major-scores',
          'title':'100校试运行A组：2026广西专业分补缺复核','checkedAt':review_date,
          'status':status,'recordCount':sum(r['schoolCode']==code for r in majors),'sourceIds':sourceids,
          'checkedUrls':list(dict.fromkeys(m['url'] for m in rows)),
          'note':note,'scope':obs['scope'],'evidenceGaps':evidence_gaps,
          'queryResults':queryresults,'supplementaryFilingRows':obs['supplementaryFilingRows']})

write('major-cutoffs-upsert.json',majors)
write('sources.json',sources)
write('school-audit-notes.json',audits)
write('observations.json',observations)
summary={'reviewedAt':review_date,'targetSchools':20,'reviewedSchools':len(audits),
         'actualMajorScoreRowsAdded':0,'supplementaryFilingRows':len(filing),
         'pendingMajorScoreRows':len(majors),
         'supplementaryFilingComparableRows':sum(r['scoreComparable'] for r in filing),
         'supplementaryFilingConflictRows':sum(not r['scoreComparable'] for r in filing),
         'sources':len(sources),'requestsAttempted':len(manifest),
         'statusCounts':dict(collections.Counter(a['status'] for a in audits))}
write('summary.json',summary)
print(json.dumps(summary,ensure_ascii=False))
