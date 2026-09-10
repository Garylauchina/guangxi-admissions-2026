#!/usr/bin/env python3
"""Validate frozen batch and publication allowlist without network or website writes."""
import collections, hashlib, json, re
from pathlib import Path
R=Path(__file__).resolve().parent
def read(n):return json.loads((R/n).read_text())
a=read('major-cutoffs-upsert.json');ss=read('sources.json');notes=read('school-audit-notes.json')
assert len(a)==38 and len(ss)==34 and len(notes)==9
ids={s['id'] for s in ss};assert len(ids)==len(ss)
for r in a:
 assert r['year']==2026 and r['province']=='广西' and r['schoolCode'] in ('10052','16302')
 assert r['scoreType']=='专业录取最低分' and r['scoreComparable'] is True and not r['scoreEvidenceGaps'] and not r['conflictFields']
 assert r['group'] is None and r['round']=='录取汇总（轮次未分）'
 assert 0<=r['score']<=r['sourceMaximumScore']<=750
 assert 'maxScore' not in r and 'averageScore' not in r
 refs=set(r['sourceIds'])|{r['sourceId']}
 for v in r['fieldSourceIds'].values():refs.update(v)
 assert refs<=ids
 if r['schoolCode']=='10052':
  assert r['rank']==int(r['sourceRecord']['minwc']) and r['rankType'] and r['fieldSourceIds']['rank']
  assert r['score']==int(r['sourceRecord']['mincj']) and r['sourceMaximumScore']==int(r['sourceRecord']['maxcj']) and r['sourceAverageScore']==int(r['sourceRecord']['avgcj'])
  assert r['sourceRecord']['year']==2026 and r['sourceRecord']['sfmc']=='广西'
  assert 'admittedCount' not in r and 'plannedCount' not in r
 else:
  assert r['rank'] is None and r['admittedCount']==int(r['sourceRecord']['录取数']) and r['plannedCount']==int(r['sourceRecord']['计划数'])
  assert r['majorType']=='正式招生大类'
for n in notes:
 assert n['auditKind']=='major-scores' and n['checkedAt'].startswith('2026-09-11') and n['checkedAt'].endswith('+08:00')
 assert set(n['sourceIds'])<=ids
 assert n['recordCount']==sum(r['schoolCode']==n['schoolCode'] for r in a)
for s in ss:
 assert s['accessedAt'].startswith('2026-09-11')
 for field in ('sha256','responseSha256'):assert re.fullmatch('[a-f0-9]{64}',s[field])
 if s.get('archiveFile'):assert hashlib.sha256((R/s['archiveFile']).read_bytes()).hexdigest()==s['sha256']
allowed=read('PUBLIC-FILES.json')['files']
for fn in allowed:
 p=Path(fn);assert not p.is_absolute() and '..' not in p.parts and p.parts[0] not in ('raw','__pycache__')
 text=(R/fn).read_text()
 assert ('/'+ 'Users/') not in text and ('/'+ 'home/') not in text
 assert not re.search(r'(?:Bearer\s+[A-Za-z0-9._-]{16,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|JSESSIONID=[A-Za-z0-9]{8,})',text)
print('PASS: 38 rows, 9 school notes, source fields/hashes, source-year/track/category, 35 explicit ranks, public allowlist.')
