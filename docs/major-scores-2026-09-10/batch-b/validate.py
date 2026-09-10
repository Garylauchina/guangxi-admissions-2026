#!/usr/bin/env python3
"""Validate provenance, individual score boundaries, and complete source exclusions."""
from pathlib import Path
from collections import Counter
import hashlib,json,re
R=Path(__file__).resolve().parent
read=lambda f:json.loads((R/f).read_text())
rows=read('major-cutoffs-upsert.json');sources=read('sources.json');audits=read('school-audit-notes.json');excluded=read('excluded-records.json');gx=read('cqnu-guangxi-table.json')
errors=[]
def check(ok,msg):
 if not ok:errors.append(msg)
ids={s['id'] for s in sources};raw_by_row={x['sourceRow']:x['cells'] for x in gx}
check(len(rows)==11,'Expected 11 clear single-major/class results')
check(len({r['id'] for r in rows})==11,'Duplicate row id')
check(Counter(r['track'] for r in rows)=={'历史':5,'物理':6},'Track totals mismatch')
check(sum(r['round'].startswith('征集') for r in rows)==1,'Collection round lost or invented')
for r in rows:
 q=raw_by_row[r['sourceRow']]
 check(r['year']==2026 and r['province']==q[0]=='广西','Wrong source year/province')
 check(r['schoolCode']=='10637' and r['school']=='重庆师范大学','Wrong institution')
 check(r['major']==q[3] and r['score']==int(q[4]),'Major or minimum score differs from source')
 check(r['track']+'类'==q[2] and r['sourceBatch']==q[1]=='本科批','Source batch/track mismatch')
 check(r['sourceNote']==q[5] and ((q[5]=='征集')==r['round'].startswith('征集')),'Collection remark mismatch')
 check(r['scoreType']=='专业录取最低分' and r['scoreComparable'] is True and 0<r['score']<=750,'Wrong score semantics')
 check('等专业' not in r['major'] and '、' not in r['major'],'Aggregate entered as single-major score')
 check(r['group'] is None and r['rank'] is None and r['majorCode'] is None,'Unpublished group/rank/code inferred')
 check(all(r[k] is None for k in ['plannedCount','admittedCount','sourceMaximumScore','sourceAverageScore']),'Unsupported count/maximum/average supplied')
 check(r['sourceId'] in ids and all(s in ids for ss in r['fieldSourceIds'].values() for s in ss),'Broken source ref')
check(excluded['fullTableDataRows']==370 and excluded['guangxiRows']==19,'Incomplete table extraction')
check(excluded['outsideGuangxiRows']==351,'Outside Guangxi rows not fully accounted')
check(len(excluded['excludedGuangxiRows'])==8,'Expected 8 excluded Guangxi rows')
check({r['sourceRow'] for r in rows}|{r['sourceRow'] for r in excluded['excludedGuangxiRows']}==set(raw_by_row),'Missing Guangxi source rows')
check(not ({r['sourceRow'] for r in rows}&{r['sourceRow'] for r in excluded['excludedGuangxiRows']}),'Row both accepted and excluded')
check(Counter('art' if '艺术' in r['track'] else 'multi' for r in excluded['excludedGuangxiRows'])=={'art':3,'multi':5},'Exclusion categories mismatch')
check(len(audits)==6 and {a['schoolCode'] for a in audits}=={'10248','19248','10246','10335','10284','10637'},'Missing school audit')
check(all(a['checkedUrls'] and a['sourceIds'] and set(a['sourceIds'])<=ids for a in audits),'Audit without source evidence')
for s in sources:
 check(hashlib.sha256((R/s['rawFile']).read_bytes()).hexdigest()==s['sha256'],'Archive hash mismatch: '+s['id'])
 if s.get('archiveSha256'):check(s['archiveSha256']==s['sha256'] and bool(s['responseSha256']),'Raw/archive hashes not separated')
for f in (R/'raw').glob('nju-*.json'):
 if '.meta.' not in f.name:
  j=json.loads(f.read_text());check('jessionid' not in j,'Session value retained in '+f.name)
for n in ['nju-scores-gx-2026-probe-1','nju-scores-gx-2026-probe-2']:
 j=read('raw/'+n+'.json');check(j['state']==1 and j['data']['zsSsgradeList']==[] and j['data']['sszygradeList']==[],'Negative current-year probe changed; review before publishing')
whitelist=read('PUBLIC-FILES.json')['files']
check(all(not f.startswith('raw/') for f in whitelist),'Raw file entered public whitelist')
for f in whitelist:
 check((R/f).is_file(),'Missing public file '+f)
 if not (R/f).is_file():continue
 txt=(R/f).read_text()
 check(not re.search(r'[\"\x27](?:jessionid|sessionid|cookie|csrf-token)[\"\x27]\s*:\s*[\"\x27][A-Za-z0-9+/=._-]{15,}',txt,re.I),'Possible literal session value in '+f)
result={'status':'PASS' if not errors else 'FAIL','recordCount':len(rows),'schoolCount':1,'auditedSchoolCount':6,'sourceCount':len(sources),'trackCounts':dict(Counter(r['track'] for r in rows)),'roundCounts':dict(Counter(r['round'] for r in rows)),'fullSourceDataRows':370,'guangxiSourceRows':19,'excludedGuangxiRows':excluded['excludedGuangxiRows'],'outsideGuangxiExcludedRows':351,'currentYearEmptySchoolCount':5,'publicWhitelistCount':len(whitelist),'errors':errors,'limitations':['PASS仅表示本批11条及对应缺口/排除规则验证通过，不表示6校专业线全部覆盖。','重庆师大未标征集的10条不能称首轮；1条征集未分次数。','5校缺口来自当前实际读取，不等于已穷尽所有发布渠道或该校不招生。']}
(R/'QA.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='excludedGuangxiRows'},ensure_ascii=False,indent=2))
if errors:raise SystemExit(1)
