"""Build an additive, evidence-linked batch from public HTML and verified image transcription."""
from pathlib import Path
import json,csv,hashlib,re
from collections import Counter
from parse_tables import NestedTables

BASE=Path(__file__).resolve().parent
def load(p):return json.loads(p.read_text())
def write(name,data):(BASE/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def decode(p):
    b=p.read_bytes()
    try:return b.decode('utf-8')
    except UnicodeDecodeError:return b.decode('gb18030')
def sid(key):return 'major-c-20260912-'+key
requests={x['key']:x for x in load(BASE/'requests.json')}
SPECS={
 'zbti-gx':('浙江工商职业技术学院2026年六省高职（专科）录取情况：广西段','浙江工商职业技术学院','2026-08-07'),
 'zbti-charter':('浙江工商职业技术学院2026年普通高校招生章程','浙江工商职业技术学院','2026-05-22'),
 'gxtcmu-early':('广西中医药大学2026年广西本科提前批录取情况','广西中医药大学','2026-07-13'),
 'gxtcmu-early-6':('广西中医药大学2026年中医学定向医学生历史类录取分数原图','广西中医药大学','2026-07-13'),
 'gxtcmu-early-7':('广西中医药大学2026年中医学定向医学生物理类录取分数原图','广西中医药大学','2026-07-13'),
 'gxtcmu-charter':('广西中医药大学2026年普通本科、高职招生章程','广西中医药大学','2026-06-10'),
 'gx-policy-faq':('广西2026年普通高校招生政策百问百答（桂林学院官方转载）','桂林学院招生办公室',None),
 'gxtcmu-regular':('广西中医药大学2026年广西本科普通批情况：原图分数口径为首次投档','广西中医药大学','2026-07-26'),
 'gxtcmu-regular-6':('广西中医药大学2026年本科首次投档专业分原图1','广西中医药大学',None),
 'gxtcmu-regular-7':('广西中医药大学2026年本科首次投档专业分原图2','广西中医药大学',None),
 'gxtcmu-junior':('广西中医药大学2026年广西高职高专普通批情况：原图为首次投档分','广西中医药大学','2026-08-07'),
 'gxtcmu-junior-6':('广西中医药大学2026年高职高专首次投档专业分原图','广西中医药大学',None),
 'buu-score':('北京联合大学2026年各省普通本科录取最低分：广西段只有专业组分','北京联合大学','2026-07-10'),
}
sources=[]
for key,(title,publisher,date) in SPECS.items():
    q=requests[key];meta=load(BASE/'raw'/(key+'.meta.json'));p=BASE/'raw'/q['file']
    assert meta['status']==200 and sha(p)==meta['sha256']
    sources.append({'id':sid(key),'title':title,'url':q['url'],'publisher':publisher,'sourceType':'official',
      'year':2026,'province':'广西','publishedAt':date,'accessedAt':meta['checkedAt'],'requestMethod':'GET',
      'sha256':meta['sha256'],'rawSha256':meta['sha256'],'archiveSha256':meta['sha256'],
      'archiveFile':'raw/'+q['file'],'method':'公开官网直接读取；不保存请求或响应头。',
      'notes':['图表分数性质按表头判别，不由网页标题或录取人数反推。']})
# The existing provincial table supplies the official five-digit code, not a guessed campus code.
existing_sources={s['id']:s for s in load(BASE/'code-sources.json')}
sources.append(existing_sources['gxeea-2026-33107'])
rows=[]
def basic(code,school,track,major,score,key,row_number,batch,group=None):
    ids=[sid(key)]
    r={'id':f'major-2026-0912c-{code}-{key}-{row_number}', 'year':2026,'province':'广西',
       'schoolCode':code,'school':school,'track':track,'batch':batch,'round':'录取汇总（轮次未分）',
       'group':group,'major':major,'score':score,'scoreType':'专业录取最低分','rank':None,'rankType':None,
       'sourceId':sid(key),'sourceIds':ids,'sourceTable':1,'sourceRow':row_number,
       'reviewedAt':'2026-09-12','evidenceStatus':'verified','scoreComparable':True,
       'scoreBasis':'750分制普通高考总分（政策认可加分按学校及广西规则计入）','scoreScaleMaximum':750,
       'scoreEvidenceGaps':[],'conflictFields':[],'admissionType':'普通类',
       'requiredSubjects':[],'subjectRule':'unknown','requirementText':None,
       'fieldSourceIds':{k:ids[:] for k in ['year','province','track','major','score','batch','round']}}
    if group:r['fieldSourceIds']['group']=ids[:]
    return r

# The HTML table explicitly supplies province, track, major, admitted count, maximum and minimum.
parser=NestedTables();parser.feed(decode(BASE/'raw/zbti-gx.html'));table=parser.tables[0]['rows']
assert table[0]==['省份','科类','序号','专业','计划数','录取数','最高分','最低分']
evidence=[]
for i,c in enumerate(table[1:],2):
    if c[0]!='广西':continue
    r=basic('12789','浙江工商职业技术学院',c[1].replace('类',''),c[3],int(c[7]),'zbti-gx',i,'高职（专科）（批次待核）')
    r.update(admittedCount=int(c[5]),sourceMaximumScore=int(c[6]),sourceTrack=c[1],sourceSequence=c[2])
    r['sourceIds'] += [sid('zbti-charter'),sid('gx-policy-faq')]
    r['fieldSourceIds'].update({k:[sid('zbti-gx')] for k in ['admittedCount','sourceMaximumScore','admissionType']})
    r['fieldSourceIds'].update(schoolCode=[sid('zbti-charter')],school=[sid('zbti-charter')],scoreBasis=[sid('zbti-charter'),sid('gx-policy-faq')],note=[sid('zbti-gx'),sid('zbti-charter')])
    r['note']='普通高考高职专科录取统计；原公告只明示高职（专科）层次，广西具体批次待核，未区分首次与征集，保留为录取汇总。原表未单列政策加分，学校按考生投档成绩安排专业。所有外语教学使用英语；选科细项及广西专业组码未在本成绩表给出，保持未知。录取人数不作为招生计划。'
    rows.append(r);evidence.append({'id':r['id'],'sourceId':sid('zbti-gx'),'sourceTable':1,'sourceRow':i,'cells':c})

medical=list(csv.DictReader((BASE/'gxtcmu-early-transcription.tsv').open(),delimiter='\t'))
assert len(medical)==72
for c in medical:
    key='gxtcmu-early-'+('6' if c['track']=='历史' else '7')
    area=c['city']+c['county']
    r=basic('10600','广西中医药大学',c['track'],'中医学（定向医学生）',int(c['minimum']),key,int(c['row']),'本科提前批其他三类',c['group'])
    r.update(admittedCount=int(c['admitted']),sourceMaximumScore=int(c['maximum']),sourceTrack=c['track'],
        serviceArea=area,serviceCity=c['city'],serviceCounty=c['county'],sourceMajor='中医学（定向医学生）',
        admissionType='定向医学生（'+area+'）',admissionCategory='农村订单定向免费医学生',
        durationYears=5,requirementText='首选'+c['track']+'；原表未列再选科目',subjectRule='unknown')
    r['sourceIds'] += [sid('gxtcmu-early'),sid('gxtcmu-charter'),sid('gx-policy-faq'),'gxeea-2026-33107']
    for f in ['admittedCount','sourceMaximumScore','serviceArea','serviceCity','serviceCounty','admissionType','requirementText']:
        r['fieldSourceIds'][f]=[sid(key)]
    r['fieldSourceIds'].update(year=[sid('gxtcmu-early')],province=[sid('gxtcmu-early')],
       major=[sid('gxtcmu-early')],school=[sid('gxtcmu-early')],schoolCode=['gxeea-2026-33107'],
       batch=[sid('gxtcmu-early'),sid('gx-policy-faq')],round=[sid('gxtcmu-early')],
       scoreBasis=[sid('gxtcmu-charter'),sid('gx-policy-faq')],durationYears=[sid('gx-policy-faq')],
       note=[sid(key),sid('gxtcmu-early'),sid('gxtcmu-charter'),sid('gx-policy-faq')])
    r['eligibility']={'ruralHouseholdRequired':True,'localHouseholdYearsMinimum':3,'sourceCityMustMatch':c['city'],
       'agreementRequired':True,'minimumServiceYearsAfterTrainingOrMasters':6,'sourceIds':[sid('gx-policy-faq'),sid('gxtcmu-charter')]}
    r['note']='原文标题明确为中医学（定向医学生）录取分数，原图列最高分、最低分、录取数，未标首次/征集，保存为汇总。定向服务地：'+area+'；按设区市生源招生。仅招农村学生，考生本人及父亲/母亲/法定监护人户籍须在农村，本人须有当地连续3年以上户籍，并符合当年高考条件。须签免费教育及定向就业协议；取得规培/助理全科培训合格证或临床专硕学位和毕业证后，须在定向乡镇卫生院服务不少于6年。学校按政策加分后总分分配专业；医药类不录取色盲色弱考生，体检还须符合定向项目规定。外语教学为英语。招生类别附县区用于保留不同服务地记录，正式专业名保持原文；录取人数不更新计划。'
    rows.append(r);evidence.append({'id':r['id'],'sourceId':sid(key),'sourceTable':1,'sourceRow':int(c['row']),'cells':c})

notes=[]
for code,school,status,text,keys in [
 ('12789','浙江工商职业技术学院','collected','取得2026官方六省专科录取表完整广西段6条，历史3、物理3，录取6人。只明示高职专科层次，具体批次未核；未明示轮次、组码和再选科目，均保留未知/汇总。其他省及非普通高考不采。',['zbti-gx','zbti-charter']),
 ('10600','广西中医药大学','partial','取得提前批中医学定向医学生72条县区科类记录（历史28条36人、物理44条75人），均有实际最高/最低分和录取数。普通本科两图40行含2预科，高职5行均写首次投档分，不能当作实际专业录取分；本批仅保留其来源和口径说明，不更新实际分库或既有投档分库。',['gxtcmu-early','gxtcmu-early-6','gxtcmu-early-7','gxtcmu-regular','gxtcmu-regular-6','gxtcmu-regular-7','gxtcmu-junior','gxtcmu-junior-6','gxtcmu-charter','gx-policy-faq']),
 ('11417','北京联合大学','not-found-current-major','实际读取2026各省普通本科录取最低分页面，广西段第15表只有科类、选考要求及专业组、录取最低分，12行均为专业组口径，无具体专业列；不采入实际专业分。页面其他省的专业分不能迁至广西。',['buu-score'])]:
    notes.append({'id':'major-score-audit-20260912-c-'+code,'auditKind':'major-scores','year':2026,'province':'广西','schoolCode':code,'school':school,'checkedAt':'2026-09-12','status':status,'recordCount':sum(r['schoolCode']==code for r in rows),'note':text,'scope':'仅限本轮已读取的官方原文及表格；未取得不代表零录取或全校所有渠道均未公开。','sourceIds':[sid(k) for k in keys],'checkedUrls':[requests[k]['url'] for k in keys]})

excluded=[{'school':'广西中医药大学','schoolCode':'10600','sourceIds':[sid(k) for k in ['gxtcmu-regular','gxtcmu-regular-6','gxtcmu-regular-7']], 'rowCount':40,'reason':'原表写首次投档最低分，38条专业投档分非实际专业录取分；另2条为少数民族预科。','disposition':'不入actual；仅保留独立研究材料，不改既有major-filing库'},
 {'school':'广西中医药大学','schoolCode':'10600','sourceIds':[sid('gxtcmu-junior'),sid('gxtcmu-junior-6')],'rowCount':5,'reason':'虽有录取数合计399，分数字段明确为首次投档最高/最低/平均分，不能由录取人数推为实际分。','disposition':'不入actual；保留源链接'},
 {'school':'北京联合大学','schoolCode':'11417','sourceIds':[sid('buu-score')],'sourceTable':15,'rowCount':12,'reason':'广西段仅专业组分数，无专业名称。'},
 {'school':'重庆三峡医药高等专科学校','schoolCode':'14008','url':requests['sxyyc-gx']['url'],'reason':'读取页眉确认sxyyc.net为该校，已在948条基线内，排除重复采集。'}]

context=load(BASE/'baseline-context.json')
checks=[]
def check(key,ok,detail=None):checks.append({'id':key,'pass':bool(ok),**({'detail':detail} if detail is not None else {})})
check('new-schools-only',not ({r['schoolCode'] for r in context['baselineSchools']}&{r['schoolCode'] for r in rows}))
check('avoid-current-20-targets',not (set(context['excludedTargetSchoolCodes'])&{r['schoolCode'] for r in rows}))
check('expected-new-count',len(rows)==78)
check('medical-count-history',sum(r['admittedCount'] for r in rows if r['schoolCode']=='10600' and r['track']=='历史')==36)
check('medical-count-physics',sum(r['admittedCount'] for r in rows if r['schoolCode']=='10600' and r['track']=='物理')==75)
check('medical-merged-boundary-yizhou',all(c['city']=='河池市' and c['county']=='宜州区' and c['group']==g for t,n,g in [('历史','19','407'),('物理','30','457')] for c in medical if c['track']==t and c['row']==n))
check('medical-last-row-shangsi-image-review',any(c['track']=='物理' and c['row']=='44' and c['city']=='防城港市' and c['county']=='上思县' and c['group']=='464' and c['maximum']==c['minimum']=='575' for c in medical))
check('distinct-ids',len({r['id'] for r in rows})==len(rows))
identity=lambda r:tuple(str(r.get(k) or '') for k in ['year','schoolCode','track','batch','group','major','round','admissionType'])
check('distinct-identities-with-service-area',len({identity(r) for r in rows})==len(rows))
sourceids={s['id'] for s in sources}
for r in rows:
    check(r['id']+'-range',0<=r['score']<=r['sourceMaximumScore']<=750)
    check(r['id']+'-single-student',r['admittedCount']!=1 or r['score']==r['sourceMaximumScore'])
    check(r['id']+'-no-inferred-rank',r['rank'] is None)
    check(r['id']+'-source-closure',all(s in sourceids for s in r['sourceIds']) and all(s in sourceids for ids in r['fieldSourceIds'].values() for s in ids))
    check(r['id']+'-group-evidence',not r['group'] or r['fieldSourceIds'].get('group'))
check('actual-score-type-only',all(r['scoreType']=='专业录取最低分' for r in rows))
check('no-filing-table-in-actual',not any('regular' in r['sourceId'] or 'junior' in r['sourceId'] for r in rows))
check('historical-baseline-snapshot',context['baselineRowCount']==948 and len(context['baselineSchools'])==23,{'sha256':context['baselineSha256'],'note':'历史预检基线，静态重建不声称当前线上库仍为948条。'})
check('medical-direct-caption',all(x in decode(BASE/'raw/gxtcmu-early.html') for x in ['2026年中医学','定向医学生','历史类录取分数情况','物理类录取分数情况']))
qa={'checkedAt':'2026-09-12','summary':{'newSchools':2,'newActualRows':len(rows),'bySchool':dict(Counter(r['school'] for r in rows)),'byTrack':dict(Counter(r['track'] for r in rows)),'admittedCount':sum(r['admittedCount'] for r in rows),'directGroupRows':sum(bool(r['group']) for r in rows),'rankRows':0,'uncomparableRows':0,'checks':len(checks),'passed':sum(c['pass'] for c in checks),'failed':sum(not c['pass'] for c in checks)},'checks':checks,'limits':['本轮确认2所新校，未凑3–5所。','无PDF来源；HTML原表和5张广西中医药原图均已目视。','透明PNG的白底预览只为显示原黑色文本，原文件和hash保持不变。','原表均没有位次，全部rank=null，不以其他年份位次补齐。','72条县区专业保持正式源名，类别和serviceArea用于区分服务地。','原计划数仅在转录证据中保留，未进入计划库。']}
write('major-cutoffs-upsert.json',rows);write('sources.json',sources);write('school-audit-notes.json',notes)
write('evidence-rows.json',evidence);write('excluded-records.json',excluded);write('QA.json',qa)
write('PUBLIC-FILES.json',{'publicFiles':['major-cutoffs-upsert.json','sources.json','school-audit-notes.json','evidence-rows.json','excluded-records.json','QA.json','README.md','PUBLIC-FILES.json','collect.py','build.py','parse_tables.py','requests.json','gxtcmu-early-transcription.tsv','importer-preflight.json','baseline-context.json','code-sources.json'],'excluded':['raw/**','__pycache__/**'],'note':'原始网页、图片、白底预览及响应元数据留本地，不公开；脚本均使用相对路径，静态重建不依赖当前线上库。'})
print(json.dumps(qa['summary'],ensure_ascii=False));print([c for c in checks if not c['pass']])
