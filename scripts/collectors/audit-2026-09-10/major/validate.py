"""Public-data boundary and integrity checks, independent of parsing decisions."""
import collections, hashlib, json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
def read(n):return json.loads((ROOT/n).read_text())
rows=read('corrected-major-cutoffs.json');filing=read('major-filing-cutoffs.json');plans=read('new-plan-supplement.json')
sources=read('sources.json');index={s['id']:s for s in sources};findings=read('findings.json')
assert len(index)==len(sources)
required={'id','year','school','schoolCode','track','batch','group','major','score','scoreType','plannedCount','admittedCount','sourceId','note','round','admissionType','rank','rankType','requiredSubjects','subjectRule','requirementText','scoreComparable','scoreEvidenceGaps','conflictFields','reviewedAt'}
assert len(rows)==720 and len(filing)==81 and len(plans)==20
for data in [rows,filing,plans]:assert len({r['id'] for r in data})==len(data)
for r in rows+filing:
    assert required<=r.keys(),r['id']
    assert r['year']==2026 and r['schoolCode'].isdigit() and len(r['schoolCode'])==5
    assert r['track'] in ('历史','物理') and 0<=r['score']<=750
    assert isinstance(r['scoreComparable'],bool)
    assert r['sourceId'] in index
    assert r['rank'] is None or (isinstance(r['rank'],int) and r['rank']>0 and r['rankType'])
    assert r['group'] is None or isinstance(r['group'],str)
    for f in ('plannedCount','admittedCount'):assert r[f] is None or isinstance(r[f],int) and r[f]>=0
    for f in ('planSourceId','qualificationSourceId'):
        if r.get(f):assert r[f] in index
    if r['admissionType']=='普通类':
        assert not any(term in r['note'] for term in ('精准专项','民族班','中外合作','国家专项','地方专项','公费师范','定向医学生')),r['id']
for r in rows:assert r['scoreType']=='专业录取最低分'
for r in filing:assert r['scoreType']=='专业投档最低分' and r['schoolCode']=='14127'
blocked=[r for r in rows if not r['scoreComparable']]
assert len(blocked)==2 and {r['major'] for r in blocked}=={'医学检验技术','预防医学'}
assert all(r['scoreEvidenceGaps'] and r['schoolCode']=='14008' for r in blocked)
assert all(r['scoreComparable'] for r in rows if r['schoolCode']=='10606')
assert len([r for r in rows if r['schoolCode']=='10598' and r['batch']=='本科提前批其他三类'])==22
assert len([r for r in rows if r['schoolCode']=='10609' and r['batch']=='本科提前批其它类（公费师范）'])==16
assert len([r for r in rows if r['schoolCode']=='10606' and r['batch']=='本科提前批其他一类'])==32
assert all(r['batch']!='本科提前批' for r in rows)
for s in sources:
    if s.get('parentSourceId'):assert s['parentSourceId'] in index
    assert s['url'].startswith('https://') and s['accessedAt'] and s['sha256']
    path=ROOT/s['rawPath']
    if not path.exists() and s['id'].startswith('gxeea-'):
        path=ROOT.parent.parent/'site-research-2026/cutoffs'/s['rawPath']
    assert path.exists(),path
    assert hashlib.sha256(path.read_bytes()).hexdigest()==s['sha256'],s['id']
for r in plans:
    original=next(x for x in rows if x['id']==r['id'].replace('audit-plan26','audit-major26'))
    assert r['plannedCount']==original['plannedCount'] and r['sourceId'] in ('ncwu-lines','lngpi-lines')
for n in findings['negativeSearches']:
    assert {'school','schoolCode','checkedAt','checkedUrls','sourceIds','result','accessLimitType'}<=n.keys()
    assert all(sid in index for sid in n['sourceIds'])
report={'result':'PASS','records':len(rows),'schools':len({r['schoolCode'] for r in rows}),'newRecords':len(rows)-253,
        'sourceCount':len(sources),'filingOnlyRecords':len(filing),'planSupplementRecords':len(plans),
        'planSupplementSeats':sum(r['plannedCount'] for r in plans),'negativeSchoolChecks':len(findings['negativeSearches']),
        'scoreNonComparable':len(blocked),'numericRankRecords':sum(r['rank'] is not None for r in rows),
        'checks':['完整字段、唯一ID、2026与科类数值边界','全部来源/辅助来源/父来源引用及本地原文件SHA256',
                  '所有普通类记录note无无关资格词','专业投档与专业录取文件分离','2条分数冲突屏蔽与玉林专业分保留',
                  '明确计划列20条104人且版本标注','13校限定范围负面检索结构完整',
                  '医大22条其他三类、玉林32条其他一类、百色16条源批次保留，无泛化提前批']}
(ROOT/'validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False,indent=2))
