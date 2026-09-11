#!/usr/bin/env python3
"""Read-only independent C audit, standard library only; raw archives stay local.

No collector parser or derived evidence file is imported. Image values come from
the reviewer's independent full visual reading in the companion TSV. Re-running
checks numerical transcription, not a new visual reading of the source images.
"""
from pathlib import Path
from html.parser import HTMLParser
from html import unescape
from collections import Counter
import csv, json, re, hashlib, datetime

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
C = BASE / 'batch-c'
checks, comparisons, inputs = [], [], {}
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p, encoding='utf-8'):
    inputs[str(p.relative_to(BASE))] = sha(p)
    return p.read_bytes().decode(encoding)
def load(p): return json.loads(read(p))
def norm(v): return re.sub(r'\s+', '', str(v or ''))
def check(name, passed, detail=None):
    checks.append(dict(name=name, passed=bool(passed), **({'detail':detail} if detail is not None else {})))
def compare(row, expected, source):
    result = []
    for field, value in expected.items():
        actual = row.get(field)
        ok = actual == value
        result.append(dict(field=field, actual=actual, sourceValue=value, passed=ok))
    comparisons.append(dict(id=row['id'], source=source, passed=all(x['passed'] for x in result), fields=result))

class Tables(HTMLParser):
    def __init__(self): super().__init__(); self.stack=[]; self.done=[]
    def handle_starttag(self, tag, attrs):
        if tag=='table': self.stack.append(dict(rows=[],row=None,cell=None))
        if not self.stack: return
        t=self.stack[-1]
        if tag=='tr': t['row']=[]
        if tag in ('td','th') and t['row'] is not None: t['cell']=dict(text='',attrs=dict(attrs))
    def handle_data(self,s):
        if self.stack and self.stack[-1]['cell'] is not None: self.stack[-1]['cell']['text']+=s
    def handle_endtag(self,tag):
        if not self.stack:return
        t=self.stack[-1]
        if tag in ('td','th') and t['cell'] is not None: t['row'].append(t['cell']); t['cell']=None
        if tag=='tr' and t['row'] is not None:t['rows'].append(t['row']);t['row']=None
        if tag=='table':self.done.append(self.stack.pop()['rows'])
def tables(html):
    parser=Tables();parser.feed(html);result=[]
    for raw_table in parser.done:
        carry={};table=[]
        for raw in raw_table:
            row={};following={}
            for c,(v,n) in carry.items():
                row[c]=v
                if n>1:following[c]=(v,n-1)
            c=0
            for cell in raw:
                while c in row:c+=1
                cs=int(cell['attrs'].get('colspan',1));rs=int(cell['attrs'].get('rowspan',1))
                v=norm(cell['text'])
                for j in range(cs):
                    row[c+j]=v
                    if rs>1:following[c+j]=(v,rs-1)
                c+=cs
            if row:table.append([row.get(i,'') for i in range(max(row)+1)])
            carry=following
        result.append(table)
    return result
def plain(html):return norm(unescape(re.sub('<[^>]*>','',html)))

rows=load(C/'major-cutoffs-upsert.json')
sources=load(C/'sources.json'); notes=load(C/'school-audit-notes.json')
source_ids={s['id'] for s in sources}
check('78 records at two schools',len(rows)==78 and Counter(r['schoolCode'] for r in rows)=={'10600':72,'12789':6})
check('Unique IDs',len({r['id'] for r in rows})==78)
check('All source references resolve',all(set(r.get('sourceIds',[])+[r['sourceId']]+[x for v in r.get('fieldSourceIds',{}).values() for x in v]) <= source_ids for r in rows))
check('Correct year and province',all(r['year']==2026 and r['province']=='广西' for r in rows))
check('Actual individual major score scope',all(r['scoreType']=='专业录取最低分' and r['scoreScaleMaximum']==750 and r['scoreComparable'] and 0<r['score']<=r['sourceMaximumScore']<=750 for r in rows))
check('Round not inferred as initial',all(r['round']=='录取汇总（轮次未分）' for r in rows))
check('No invented rank, mean or plan count',all(r.get('rank') is None and r.get('sourceAverageScore') is None and r.get('plannedCount') is None for r in rows))
check('Positive admitted count',all(r['admittedCount']>0 for r in rows))
check('No group reference promoted to actual score',all(r.get('referenceScore') is None and r.get('matchedGroupId') is None for r in rows))
check('Local review date and stable note type',all(str(n['checkedAt']).startswith('2026-09-12') and n['auditKind']=='major-scores' and n.get('id') for n in notes))

