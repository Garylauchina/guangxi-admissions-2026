#!/usr/bin/env python3
"""Import explicit public research outputs. Never imports parent project/private data."""
import argparse
import json
import os
import tempfile
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
base_plans = read('plans','plans.json')
base_scope = {(r['school'],r['track'],r['batch']) for r in base_plans}
# Keep the admissions bulletin's plan figures in major-cutoffs details, while
# avoiding duplicate plan rows where a dedicated pre-admission plan was collected.
supplement_plans = [r for r in read('cutoffs','plans-supplement.json',True)
                    if (r['school'],r['track'],r['batch']) not in base_scope]
payloads = {
    'cutoffs': read('cutoffs','cutoffs-all.json'),
    'plans': base_plans + supplement_plans,
    'major-cutoffs': read('cutoffs','major-cutoffs.json') + read('plans','majorCutoffs.json',True),
    'special-programs': read('special','special-programs.json'),
    'policies': read('special','policies.json'),
}
for name, rows in payloads.items():
    ids=set()
    for row in rows:
        assert row.get('year') == 2026, f'Missing/wrong year in {name}: {row.get("id")}'
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
        for score in row.get('scoreRecords', []):
            assert score.get('year') == 2026
            for sid in score.get('sourceIds', []):
                assert sid in sources, f'Missing special-score source {sid}'
# Validate the complete snapshot before replacing any published input. Missing
# optional research must never silently erase a whole existing dataset.
payloads['sources'] = list(sources.values())
with tempfile.TemporaryDirectory(dir=ROOT / 'site/data') as staging:
    for name, rows in payloads.items():
        Path(staging, name + '.json').write_text(json.dumps(rows,ensure_ascii=False,separators=(',',':')))
    for name, rows in payloads.items():
        os.replace(Path(staging, name + '.json'), ROOT / f'site/data/{name}.json')
        print(name, len(rows))
print('Imported source snapshot only. Reapply the reviewed audit corrections and rebuild school coverage before validation/deployment.')
