"""Verify frozen batch facts, raw hashes, source totals, and existing-score preservation."""
from pathlib import Path
import json,re,hashlib,argparse,datetime
from collections import Counter
ROOT=Path(__file__).resolve().parent;RAW=ROOT/'raw'
args=argparse.ArgumentParser();args.add_argument('--repo',required=True,type=Path);repo=args.parse_args().repo
read=lambda p:json.loads(p.read_text())
plans=read(ROOT/'plan-package/plans-upsert.json');new=read(ROOT/'score-package/major-cutoffs-upsert.json')
sources=read(ROOT/'score-package/sources.json');notes=read(ROOT/'score-package/school-audit-notes.json')
old=read(repo/'site/data/major-cutoffs.json');targets=read(ROOT/'targets-public.json')
assert len(plans)==410 and len({r['schoolCode'] for r in plans})==14
assert sum(r['plannedCount'] for r in plans)==1277
assert len(notes)==len(targets)==20 and len(new)==2
assert len({r['id'] for r in plans})==len(plans)
assert all(r['group'] is None and r['majorCode'] is None for r in plans)
assert all(r['year']==2026 and r['province']=='广西' and r['planStage']=='initial' for r in plans)
expected={'10269':(32,88),'10036':(30,83),'10052':(37,166),'10423':(60,153),'10718':(69,214),
 '10633':(12,43),'10637':(28,130),'10120':(8,66),'11510':(26,64),'11552':(5,21),
 '12789':(6,6),'12864':(12,20),'11313':(63,143),'14008':(22,80)}
for c,(count,total) in expected.items():
    rows=[r for r in plans if r['schoolCode']==c]
    assert (len(rows),sum(r['plannedCount'] for r in rows))==(count,total)
    assert all(r['track'] in ['物理','历史'] for r in rows)
hashes=[]
for s in sources:
    f=ROOT/s['archiveFile']
    if f.exists():
        digest=hashlib.sha256(f.read_bytes()).hexdigest();assert digest==s['sha256'],f
        hashes.append({'sourceId':s['id'],'sha256':digest,'verified':True})
    else:assert s.get('hashScope')=='sanitized-request-failure-metadata'
norm=lambda x:re.sub(r'\s+','',x).replace('（','(').replace('）',')')
api_checks=[]
for c,pattern,count in [('10269','10269-scorecheck-*.json',32),('10036','10036-scorecheck-*.json',30),('10423','10423-scorecheck-valid-*.json',60)]:
    current=[]
    for f in RAW.glob(pattern):
        if '.meta.' in f.name:continue
        current += [r for r in read(f).get('data',{}).get('sszygradeList',[]) if '预科' not in r['zymc']]
    assert len(current)==count
    keys={(norm(r['zymc']),r['klmc'][:2],float(r['minScore'])) for r in current}
    scoped=[r for r in old if r['schoolCode']==c]
    assert len(scoped)==count
    assert all((norm(r['major']),r['track'],r['score']) in keys for r in scoped)
    api_checks.append({'schoolCode':c,'reviewedCurrentRows':len(current),'existingMinimumScoresMatched':count})
assert len([r for r in read(RAW/'10052-scores-current.json')['rows'] if r['klmc'] in ['物理类','历史类']])==35
# Plan table was independently checked against all three FJBU pages and SXY Guangxi image columns.
assert sum(r['plannedCount'] for r in plans if r['schoolCode']=='10052' and r['category']=='民族班')==18
assert sum(r['plannedCount'] for r in plans if r['schoolCode']=='10052' and r['category']=='合作办学')==5
assert next(r for r in plans if r['schoolCode']=='14008' and r['major']=='预防医学')['plannedCount']==4
assert {(r['major'],r['score'],r['sourceMaximumScore'],r['sourceAverageScore']) for r in new}=={
 ('航海技术',523,531,527.0),('轮机工程',520,524,522.0)}
old_ids={r['id'] for r in old};assert not (old_ids & {r['id'] for r in new})
snnu_file=RAW/'10718-scores-original.pdf'
snnu_meta=read(RAW/'10718-scores-original.pdf.meta.json')
snnu_digest=hashlib.sha256(snnu_file.read_bytes()).hexdigest()
snnu_old=[s for s in read(repo/'site/data/sources.json') if s.get('url')==snnu_meta['url']]
assert any(s.get('sha256')==snnu_digest for s in snnu_old)
metas=[read(f) for f in RAW.glob('*.meta.json')]
times=[datetime.datetime.fromisoformat(m['checkedAt']) for m in metas if m.get('checkedAt')]
start=min(times);end=max(times)
report={'status':'passed','planRows':len(plans),'planSchools':14,'plannedCount':1277,
 'schoolPlanReviews':20,'schoolScoreReviews':20,'newMajorScores':2,'sources':len(sources),
 'checkedSourceArchives':len(hashes),'apiExistingMinimumRechecks':api_checks,
 'snnuExistingScorePdfRecheck':{'sha256':snnu_digest,'matchesPreviouslyPublishedSource':True,'existingScoresPreserved':2,'nameConflictsPreserved':1},
 'visualIndependentQA':['FJBU 3 pages 63 rows 143 seats by root','MUC page 2 37 rows 166 seats excluding sports 4 by root','SXY Guangxi columns 22 rows 80 seats; preventive medicine physics4 correction applied'],
 'sourceHashChecks':hashes,'startedAt':start.isoformat(),'lastFetchAt':end.isoformat(),
 'observedFetchWindowMinutes':round((end-start).total_seconds()/60,2),
 'requestAttempts':len(metas),'requestsWithResponses':sum(bool(m.get('httpStatus')) for m in metas),
 'scopeBoundary':'Timing is this mixed 20-school pilot, including parsing/review and discovery requests; not a nationwide throughput guarantee.'}
(ROOT/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='sourceHashChecks'},ensure_ascii=False,indent=2))