hash_count=0
for s in sources:
    if not s.get('archiveFile'):continue
    path=C/s['archiveFile'];inputs[str(path.relative_to(BASE))]=sha(path)
    check('Archived source SHA256 '+s['id'],sha(path)==s.get('archiveSha256',s.get('sha256')))
    hash_count+=1

html=read(C/'raw/zbti-gx.html','gb18030')
text=plain(html)
check('ZBTI source title specifies 2026', '我校2026年湖南、辽宁、重庆、广西、福建、青海6省高职（专科）录取情况' in text)
table=[t for t in tables(html) if t and t[0]==['省份','科类','序号','专业','计划数','录取数','最高分','最低分']][0]
gx=[(i,t) for i,t in enumerate(table) if t[0]=='广西']
check('Six directly labelled Guangxi rows',len(gx)==6)
for index,t in gx:
    found=[r for r in rows if r['schoolCode']=='12789' and r['major']==t[3] and r['track']==t[1][:2]]
    check('ZBTI unique '+t[1]+t[3],len(found)==1)
    r=found[0]
    compare(r,dict(year=2026,province='广西',track=t[1][:2],sourceTrack=t[1],major=t[3],sourceSequence=t[2],sourceRow=index+1,
                   admittedCount=int(t[5]),sourceMaximumScore=int(t[6]),score=int(t[7]),rank=None,group=None,plannedCount=None,
                   round='录取汇总（轮次未分）',admissionType='普通类'), 'batch-c/raw/zbti-gx.html')
check('ZBTI explicit plan equals admission in these six cells but not copied into plan count',all(int(t[4])==1 for _,t in gx))
zcharter=plain(read(C/'raw/zbti-charter.html','gb18030'))
check('ZBTI official school code and 2026 charter', '12789' in zcharter and '2026年普通高校招生章程' in zcharter)
check('ZBTI admission score and English teaching rules', '投档成绩' in zcharter and '英语' in zcharter)
check('ZBTI exact provincial batch not inferred',all(r['batch']=='高职（专科）（批次待核）' for r in rows if r['schoolCode']=='12789'))

early=plain(read(C/'raw/gxtcmu-early.html'))
check('GXT original title/body year province and counts', '我校2026年在广西本科提前批共录取考生111人，其中历史类36人、物理类75人' in early)
check('GXT major and track captions explicitly actual admission scores',all('2026年中医学（定向医学生）'+t+'类录取分数情况' in early for t in ['历史','物理']))
manual=list(csv.DictReader(read(HERE/'gxtcmu-independent-image-reading.tsv').splitlines(),delimiter='\t'))
check('Independent manual reading covers all 72 rows',len(manual)==72 and Counter(x['track'] for x in manual)=={'历史':28,'物理':44})
for x in manual:
    track=x['track'];source='major-c-20260912-gxtcmu-early-'+('6' if track=='历史' else '7')
    found=[r for r in rows if r['sourceId']==source and r['sourceRow']==int(x['row'])]
    check('GXT unique '+track+x['row'],len(found)==1)
    r=found[0];area=x['city']+x['county']
    compare(r,dict(year=2026,province='广西',schoolCode='10600',track=track,sourceTrack=track,group=x['group'],serviceCity=x['city'],serviceCounty=x['county'],serviceArea=area,
                   admittedCount=int(x['admitted']),sourceMaximumScore=int(x['maximum']),score=int(x['minimum']),rank=None,plannedCount=None,
                   major='中医学（定向医学生）',admissionType='定向医学生（'+area+'）',admissionCategory='农村订单定向免费医学生',
                   batch='本科提前批其他三类',round='录取汇总（轮次未分）',requirementText='首选'+track+'；原表未列再选科目',durationYears=5),
                   'batch-c/raw/gxtcmu-early-'+('6' if track=='历史' else '7')+'.png; independent full-image reading')
    check('GXT direct image group evidence '+track+x['row'],r['fieldSourceIds']['group']==[source])
    expected=dict(ruralHouseholdRequired=True,localHouseholdYearsMinimum=3,sourceCityMustMatch=x['city'],agreementRequired=True,minimumServiceYearsAfterTrainingOrMasters=6)
    check('GXT structured eligibility '+track+x['row'],all(r['eligibility'].get(k)==v for k,v in expected.items()))
