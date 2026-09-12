"""Freeze source hashes and statistical facts; raw responses stay local."""
from pathlib import Path
import json, hashlib, re
import pdfplumber
ROOT=Path(__file__).resolve().parent
RAW=ROOT/'raw'
checks=[]
def load(n): return json.loads((RAW/n).read_text())
def save(n,x): (ROOT/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def check(n,c):
    assert c,n
    checks.append({'check':n,'passed':True})
evidence=[]
rows=load('ccmu-gx-2026-0.json')['list']
menu=load('ccmu-params-majors.json')['majorList']
check('CCMU six majors equal complete selected menu',len(rows)==6 and set(menu)=={r['majorName'] for r in rows})
for i,r in enumerate(rows,1):
    check(f'CCMU row{i} identity and range',r['year']==2026 and r['cityName']=='广西' and r['scienceClass']=='物理类' and r['type']=='普通类' and r['batch']=='本科普通批' and 0<r['lowScore']<=r['avgScore']<=r['hightScore']<=750)
    fields=['majorName','year','cityName','scienceClass','type','batch','lowScore','avgScore','hightScore','enrollNum','lowScoreRank','majorGroup','xkkm','remark']
    evidence.append({'file':'ccmu-gx-2026-0.json','sourceRow':i,'fields':{k:r[k] for k in fields}})
check('CCMU official actual score admission basis','高考实考分和专业志愿为录取依据' in (RAW/'ccmu-charter.html').read_text())
with pdfplumber.open(RAW/'snnu-current.pdf') as doc:
    page=doc.pages[1].extract_text()
    check('SNNU current PDF year and Guangxi','2026年' in page and '广西' in page)
    gx=page.split('国家公费师范生 602')[-2:]
    check('SNNU two literal programme minima','电子信息技术（中外合作办学） 563' in page and '物理学（中外合作办学） 517' in page)
    for i,(major,score) in enumerate([('电子信息技术（中外合作办学）',563),('物理学（中外合作办学）',517)],13):
        evidence.append({'file':'snnu-current.pdf','page':2,'sourceRow':i,'fields':{'majorName':major,'lowScore':score,'year':2026,'cityName':'广西','scienceClass':'物理类','type':'中外合作办学'}})
check('SNNU charter has different electronic major label','电子信息科学与技术（中外合作办学）' in (RAW/'snnu-charter.html').read_text())
queries=[]
for prefix,tr in [('sisu','物理类'),('sisu','历史类'),('snnu','理工'),('snnu','文史')]:
    for year in [2026,2025]:
        fn=f'{prefix}-gx-{year}-{tr}.json';d=load(fn)
        rr=d['data']['sszygradeList'] if prefix=='sisu' else d['list']
        check(fn+' success and expected empty/positive',(d.get('state')==1 if prefix=='sisu' else d['success'] and d['code']==200) and (len(rr)==0 if year==2026 else len(rr)>0))
        m=load(fn+'.meta.json');check(fn+' correct province/year request',m['data'].get('ssmc',m['data'].get('sf'))=='广西' and str(m['data'].get('zsnf',m['data'].get('nf')))==str(year))
        queries.append({'file':fn,'year':year,'rowCount':len(rr),'responseSuccess':True,'request':m['data']})
for fn in ['njmu-old.pdf','njucm-gx-2025.pdf','bjut-old.pdf']:
    with pdfplumber.open(RAW/fn) as doc:
        text='\n'.join(p.extract_text() or '' for p in doc.pages)
        check(fn+' old year and Guangxi', '2025' in text and '广西' in text and '2026' not in text)
metas=[]
for p in sorted(RAW.glob('*.meta.json')):
    m=json.loads(p.read_text())
    if m.get('sha256'):
        check(m['name']+' archive hash',hashlib.sha256((RAW/m['name']).read_bytes()).hexdigest()==m['sha256'])
    metas.append(m)
save('source-manifest.json',metas)
save('evidence-rows.json',evidence)
save('review-evidence.json',{'reviewedAt':'2026-09-12','checks':checks,'queries':queries,'manualReview':['SNNU PDF page2 rendered: Guangxi physical cooperative electronic 563 and physics 517; programme-name discrepancy retained.','NJMU PDF page19 rendered: Guangxi starts at2025.','NJUCM PDF page1 rendered: 2025 professional filing minima, excluded.','BJUT PDF pages1–2 extracted: Guangxi 2025 only.']})
print('PASS',len(checks),'checks',len(evidence),'rows',len(metas),'sources')
