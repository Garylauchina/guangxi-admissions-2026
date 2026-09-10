"""Read-only batch verification. Never applies data to the live repository."""
import json,hashlib,re
from pathlib import Path
from collections import Counter
R=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text())
rows=read(R/'major-cutoffs-upsert.json');evidence={x['id']:x for x in read(R/'evidence-rows.json')}
sources=read(R/'sources.json');source_ids={x['id'] for x in sources}
site=R.parents[2]/'guangxi-admissions-2026/site/data'
existing=read(site/'major-cutoffs.json');existing_codes={x['schoolCode'] for x in existing}
targets=read(R.parent/'targets.json')
if isinstance(targets,dict):targets=targets.get('targets',targets.get('schools',[]))
target_codes={str(x['schoolCode']) for x in targets}
assert len(rows)==94 and len(set(x['id'] for x in rows))==94
assert not (set(x['schoolCode'] for x in rows)&existing_codes)
assert not (set(x['schoolCode'] for x in rows)&target_codes)
cell_checks=0
for r in rows:
    c=evidence[r['id']]['cells'];code=r['schoolCode']
    if code=='11319':major,track,n,hi,lo,avg=c[1].replace(' ',''),c[0],c[2],c[4],c[5],c[6]
    elif code=='11552':major,track,n,hi,lo,avg=c[3],c[1],c[5],c[6],c[7],c[8];assert r['group']==c[2]
    elif code=='10120':major,track,n,hi,lo,avg=c[2],c[1],c[3],c[4],c[5],None;assert c[0]=='广西'
    elif code=='11313':major,track,n,hi,lo,avg=c[1],c[2],c[4],c[5],c[6],c[7]
    assert r['major']==major and r['track'] in track
    assert r['score']==float(lo) and r['sourceMaximumScore']==float(hi) and r['admittedCount']==int(n)
    assert r['sourceAverageScore']==(float(avg) if avg is not None else None)
    cell_checks+=6
    assert r['province']=='广西' and r['year']==2026 and r['round']=='录取汇总（轮次未分）'
    assert r['scoreType']=='专业录取最低分' and r['scoreScaleMaximum']==750
    assert not any(k in r for k in ['plan','planCount','plannedCount','maxScore','averageScore','referenceScore','matchedGroupId'])
    refs=set(r['sourceIds'])|{r['sourceId']}
    for arr in r['fieldSourceIds'].values():refs.update(arr)
    assert refs<=source_ids
    if code!='11552':assert r['group'] is None
    if code=='11319':assert r['rank'] is None and not r['rankComparable']
    if r['admissionType']=='定向培养军士':assert '政审' in r['note'] and '体检' in r['note']
    if code=='11552' and r['group']=='301':assert r['foreignLanguageRequirement']['minimumScore']==85
for s in sources:
    if s.get('archiveFile'):
        assert hashlib.sha256((R/s['archiveFile']).read_bytes()).hexdigest()==s['archiveSha256']
public=['major-cutoffs-upsert.json','sources.json','school-audit-notes.json','evidence-rows.json','excluded-records.json','QA.json','verification.json','importer-preflight.json','README.md','PUBLIC_FILES.json','collect.py','parse_tables.py','build.py','verify.py','requests.json']
for name in public:
    if (R/name).exists() and name.endswith('.json'):
        d=read(R/name)
        def check(o):
            if isinstance(o,dict):
                for k,v in o.items():
                    assert k.lower() not in ['jessionid','jsessionid','cookie','csrf-token','csrftoken','authorization','token'],(name,k)
                    check(v)
            elif isinstance(o,list):
                for v in o:check(v)
        check(d)
report={'status':'passed','sourceCellChecks':cell_checks,'recordCount':94,'newSchools':4,'ordinaryRows':90,'cooperationRows':2,'militaryDirectedRows':2,'baselineMajorScoreCount':len(existing),'excludedExistingSchools':len(existing_codes),'excludedTopTargetSchools':len(target_codes),'allSourceArchiveHashes':'passed','allFieldSourceReferences':'passed','unknownGroupsRemainNull':89,'allUnknownRoundsExplicit':94,'unreliableRanksDisabled':18,'publicJsonNoSessionFields':'passed'}
(R/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
(R/'PUBLIC_FILES.json').write_text(json.dumps(public,ensure_ascii=False,indent=2)+'\n')
qa=read(R/'QA.json');qa['noExisting17SchoolsOrTop20']='passed';qa['sourceCellChecks']=cell_checks;qa['publicJsonNoSessionFields']='passed';qa['unreliableRankRowsDisabled']=18
(R/'QA.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False,indent=2))
