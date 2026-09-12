"""Build separate major-score scope reviews and cross-scope observations from frozen local evidence."""
from pathlib import Path
import json,hashlib,re,datetime,argparse
from collections import Counter
from build import ROOT,RAW,OUT,TARGETS,plans,sources,src,tables,NOW
SCORE=ROOT/'score-package';SCORE.mkdir(exist_ok=True)
args=argparse.ArgumentParser();args.add_argument('--repo',type=Path,required=True)
REPO=args.parse_args().repo.resolve()
old_scores=json.loads((REPO/'site/data/major-cutoffs.json').read_text())
score_files={
 '10052':['10052-entry-2.html','10052-scores-current.json'],
 '10718':['10718-score-types.json','10718-scores-current-2.json','10718-scores-current-3.json','10718-scores-original.pdf'],
 '10025':['10025-scores-current.json'],
 '10043':['10043-entry-1.html','10043-entry-2.html'],
 '10633':['10633-entry-4.html','10633-scores-original.png'],
 '10637':['10637-entry-1.html'],
 '11319':['11319-entry-1.html','11319-entry-3.html'],
 '16302':['16302-entry-2.html'],
 '11552':['11552-entry-2.html'],
 '10120':['10120-entry-1.html'],
 '11313':['11313-entry-2.html','11313-score-original.pdf'],
 '11765':['11765-entry-3.html'],
 '11510':['11510-entry-1.html','11510-score-early.html','11510-charter.html'],
 '12789':['12789-entry-2.html'],
 '12864':['12864-entry-1.html','12864-score-original.png'],
 '12758':['12758-entry-2.html'],
 '14008':['14008-entry-1.html']}
for c,pattern in [('10269','10269-scorecheck-*.json'),('10036','10036-scorecheck-*.json'),('10423','10423-scorecheck-valid-*.json')]:
    score_files[c]=[f.name for f in sorted(RAW.glob(pattern)) if '.meta.' not in f.name]
for c,files in score_files.items():
    for n in files:src(n,'major-score-scope-review')

records=[]
sid=src('11510-score-early.html','major-score-data');charter=src('11510-charter.html','score-basis-and-restrictions')
rows=next(t['rows'] for t in tables('11510-score-early.html') if t['rows'][0][0]=='省份')
for i,r in enumerate(rows[1:],2):
    assert r[:5]==['广西','本科提前批','非定向','4','物理']
    minimum,maximum,average=int(r[10]),int(r[9]),float(r[11])
    assert minimum<=average<=maximum and int(r[6])==int(r[7])==2
    records.append({'id':'major-2026-pilot-b-sdjtu-early-'+str(i),'year':2026,'province':'广西',
        'schoolCode':'11510','school':'山东交通学院','track':'物理','sourceTrack':'物理',
        'batch':'本科提前批','group':None,'major':r[5],'majorCode':None,'score':minimum,
        'sourceMaximumScore':maximum,'sourceAverageScore':average,'scoreType':'专业录取最低分',
        'plannedCount':int(r[6]),'admittedCount':int(r[7]),'sourceControlScore':int(r[8]),
        'round':'录取汇总（轮次未分）','admissionType':'航海类','sourceCategory':'非定向',
        'scoreBasis':'普通高考总分（学校章程认可省级加分投档政策；原表未另列加分处理）',
        'scoreScaleMaximum':750,'sourceId':sid,'sourceIds':[sid,charter],
        'fieldSourceIds':{k:[sid] for k in ['score','sourceMaximumScore','sourceAverageScore','plannedCount','admittedCount','batch','major']},
        'sourceRow':i,'reviewedAt':NOW,'rank':None,'rankType':None,'evidenceStatus':'verified',
        'scoreComparable':True,'scoreEvidenceGaps':[],'conflictFields':[],
        'requiredSubjects':[],'subjectRule':'unknown','requirementText':None,
        'note':'官网2026年7月10日广西本科提前批专业结果。最低分取录取最低分列，368为控制线；计划数与录取数各列均为2。轮次和广西专业组未列。航海类另有辨色力、视力和船员体检条件，公共外语须选英语，详见学校章程。'})
    records[-1]['fieldSourceIds']['scoreBasis']=[charter]

