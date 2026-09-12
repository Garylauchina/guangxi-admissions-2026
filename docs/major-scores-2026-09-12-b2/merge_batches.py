"""Combine reviewed facts only; importing into the website is a separate step."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent
for filename in ['major-cutoffs-upsert.json', 'sources.json', 'school-audit-notes.json']:
    merged = {}
    for package in ['batch-a', 'batch-b', 'batch-c', 'batch-root']:
        rows = json.loads((ROOT / package / filename).read_text())
        for row in rows:
            if row['id'] in merged:
                # Different schools may cite the same existing provincial code source.
                assert filename == 'sources.json' and merged[row['id']] == row, f"Conflicting/repeated batch ID: {row['id']}"
            merged[row['id']] = row
    (ROOT / filename).write_text(json.dumps(list(merged.values()), ensure_ascii=False, indent=2) + '\n')
    print(filename, len(merged))
