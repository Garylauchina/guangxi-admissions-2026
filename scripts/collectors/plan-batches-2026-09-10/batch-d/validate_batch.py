from pathlib import Path
import json,hashlib,re
R=Path(__file__).resolve().parent;ROOT=next(p for p in R.parents if (p/'site/data').is_dir())
def load(n):return json.loads((R/n).read_text())
p=load('plans-upsert.json');sources=load('sources.json');qa=[]
def check(name,ok):qa.append({'name':name,'passed':bool(ok)});assert ok,name
check('49 initial 2026 Guangxi physics rows / 531 seats',len(p)==49 and sum(x['plannedCount'] for x in p)==531 and all(x['year']==2026 and x['province']=='广西' and x['track']=='物理' and x['planStage']=='initial' for x in p))
check('All missing Guangxi group codes remain null',all(x['group'] is None and x['schoolGroupLabel'] and x['groupMissingReason'] for x in p))
check('Unique records; no collision with prior batch C',len({x['id'] for x in p})==49 and not ({x['id'] for x in p}&{x['id'] for x in json.loads((ROOT/'docs/plan-batches-2026-09-10/batch-c/plans-upsert.json').read_text())}))
check('No arts sports supplementary preparatory rows',all(x['category'] in ['普通类','中外合作办学'] and '艺术' not in x['major'] and '预科' not in x['major'] for x in p))
check('CSU rows and aggregate source counts agree',sum(x['plannedCount'] for x in p if x['schoolCode']=='10533')==321 and len([x for x in p if x['schoolCode']=='10533'])==26)
check('SCUT source has 23 rows / 210 seats',sum(x['plannedCount'] for x in p if x['schoolCode']=='10561')==210 and len([x for x in p if x['schoolCode']=='10561'])==23)
check('CSU cooperation explicitly marked 3 rows 3 seats',len([x for x in p if x['category']=='中外合作办学'])==3 and sum(x['plannedCount'] for x in p if x['category']=='中外合作办学')==3)
check('Source links resolve including identity fields',all(x['sourceId'] in {s['id'] for s in sources} and all(sid in {s['id'] for s in sources} for ids in x['fieldSourceIds'].values() for sid in ids) for x in p))
check('Missing tuition never guessed',all(x['tuition'] is None and '未列学费' in x['note'] for x in p))
check('CSU clinical biology requirements retained',all(x['requiredSubjects']==['化学','生物'] for x in p if x['schoolCode']=='10533' and x['schoolGroupLabel'].startswith('物化生')))
check('SCUT explicit no-elective group retained',next(x for x in p if x['schoolCode']=='10561' and x['major']=='大数据管理与应用')['subjectRule']=='none')
csu=load('evidence/csu.json')['data']['list']
check('CSU every original remark and direction retained',all('原表备注：' in x['note'] and x.get('rawMajor') is not None and x.get('majorDirections') is not None for x in p if x['schoolCode']=='10533'))
for key,f in [('csu','csu.json'),('scut','scut.html')]:check(key+' evidence hash matches',next(s['sha256'] for s in sources if s['id']=='batch-d-2026-'+key)==hashlib.sha256((R/'evidence'/f).read_bytes()).hexdigest())
entry=(R/'evidence/csu-entry.html').read_text();check('CSU current official page publicly configures API',all(s in entry for s in ['sch_school_id: 21393','https://job-web-api.jobpi.cn','App.init(3605)']))
result={'status':'PASS','checkedAt':'2026-09-10','rows':49,'seats':531,'checks':qa,'limitations':['49条group=null，不能据校内组名称匹配广西首轮分数。','仅物理类普通招生查询；不等于两校全部广西计划。','学费未列，全部null；中南中外合作3条显式标记。','未将大类分流专业拆成独立招生名额。']}
(R/'QA.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print('PASS',len(qa),'checks')
