from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parent;E=R/'evidence'
def read(p):return json.loads(p.read_text())
a=read(R/'plans-upsert.json');sources=read(R/'sources.json');qa=read(R/'QA.json');checks=[]
def check(name,ok):checks.append({'check':name,'passed':bool(ok)});assert ok,name
for key in ['bit','buaa','sysu']:
 d=read(E/(key+'.json'));m=read(E/(('sysu_session' if key=='sysu' else key)+'.meta.json'))
 check(key+' 脱敏响应哈希',hashlib.sha256((E/(key+'.json')).read_bytes()).hexdigest()==m['sanitizedSha256'])
 check(key+' 无会话响应字段',not any(k in d for k in ['jessionid','jsessionid','token','csrfToken']))
for key in ['bit','buaa','hit','sysu','hust']:
 s=next(s for s in sources if s['id']=='top20-c-2026-'+key)
 file=E/(key+('.json' if key in ['bit','buaa','sysu'] else '.html'))
 check(key+' 来源哈希闭合',s['sha256']==hashlib.sha256(file.read_bytes()).hexdigest())
site=R.parents[2]/'site/data/plans.json'
if site.exists():
 ids={p['id'] for p in read(site)}
 # IDs may be present after authorized parent integration; contents must then agree.
 existing={p['id']:p for p in read(site)}
 check('现站同ID不冲突',all(p['id'] not in ids or all(existing[p['id']].get(k)==p.get(k) for k in ['schoolCode','year','major','group','plannedCount']) for p in a))
else:
 checks.append({'check':'现站同ID不冲突','passed':None,'note':'未提供现站数据文件，检查未执行；数据与来源检查仍执行。'})
check('北航软件分流收费逐项保留',sum('15000' in p.get('tuitionNote','') for p in a if p['schoolCode']=='10006')==2)
check('华科软件分学年收费',any(p['schoolCode']=='10487' and p['major']=='软件工程' and p['tuition']==5850 and '16000' in p['tuitionNote'] for p in a))
check('哈工大大湾区收费',next(p for p in a if p['schoolCode']=='10213' and p['major']=='具身智能（大湾区班）')['tuition']==6230)
qa['verificationChecks']=checks;qa['passed']=qa['passed'] and all(c['passed'] is not False for c in checks)
(R/'QA.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'passed':qa['passed'],'buildChecks':len(qa['checks']),'verificationChecks':len(checks),'rows':len(a),'seats':sum(p['plannedCount'] for p in a)},ensure_ascii=False))
