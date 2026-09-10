"""Build this bounded batch from archived public university tables, never filing cutoffs."""
import json,hashlib,datetime,re
from pathlib import Path
from collections import Counter
from parse_tables import parse
import pdfplumber
R=Path(__file__).resolve().parent
RAW=R/'raw'
CHECKED=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
PREFIX='major-c-20260911-'
def dump(name,data):
    (R/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
def sid(key):return PREFIX+key
descriptions={
 'juwp-gx-6212':('江西水利电力大学2026年广西本科批录取公告','江西水利电力大学','2026-07-27','2026广西本科批；第二张表逐专业。正文署期2026-07-23，网页发布时间2026-07-27。'),
 'juwp-gx-6502':('江西水利电力大学2026年广西高职高专提前批定向类录取公告','江西水利电力大学','2026-08-04','2026广西高职高专提前批定向类；第二张表逐专业。正文署期2026-08-03。'),
 'juwp-charter':('江西水利电力大学2026年普通高考招生章程','江西水利电力大学',None,'第2、14、15、19、20、26—28条支持学校身份、分数加分口径与报考条件。'),
 'sctu-gx-2267':('四川旅游学院2026年在广西普通本科批次录取结束','四川旅游学院','2026-07-25','2026广西普通本科物理与历史；原表直接列专业组及专业实录人数和最高最低平均分。'),
 'sctu-charter':('四川旅游学院2026年普通高等教育本专科招生章程','四川旅游学院','2026-05-20','第11—13、15—16条支持录取成绩口径与英语、专业志愿、体检条件。'),
 'sxdt-admission':('山西大同大学2026年本科招生录取进展（四）','山西大同大学','2026-07-25','2026广西本科录取完成；只取原表广西8个专业行，未取其他省份。'),
 'sxdt-charter':('山西大同大学2026年本科招生章程','山西大同大学','2026-06-01','第5条学校代码；第19、22—26条支持普通专业录取口径及报考要求。'),
 'fjbu-gx':('福建商学院2026年广西壮族自治区本科专业招生录取情况表（公告页）','福建商学院','2026-07-20','公告页直接嵌入本批次使用的2页PDF。'),
 'fjbu-pdf':('福建商学院2026年本科专业招生录取情况表（广西-143，2页PDF）','福建商学院','2026-07-20','PDF序号1—63逐行提取；两页均经渲染视觉核对，科类组别是选科文字，未公布广西3位专业组码。'),
 'fjbu-charter':('福建商学院2026年普通高考招生章程','福建商学院','2026-05-14','第5、16—21条支持学校代码、教学外语、体检与专业成绩口径。'),
 'ccut-entry':('长春工业大学历年分数公开查询入口','长春工业大学',None,'默认结果是2026吉林，不是广西。'),
 'ccut-provinces':('长春工业大学历年分数省份选项','长春工业大学',None,'公开前端省份下拉选项含广西。'),
 'ccut-gx-years':('长春工业大学广西本科历年分数年份选项','长春工业大学',None,'公开接口parentCode=sf,cc、parentValue=广西,本科返回年份2025—2020，不含2026。'),
 'ccut-gx-tracks':('长春工业大学2026广西本科科类查询结果','长春工业大学',None,'2026广西本科查询无科类选项。'),
 'ccut-gx-2026':('长春工业大学2026广西本科分数查询结果','长春工业大学',None,'公开表单查询2026广西本科，无结果。'),
 'qjnu-status':('曲靖师范学院2026年录取进度','曲靖师范学院','2026-08-06','广西普通类显示7.21录取结束，但对应公告标题只是文字，并无可点专业分表。'),
 'qjnu-history':('曲靖师范学院历年录取分数栏目','曲靖师范学院',None,'栏目最新全日制本科分省分专业统计为2025。'),
 'sicnu-notices':('四川师范大学招生信息最新公告入口（访问受限）','四川师范大学',None,'本轮HTTPS返回WAF安全助手，没有可读取的公告正文；HTTP同样。搜索仅作公告存在性线索，未导入摘要分数。'),
 'hzu-gx':('湖州学院2026年广西普通类录取快讯','湖州学院','2026-07-25','只公布首轮物理类、历史类整体最高最低分，未发布单专业实录最低分。'),
}
sources=[]
for key,(title,publisher,date,note) in descriptions.items():
    m=json.loads((RAW/(key+'.meta.json')).read_text())
    sources.append({'id':sid(key),'title':title,'url':m['url'],'publisher':publisher,'publishedAt':date,'accessedAt':m['checkedAt'],'sha256':m.get('rawSha256'),'archiveSha256':m.get('archiveSha256'),'archiveFile':'raw/'+m.get('archiveFile',''),'requestMethod':'POST' if m.get('request') else 'GET','query':m.get('request'),'year':2026,'province':'广西','note':note,'method':'官方公开网页或附件直接读取；归档仅供本地复核，不发布完整网页及访问会话。'})
for s in sources:
    if any(s['id']==sid(k) for k in ['ccut-entry','ccut-provinces','qjnu-history','sicnu-notices']):
        s['queryTarget']={'year':2026,'province':'广西'};s['year']=None;s['province']=None
# Reuse existing official province filing table solely for school-code/batch identity.
site=R.parents[2]/'guangxi-admissions-2026/site/data'
existing_sources=json.loads((site/'sources.json').read_text())
for key in ['gxeea-2026-33106','gxeea-2026-33107']:
    sources.append(next(s for s in existing_sources if s['id']==key))
rows=[];evidence=[];excluded=[]
schools={'11319':'江西水利电力大学','11552':'四川旅游学院','10120':'山西大同大学','11313':'福建商学院'}
def base(code,track,major,key,table,rownum,sourcecells,score,maximum=None,average=None,count=None,group=None,admission='普通类',batch='本科普通批'):
    source=sid(key);identity_source='gxeea-2026-33106' if track=='历史' else 'gxeea-2026-33107'
    r={'id':f'major-2026-0911c-{code}-{key}-{table}-{rownum}','year':2026,'province':'广西','schoolCode':code,'school':schools[code],'track':track,'batch':batch,'round':'录取汇总（轮次未分）','group':group,'major':major,'score':float(score),'scoreType':'专业录取最低分','rank':None,'sourceMaximumScore':float(maximum) if maximum is not None else None,'sourceAverageScore':float(average) if average is not None else None,'admittedCount':int(count) if count is not None else None,'admissionType':admission,'sourceId':source,'sourceIds':[source],'sourceTable':table,'sourceRow':rownum,'reviewedAt':CHECKED,'evidenceStatus':'verified','scoreComparable':True,'scoreBasis':'750分制普通高考总分（含按政策认可的加分）','scoreScaleMaximum':750,'scoreEvidenceGaps':[],'conflictFields':[],'requiredSubjects':[],'subjectRule':'unknown','requirementText':None,'note':'原公告未区分首轮与征集，保存为录取汇总；未用录取人数更新招生计划。','fieldSourceIds':{k:[source] for k in ['year','province','school','track','major','score','sourceMaximumScore','sourceAverageScore','admittedCount','admissionType','round']}}
    r['fieldSourceIds'].update(schoolCode=[identity_source],batch=[source,identity_source])
    if group:r['fieldSourceIds']['group']=[source]
    if r['score'].is_integer():r['score']=int(r['score'])
    evidence.append({'id':r['id'],'sourceId':source,'sourceTable':table,'sourceRow':rownum,'cells':sourcecells})
    rows.append(r);return r
def charter(r,key,note):
    s=sid(key);r['sourceIds'].append(s);r['fieldSourceIds']['scoreBasis']=[s];r['fieldSourceIds']['note']=[r['sourceId'],s];r['note']+=' '+note
def subjects(r,raw):
    r['sourceTrack']=raw
    if '化学' in raw:r.update(requiredSubjects=['化学'],subjectRule='all',requirementText='首选物理，再选化学')
    elif '生物' in raw:r.update(requiredSubjects=['生物'],subjectRule='all',requirementText='首选物理，再选生物')
    elif '不限' in raw:r.update(subjectRule='none',requirementText=f'首选{r["track"]}，再选不限')
    if r['subjectRule']!='unknown':r['fieldSourceIds']['requiredSubjects']=[r['sourceId']];r['fieldSourceIds']['requirementText']=[r['sourceId']]
for key,table,batch in [('juwp-gx-6212',2,'本科普通批'),('juwp-gx-6502',2,'高职高专提前批定向类')]:
    ts=parse(RAW/(key+'.html'));body=ts[1]['rows'];assert body[0][1]=='专业名称'
    for num,c in enumerate(body[1:],2):
        raw,major,n,control,maximum,minimum,avg,rank=c
        major=major.replace(' ','')
        admission='定向培养军士' if '6502' in key else ('中外合作办学' if '中外合作' in major else '普通类')
        r=base('11319','历史' if '历史' in raw else '物理',major,key,table,num,c,minimum,maximum,avg,n,admission=admission,batch=batch)
        r.update(sourceMinimumRank=int(rank),rankComparable=False,rankEvidenceGaps=['高校原表本科位次跨行次序有不一致；本校位次暂不参与比较'])
        r['fieldSourceIds']['sourceMinimumRank']=[r['sourceId']]
        subjects(r,raw)
        note='学校认可经教育部批准的省级优惠加分政策。原表位次跨行次序存在不一致（如物化水土保持544分列38324、测绘543分列37700），因此本校位次仅保留为原始值，不用于比较；分数本身上下界检查通过。'
        if major=='英语':note+=' 英语专业仅招高考英语语种考生。';r['foreignLanguageRequirement']={'language':'英语','minimumScore':None,'sourceIds':[sid('juwp-charter')]}
        if admission=='定向培养军士':note+=' 属定向培养军士，须符合2026定向培养军士报考、政审、体检和录取要求，学费8000元/学年；原表未单列性别或更细资格。'
        if admission=='中外合作办学':note+=' 土木工程为与荷兰萨克逊应用科技大学合作项目，学费25000元/学年；中外合作专业不得转入普通专业。赴荷兰学习为满足条件后的申请选项，非本表普通分数录取附加要求。'
        if major in ['地质工程','园林']:note+=' 章程提示色弱考生谨慎报考本专业。'
        if major=='计算机科学与技术':note+=' 章程提示不能准确识别显示器红黄绿蓝紫颜色数码字母者谨慎报考。'
        charter(r,'juwp-charter',note)
    for num,c in enumerate(ts[0]['rows'][1:],2):excluded.append({'sourceId':sid(key),'sourceTable':1,'sourceRow':num,'cells':c,'reason':'科类/批次整体汇总，不是单专业录取分'})
for num,c in enumerate(parse(RAW/'sctu-gx-2267.html')[0]['rows'][1:],2):
    province,raw,g,major,planned,admitted,maximum,minimum,avg=c;assert province=='广西'
    r=base('11552','历史' if '历史' in raw else '物理',major,'sctu-gx-2267',1,num,c,minimum,maximum,avg,admitted,group=g,admission='中外合作办学' if '中外合作' in major else '普通类')
    r['sourceTrack']=raw
    note='章程以政策加分或降分后投档成绩作为录取和安排专业依据。'
    if '中外合作' in major:
        note+=' 与法国EPF工程师学院合作项目：英语单科至少85分；仅录取填报本专业志愿者，入学后不得转入其他专业。'
        r['foreignLanguageRequirement']={'language':'英语','minimumScore':85,'sourceIds':[sid('sctu-charter')]}
    if major=='烹饪与营养教育':note+=' 要求裸眼或矫正视力4.8及以上且无色盲。'
    charter(r,'sctu-charter',note)
for num,c in enumerate(parse(RAW/'sxdt-admission.html')[0]['rows'][1:],2):
    if c[0]!='广西':continue
    province,raw,major,n,maximum,minimum=c
    r=base('10120','历史' if '历史' in raw else '物理',major,'sxdt-admission',1,num,c,minimum,maximum,count=n)
    r['sourceTrack']=raw
    charter(r,'sxdt-charter','章程按投档成绩从高到低安排普通专业，认可省级政策加分或降分征集规定。原公告未列选科要求和专业组码，不能据专业名称推断。')
with pdfplumber.open(RAW/'fjbu-pdf.pdf') as pdf:
    seq=[]
    for pi,page in enumerate(pdf.pages,1):
        ts=page.extract_tables();assert len(ts)==1
        for c in ts[0][1:]:
            num,major,raw,planned,admitted,maximum,minimum,avg,control,delta=c;seq.append(int(num))
            r=base('11313','历史' if '历史' in raw else '物理',major,'fjbu-pdf',pi,int(num),c,minimum,maximum,avg,admitted)
            r['sourcePage']=pi;r['sourceIds'].append(sid('fjbu-gx'));subjects(r,raw)
            note='学校以政策加分后的投档成绩调配专业；原表科类（组别）为选科组合文字，未提供广西专业组码。日语专业安排日语课堂教学，其余专业公共外语为英语。'
            if major=='零售业管理' and r['track']=='历史':note+=' 原表计划2人、实际录取1人，最高最低平均均491；保留实际分数，不视为零录取，也不推定后续征集分数。'
            charter(r,'fjbu-charter',note)
    assert seq==list(range(1,64))
assert Counter(r['schoolCode'] for r in rows)=={'11319':18,'11552':5,'10120':8,'11313':63}
for r in rows:
    lo,hi,avg=r['score'],r['sourceMaximumScore'],r['sourceAverageScore']
    assert r['admittedCount']>0 and 0<=lo<=hi<=750
    assert avg is None or lo<=avg<=hi
    if r['admittedCount']==1:assert lo==hi and (avg is None or avg==lo)
    assert not any(k in r for k in ['plannedCount','planCount','maxScore','averageScore'])
notes=[]
def audit(code,school,status,keys,note,count=0,gaps=None):
    ss=[next(x for x in sources if x['id']==sid(k)) for k in keys]
    notes.append({'id':'major-score-review-20260911c-'+code,'auditKind':'major-scores','title':'2026广西专业录取分核查','year':2026,'province':'广西','schoolCode':code,'school':school,'status':status,'checkedAt':CHECKED,'entryUrl':ss[0]['url'],'checkedUrls':[s['url'] for s in ss],'sourceIds':[s['id'] for s in ss],'importedRecordCount':count,'note':note,'evidenceGaps':gaps or []})
for code,keys in {'11319':['juwp-gx-6212','juwp-gx-6502','juwp-charter'],'11552':['sctu-gx-2267','sctu-charter'],'10120':['sxdt-admission','sxdt-charter'],'11313':['fjbu-gx','fjbu-pdf','fjbu-charter']}.items():
    n=sum(r['schoolCode']==code for r in rows)
    audit(code,schools[code],'collected',keys,f'本轮采集{n}条2026广西单专业实际录取最低分，所有数值逐行对应官方原表，未用学校或专业组投档线代替专业录取分。完整覆盖列明原表的广西普通高考专业行；未证明覆盖学校全年全部录取轮次。'+('其中2条为定向培养军士，单独保留资格类别；原表位次跨行次序有不一致，rank全部留空、原值放sourceMinimumRank供核查，不参与位次比较。' if code=='11319' else ''),n,['原公告未明确区分首轮与征集；不冒称首轮',*(['专业组码未在该分数表公布'] if code!='11552' else []),*(['山西大同原表未提供平均分、位次和专业选科要求'] if code=='10120' else []),*(['原表最低分位次跨行次序不一致，位次比较停用'] if code=='11319' else [])])
audit('10190','长春工业大学','entry-only-year-gap',['ccut-entry','ccut-provinces','ccut-gx-years','ccut-gx-tracks','ccut-gx-2026'],'已按公开JS的省份/层次/年份级联接口核查：广西本科年份选项只含2025—2020；2026广西科类返回空，直接2026广西本科表单也无结果。默认页的2026吉林专业数据未入库。',gaps=['2026广西专业录取分未公开在本轮所查查询条件下'])
audit('10684','曲靖师范学院','entry-only-year-gap',['qjnu-status','qjnu-history'],'2026进度页显示广西普通类7月21日录取结束，公告标题为无链接文本；历年分数栏目最新全日制本科分省分专业表为2025。未将录取进度或2025统计作2026专业分。',gaps=['2026广西单专业录取统计未取得'])
audit('10636','四川师范大学','unavailable',['sicnu-notices'],'公开招生首页及公告栏目本轮返回WAF安全助手环境检查页；HTTPS、HTTP均未取得正文，当前无可用浏览器。搜索结果显示2026广西普通本科录取结束公告线索，但未以摘要拼接数据。',gaps=['2026广西专业原表访问受限'])
audit('13287','湖州学院','group-only',['hzu-gx'],'官方2026广西普通录取快讯仅给出物理/历史科类整体最高最低分，并注明正投不含征集；无单专业实际最低分，未导入该汇总数。',gaps=['单专业录取最低分缺失'])
for name,data in [('major-cutoffs-upsert.json',rows),('sources.json',sources),('school-audit-notes.json',notes),('evidence-rows.json',evidence),('excluded-records.json',excluded)]:dump(name,data)
report={'checkedAt':CHECKED,'recordCount':len(rows),'schools':dict(Counter(r['school'] for r in rows)),'tracks':dict(Counter(r['track'] for r in rows)),'admissionTypes':dict(Counter(r['admissionType'] for r in rows)),'admittedPeople':sum(r['admittedCount'] for r in rows),'directGroupCodeRows':sum(bool(r['group']) for r in rows),'unknownRoundRows':len(rows),'nonComparableRows':sum(not r['scoreComparable'] for r in rows),'sources':len(sources),'auditSchools':len(notes),'excludedAggregateRows':len(excluded),'pdfVisualReview':'2页已核对，序号1—63连续，表头、科类、最低最高平均、人数均对齐','sourceMinimumMaximumAverageChecks':'passed','oneAdmitChecks':'passed','noPlanMutationFields':'passed','noExisting17SchoolsOrTop20':'must be verified against current importer/baseline before delivery'}
dump('QA.json',report)
print(json.dumps(report,ensure_ascii=False,indent=2))
