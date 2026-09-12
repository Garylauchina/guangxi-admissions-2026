#!/usr/bin/env python3
"""Validate this frozen public bundle, optionally checking local raw archive hashes."""
from pathlib import Path
import hashlib,json,re,sys
R=Path(__file__).resolve().parent
def read(n):return json.loads((R/n).read_text())
scores=read('major-cutoffs-upsert.json');sources=read('sources.json');notes=read('school-audit-notes.json');e=read('query-evidence.json');c=read('review-context.json')
assert scores==[] and len(sources)==60 and len(notes)==7 and len(e['schools'])==7
ids={s['id'] for s in sources};assert len(ids)==60
assert {n['schoolCode'] for n in notes}=={'10422','10268','10590','10272','10559','10652','10019'}
for n in notes:
 assert n['id'].startswith('major-score-audit-20260912b2-a-') and n['auditKind']=='major-scores' and n['year']==2026 and n['province']=='广西'
 assert n['checkedAt']==c['checkedAt'] and n['checkedAt'].startswith(c['reviewDate']) and n['checkedAt'].endswith('+08:00')
 assert set(n['sourceIds'])<=ids and n['checkedUrls'] and n['note']
for s in sources:
 assert s['id'].startswith('major-20260912b2-a-') and re.match(r'https?://',s['url'])
 assert s['accessedAt'].endswith('+08:00')
 for k in ['sha256','archiveSha256','responseSha256']:assert re.fullmatch('[a-f0-9]{64}',s[k])
 if '--raw' in sys.argv:assert hashlib.sha256((R/s['archiveFile']).read_bytes()).hexdigest()==s['sha256']
for code,num in [('10422',9),('10019',6)]:
 d=e['schools'][code];assert d['availableGuangxiYears']==['2023','2024','2025'] and len(d['queries'])==num
 assert all(q['state']==1 and q['majorRows']==0 and q['parameters']['zsnf']=='2026' for q in d['queries'])
 assert len(d['oldYearControls'])==2 and all(q['majorRows']>0 and q['parameters']['zsnf']=='2025' for q in d['oldYearControls'])
assert e['schools']['10272']['captchaRequired'] and not e['schools']['10272']['actualScoreQueriesRun']
assert e['schools']['10590']['tableYears']==[2025,2024] and e['schools']['10559']['latestScoreYear']==2025
for fn in read('PUBLIC-FILES.json')['files']:
 p=Path(fn);assert not p.is_absolute() and '..' not in p.parts and p.parts[0] not in ['raw','__pycache__']
 t=(R/fn).read_text()
 assert ('/'+'Users/') not in t and ('/'+'home/') not in t
 assert not re.search(r'Bearer\s+[A-Za-z0-9._-]{16,}|JSESSIONID=[A-Za-z0-9]{8,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',t)
 if fn.endswith('.py'):compile(t,fn,'exec')
print('PASS: frozen dates, 7 school scopes, 60 source refs, 15 successful empty queries, 4 old controls, publication allowlist'+('; 60 raw archive hashes' if '--raw' in sys.argv else ''))
