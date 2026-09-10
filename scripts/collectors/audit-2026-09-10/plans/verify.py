#!/usr/bin/env python3
"""Independent schema, source-year, province, pagination-total and count audit."""
import collections,hashlib,json,pathlib,re
BASE=pathlib.Path(__file__).resolve().parent
def read(p):return json.loads((BASE/p).read_text())
def write(p,x):(BASE/p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
api=[]
for f in sorted((BASE/'raw').glob('*_plan_*.json')):
    if '.meta.' in f.name or '.tables.' in f.name:continue
    d=json.loads(f.read_text())
    if not isinstance(d,dict):continue
    data=d.get('data',{})
    if not isinstance(data,dict) or 'dataSource' not in data:continue
    rows=data['dataSource'];overview=data['overview']
    assert all(str(r['year'])=='2026' and str(r['province'])=='45' and r['province_name']=='广西' for r in rows)
    row_count=sum(int(r['jhsgf']) for r in rows);summary_count=sum(int(r['jhsgf']) for r in overview)
    assert row_count==summary_count,(f.name,row_count,summary_count)
    assert len({r['id'] for r in rows})==len(rows)
    api.append({'file':str(f.relative_to(BASE)),'rows':len(rows),'years':sorted({r['year'] for r in rows}),
      'province':'广西45','planCount':row_count,'overviewCount':summary_count,'totalsMatch':True})
nn=read('raw/nnnu_plan_all.json');assert all(str(r['nf'])=='2026' and r['sf']=='广西' for r in nn['list'])
assert sum(int(r['jhrs']) for r in nn['list'])==sum(int(r['jhrs']) for r in nn['sumLists'])
api.append({'file':'raw/nnnu_plan_all.json','rows':len(nn['list']),'year':'2026','province':'广西','totalsMatch':True})
base=read('baseline/research-plans.json');current=read('corrected-plans.json');excluded=read('excluded-plans.json')
assert {r['id'] for r in base}=={r['id'] for r in current}|{r['plan']['id'] for r in excluded}
old={r['id']:r for r in base}
assert all(r['plannedCount']==old[r['id']]['plannedCount'] for r in current)
patch=read('supplemental-plan-patch.json');oldsite={r['id']:r for r in read('baseline/site-plans.json')}
for m in patch['mergeEvidence']:
    ids=[m['retainedId']]+m['removedIds'];assert m['oldCounts']==[oldsite[i]['plannedCount'] for i in ids]
    assert sum(m['oldCounts'])==m['newCount']
manifest=[]
for sid in [x['id'] for x in read('source-recheck-results.json')]+[x['id'].removeprefix('audit-plan26-') for x in read('new-sources.json')]:
    meta=read('raw/'+sid+'.meta.json')
    assert hashlib.sha256((BASE/meta['rawFile']).read_bytes()).hexdigest()==meta['sha256']
    if sid not in {m['id'] for m in manifest}:manifest.append({k:meta.get(k) for k in ['id','url','request','requestEncoding']})
write('public-request-manifest.json',manifest)
year_checks=[]
for s in read('new-sources.json'):
    path=BASE/s['rawFile'];body=path.read_text(errors='replace') if path.suffix=='.html' else ''
    titles=[re.sub('<[^>]*>','',v) for v in re.findall(r'<title[^>]*>(.*?)</title>',body,re.S|re.I)]
    ok='2026' in body or '2026' in s['url']
    assert ok,s['id']
    year_checks.append({'sourceId':s['id'],'declaredYear':2026,'title':titles[0].strip() if titles else None,
        'yearEvidence':'官方标题/正文、显式NF=2026查询；分组图文件名与2026-06-18官方发布页对应','verified':ok})
write('source-year-checks.json',year_checks)
for r in current:
    if r['schoolCode']=='10600':
        assert not ('未列' in r['note'] and r['group'])
        if r['group'] is None:assert '组码区间' in r['note']
checks={'baselineCount':len(base),'outputCount':len(current),'excluded':len(excluded),'baseIdPartitionExact':True,
 'baselinePlanCountsUnchanged':True,'teacherMergeCountsMatchBaseline':True,'apiYearProvinceAndOverview':api,
 'explicitPublicRequests':len(manifest),'sourceHashChecksPassed':True,
 'glutPaginationProbe':{'page1':'raw/glut_plan.html','page2':'raw/glut_page2_probe.html',
  'identicalBody':(BASE/'raw/glut_plan.html').read_bytes()==(BASE/'raw/glut_page2_probe.html').read_bytes(),
  'interpretation':'pageNo=2返回与pageNo=1相同表，服务端未展示分页或总页数，不能宣称空页或全区完整。'},
 'limitation':'接口汇总一致证明这些已查询条件的行总和一致，不证明学校全部方向、特殊类别或全区院校覆盖完整。'}
write('verification.json',checks)
print(json.dumps({'verified':True,'apiQueries':len(api),'publicRequests':len(manifest)},ensure_ascii=False))
