"""Read-only value/provenance verification; writes only verification.json in this package."""
from pathlib import Path
from collections import Counter
import json,hashlib,re
R=Path(__file__).resolve().parent
rows=json.loads((R/'major-cutoffs-upsert.json').read_text());sources=json.loads((R/'sources.json').read_text());checks=[]
def ck(name,ok):
 checks.append({'check':name,'pass':bool(ok)})
 if not ok:raise AssertionError(name)
for r in rows:
 key=r['sourceId'].removeprefix('major-20260912-b-');raw=json.loads((R/'raw'/f'{key}.json').read_text());x=raw['data']['sszygradeList'][r['sourceRow']-1]
 for field,value in {'year':int(x['nf']),'province':x['ssmc'],'track':x['klmc'][:2],'major':x['zymc'],'score':float(x['minScore']),'sourceMaximumScore':float(x['maxScore']),'sourceAverageScore':float(x['avgScore']),'admittedCount':x['rs'],'sourceCategory':x['zslx'],'sourceSubjectRequirement':x['zyzname']}.items():ck(r['id']+':'+field,r[field]==value)
 ck(r['id']+':unknown-fields-not-inferred',r['group'] is None and r['rank'] is None and r['majorCode'] is None and r['plannedCount'] is None)
 ck(r['id']+':aggregated-round',r['round']=='录取汇总（轮次未分）')
 if '公费师范' in r['major']:ck(r['id']+':public-normal-type',r['admissionType']=='公费师范生' and '协议' in r['requirementText'])
 if r['sourceCategory'] in ['国家专项','高校专项']:ck(r['id']+':special-type',r['admissionType']==r['sourceCategory'] and '资格' in r['requirementText'])
for s in sources:
 if s['id'].startswith('major-20260912-b-'):
  f=R/s['archiveFile'];ck(s['id']+':sha256',hashlib.sha256(f.read_bytes()).hexdigest()==s['sha256'])
ck('32-rows-88-admitted',len(rows)==32 and sum(r['admittedCount'] for r in rows)==88)
ck('all-seven-notes-local-date',len(json.loads((R/'school-audit-notes.json').read_text()))==7 and all(n['checkedAt'].startswith('2026-09-12') for n in json.loads((R/'school-audit-notes.json').read_text())))
result={'status':'PASS','checks':checks,'summary':{'checks':len(checks),'rawValueFieldsCompared':32*10,'sourcesHashChecked':49,'rows':len(rows),'admittedCount':sum(r['admittedCount'] for r in rows),'scope':'Raw values and row interpretation only; no inference from sourceRecord or group statistics.'}}
(R/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result['summary'],ensure_ascii=False))
