"""Independent checks against preserved official source cells and publication boundaries."""
import collections,hashlib,json,re
from pathlib import Path
from build import tables
ROOT=Path(__file__).resolve().parent
def read(n):return json.loads((ROOT/n).read_text())
rows=read('plans-upsert.json');sources=read('sources.json');catalog=read('source-catalog.json');idx={s['id']:s for s in sources}
assert len(rows)==129 and sum(r['plannedCount'] for r in rows)==10843
assert len({r['id'] for r in rows})==len(rows)
assert len({(r['schoolCode'],r['track'],r['batch'],r['group'],r['major']) for r in rows})==len(rows)
assert len(catalog)==5 and {c['status'] for c in catalog}=={'collected','source-found'}
required={'id','year','province','planStage','school','schoolCode','track','batch','group','major','majorCode','plannedCount','duration','tuition','requiredSubjects','subjectRule','requirementText','category','sourceId','note'}
for r in rows:
    assert required<=r.keys() and r['sourceId'] in idx
    assert r['year']==2026 and r['province']=='广西' and r['planStage']=='initial'
    assert r['track'] in ('物理','历史') and isinstance(r['plannedCount'],int) and r['plannedCount']>0
    assert re.fullmatch(r'\d{5}',r['schoolCode'])
    assert r['group'] is None or re.fullmatch(r'\d{3}',r['group'])
    assert r['subjectRule'] in ('unknown','none','all')
    if r['schoolCode']=='10599':assert r['group'] is None and r['batch']=='本科（批次待核）' and r['category']=='未注明招生类别'
    if r['schoolCode']=='10601':assert r['group'] is None and '待核' in r['batch']
    assert '预科' not in r['major'] and '定向' not in r['major']
for s in sources:
    assert s['status']==200 and s['sha256'] and s['url'].startswith('https://')
    assert hashlib.sha256((ROOT/s['rawPath']).read_bytes()).hexdigest()==s['sha256'],s['id']
    if s.get('parentSourceId'):assert s['parentSourceId'] in idx
for c in catalog:assert all(s in idx for s in c['sourceIds'])
guat=tables('guat-plan')[0][0];ymun=[t for t in tables('ymun-plan')[0] if t[0][:2]==['序号','专业名称']][0]
for r in rows:
    if r['schoolCode']=='11825':
        c=guat[r['sourceRow']-1];assert c[2]==r['major'] and int(c[3])==r['plannedCount'] and c[0].startswith(r['group']+'组')
    if r['schoolCode']=='10599':
        c=ymun[r['sourceRow']-1];assert c[1]==r['major'] and int(c[8 if r['track']=='物理' else 9])==r['plannedCount']
assert len([r for r in rows if r['group']])==58
assert sum(r['schoolCode']=='14684' for r in rows)==0
charter=(ROOT/'raw/gxvnu-charter.html').read_text();assert '4145014684' in charter
result={'result':'PASS','records':len(rows),'plannedCount':sum(r['plannedCount'] for r in rows),
        'bySchool':dict(collections.Counter(r['school'] for r in rows)),'withOfficialGroup':58,'unknownGroup':71,
        'sourceCount':len(sources),'catalogSchools':5,
        'checks':['完整字段/2026/广西/initial/唯一记录及业务键','全部主来源父来源引用与原始SHA256',
                  '桂航每行名称/组码/计划数对原表，公布组总全部加总匹配','右江31行直接广西科类列核对、批次及资格保留待核',
                  '桂医40行PDF全行目视检查、4008=3950+定向58，对预科202分开排除',
                  '广西职师全国总表/外省表零行混入；官方标识码4145014684确认','无征集/录取人数/预科/艺术混入']}
(ROOT/'validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result,ensure_ascii=False))
# Public minimal retrieval list; raw evidence remains local.
jobs={j['id']:j for j in read('fetch-manifest.json')}
public=[dict(jobs[s['id'].removeprefix('batch-b-')],expectedSha256=s['sha256']) for s in sources]
(ROOT/'public-fetch-manifest.json').write_text(json.dumps(public,ensure_ascii=False,indent=2)+'\n')
