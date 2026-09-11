#!/usr/bin/env python3
"""Verify this gap-only batch and publication allowlist, without network or repo writes."""
import hashlib,json,re
from pathlib import Path
R=Path(__file__).resolve().parent
def read(n):return json.loads((R/n).read_text())
scores=read('major-cutoffs-upsert.json');sources=read('sources.json');notes=read('school-audit-notes.json');e=read('query-evidence.json')
assert scores==[] and len(notes)==7 and len(sources)==51 and e['recordCount']==0
assert {n['schoolCode'] for n in notes}=={'10141','10053','10004','10008','10027','10183','19614'}
ids={s['id'] for s in sources};assert len(ids)==len(sources)
assert len({n['id'] for n in notes})==7
for n in notes:
 assert n['year']==2026 and n['province']=='广西' and n['auditKind']=='major-scores' and n['recordCount']==0
 assert n['checkedAt'].startswith('2026-09-12') and n['checkedAt'].endswith('+08:00')
 assert n['note'] and n['checkedUrls'] and set(n['sourceIds'])<=ids
for s in sources:
 assert s['accessedAt'].startswith('2026-09-12') and s['accessedAt'].endswith('+08:00')
 assert s['url'].startswith('https://')
 for key in ['sha256','responseSha256']:assert re.fullmatch('[a-f0-9]{64}',s[key])
assert e['schools']['10183']['total']==e['schools']['10183']['rows']==1704
assert set(e['schools']['10183']['yearCounts'])=={'2022','2023','2024','2025'}
assert e['schools']['10027']['scoreYear']==2025
for q in e['schools']['19614']['queries']:assert q['xqmc']=='电子科技大学（沙河校区）' and q['nf']=='2026' and q['majorRows']==0
for fn in read('PUBLIC-FILES.json')['files']:
 p=Path(fn);assert not p.is_absolute() and '..' not in p.parts and p.parts[0] not in ('raw','__pycache__')
 text=(R/fn).read_text()
 assert ('/'+ 'Users/') not in text and ('/'+ 'home/') not in text
 assert not re.search(r'Bearer\s+[A-Za-z0-9._-]{16,}|JSESSIONID=[A-Za-z0-9]{8,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',text)
print('PASS: 7 audited schools, 0 eligible rows, 51 source refs and hashes, date/year/campus boundaries, public allowlist.')
