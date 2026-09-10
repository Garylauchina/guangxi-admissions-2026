"""Normalize fresh public 2026 Guangxi plan queries. No inference of missing group codes."""
from collect import BASE
import json,re,hashlib,collections,datetime
plans=[];sources=[];checks=[]
def load(key,suffix='json'):return json.load(open(BASE/'raw'/f'{key}.{suffix}'))
def source(key,school,pub=None,method='公开高校招生查询表；逐行核对 2026 年与广西，保存原始响应'):
 m=load(key+'.meta');s={'id':'plan26-'+key,'title':school+'2026年广西招生计划','url':m['url'],'publishedAt':pub,'accessedAt':m['accessedAt'],'sha256':m['sha256'],'recordCount':0,'method':method,'rawFile':m['rawFile']};sources.append(s);return s

def subjects(req,track):
 req=req or ''
 # requiredSubjects lists re-selected subjects only; track already records the first subject.
 subs=[x for x in ['化学','生物','思想政治','地理'] if x in req]
 if '政治' in req and '思想政治' not in subs:subs.append('思想政治')
 if not req or req in ['物理类','历史类']:return [],'unknown'
 if '不限' in req or '不提' in req:return [],'none'
 if not subs and (re.fullmatch(r'(首选)?(物理|历史)(类)?',req) or '1门科目必须选考' in req):return [],'none'
 subs=['政治' if x=='思想政治' else x for x in subs]
 return subs,'any' if ('或' in req or '其中一' in req) and len(subs)>1 else 'all' if subs else 'unknown'

def add(src,code,school,track,major,count,batch='本科普通批',group=None,majorCode=None,req='',tuition=None,duration=None,note='',category='普通类',rawId=None):
 if track not in ['物理','历史']:return
 if not str(count).isdigit() or int(count)<=0:return
 group=str(group) if group and re.fullmatch(r'\d{3}',str(group)) else None
 required,rule=subjects(req,track)
 if not group:
  hit=re.search(r'专业组(?:号)?[：:]\s*(\d{3})',note)
  if hit:group=hit[1]
 batch={'本科综合':'本科普通批','普通本科批':'本科普通批','本科批':'本科普通批'}.get(batch,batch)
 # Some official public APIs put the plan category in major/exam_direction while plan_type is generic.
 # Major includes exam_direction where that field exists. Use only explicit labels, never infer a group.
 if category in ('普通类', '非定向', ''):
  for marker,label in [('精准专项','精准专项'),('国家专项','国家专项计划'),('地方专项','地方专项计划'),('中外合作','中外合作办学'),('民族班','民族班'),('公费师范','地方公费师范生'),('免费医学定向','免费医学定向生'),('少数民族预科','少数民族预科班')]:
   if marker in major:
    category=label
    break
 row=dict(id='',year=2026,schoolCode=code,school=school,track=track,batch=batch,group=group,major=major,majorCode=majorCode or None,requiredSubjects=required,subjectRule=rule,plannedCount=int(count),tuition=tuition or None,duration=duration or None,note=note,sourceId=src['id'],category=category,requirementText=req or None)
 seed='|'.join(str(v) for v in [code,track,batch,group,major,category,rawId or len(plans),src['id']])
 row['id']='plan26-'+hashlib.sha256(seed.encode()).hexdigest()[:16];plans.append(row);src['recordCount']+=1

def track(s):return '物理' if '物理' in s and not re.search('艺术|体育',s) else '历史' if '历史' in s and not re.search('艺术|体育',s) else None
s=source('gxnu_plan','广西师范大学',method='官网 2026 广西招生查询 HTML，包含普通及专项；页面未给专业组码和再选科目时留空')
t=load('gxnu_plan.tables')[0];assert all(r[0]=='2026' for r in t[1:-1]);checks.append({'sourceId':s['id'],'rowCount':len(t)-2,'sumCount':sum(int(r[7]) for r in t[1:-1]),'sourceTotal':int(t[-1][1])})
for i,r in enumerate(t[1:-1]):add(s,'10602','广西师范大学',track(r[5]),r[2],r[7],batch=r[6],majorCode=r[1],category=r[4],note='；'.join(x for x in [r[3],r[4],r[8]] if x),rawId=i)
s=source('nnnu_plan_all','南宁师范大学');d=load('nnnu_plan_all');assert d['success'];assert all(r['nf']=='2026' and r['sf']=='广西' for r in d['list'])
checks.append({'sourceId':s['id'],'rowCount':len(d['list']),'sumCount':sum(r['jhrs'] for r in d['list']),'sourceTotal':sum(r['jhrs'] for r in d['sumLists'])})
for i,r in enumerate(d['list']):add(s,'10603','南宁师范大学',track(r['klmc']),r['zymc'],r['jhrs'],batch=r['pcmc'],group=r['zygroup'],majorCode=r['zydh'] or r['zydm'],req=r['xkkm'] or r['xkyq'],tuition=r['zyxf'],duration=r['xzmc'],category=r['zslb'],note='；'.join(str(r.get(k,'')) for k in ['remarks','zybz','reserve1','reserve2','reserve3'] if r.get(k)),rawId=i)
s=source('glut_plan','桂林理工大学');t=load('glut_plan.tables')[0];assert all(r[0]=='2026' and r[1]=='广西' for r in t[1:]);checks.append({'sourceId':s['id'],'rowCount':len(t)-1,'pagination':'pageSize=1000; response table below limit'})
for i,r in enumerate(t[1:]):add(s,'10596','桂林理工大学',track(r[4]),r[3],r[8],batch=r[6],category=r[7],note='；'.join(x for x in [r[9],'校区/培养地点：'+r[5],r[7]] if x),rawId=i)
for key in ['guet_plan','guet_national','guet_local','guet_ethnic','guet_joint','guet_preparatory']:
 s=source(key,'桂林电子科技大学');t=load(key+'.tables')[0];assert all(r[0]=='广西' and r[1]=='2026' for r in t[1:]);checks.append({'sourceId':s['id'],'rowCount':len(t)-1})
 for i,r in enumerate(t[1:]):add(s,'10595','桂林电子科技大学',track(r[4]),r[5],r[7],batch=r[3],category=r[2],req=r[6],note=r[8],rawId=i)
