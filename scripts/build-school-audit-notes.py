#!/usr/bin/env python3
"""Build public school-level review notes from the explicitly reviewed audit bundle."""
import argparse
import json
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser();parser.add_argument('audit_dir',type=Path);args=parser.parse_args()
def read(path):return json.loads(path.read_text())
sources={s['id']:s for s in read(ROOT/'site/data/sources.json')}
notes=[]
for r in read(args.audit_dir/'major/negative-findings.json'):
    notes.append({'id':'review-major-gap-'+r['schoolCode'],'year':2026,'school':r['school'],'schoolCode':r['schoolCode'],
      'title':'专业录取资料的检索结果','status':'仍有缺口','note':r['result'],
      'accessLimitType':r['accessLimitType'],'checkedAt':r['checkedAt'],'sourceIds':r['sourceIds'],'checkedUrls':r['checkedUrls']})
groups=defaultdict(list)
for row in read(ROOT/'site/data/major-cutoffs.json'):groups[row['schoolCode']].append(row)
for code,rows in groups.items():
    pending=sum(r.get('scoreComparable') is False for r in rows)
    notes.append({'id':'review-major-collected-'+code,'year':2026,'school':rows[0]['school'],'schoolCode':code,
      'title':'已取得专业录取资料','status':'部分资料已核实',
      'note':f'本轮核对官方专业录取资料，现收录{len(rows)}条，保留各自首轮、征集或录取汇总口径；条数不等于独立专业数或完整计划覆盖。'+(f'其中{pending}条分数存在原文冲突，暂不参与分数比较。' if pending else ''),
      'checkedAt':'2026-09-10','sourceIds':sorted({r['sourceId'] for r in rows})})
groups=defaultdict(list)
for row in read(args.audit_dir/'plans/corrected-plans.json'):groups[row['schoolCode']].append(row)
for code,rows in groups.items():
    ids=set()
    for r in rows:
        ids.add(r['sourceId'])
        for refs in r.get('fieldSourceIds',{}).values():ids.update(refs)
    note=f'复查本站已收录计划及补充来源，现保留{len(rows)}条基础计划；未找到足够证据的组码、批次、选科、学费或学制继续留空或标注待核。此记录不证明该校所有招生计划已收齐。'
    if code=='10602':note+=' 67条预科直升计划已移出当前高考筛选，另修正地方公费师范生分类。'
    if code=='10606':note+=' 20条艺术体育计划已移出普通类筛选；另将公告分列的两项公费师范计划按原始招生计划合并为5人和4人。'
    if code=='10600':note+=' 分组原图补齐47条组码和42条明确体检禁忌；40条本科人数未拆分预科直升，不能当作已确认高考可填人数。'
    if code=='11548':note+=' 4条预科学制原接口写4年，但未区分预科阶段，展示为待核实并保留原值。'
    notes.append({'id':'review-plans-'+code,'year':2026,'school':rows[0]['school'],'schoolCode':code,
      'title':'已收录专业计划复查','status':'字段缺口已标注','note':note,'checkedAt':'2026-09-10','sourceIds':sorted(ids)})
notes.append({'id':'review-plans-12608','year':2026,'school':'重庆工程学院','schoolCode':'12608',
  'title':'不限选科的规则修正','status':'已修正','note':'原表6条选科明确为不限，规则统一为再选科目不限；其余未取得的学制继续待核。','checkedAt':'2026-09-10','sourceIds':['cqie-plan-2026-78111']})
for note in notes:
    assert note['sourceIds'] and all(sid in sources for sid in note['sourceIds'])
assert len({r['id'] for r in notes})==len(notes)
(ROOT/'site/data/school-audit-notes.json').write_text(json.dumps(notes,ensure_ascii=False,separators=(',',':')))
print(json.dumps({'reviewNotes':len(notes),'schoolsWithReviewNotes':len({r['schoolCode'] for r in notes})}))