details={
 '10269':'本轮重新读取2026广西8个科类/类别/选科组合，仍为32条专业行；普通本科、提前公费师范、国家专项、高校专项范围保留。计划同样32条88人，但相等不代表组码已核实。',
 '10036':'本轮重新读取既有2026广西普通/提前/专项/合作组合，保持现有30条专业分；同专业可能有多类别，不将类别合并。初始计划新增30条83人。',
 '10052':'本轮2026广西专业录取API36行，其中体育1行不纳入普通专业分，现有35条范围保持。初始计划37条166人，比现有专业分多出的物理新闻传播学类、外国语言文学类列为待追查；计划PDF右侧是2025分数，不导入2026。',
 '10423':'本轮按既有2026广西查询参数重新获取实际专业表，保留60条普通、提前、国家专项、高校专项、合作专业分及其原类别。预科汇总不拆专业；计划新增60条153人，姓名/类别差异仅作追查线索。',
 '10718':'本轮2026广西计划API成功取得69条214人；专业分API菜单仍没有广西2026项，2026普通物理/历史请求均空，此结果与旧轮相同。另行重取官方2026合作办学分数PDF，原有2条实际专业分来自该PDF而非API；1条专业名称冲突保留，不能凭新计划同名猜改。',
 '10025':'本轮重新请求2026广西物理普通类本科普通批专业分，仍有6条；计划年份菜单仅到2025。分数为学校实考分规则，保持既有口径，不用计划查询旧年或录取人数补2026计划。',
 '10043':'本轮重读2026广西普通类与中外合作查询页，保留11条普通高考专业分。艺体/运训单招另有规则，不纳入本批。计划栏目未取得可用广西初始专业数据。',
 '10633':'本轮核对2026录取统计公告，已采范围仍为12条。计划接口广西14条中排除2条体育后为12条43人；未知组码/再选科目不由专业名称推算。',
 '10637':'本轮重新读取广西原表16条普通科类统计，其中社会工作等专业、秘书学等专业、工商管理类与旅游管理、材料类等专业、光电信息科学与工程等专业5条是多专业汇总，不能拆成逐专业线；保留11条实际单专业/正式专业类及食品质量与安全征集标记。',
 '11319':'本轮重读现有广西录取公告，既有18条专业分仍按原公告范围保留；计划系统本轮受证书过期/HTTP404影响，不能用录取人数替代初始计划。',
 '16302':'本轮重读2026广西3个正式招生大类录取表，保留工商管理类/金融学类/电子信息类分数。学校按大类录取，不把大类最低分再拆给所含各专业；后期统计计划人数未明初始阶段，另留线索。',
 '11552':'本轮重读2026广西本科公告，保留5条专业分及合作办学类别；取得匹配的普通科类计划5条21人，另外艺术计划2条不纳入。',
 '10120':'本轮重读2026广西录取统计页，保留8条专业分；初始计划8条66人。仍缺组码和正式批次，专业体检备注来自计划原文。',
 '11313':'本轮重新下载官方2026广西录取PDF，SHA256与旧证据一致，63条现有分数范围保持；计划3页广西列独立逐行复核为63条143人。未把国标专业代码作为广西填报码。',
 '11765':'本轮重新下载2026外省本科录取表，与旧证据SHA256一致，城市地下空间工程平均分高于最高分冲突仍在；保留16条及1条不可比标记。初始计划表未分科类，不能据专业分或名称猜分历史/物理。',
 '11510':'初始计划26条64人与现有本科普通批24条60人对账，定位并取得2026广西本科提前批公告，新增航海技术最低523、轮机工程最低520两条，各计划/录取2人。两条均另有航海体检条件，仍缺专业组与轮次。',
 '12789':'本轮重读2026六省录取公告广西段，保留6条专业分；地图明确2026广西6人，点击官方参数查询得6条初始专业计划，历史3、物理3。计划页附带的是2025分数，不替换2026专业分。',
 '12864':'本轮重新下载2026广西录取原图，SHA256与旧图一致；保留12条专业分。初始计划页按历史/物理逐列读取12条20人，各科10人。',
 '12758':'本轮重读2026广西高职专科普通类录取公告，保留9条专业分。初始专科计划5专业共20人不分物理/历史，不能按录取人数反拆；本科计划不含广西。',
 '14008':'本轮重读2026广西录取原文，SHA256与旧证据一致；医学检验技术与预防医学两条录取1人但最低/最高不同的冲突未修正。初始计划原图经独立复核新增22条80人，不能据计划数猜改原录取分。'}
