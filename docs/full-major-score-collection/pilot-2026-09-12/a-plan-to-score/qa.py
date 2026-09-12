#!/usr/bin/env python3
"""Offline fact and provenance checks; does not change the live dataset."""
import collections, hashlib, json, pathlib
ROOT=pathlib.Path(__file__).resolve().parent
def read(name):return json.loads((ROOT/name).read_text())
targets=read('targets.json'); observations=read('observations.json')
sources=read('sources.json'); audits=read('school-audit-notes.json')
majors=read('major-cutoffs-upsert.json'); filing=read('supplementary-major-filing.json')
manifest=read('fetch-manifest.json');index={r['id']:r for r in manifest}
assert len(targets)==20 and len(observations)==20 and len(audits)==20
assert {r['schoolCode'] for r in targets}=={r['schoolCode'] for r in audits}
assert all(r['http200Responses']>0 for r in observations)
assert len(majors)==117 and all(not r['scoreComparable'] for r in majors)
assert len(filing)==55 and sum(not r['scoreComparable'] for r in filing)==1
for source in sources:
    path=ROOT/index[source['id']]['rawFile']
    assert hashlib.sha256(path.read_bytes()).hexdigest()==source['sha256']
for row in majors:
    raw=read(index[row['sourceId']]['rawFile'])['data']['major_data_source'][row['sourceRow']-1]
    assert raw['year']=='2026' and raw['province']=='45'
    assert raw['major']==row['major'] and float(raw['min_score'])==row['score']
    assert int(raw['lowest_position'])==row['rank']
    assert row['score']<=row['sourceAverageScore']<=row['sourceMaximumScore']
    assert row['round']=='录取汇总（轮次未分）'
    assert row['majorCode'] is None and row['group'] is None
    assert row['conflictFields']==['year','sourceTitle']
    assert row['sourceTitleYear']==2025 and row['scoreEvidenceGaps']
for code in ['10007','10006','10558','10284','10358','10002']:
    rows=[m for m in manifest if m['id'].startswith('p100a-'+code+'-scores-2026-')]
    assert rows
    for m in rows:
        r=read(m['rawFile']); assert r['state']==1
        assert r['data']['sszygradeList']==[] and r['data']['zsSsgradeList']==[]
for m in manifest:
    if m['id'].startswith('p100a-10603-query2026-'):
        r=read(m['rawFile']);assert r['code']==200 and r['success'] and r['list']==[]
assert json.loads(read(index['p100a-10602-query2026']['rawFile']))==[]
report={'checks':'passed','schools':20,'sourcesWithMatchingHash':len(sources),
        'verifiedActualRows':0,'pendingYearConflictRows':117,'filingRows':55,
        'filingBySchool':dict(collections.Counter(r['school'] for r in filing)),
        'filingNameConflictRows':1,
        'limits':'HTML原表与API字段核对；专业投档候选由根线程独立复核；年份冲突117条一律不比较。'}
(ROOT/'qa.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False))
