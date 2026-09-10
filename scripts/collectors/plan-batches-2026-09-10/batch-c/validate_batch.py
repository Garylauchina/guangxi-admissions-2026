"""Validate factual boundaries and compatibility without changing website data."""
from pathlib import Path
from collections import Counter,defaultdict
import json,re,hashlib
R=Path(__file__).resolve().parent
ROOT=next(p for p in R.parents if (p/'site/data').is_dir())
def read(p):return json.loads(p.read_text())
p=read(R/'plans-upsert.json');s=read(R/'sources.json');c=read(R/'source-catalog.json')
old=read(ROOT/'site/data/plans.json')
cut=read(ROOT/'site/data/cutoffs.json')
checks=[]
def check(name,ok,detail=None):
 checks.append(dict(name=name,pass_=bool(ok),detail=detail));assert ok,name
def key(r):return '|'.join([str(r.get('year')),str(r.get('schoolCode')),re.sub(r'[（）()\s]','',r.get('school','')),r.get('track',''),r.get('batch',''),str(r.get('group'))])
ci={key(r):r for r in cut if r['round']=='首轮'}
check('56 rows, 184 seats, 2 schools',len(p)==56 and sum(r['plannedCount'] for r in p)==184 and len({r['schoolCode'] for r in p})==2)
check('Unique row IDs',len({r['id'] for r in p})==len(p))
check('No collisions with other source collections',not ({r['id'] for r in p}&{r['id'] for r in old if not r['id'].startswith('plan26-batch-c-')}))
check('Year province and initial stage explicit',all(r['year']==2026 and r['province']=='广西' and r['planStage']=='initial' for r in p))
check('Only valid initial undergraduate tracks and positive counts',all(r['batch']=='本科普通批' and r['track'] in ['历史','物理'] and type(r['plannedCount'])==int and r['plannedCount']>0 for r in p))
check('All 56 rows map to exact existing first-round identity',all(key(r) in ci for r in p))
check('14 exact official Guangxi groups',len({key(r) for r in p})==14 and all(re.fullmatch(r'\d{3}',r['group']) for r in p))
check('Sources resolve',all(r['sourceId'] in {x['id'] for x in s} for r in p) and all(set(r['sourceIds']) <= {x['id'] for x in s} for r in c))
check('JNU ordinary 97 and national 12',sum(r['plannedCount'] for r in p if r['schoolCode']=='10559' and r['category']=='普通类')==97 and sum(r['plannedCount'] for r in p if r['schoolCode']=='10559' and r['category']=='国家专项计划')==12)
check('JNU art rows excluded exactly 4 seats',sum(r['count'] for r in read(R/'excluded-rows.json'))==4 and len(read(R/'excluded-rows.json'))==3)
check('JNU national nursing restriction retained',any(r['major']=='护理学' and '不允许转专业' in r['note'] and '色盲色弱' in r['note'] for r in p))
check('JXPU 17 rows 75 seats and unlisted electives unknown',sum(r['plannedCount'] for r in p if r['schoolCode']=='11785')==75 and all(r['subjectRule']=='unknown' for r in p if r['schoolCode']=='11785'))
check('All public plan tuition and durations preserved',all(type(r['tuition'])==int and r['tuition']>0 and r['duration'] for r in p))
check('Search-only Huzhou not imported',all(r['schoolCode']!='10347' for r in p) and next(r for r in c if r['schoolCode']=='10347')['status']=='source-found')
check('Catalog status vocabulary',all(r['status'] in ['collected','source-found','entry-only','unavailable'] for r in c))
for name,sid in [('jnu','batch-c-2026-jnu'),('jxpu','batch-c-2026-jxpu')]:
 expected=next(x for x in s if x['id']==sid)['sha256']
 check(name+' downloaded evidence SHA256',hashlib.sha256((R/'evidence'/f'{name}.html').read_bytes()).hexdigest()==expected)
groups=defaultdict(lambda:{'rows':0,'seats':0})
for r in p:groups[key(r)]['rows']+=1;groups[key(r)]['seats']+=r['plannedCount']
result={'checkedAt':'2026-09-10','status':'PASS','rows':len(p),'seats':sum(r['plannedCount'] for r in p),'groups':dict(groups),'checks':checks,'limitations':['江西职业技术大学原计划没有再选科目要求，17条保持unknown。','湖州16条仅官方搜索返回完整段，原页直读失败，移出正式新增计划。','高校公布的初始计划仍以广西招生部门最终公布及调整为准。']}
(R/'QA.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(f"PASS {len(checks)} checks; {len(p)} rows; 184 seats; {len(groups)} groups")
