#!/usr/bin/env python3
"""Import explicit public research outputs. Never imports parent project/private data."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('input_dir', type=Path, help='Directory with cutoffs/, plans/, ranks/, special/ research outputs')
args = parser.parse_args()
sources = {}

def read(folder, name, optional=False):
    path=args.input_dir / folder / name
    if optional and not path.exists():
        return []
    value=json.loads(path.read_text())
    assert isinstance(value,list), str(path)
    return value

def merge_sources(rows):
    for source in rows:
        s = dict(source)
        for key in ['rawPath','rawFile','localPath','rawFiles']:
            s.pop(key,None)
        if s['id'] in sources:
            assert sources[s['id']]['url'] == s['url'], f"Source collision {s['id']}"
        sources[s['id']]=s

merge_sources(read('cutoffs','sources.json'))
merge_sources(read('cutoffs','sources-major.json',True))
merge_sources(read('plans','sources.json',True))
merge_sources(read('ranks','sources.json'))
merge_sources(read('special','sources.json',True))
base_plans = read('plans','plans.json',True)
base_scope = {(r['school'],r['track'],r['batch']) for r in base_plans}
# Keep the admissions bulletin's plan figures in major-cutoffs details, while
# avoiding duplicate plan rows where a dedicated pre-admission plan was collected.
supplement_plans = [r for r in read('cutoffs','plans-supplement.json',True)
                    if (r['school'],r['track'],r['batch']) not in base_scope]
payloads = {
    'cutoffs': read('cutoffs','cutoffs-all.json'),
    'plans': base_plans + supplement_plans,
    'major-cutoffs': read('cutoffs','major-cutoffs.json',True) + read('plans','majorCutoffs.json',True),
    'special-programs': read('special','special-programs.json',True),
    'policies': read('special','policies.json',True),
}
for name, rows in payloads.items():
    ids=set()
    for row in rows:
        assert row.get('year',2026) == 2026, f'Wrong year in {name}: {row.get("id")}'
        assert row['id'] not in ids, f'Duplicate {name}: {row["id"]}'
        ids.add(row['id'])
        for key in ['localPath','rawPath','rawFile']:
            row.pop(key,None)
        if 'requiredSubjects' in row:
            row['requiredSubjects']=[x.replace('思想政治','政治') for x in row['requiredSubjects']]
        for score in row.get('scoreRecords', []):
            if not score.get('formula'):
                score['formulaStatus']='unverified'
                score['note']=(score.get('note','')+' 计算公式及满分口径尚未核实，保留原文数值，不跨分制比较。').strip()
        for sid in row.get('sourceIds', [row['sourceId']] if row.get('sourceId') else []):
            assert sid in sources, f'Missing source {sid}'
    (ROOT / f'site/data/{name}.json').write_text(json.dumps(rows,ensure_ascii=False,separators=(',',':')))
    print(name, len(rows))
(ROOT / 'site/data/sources.json').write_text(json.dumps(list(sources.values()),ensure_ascii=False,indent=2))
print('sources',len(sources))
