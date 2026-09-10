"""Validate the published rows and, when available, their archived public bytes."""
from collect import BASE
import json, hashlib, collections, datetime

plans = json.load(open(BASE / 'plans.json'))
sources = json.load(open(BASE / 'sources.json'))
by_id = {s['id']: s for s in sources}
assert len(by_id) == len(sources)
assert len({r['id'] for r in plans}) == len(plans)
assert all(r['sourceId'] in by_id for r in plans)
assert all(r['year'] == 2026 and r['track'] in ('物理', '历史') for r in plans)
assert all(type(r['plannedCount']) is int and r['plannedCount'] > 0 for r in plans)
assert all(r['subjectRule'] in ('all', 'any', 'none', 'unknown') for r in plans)
assert all(set(r['requiredSubjects']) <= {'化学', '生物', '政治', '地理'} for r in plans)
assert all(r['group'] is None or (len(r['group']) == 3 and r['group'].isdigit()) for r in plans)
assert all(s['recordCount'] == sum(r['sourceId'] == s['id'] for r in plans) for s in sources)

# Independent review regression: explicit direction labels must survive category normalization.
finance_special = [r for r in plans if r['schoolCode'] == '11548' and '精准专项' in r['major']]
assert len(finance_special) == 19
assert all(r['category'] == '精准专项' for r in finance_special)
explicit_joint = [r for r in plans if '中外合作' in r['major']]
assert all(r['category'] == '中外合作办学' for r in explicit_joint)
assert all(r['group'] is None for r in plans if r['schoolCode'] == '11548')

verified, missing = [], []
for s in sources:
    path = BASE / s['rawFile']
    if not path.exists():
        missing.append(s['id'])
        continue
    assert hashlib.sha256(path.read_bytes()).hexdigest() == s['sha256'], s['id']
    verified.append(s['id'])

report = {
    'checkedAt': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'year': 2026, 'rowCount': len(plans), 'sourceCount': len(sources),
    'schoolCount': len({r['schoolCode'] for r in plans}),
    'structuralChecksPassed': True,
    'rawHashesVerified': len(verified), 'rawHashesNotChecked': missing,
    'financePreciseSpecialRowsVerified': len(finance_special),
    'explicitJointProgramRowsVerified': len(explicit_joint),
    'imageReview': '北部湾PDF两页、广西中医药图片和百色图片已直接查看。中医药本科2470、预科132、高职400人核对；百色只转录单一科类。',
    'completeProvinceCoverage': False,
    'limits': [
        '计划合计包含专项、预科等不同类别，不等于普通统考可填余额。',
        '广西中医药本科表明确含预科直升，但未单列直升人数。',
        '招生计划未全区覆盖；部分公开来源缺批次/组码/选科要求，保留待核。',
        'source publishedAt为页面发布日期；未知日期为null，未用访问日冒充发布日期。',
        '本报告不验证预测录取概率，不将组投档线当作专业实际录取线。'
    ]
}
(BASE / 'QA.json').write_text(json.dumps(report, ensure_ascii=False, indent=2))
print(json.dumps(report, ensure_ascii=False))
