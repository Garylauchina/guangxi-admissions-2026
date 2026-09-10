#!/usr/bin/env python3
from pathlib import Path
from collections import Counter
import hashlib,json
R=Path(__file__).resolve().parent
read=lambda p:json.loads((R/p).read_text())
p=read('plans-upsert.json');s=read('sources.json');c=read('source-catalog.json');t=read('target-results.json');manual=read('transcribed-sjtu-2026.json')
sids={x['id'] for x in s};errors=[]
def check(ok,msg):
 if not ok:errors.append(msg)
check(len(p)==30,'Expected 30 directly evidenced plan rows')
check(len({x['id'] for x in p})==len(p),'Duplicate plan id')
check(all(x['year']==2026 and x['province']=='广西' and x['planStage']=='initial' for x in p),'Wrong plan year/province/stage')
check(all(isinstance(x['plannedCount'],int) and x['plannedCount']>0 for x in p),'Invalid directly reported plan count')
check(all(x['group'] is None for x in p),'Image does not support any province group mapping')
check(all(x['subjectRule']=='unknown' and not x['requiredSubjects'] for x in p if x['schoolCode']!='10284'),'Image does not support further subject rule')
check(all(x['sourceId'] in sids and set(x['sourceIds'])<=sids for x in p),'Broken plan source link')
check(all('admittedCount' not in x and 'score' not in x for x in p),'Admission count/score leaked into plan data')
check({x['schoolCode'] for x in p}=={'10248','19248','10284'},'Wrong institution code')
check(sum(x['plannedCount'] for x in p if x['schoolCode']=='10248')==35,'SJTU main campus Guangxi physics sum != 35')
check(sum(x['plannedCount'] for x in p if x['schoolCode']=='19248')==15,'SJTU medical Guangxi sum != 15')
check(sum(x['plannedCount'] for x in p if x['schoolCode']=='10248')+1==36,'SJTU source all-track subtotal 36 != physics 35 + history 1')
nj=read('raw/nju-gx-2026-normal.json')['data']['zsjhList'];np=[x for x in p if x['schoolCode']=='10284']
check(len(np)==12 and sum(x['plannedCount'] for x in np)==47,'NJU count/total incorrect')
for x in np:
 raw=nj[x['sourceRow']-1]
 check(x['major']==raw['zymc'] and x['plannedCount']==raw['zsjhs'],'NJU source row/name/count mismatch')
 check(x['duration']==raw['zyxz']=='四年' and x['requiredSubjects']==['化学'] and x['subjectRule']=='all','NJU duration/subject mismatch')
 check(x['tuition'] is None and x['majorCode'] is None and x['batch']=='本科（批次待核）','NJU unsupported missing field filled')
 check(x['sourceDisciplineCode']==raw['zydm'],'NJU raw discipline code mismatch')
check(len(t)==6 and len({x['cutoffId'] for x in t})==6,'Missing/duplicate locked targets')
check([x['priority'] for x in t]==[3,4,5,8,9,15],'Changed locked target priorities')
check(all(x['matchedPlanCount']==0 and x['status'] in ['source-found','entry-only'] for x in t),'Unsupported completed target status')
check(all(set(x['sourceIds'])<=sids and x['checkedUrls'] for x in t),'Broken target evidence')
check(len(c)==5 and all(set(x['sourceIds'])<=sids for x in c),'Broken school catalog')
for x in s:
 if x['rawFile']:
  check(hashlib.sha256((R/x['rawFile']).read_bytes()).hexdigest()==x['sha256'],'Raw hash mismatch '+x['id'])
 else: check(x['httpStatus']=='error' and x['sha256'] is None,'Missing raw must be explicit failed attempt '+x['id'])
check(hashlib.sha256((R/'raw/sjtu-2026-plan-image.png').read_bytes()).hexdigest()==manual['imageSha256'],'Image differs from visually reviewed transcription')
report={'status':'pass' if not errors else 'fail','planRows':len(p),'plannedCount':sum(x['plannedCount'] for x in p),'schoolRows':dict(Counter(x['schoolCode'] for x in p)),'targetCount':len(t),'matchedTargets':0,'targetStatuses':dict(Counter(x['status'] for x in t)),'sourceCount':len(s),'errors':errors,'limitations':['通过表示字段、来源引用、原始文件哈希和列小计校验通过，不表示6个专业组补齐。','图像行来自目视人工核录；离线重建会核验已审核图像哈希，图像变化须重新审阅。','再选科目、组码、学制学费和广西省内批次均未猜补。']}
(R/'QA.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False,indent=2))
if errors:raise SystemExit(1)
