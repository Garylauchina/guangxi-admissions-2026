"""Verify packaged claims from original responses and archive hashes, no network."""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parent;checks=[]
def get(n):return json.loads((R/n).read_text())
def ck(n,v):checks.append({'name':n,'passed':bool(v)})
sources=get('sources.json');notes=get('school-audit-notes.json');rows=get('major-cutoffs-upsert.json');ctx=get('audit-context.json')
ck('No unverified actual row',rows==[])
for s in sources:
 if s.get('archiveFile'):
  p=R/s['archiveFile'];ck('SHA '+s['id'],hashlib.sha256(p.read_bytes()).hexdigest()==s['archiveSha256'])
for slug in ['cuc','cufe','buct']:
 p=get('raw/'+slug+'-param.json')['data']['ssmc_nf_klmc_sex_campus_zslx_list']
 years=[int(k.split('_')[1]) for x in p for k in x if k.startswith('广西_')]
 ck(slug+' menu no 2026',max(years)==2025)
 for track in ['物理类','历史类']:
  d=get(f'raw/{slug}-gx-2026-{track}.json');ck(slug+' empty '+track,d['state']==1 and d['data']['sszygradeList']==[])
 for p in (R/'raw').glob(slug+'-gx-2025-*.json'):
  if p.name.endswith('meta.json'):continue
  d=json.loads(p.read_text());ck(p.stem+' positive',d['state']==1 and len(d['data']['sszygradeList'])>0)
for p in (R/'raw').glob('jnu-gx-2026-*.json'):
 if p.name.endswith('meta.json'):continue
 d=json.loads(p.read_text());ck(p.stem+' successful empty',d['code']=='1000000' and d['data']['provinceSpecializedSubjectScoreVOS']==[])
for sid,n in [(3,9),(2,1)]:
 d=get(f'raw/jnu-gx-2025-{sid}-1.json');ck('JNU old '+str(sid),d['code']=='1000000' and len(d['data']['provinceSpecializedSubjectScoreVOS'])==n)
ck('Seven targets exact',{n['schoolCode'] for n in notes}=={'10033','10295','10730','14851','10010','10034','10570'})
ck('Frozen audit time',all(n['checkedAt']==ctx['checkedAt'] for n in notes))
for n in notes:ck('References '+n['schoolCode'],bool(n['sourceIds']) and set(n['sourceIds'])<={s['id'] for s in sources})
result={'checkedAt':ctx['checkedAt'],'status':'PASS' if all(x['passed'] for x in checks) else 'FAIL','checks':checks,'summary':{'checks':len(checks),'passedChecks':sum(x['passed'] for x in checks),'newMajorRows':0}}
(R/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result['summary']));assert result['status']=='PASS'
