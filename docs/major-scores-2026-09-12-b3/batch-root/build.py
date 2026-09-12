"""Offline rebuild from frozen statistical facts; no network or private paths."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parent
DATE='2026-09-12'
def load(n):return json.loads((ROOT/n).read_text())
def save(n,x):(ROOT/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def sid(n):return 'major-20260912b3-root-'+n.replace('.','-')
definitions={
 'sisu':('10271','上海外国语大学','empty-current-response','沿首页新入口aopress.shisu.edu.cn查询，而非停留在旧633栏目。广西菜单最高2025；按真实字段查询2026物理/历史普通类均state=1且分专业数组为空，2025同口径正对照为6/5条。仅确认这两个组合的缺口，不扩大到所有类别和发布渠道。'),
 'njmu':('10312','南京医科大学','entry-only-year-gap','往年录取栏目最新江苏省外专业资料发布于2026-05-12，但附件标题为21–25年，33页PDF第19页广西明确从2025开始；读到旧年专业分，不补成2026。'),
 'njucm':('10315','南京中医药大学','entry-only-year-gap','当前专业投档线目录最新为2025；广西14行附件标题明确2025年本科招生专业平行志愿投档线。年份及投档统计口径均不符合本轮实际专业录取分收录条件。'),
 'snnu':('10718','陕西师范大学','collected-partial','2026-08-03公告的11页PDF第2页广西有12行科类/招生类别汇总，不能拆成专业分；另2行明确中外合作专业：物理学517，电子信息技术563。后一名称与2026章程电子信息科学与技术不一致，按原名保留为待核记录并退出比较，不擅自更名。第10页体育综合分排除。历年专业查询菜单最高2025，2026两科普通类成功空数组，2025正对照正常。'),
 'bjut':('10005','北京工业大学','entry-only-year-gap','当前招生首页与历年分数入口链接2025京外普通类专业录取统计，5页PDF广西位于第1–2页，明确属于2025。所读入口未取得2026广西专业分，不将2026计划当作成绩。'),
 'ccmu':('10025','首都医科大学','collected-partial','沿学校主页进入zhsh.ccmu.edu.cn真实招生域名，9月2日专业录取信息页连到公开统计表单及菜单。2026广西仅物理类/普通类/本科普通批组合，专业菜单6项与实际表6行完全一致。最高/最低/平均分直接发布，人数、位次、组码、广西专业代号与轮次未列。表单xkkm字段的页面表头是年制，不能误认再选科目。章程以高考实考分安排专业，政策加分只用于后续同分排序。旧zs域名连接失败不用于判断当前入口是否可用。')}
labels={'home':'招生官网入口','scores':'历年分数目录','major':'专业录取信息','major-form':'公开专业统计表单与字段表头','major.js':'公开专业统计前端','charter':'2026招生章程','current':'2026录取最低分公告','old':'往年专业分附件','params-majors':'2026广西完整专业菜单'}
sources=[]
for m in load('source-manifest.json'):
    fn=m['name'];prefix=fn.split('-')[0];school=definitions[prefix][1];key=fn[len(prefix)+1:].rsplit('.',1)[0]
    actual=fn in ['ccmu-gx-2026-0.json','snnu-current.pdf']
    year=2025 if '2025' in fn or fn in ['njmu-old.pdf','njucm-latest.html','bjut-old.pdf','sisu-old-stats.html'] else (2026 if actual or 'charter' in fn else None)
    source={'id':sid(fn),'title':school+'：'+labels.get(key,key),'url':m['url'],'publisher':school,'year':year,'publishedAt':{'snnu-current.pdf':'2026-08-03','snnu-current.html':'2026-08-03','ccmu-major.html':'2026-09-02','ccmu-charter.html':'2026-05-29'}.get(fn),'accessedAt':m['checkedAt'],'sha256':m.get('sha256'),'responseSha256':m.get('responseSha256'),'requestMethod':m['requestMethod'],'requestData':m.get('data'),'httpStatus':m.get('httpStatus'),'evidenceRole':'actual-major-score-source' if actual else 'source-review','archiveFile':fn,'notes':[definitions[prefix][3]]}
    if m.get('error'):source['accessError']=m['error']
    sources.append(source)
sources.extend(load('code-sources.json'))
records=[]
for e in load('evidence-rows.json'):
    r=e['fields'];iscc=e['file'].startswith('ccmu');prefix='ccmu' if iscc else 'snnu';code,school=definitions[prefix][:2];src=sid(e['file']);charter=sid(prefix+'-charter.html');conflict=not iscc and r['majorName'].startswith('电子信息技术')
    codeSource='gxeea-2026-33107'
    note='学校直接公布的具体专业最低录取分。专业组码、广西填报专业代号、再选科目、位次和首次/征集轮次未列，保持未知。'
    if iscc:
        note+='章程明确进档后按高考实考分安排专业，政策加分仅用于后续同分排序。'
        req='非英语语种考生入学后须改学英语。依章程第十二条，须核对视力、色觉、听力、嗅觉、口吃及医学类肝功能等体检限制；原分数表不等于体检合格证明。'
    else:
        req='仅录取有该专业志愿考生；3+1培养，第四学年赴匈牙利塞格德大学；部分课程英语授课，非英语考生谨慎报考；入学后不得申请转专业。学费以2026新生缴费须知为准。'
        note+='依据章程按投档成绩安排专业，认可规定的全国性高考加分。'
    gaps=[]
    if conflict:
        gaps=['分数表专业名称与2026章程不一致，563分对应的正式专业名称待学校确认']
        note+=' 原表写电子信息技术（中外合作办学），章程写电子信息科学与技术（中外合作办学）；保留原名及分数，不自动认定为同一专业，退出分数比较。'
    refs=[src,charter,codeSource]
    if iscc:refs.extend([sid('ccmu-major.html'),sid('ccmu-major-form.html'),sid('ccmu-params-majors.json')])
    else:refs.append(sid('snnu-current.html'))
    fields={k:[src] for k in ['year','province','track','major','score','admissionType']}
    fields.update(schoolCode=[codeSource],scoreBasis=[charter],admissionRequirements=[charter],note=refs)
    if iscc:fields.update({k:[src] for k in ['batch','sourceMaximumScore','sourceAverageScore']})
    if conflict:fields.update(scoreComparable=[src,charter],conflictFields=[src,charter])
    rec={'id':f'major-20260912b3-root-{code}-{e["sourceRow"]}','year':2026,'province':'广西','schoolCode':code,'school':school,'sourceSchool':school,'track':'物理','sourceTrack':r['scienceClass'],'batch':r.get('batch','本科批（精确批次待核）'),'round':'录取汇总（轮次未分）','group':None,'major':r['majorName'],'majorCode':None,'score':r['lowScore'],'scoreType':'专业录取最低分','rank':None,'sourceId':src,'sourceIds':refs,'sourceRow':e['sourceRow'],'sourceTable':'list' if iscc else 'PDF第2页广西区块，第13–14数据行','reviewedAt':DATE,'evidenceStatus':'source-conflict' if conflict else 'verified','scoreComparable':not conflict,'scoreBasis':'750分制高考实考分（依学校章程专业录取口径）' if iscc else '750分制普通高考总分（含学校认可的全国性政策加分）','scoreScaleMaximum':750,'scoreEvidenceGaps':gaps,'conflictFields':['major'] if conflict else [],'admissionType':r['type'],'sourceCategory':r['type'],'requiredSubjects':[],'subjectRule':'unknown','requirementText':'首选物理；原成绩表未列再选科目','fieldSourceIds':fields,'sourceMaximumScore':r.get('hightScore'),'sourceAverageScore':r.get('avgScore'),'sourceScoreHeader':'最低分' if iscc else '录取最低分','admissionRequirements':req,'note':note}
    if 'page' in e:rec['sourcePage']=e['page']
    records.append(rec)
notes=[]
for prefix,(code,school,status,note) in definitions.items():
    ss=[s for s in sources if s['id'].startswith(sid(prefix+'-'))]
    notes.append({'id':'review-major-20260912b3-root-'+code,'year':2026,'province':'广西','schoolCode':code,'school':school,'auditKind':'major-scores','checkedAt':DATE,'title':'2026广西专业录取分来源核查','status':status,'recordCount':sum(r['schoolCode']==code for r in records),'sourceIds':[s['id'] for s in ss],'checkedUrls':list(dict.fromkeys(s['url'] for s in ss)),'note':note,'scope':'仅列明官方入口、附件及真实查询组合；未取得不等于未招生或所有渠道未发布。'})
assert len(records)==8 and sum(r['scoreComparable'] for r in records)==7 and len(notes)==6
for n,d in [('sources.json',sources),('major-cutoffs-upsert.json',records),('school-audit-notes.json',notes)]:save(n,d)
review=load('review-evidence.json')
save('QA.json',{'status':'passed','reviewedAt':DATE,'newScoreRecords':8,'comparableRecords':7,'nameConflictRecords':1,'reviewedSchools':6,'sources':len(sources),'checks':review['checks'],'manualReview':review['manualReview'],'limits':['陕师电子专业名冲突退出比较','其余科类汇总、体育和旧年资料不入库','原表未列人数及位次','首医年制字段不当选科','批次/轮次/组码未知时不推定']})
print('PASS',len(records),'rows',len(sources),'sources',len(notes),'notes')