for path in sorted((BASE/'raw').glob('gxmzu_plan_[0-9]*.json')):
 key=path.stem
 if not re.fullmatch(r'gxmzu_plan_\d+',key):continue
 s=source(key,'广西民族大学');d=load(key)['data'];rs=d['dataSource'];assert all(r['year']=='2026' and r['province']=='45' for r in rs)
 checks.append({'sourceId':s['id'],'rowCount':len(rs),'sumCount':sum(int(r['jhsgf']) for r in rs),'sourceTotal':sum(int(r['jhsgf']) for r in d['overview'])})
 for r in rs:add(s,'10608','广西民族大学',track(r['subjects']),r['major']+('（'+r['exam_direction']+'）' if r['exam_direction'] else ''),r['jhsgf'],batch=r['batch'],group=r['major_group'],majorCode=r['major_num'] or r['major_code'],req=r['kskmyqzwgf'],tuition=r['fee_standard'],duration=r['educational_code'],category=r['plan_type'] if r['plan_nature']=='非定向' else r['plan_nature'],note='；'.join(str(r.get(k,'')) for k in ['major_remark','school_location','wyyzgf','remark'] if r.get(k)),rawId=r['id'])
# Extra collectors may provide an already normalized, public-only source bundle.
for p in sorted(BASE.glob('supplement-*.json')):
 d=json.load(open(p));plans.extend(d['plans']);sources.extend(d['sources']);checks.extend(d.get('checks',[]))
assert all(c.get('sumCount')==c.get('sourceTotal') for c in checks if 'sourceTotal'in c)
assert len({r['id'] for r in plans})==len(plans)
assert all(r['year']==2026 and r['track'] in ['物理','历史'] for r in plans)
source_ids={s['id'] for s in sources};assert all(r['sourceId'] in source_ids for r in plans)
for s in sources: s['recordCount']=sum(r['sourceId']==s['id'] for r in plans)
coverage=[]
for code in sorted({r['schoolCode'] for r in plans}):
 rs=[r for r in plans if r['schoolCode']==code];coverage.append({'schoolCode':code,'school':rs[0]['school'],'planRows':len(rs),'plannedCount':sum(r['plannedCount'] for r in rs),'tracks':sorted({r['track'] for r in rs}),'withGroupCode':sum(bool(r['group']) for r in rs),'completeProvinceCoverage':False})
report={'year':2026,'checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'schoolCount':len(coverage),'planRows':len(plans),'plannedCount':sum(r['plannedCount'] for r in plans),'rowsWithGroupCode':sum(bool(r['group']) for r in plans),'checks':checks,'coverage':coverage,'limitations':['仅收录已取得官方公开来源的专业计划，非全区完整招生计划库。','普通物理/历史科类单独筛选，艺术体育及不分科类记录未混入。','requiredSubjects仅列再选科目；首选科目见track；未知要求subjectRule=unknown。','专业组码未知时为null，禁止按院校最低线推定专业录取线。','tuition和duration保留官方原文，未公布时null；计划数不同于最终录取人数。']}
for file,data in [('plans.json',plans),('sources.json',sources),('validation.json',report),('coverage.json',coverage),('majorCutoffs.json',[])]:
 (BASE/file).write_text(json.dumps(data,ensure_ascii=False,indent=2))
print(json.dumps({k:report[k] for k in ['schoolCount','planRows','plannedCount','rowsWithGroupCode']},ensure_ascii=False))