notes=[];observations=[];catalog=json.loads((OUT/'source-catalog.json').read_text())
for c,t in TARGETS.items():
    ss=[src(n,'major-score-scope-review') for n in score_files[c]]
    old=[x for x in old_scores if x['schoolCode']==c];new=[x for x in records if x['schoolCode']==c]
    status='collected' if new else 'reviewed-existing-scores'
    note={'id':'major-score-scope-review-pilot-b-20260912-'+c,'year':2026,'province':'广西',
        'schoolCode':c,'school':t['school'],'auditKind':'major-scores','checkedAt':NOW,'status':status,
        'sourceIds':ss,'checkedUrls':list(dict.fromkeys(sources[s]['url'] for s in ss)),
        'note':details[c],'recordCount':len(new),'existingRecordCount':len(old),
        'scope':'仅本轮列明的官网表格/API范围；未取得不等于无录取，不宣称全校渠道完备。'}
    notes.append(note)
    pr=[r for r in plans if r['schoolCode']==c]
    keys={(x['track'],x['major']) for x in old+new}
    unmatched=[{'planId':x['id'],'track':x['track'],'major':x['major'],'category':x['category'],'plannedCount':x['plannedCount']} for x in pr if (x['track'],x['major']) not in keys]
    cat=next(x for x in catalog if x['schoolCode']==c)
    observations.append({'taskId':t['taskId'],'year':2026,'province':'广西','schoolCode':c,'school':t['school'],
        'checkedAt':NOW,'auditKinds':['plans','major-scores'],'reviewStatus':'reviewed','planStatus':cat['status'],
        'planRowCount':len(pr),'plannedCount':sum(x['plannedCount'] for x in pr),
        'existingMajorScoreCount':len(old),'addedMajorScoreCount':len(new),
        'scoreReviewStatus':status,'planNote':cat['note'],'scoreNote':details[c],
        'planSourceIds':cat['sourceIds'],'scoreSourceIds':ss,
        'sourceScopeComplete':False,'completePlanDenominatorKnown':False,
        'remainingGaps':cat['remainingGaps']+(['专业分API未提供2026广西其他类别，现有分数范围限于合作PDF'] if c=='10718' else []),
        'reconciliationMethod':'同校代码、首选科目、专业名称精确相等仅生成追查线索，未据此合并类别/轮次/组码；名称不等不直接认定缺专业录取。',
        'planNamesWithoutExactScoreName':unmatched})
for name,value in [('major-cutoffs-upsert',records),('sources',list(sources.values())),('school-audit-notes',notes)]:
    (SCORE/(name+'.json')).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
(ROOT/'scope-review-observations.json').write_text(json.dumps(observations,ensure_ascii=False,indent=2)+'\n')
(ROOT/'score-review-summary.json').write_text(json.dumps({'schools':20,'addedScores':len(records),'planRows':len(plans),'planSchools':14,'sources':len(sources),'planned':sum(x['plannedCount'] for x in plans)},ensure_ascii=False,indent=2)+'\n')
print('Scope reviews',len(observations),'new major scores',len(records))