check('GXT independent per-track admission totals', {t:sum(int(x['admitted']) for x in manual if x['track']==t) for t in ['历史','物理']}=={'历史':36,'物理':75})
check('GXT explicit source planned totals', {t:sum(int(x['planned']) for x in manual if x['track']==t) for t in ['历史','物理']}=={'历史':36,'物理':75})

charter=plain(read(C/'raw/gxtcmu-charter.html'));faq=plain(read(C/'raw/gx-policy-faq.html'))
segment=faq[faq.find('75.'):faq.find('78.')]
check('Official rural household and three-year eligibility', '农村' in segment and '连续3年以上户籍' in segment)
check('Official city-based source-area and agreement eligibility', '设区市' in segment and '协议' in segment)
check('Official post-training service term, not plain graduation term', '不少于6年' in segment and '规范化培训' in segment)
check('Official exact directed undergraduate batch', '本科提前批其他三类' in segment)
check('Official five-year duration', '5年' in segment)
check('GXT charter allows policy bonus and English teaching', '加分' in charter and '以英语作为外语教学语种' in charter)
check('Medical colour-vision restrictions', '色盲' in charter and '色弱' in charter)
check('Province ordinary score includes permitted policy bonus', '高考总分' in faq and '政策性加分' in faq)
excluded=load(C/'excluded-records.json')
check('All 45 filing-score source rows excluded',sum(x.get('rowCount',0) for x in excluded if x.get('schoolCode')=='10600')==45)
check('No ordinary/junior filing source admitted as actual',not any('gxtcmu-regular' in r['sourceId'] or 'gxtcmu-junior' in r['sourceId'] for r in rows))

all_pass=all(x['passed'] for x in checks) and all(x['passed'] for x in comparisons)
result=dict(reviewedAt=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),status='PASS' if all_pass else 'FAIL',
            scope='Independent full source-value review of C 78 new actual-major-score rows; public repository untouched',
            summary=dict(rows=len(rows),sourceFieldComparisons=sum(len(x['fields']) for x in comparisons),passedFieldComparisons=sum(f['passed'] for x in comparisons for f in x['fields']),
                         checks=len(checks),passedChecks=sum(x['passed'] for x in checks),sourceArchiveHashes=hash_count,
                         admittedTotal=sum(r['admittedCount'] for r in rows),gxtcmuAdmitted=111,zbtiAdmitted=6),
            correctedFindings=[dict(id='gxtcmu-physics-shangsi-score',status='closed',recordId='major-2026-0912c-10600-gxtcmu-early-7-44',fields=['score','sourceMaximumScore'],before=576,after=575,source='Original physics image last row; independently reread at enlarged size'),
                               dict(id='zbti-batch-evidence',status='closed' if all(r['batch']=='高职（专科）（批次待核）' for r in rows if r['schoolCode']=='12789') else 'open',fields=['batch'],reason='Original article states higher vocational/specialist level without an exact Guangxi batch name')],
            visualReview=dict(historyRows=28,physicsRows=44,allMergedCityGroupBoundariesChecked=True,images=['batch-c/raw/gxtcmu-early-6.png','batch-c/raw/gxtcmu-early-7.png'],readingAid='White-background previews only; original transparent images retained and hashed',
                              specialRows=['History row19 河池市宜州区/407','Physics row30 河池市宜州区/457','Physics row44 防城港市上思县/464 575/575'],
                              exclusions='Original regular and junior image headers explicitly say 首次投档; no actual score inferred from admitted count'),
            inputs=inputs,checks=checks,rows=comparisons)
(HERE/'QA.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(status=result['status'],summary=result['summary'],failedChecks=[x for x in checks if not x['passed']],failedRows=[x for x in comparisons if not x['passed']]),ensure_ascii=False,indent=2))
raise SystemExit(0 if all_pass else 1)
