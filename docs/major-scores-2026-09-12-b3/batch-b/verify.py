"""Read original retained sources and verify the frozen increment; Python stdlib."""
from pathlib import Path
from collections import Counter
import json,hashlib,re,zipfile,xml.etree.ElementTree as ET
R=Path(__file__).resolve().parent;RAW=R/'raw';checks=[];comparisons=[]
def load(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ck(n,b):checks.append({'name':n,'passed':bool(b)})
rows=load(R/'major-cutoffs-upsert.json');sources=load(R/'sources.json');notes=load(R/'school-audit-notes.json');ctx=load(R/'audit-context.json');q=load(R/'QA.json')
for r in rows:
 s=next(x for x in sources if x['id']==r['sourceId']);d=load(R/s['archiveFile']);x=d['data']['sszygradeList'][r['sourceRow']-1]
 fields={'year':int(x['nf']),'province':x['ssmc'],'track':x['klmc'][:2],'sourceTrack':x['klmc'],'major':x['zymc'],'sourceCategory':x['zslx'],'score':x['minScore'],'sourceMaximumScore':x['maxScore'],'sourceAverageScore':x['avgScore'],'sourceMajorCode':x.get('zydm') or None,'group':None,'rank':None,'admittedCount':None,'plannedCount':None,'round':'录取汇总（轮次未分）','sourceBatch':x.get('pcmc') or None}
 comparisons.append({'id':r['id'],'sourceId':r['sourceId'],'sourceRow':r['sourceRow'],'fields':[{'field':k,'expected':v,'actual':r.get(k),'passed':r.get(k)==v} for k,v in fields.items()]})
 ck('Row origin/identity '+r['id'],d['state']==1 and all(r.get(k)==v for k,v in fields.items()))
 ck('Comparison and score evidence '+r['id'],r['scoreType']=='专业录取最低分' and r['scoreScaleMaximum']==750 and r['scoreComparable'] and not r['scoreEvidenceGaps'] and not r['conflictFields'])
 ck('Unknown field boundary '+r['id'],r['majorCode'] is None and r['group'] is None and '待核' in r['batch'])
 if r['sourceCategory']=='中外合作办学':ck('Cooperation subject/transfer conditions '+r['id'],r['requiredSubjects']==['化学'] and r['subjectRule']=='all' and '非中外合作' in r['admissionRequirements'] and r['fieldSourceIds'].get('requiredSubjects'))
 if r['sourceCategory']=='普通类':ck('General note has no misleading special-route methods '+r['id'],not re.search('预科|专项|中外合作',r['note']))
for s in sources:
 if s['archiveFile']:ck('Archive '+s['id'],sha(R/s['archiveFile'])==s['archiveSha256']==s['sha256'])
 else:ck('Failure distinguished '+s['id'],s['accessOutcome']=='access-failed' and s['sha256'] is None)
for f,h in q['outputHashes'].items():ck('QA output fingerprint '+f,sha(R/f)==h)
ck('Notes use frozen same audit time',all(x['checkedAt']==ctx['reviewedAt'] for x in notes))
ck('Configured school scope',len(notes)==7 and set(x['schoolCode'] for x in notes)==set(x[0] for x in ctx['scope']))
# Read the actual workbook XML rather than the collector output.
ns={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
with zipfile.ZipFile(RAW/'njupt-2025.xlsx') as z:
 shared=ET.fromstring(z.read('xl/sharedStrings.xml'));strings=[''.join(e.itertext()) for e in shared.findall('m:si',ns)]
 title='南京邮电大学2025年各专业录取分数统计（广西）';ck('Actual workbook explicitly 2025 Guangxi',title in strings)
# No opaque session values in retained query responses.
for p in RAW.glob('shu-gx-*.html'):ck('FineUI session state redacted '+p.name,'F.f_viewState(__VIEWSTATE' not in p.read_text())
for p in RAW.glob('ouc-*.json'):
 if '.meta' in p.name:continue
 def session_keys(v):
  if isinstance(v,dict):return any(k.lower() in ['jessionid','jsessionid','csrftoken','csrf-token','sessionid'] or session_keys(x) for k,x in v.items())
  if isinstance(v,list):return any(session_keys(x) for x in v)
  return False
 ck('JSON session redacted '+p.name,not session_keys(load(p)))
fields=[x for r in comparisons for x in r['fields']]
out={'status':'PASS' if all(x['passed'] for x in checks) else 'FAIL','reviewedAt':ctx['reviewedAt'],'summary':{'rows':len(rows),'fieldComparisons':len(fields),'passedFields':sum(x['passed'] for x in fields),'checks':len(checks),'passedChecks':sum(x['passed'] for x in checks)},'checks':checks,'rowComparisons':comparisons,'inputHashes':{f:sha(R/f) for f in ['major-cutoffs-upsert.json','sources.json','school-audit-notes.json','QA.json']}}
(R/'verification.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'status':out['status'],'summary':out['summary'],'failed':[x for x in checks if not x['passed']]},ensure_ascii=False,indent=2))
if out['status']!='PASS':raise SystemExit(1)
