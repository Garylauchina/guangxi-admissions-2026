"""Build B30 public statistical facts from local archived official evidence.

No network calls and no live-site writes. raw/ stays local. Run after collector.py.
Only PUBLIC-FILES.txt is eligible for publication; complete API/HTML/image/PDF
responses and request manifests are deliberately excluded.
"""
from pathlib import Path
from html.parser import HTMLParser
import json, re, hashlib, datetime, collections

ROOT = Path(__file__).resolve().parent
RAW = ROOT / 'raw'
NOW = datetime.datetime.now(datetime.timezone.utc).isoformat()
PREFIX = 'major-20260920-b-'

def read(name): return json.loads((ROOT / name).read_text())
def write(name, value): (ROOT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n')
def sid(raw_id): return PREFIX + raw_id
def number(value):
    n = float(value)
    return int(n) if n.is_integer() else n

class Tables(HTMLParser):
    """Keep original cell text and expand row/col spans within each table."""
    def __init__(self):
        super().__init__(); self.depth=0; self.tables=[]; self.rows=[]; self.row=None; self.cell=None
    def handle_starttag(self, tag, attrs):
        attrs=dict(attrs)
        if tag=='table':
            self.depth+=1
            if self.depth==1: self.rows=[]
        if self.depth!=1:return
        if tag=='tr': self.row=[]
        elif tag in ('td','th') and self.row is not None:
            self.cell={'text':[], 'rowspan':int(attrs.get('rowspan','1')), 'colspan':int(attrs.get('colspan','1'))}
    def handle_data(self, data):
        if self.cell is not None:self.cell['text'].append(data)
    def handle_endtag(self, tag):
        if self.depth==1 and tag in ('td','th') and self.cell is not None:
            self.cell['text']=re.sub(r'\s+','', ''.join(self.cell['text'])).strip()
            self.row.append(self.cell); self.cell=None
        if self.depth==1 and tag=='tr' and self.row is not None:
            self.rows.append(self.row); self.row=None
        if tag=='table':
            if self.depth==1:self.tables.append(self.expand(self.rows))
            self.depth-=1
    @staticmethod
    def expand(rows):
        carry={}; result=[]
        for row in rows:
            cells={k:v[0] for k,v in carry.items()}
            carry={k:(v[0],v[1]-1) for k,v in carry.items() if v[1]>1}
            col=0
            for c in row:
                while col in cells: col+=1
                for k in range(c['colspan']):
                    cells[col+k]=c['text']
                    if c['rowspan']>1:carry[col+k]=(c['text'],c['rowspan']-1)
                col+=c['colspan']
            result.append([cells.get(k,'') for k in range(max(cells,default=-1)+1)])
        return result

def tables(raw_id):
    m=meta[raw_id]; p=RAW/m['archiveFile']; h=Tables();h.feed(p.read_text());return h.tables

targets = {r['schoolCode']:r['school'] for r in read('targets.json')}
facts=read('audit-facts.json')
for f in facts:
    f['rawIds']=['11646-admissions' if x=='11646-scores-entry' else x for x in f['rawIds']]
meta={}
for path in RAW.glob('*.meta.json'):
    m=json.loads(path.read_text()); raw_id=m['id']
    if 'rawFile' in m:
        m['archiveFile']=Path(m['rawFile']).name
        m['archiveSha256']=m.get('sha256'); m['rawSha256']=m.get('responseSha256')
        m['checkedAt']=m['accessedAt'];m['status']=m.get('httpStatus')
    meta[raw_id]=m

smu_ids = ['10254-result-'+str(n) for n in range(14,22)] + ['10254-extra-'+str(n) for n in range(9,17)]
next(f for f in facts if f['schoolCode']=='10254')['rawIds'].extend(smu_ids)
used=sorted(set(x for f in facts for x in f['rawIds']))
sources=[];manifest=[]
for raw_id in used:
    m=meta[raw_id]; code=m['schoolCode']; filename=m.get('archiveFile'); digest=None
    if filename:
        digest=hashlib.sha256((RAW/filename).read_bytes()).hexdigest()
        assert digest==m['archiveSha256'], (raw_id,'archive checksum')
    title=f"{targets[code]}：官方录取分来源核查（{raw_id.split('-',1)[1]}）"
    source={
        'id':sid(raw_id),'title':title,'url':m.get('finalUrl',m['url']),
        'publisher':targets[code], 'year':2026 if raw_id in ['10047-next','10047-score-image','10047-charter','10353-charter','10353-charter-pdf','10254-charter','11835-score26','11835-score26body'] or raw_id in smu_ids else None,
        'publishedAt':None,'accessedAt':m['checkedAt'],'sha256':digest,
        'responseSha256':m.get('rawSha256'),'httpStatus':m.get('status'),
        'requestMethod':m.get('method','POST' if 'data' in m else 'GET'),
        'evidenceType':'public-response','evidenceRole':'major-score-audit',
        'notes':['公开源仅发布统计事实及此来源元数据；完整响应、图像、PDF和会话均仅存本地。']
    }
    if raw_id=='10047-next':source['publishedAt']='2026-07-30'
    if raw_id=='10047-charter':source['publishedAt']='2026-05-29'
    if raw_id in ['11835-score26','11835-score26body']:source['publishedAt']='2026-07-16'
    sources.append(source)
    manifest.append({'id':sid(raw_id),'schoolCode':code,'url':source['url'],
        'localArchiveFile':'raw/'+filename if filename else None,
        'archiveSha256':digest,'originalResponseSha256':m.get('rawSha256'),
        'checkedAt':m['checkedAt'],'httpStatus':m.get('status'),'publicRawResponse':False,
        'requestMethod':source['requestMethod']})

evidence=[]; scores=[]
def add(code, track, major, minimum, batch, raw_id, locator, original, maximum=None, average=None,
        source_batch=None, source_track=None, requirement=None, source_major=None, included=None):
    ordinal=1+sum(r['schoolCode']==code for r in scores)
    record_id=f'{PREFIX}{code}-r{ordinal:03d}'
    charter='10353-charter-pdf' if code=='10353' else code+'-charter'
    source_ids=[sid(raw_id),sid(charter)]
    if code=='10047':source_ids.insert(1,sid('10047-next'))
    basis='普通高考投档成绩（按学校章程认可的政策加分口径）'
    r={'id':record_id,'year':2026,'province':'广西','schoolCode':code,'school':targets[code],
       'track':track,'batch':batch,'group':None,'majorCode':None,'major':major,
       'score':number(minimum),'scoreType':'专业录取最低分','round':'录取汇总（轮次未分）',
       'admissionType':'中外合作办学' if '中外合作' in major else '普通类',
       'rank':None,'rankType':None,'scoreScaleMaximum':750,'scoreBasis':basis,
       'sourceMaximumScore':number(maximum) if maximum is not None else None,
       'sourceAverageScore':number(average) if average is not None else None,
       'sourceBatch':source_batch or batch,'sourceTrack':source_track or track,
       'sourceCategory':'普通本科（非校考）' if code=='10047' else source_batch or batch,
       'sourceMajorName':source_major or major,'sourceLocator':locator,
       'sourceId':sid(raw_id),'sourceIds':source_ids,'reviewedAt':NOW,
       'evidenceStatus':'verified','scoreComparable':True,'scoreEvidenceGaps':[], 'conflictFields':[],
       'requiredSubjects':[],'subjectRule':'unknown','requirementText':requirement,
       'fieldSourceIds':{k:[sid(raw_id)] for k in ['year','province','major','track','score','batch','round','admissionType']},
       'note':'学校公布的专业录取统计未分首轮与征集，保留录取汇总口径；组码、广西专业填报码和位次未公布，不按分数或相似专业反推。'}
    r['fieldSourceIds']['scoreBasis']=[sid(charter)]
    if code=='10047':r['fieldSourceIds']['batch']=[sid(charter),sid('10047-next')]
    if maximum is not None:r['fieldSourceIds']['sourceMaximumScore']=[sid(raw_id)]
    if average is not None:r['fieldSourceIds']['sourceAverageScore']=[sid(raw_id)]
    if requirement:
        if '再选化学' in requirement:r['subjectRule']='all';r['requiredSubjects']=['化学']
        elif '再选不限' in requirement:r['subjectRule']='none'
        else:raise AssertionError(('unhandled requirement',requirement))
        r['fieldSourceIds']['requirementText']=[sid(raw_id)]
    if included:r['includedMajorsText']=included;r['note']+=' 原表以一个专业（类）统计，括号成员仅作原文说明，不拆成独立分数。'
    if code=='10047':r['note']+=' 非校考普通本科专业，章程第16、17条确认投档分和加分口径；原图招生计划不作录取人数或初始计划导入。'
    if code=='10353':r['note']+=' 接口planNumber未在可见分数表标示，不推定为录取人数。'
    scores.append(r)
    evidence.append({'recordId':record_id,'schoolCode':code,'school':targets[code],'rawId':raw_id,
                     'sourceIds':source_ids,'locator':locator,'statisticalYear':2026,'province':'广西',
                     'sourceFields':original,'scoreBasisSource':sid(charter),'normalization':{
                         'major':major,'track':track,'batch':batch,'round':r['round'],
                         'minimumScore':r['score'],'maximumScore':r['sourceMaximumScore'],
                         'averageScore':r['sourceAverageScore'],'admissionType':r['admissionType']}})

smu_combinations=[]
for raw_id in smu_ids:
    raw=(RAW/meta[raw_id]['archiveFile']).read_text(); tt=tables(raw_id)
    rows=[(ti,ri,row) for ti,t in enumerate(tt,1) for ri,row in enumerate(t,1) if len(row)==8 and row[0]=='2026']
    if not rows:assert '没有您想要的查询结果' in raw, (raw_id,'not an explicit empty response')
    smu_combinations.append({'sourceId':sid(raw_id),'url':meta[raw_id]['url'],'resultRows':len(rows),
        'interpretation':'actual-major-rows' if rows else 'explicit-empty-current-query'})
    for ti,ri,v in rows:
        assert v[1]=='广西' and v[3] in ['物理类','历史类']
        add('10254',v[3].removesuffix('类'),v[5],v[7], '本科提前批' if v[2]=='提前批' else '本科普通批',raw_id,
            {'table':ti,'row':ri,'columns':['年份','省份','批次','科类','选考科目要求','专业','最高分','最低分']},
            dict(zip(['year','province','batch','track','subjectRequirements','major','maximumScore','minimumScore'],v)),
            maximum=v[6],source_batch=v[2],source_track=v[3],requirement=v[4])
assert len(scores)==36

zj_data=json.loads((RAW/'10353-data.json').read_text())['data']
zj_gx=[(i,r) for i,r in enumerate(zj_data) if str(r['year'])=='2026' and r['province']=='广西']
assert len(zj_gx)==32
excluded=[]
for idx,row in zj_gx:
    if '预科' in row['major'] or '预科' in row['type']:
        excluded.append({'schoolCode':'10353','locator':f'/data/{idx}','year':2026,'province':'广西','major':row['major'],'category':row['category'],'reason':'预科路线不属于本次普通本科专业最低分'});continue
    assert row['category'] in ['物理','历史'] and row['type']=='本科普通批'
    major=row['major']; included=None
    if '（含' in major:
        major,included=major.split('（含',1); included=included.removesuffix('）')
    visible={k:row[k] for k in ['year','province','category','major','type','zdscore','zgscore','pjscore']}
    add('10353',row['category'],major,row['zdscore'],row['type'],'10353-data',{'jsonPointer':f'/data/{idx}'},
        visible,maximum=row['zgscore'],average=row['pjscore'],source_major=row['major'],included=included)
assert len(scores)==66

# Complete Guangxi section, independently read from the official image.
for j,(track,major,minimum,plan) in enumerate([
        ('历史','美术学',582,2),
        ('物理','艺术史论（中外合作办学）',565,1),
        ('历史','艺术史论（中外合作办学）',498,3)],1):
    add('10047',track,major,minimum,'本科普通批','10047-score-image',
        {'section':'广西','rowWithinProvince':j,'columns':['省(市、区)','招生专业','科类','招生计划','最低分数线']},
        {'province':'广西','major':major,'track':track+'类','sourcePlannedCount':plan,'minimumScore':minimum},
        source_batch='普通本科批次',source_track=track+'类')
assert len(scores)==69

# A separate direct group table. Never derive a group minimum from major rows.
groups=[]
for ti,tab in enumerate(tables('11835-score26body'),1):
    for ri,row in enumerate(tab,1):
        if len(row)!=6 or row[0]!='广西' or not re.fullmatch(r'本科批专业组\d{3}',row[1]):continue
        group=re.search(r'\d{3}',row[1]).group();track=row[2]
        assert track in ['物理','历史']
        g={'id':f'group-admission-20260920-b-11835-{group}','year':2026,'province':'广西',
           'schoolCode':'11835','school':targets['11835'],'group':group,'track':track,
           'batch':'本科普通批','sourceBatch':row[1],'round':'录取汇总（轮次未分）',
           'admissionType':'普通类','scoreType':'专业组录取最低分','score':number(row[4]),
           'sourceMaximumScore':number(row[3]),'sourceAverageScore':number(row[5]),
           'rank':None,'rankType':None,'sourceId':sid('11835-score26body'),
           'sourceIds':[sid('11835-score26body'),sid('11835-score26')],
           'fieldSourceIds':{k:[sid('11835-score26body')] for k in ['year','province','group','track','batch','score','round']},
           'sourceLocator':{'table':ti,'row':ri,'sourceCells':row},'reviewedAt':NOW,
           'evidenceStatus':'direct-group-admission-table',
           'note':'官方2026本科录取分数线原表直接列广西专业组最高、最低和平均分；未区分首轮/征集。未由专业最低值推定，未使用省考试院投档表。国家专项两科未列组码，未收入本候选。'}
        groups.append(g)
assert len(groups)==5, groups
assert {g['group']:g['score'] for g in groups}=={'101':579,'102':560,'103':562,'104':570,'105':543}

audits=[];observations=[]
for fact in facts:
    code=fact['schoolCode']; src=[sid(i) for i in fact['rawIds']]
    timestamps=sorted(meta[i]['checkedAt'] for i in fact['rawIds']); start,end=map(datetime.datetime.fromisoformat,[timestamps[0],timestamps[-1]])
    urls=list(dict.fromkeys(meta[i].get('finalUrl',meta[i]['url']) for i in fact['rawIds']))
    n=sum(r['schoolCode']==code for r in scores)
    audit={'id':PREFIX+'review-'+code,'year':2026,'province':'广西','schoolCode':code,'school':targets[code],
           'auditKind':'major-scores','checkedAt':NOW,'title':'2026广西专业录取分来源核查',
           'status':fact['status'],'recordCount':n,'sourceIds':src,'checkedUrls':urls,
           'note':fact['finding']+' 尚存缺口：'+fact['remaining'],
           'scope':'本轮列明的官方渠道与真实查询组合；未取得不等于未招生或所有渠道未发布。'}
    audits.append(audit)
    school_meta=[m for m in meta.values() if m.get('schoolCode')==code]
    observations.append({'schoolCode':code,'school':targets[code],'checkedOn':'2026-09-20',
        'auditKind':'major-scores','status':fact['status'],'newMajorScoreRows':n,
        'checkedUrls':urls,'sourceIds':src,'checkedRequestCount':len(school_meta),
        'observedStatisticalYears':fact['years'],'tracksInScope':['物理','历史'],
        'currentYearMenuEnumerated':code in ['10254','10353'],
        'finding':fact['finding'],'remainingGaps':fact['remaining'],
        'firstRecordedRequestAt':timestamps[0],'lastRecordedRequestAt':timestamps[-1],
        'elapsedEvidenceSpanSeconds':round((end-start).total_seconds(),2),
        'timingMethod':'已选证据首末请求的交错执行时间跨度，含其他学校工作，非独占人工耗时；不能逐校求和。',
        'scopeComplete':False,'boundedReviewComplete':True,
        'failedRequests':[{'url':m['url'],'httpStatus':m.get('status'),'checkedAt':m['checkedAt']}
                          for m in school_meta if m.get('status') not in [200,201,204]],
        'queryCombinations':smu_combinations if code=='10254' else None})

assert len(audits)==len(observations)==len(targets)==30
assert set(f['schoolCode'] for f in facts)==set(targets)
assert len({r['id'] for r in scores})==69
for r in scores:
    assert r['year']==2026 and r['province']=='广西' and r['group'] is None and r['rank'] is None
    assert 0<=r['score']<=750
    if r['sourceMaximumScore'] is not None:assert r['score']<=r['sourceMaximumScore']<=750
    if r['sourceAverageScore'] is not None:assert r['score']<=r['sourceAverageScore']<=r['sourceMaximumScore']
    assert '、' not in r['major'] and '预科' not in r['major']
    assert not ('admittedCount' in r or 'plannedCount' in r)
    assert not r['scoreEvidenceGaps'] and not r['conflictFields']

for name,data in [('major-cutoffs-upsert.json',scores),('sources.json',sources),('source-manifest.json',manifest),
                  ('school-audit-notes.json',audits),('observations.json',observations),
                  ('evidence-rows.json',evidence),('excluded-rows.json',excluded),
                  ('group-admission-candidates.json',groups),
                  ('targets-public.json',[{'schoolCode':k,'school':v} for k,v in targets.items()])]:write(name,data)
stats={'majorRows':len(scores),'schoolsWithNewMajorScores':len(set(r['schoolCode'] for r in scores)),
       'majorRowsBySchool':dict(collections.Counter(r['school'] for r in scores)),
       'majorRowsByTrack':dict(collections.Counter(r['track'] for r in scores)),
       'groupCandidates':len(groups),'auditedSchools':len(audits),'sourceRecords':len(sources),
       'auditStatuses':dict(collections.Counter(r['status'] for r in audits))}
write('QA.json',{'checkedAt':NOW,'status':'passed-local-schema-and-source-checks','statistics':stats,
      'checks':{'yearAndProvinceFilteredPerRow':True,'archiveHashesVerified':True,
                'sourceFieldMappingForAllRows':True,'minimumMaximumAverageOrder':True,
                'noGroupOrRankInferred':True,'noCountsRepurposed':True,'noPriorYearImported':True,
                'onlyStatisticalFactsInPublicPackage':True,'all30HaveBoundedAudit':True,
                'smu16MenuCombinations':True,'zjgs32RowsMinus2Preparatory':True,
                'cafa3ImageRowsIndependentReviewByParent':True,'zjgsCharter2PagesVisuallyReviewed':True},
      'limitations':['独立复核不等于全渠道完整收录；30校均保留scopeComplete=false。',
                     'currentYearMenuEnumerated只表示本年查询源取得/筛选，不表示大学所有渠道已穷尽。',
                     'raw和会话材料不在公有白名单；导入预检结果另见preflight.json。']})
print(json.dumps(stats,ensure_ascii=False,indent=2))
