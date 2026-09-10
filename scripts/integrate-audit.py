#!/usr/bin/env python3
"""Integrate the explicitly reviewed 2026 audit bundle; no source scraping here."""
import argparse
import json
import os
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('audit_dir', type=Path)
args = parser.parse_args()
audit = args.audit_dir

def read(path):
    return json.loads(path.read_text())

def clean(value):
    if isinstance(value, list):
        return [clean(item) for item in value]
    if isinstance(value, dict):
        return {key: clean(item) for key, item in value.items()
                if key not in {'rawFile', 'rawPath', 'rawFiles', 'localPath'}}
    return value

sources = {row['id']: row for row in read(ROOT/'site/data/sources.json')}
for file in ['plans/new-sources.json', 'major/sources.json', 'special/sources.json']:
    for row in read(audit/file):
        if row['id'] in sources:
            assert sources[row['id']]['url'] == row['url'], f"Source identity changed: {row['id']}"
        sources[row['id']] = clean(row)

baseline_ids = {r['id'] for r in read(audit/'plans/baseline/research-plans.json')}
patch = read(audit/'plans/supplemental-plan-patch.json')
replaced = baseline_ids | set(patch['deleteIds']) | {r['id'] for r in patch['upsert']}
new_plans = read(audit/'major/new-plan-supplement.json')
replaced |= {r['id'] for r in new_plans}
plans = read(audit/'plans/corrected-plans.json') + [r for r in read(ROOT/'site/data/plans.json') if r['id'] not in replaced] + patch['upsert'] + new_plans
for row in plans:
    if row.get('sourceId') == 'cqie-plan-2026-78111' and row.get('requirementText') == '不限':
        assert row['requiredSubjects'] == []
        row['subjectRule'] = 'none'
    if row['id'] == 'plan26-0dd04deaa835e2fb':
        # The 2026 Guangxi API names the exact batch for all 22 county-specific
        # clinical-medicine directed rows; keep the original published 62 seats.
        row['batch'] = '本科提前批其他三类'
        row.setdefault('fieldSourceIds', {}).setdefault('batch', []).append('gxmu-lines-2026-valid')
        row['fieldSourceIds']['batch'] = list(dict.fromkeys(row['fieldSourceIds']['batch']))
payloads = {
    'plans': plans,
    'major-cutoffs': read(audit/'major/corrected-major-cutoffs.json'),
    'major-filing-cutoffs': read(audit/'major/major-filing-cutoffs.json'),
    'special-programs': read(audit/'special/corrected-special-programs.json'),
    'policies': read(audit/'special/policies.json'),
}

def validate_refs(value):
    if isinstance(value, list):
        for item in value:
            validate_refs(item)
    if isinstance(value, dict):
        if value.get('sourceId'):
            assert value['sourceId'] in sources, value['sourceId']
        for sid in value.get('sourceIds', []):
            assert sid in sources, sid
        for refs in value.get('fieldSourceIds', {}).values():
            for sid in refs:
                assert sid in sources, sid
        for item in value.values():
            validate_refs(item)

for name, rows in payloads.items():
    assert isinstance(rows, list) and len({r['id'] for r in rows}) == len(rows), name
    for row in rows:
        assert row.get('year') == 2026, (name, row.get('id'))
        validate_refs(row)
payloads['sources'] = list(sources.values())
with tempfile.TemporaryDirectory(dir=ROOT/'site/data') as staging:
    for name, rows in payloads.items():
        Path(staging, name+'.json').write_text(json.dumps(clean(rows), ensure_ascii=False, indent=2) + '\n' if name == 'sources' else json.dumps(clean(rows), ensure_ascii=False, separators=(',', ':')))
    for name, rows in payloads.items():
        os.replace(Path(staging, name+'.json'), ROOT/f'site/data/{name}.json')
        print(name, len(rows))
print('Next: update school audit notes, build coverage, and run data and interaction checks before deployment.')
