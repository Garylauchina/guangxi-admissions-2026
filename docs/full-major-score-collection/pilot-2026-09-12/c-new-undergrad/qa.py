"""Validate the frozen public package and the separately run read-only import report."""
import collections, hashlib, json, re
from pathlib import Path
ROOT = Path(__file__).resolve().parent
def load(name):
    return json.loads((ROOT / name).read_text())
scores, sources, notes = [load(n) for n in ['major-cutoffs-upsert.json', 'sources.json', 'school-audit-notes.json']]
assert len(scores) == 141 and len(notes) == 30
assert len({r['schoolCode'] for r in notes}) == 30
assert collections.Counter(r['schoolCode'] for r in scores) == {'10589':65,'11414':21,'10542':37,'10511':17,'10366':1}
assert len({r['id'] for r in sources}) == len(sources)
source_ids = {r['id'] for r in sources} | {'gxeea-2026-33106', 'gxeea-2026-33107'}
for row in scores + notes:
    assert all(s in source_ids for s in row['sourceIds'])
for row in scores:
    assert row['year'] == 2026 and row['province'] == '广西'
    assert row['group'] is None and row['majorCode'] is None
    assert row['scoreComparable'] is True and not row['scoreEvidenceGaps']
    if row['schoolCode'] == '10511':
        assert row['rank'] is None and re.fullmatch(r'\d+-\d+', row['sourceRankText'])
    if row['schoolCode'] == '10366':
        assert row['score'] == 602 and row['admittedCount'] == 1 and row['sourcePage'] == 2
for item in load('source-manifest.json'):
    if item['archiveFile'] and (ROOT / 'raw' / item['archiveFile']).exists():
        actual = hashlib.sha256((ROOT / 'raw' / item['archiveFile']).read_bytes()).hexdigest()
        assert actual == item['sha256'], item['name']
report = load('importer-preflight.json')
assert report['added'] == 141 and report['updated'] == 0
files = [line.strip() for line in (ROOT / 'PUBLIC-FILES.txt').read_text().splitlines() if line.strip()]
assert len(files) == len(set(files))
assert all('/' not in name and (ROOT / name).is_file() for name in files)
for name in files:
    text = (ROOT / name).read_text()
    private_path_pattern = '|'.join('/' + part + '/' for part in ['Users', 'home'])
    assert not re.search(private_path_pattern + r'|Bearer\s+[A-Za-z0-9]|spread' + r'Token=', text), name
    assert not re.search(r'(?i)(?:cookie|csrf-token|authorization)\s*[:=]\s*["\']?(?:eyJ|[A-Fa-f0-9]{24,})', text), name
qa = load('QA.json')
qa.update(status='passed', importerPreflight='passed-read-only',
          importerAdded=report['added'], importerUpdated=report['updated'],
          publicWhitelistFiles=len(files), localRawHashes='passed', privacyWhitelistScan='passed')
(ROOT / 'QA.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2)+'\n')
print('PASS: 141 rows, 30 audits, source hashes, read-only importer, public whitelist')
