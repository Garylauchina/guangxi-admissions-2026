#!/usr/bin/env python3
"""Verify frozen package facts, publication whitelist and optional local raw hashes."""
import hashlib,json,re,sys
from pathlib import Path
R=Path(__file__).resolve().parent
def read(n):return json.loads((R/n).read_text())
s=read('sources.json');n=read('school-audit-notes.json');e=read('query-evidence.json');c=read('review-context.json')
assert read('major-cutoffs-upsert.json')==[] and len(s)==51 and len(n)==7
ids={x['id'] for x in s};assert len(ids)==51 and {x['schoolCode'] for x in n}=={'10635','10359','10712','11078','10079','10403','10161'}
for x in n:
 assert x['id'].startswith('major-score-audit-20260912b3-a-') and x['auditKind']=='major-scores'
 assert x['year']==2026 and x['province']=='广西' and set(x['sourceIds'])<=ids
 assert x['checkedAt']==c['checkedAt'] and x['checkedAt'].startswith('2026-09-12') and x['checkedAt'].endswith('+08:00')
for x in s:
 assert x['id'].startswith('major-20260912b3-a-') and x['accessedAt'].endswith('+08:00')
 for f in ['sha256','archiveSha256','responseSha256']:assert re.fullmatch('[0-9a-f]{64}',x[f])
 if x['httpStatus']!=200:assert x['recordCount'] is None
 if '--raw' in sys.argv:assert hashlib.sha256((R/x['archiveFile']).read_bytes()).hexdigest()==x['sha256']
for code,count in [('10359',3),('10712',5),('10403',3)]:
 x=e['schools'][code];assert '2026' not in x['availableGuangxiYears'] and len(x['queries'])==count
 assert all(q['applicationSuccess'] and q['majorRows']==0 for q in x['queries'])
 assert len(x['oldYearControls'])==2 and all(q['majorRows']>0 for q in x['oldYearControls'])
assert e['schools']['10359']['sourceScopeWarning']=='所有分数均为第一次投档数据'
g=e['schools']['11078'];assert len(g['currentQueries'])==3 and all(q['applicationCode']=='9999' and not q['successfulArrayResponse'] for q in g['currentQueries'])
assert g['oldYearControl']['totalRows']==g['oldYearControl']['receivedRows']==17
assert e['schools']['10079']['tableYears']==[2025] and e['schools']['10079']['guangxiRows']==41
assert not e['schools']['10161']['attachmentBodyVerified'] and not e['schools']['10635']['actualScoreQueriesRun']
for fn in read('PUBLIC-FILES.json')['files']:
 p=Path(fn);assert not p.is_absolute() and '..' not in p.parts and p.parts[0] not in ['raw','__pycache__']
 t=(R/fn).read_text();assert ('/'+'Users/') not in t and ('/'+'home/') not in t
 assert not re.search(r'Bearer\s+[A-Za-z0-9._-]{16,}|JSESSIONID=[A-Za-z0-9]{8,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',t)
 if fn.endswith('.py'):compile(t,fn,'exec')
print('PASS: 7 schools, 51 sources, frozen dates, 11 valid empty arrays, 3 no-match messages, 7 positive controls, public whitelist'+('; 51 raw hashes' if '--raw' in sys.argv else ''))
