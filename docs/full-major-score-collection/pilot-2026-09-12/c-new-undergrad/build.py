"""Offline rebuild from frozen statistical facts and public source metadata."""
import collections, datetime, json, re
from pathlib import Path
ROOT = Path(__file__).resolve().parent
DATE = '2026-09-12'
def load(name):
    return json.loads((ROOT / name).read_text())
def save(name, value):
    (ROOT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
def sid(name):
    return 'major-20260912pilot-c-' + name
targets = {r['schoolCode']: r for r in load('targets.json')}
definitions = load('audit_definitions.json')
assert set(targets) == set(definitions) and len(targets) == 30
manifest = load('source-manifest.json')
facts = load('evidence-rows.json')
actual = {r['file'].rsplit('.', 1)[0] for r in facts}
charters = {'10589': '10589-charter', '11414': '11414-charter-body-session',
            '10511': '10511-charter', '10542': '10542-charter', '10366': '10366-charter-pdf'}
headers = {'10589': '10589-query', '11414': '11414-lnfs',
           '10511': '10511-admit', '10542': '10542-form', '10366': '10366-2026'}
sources = []
for m in manifest:
    code = m['schoolCode']
    school = targets[code]['school']
    key = m['name'][len(code) + 1:]
    if m['name'] in actual:
        label = '2026广西具体专业录取最低分'
    elif 'charter' in key:
        label = '招生章程与专业录取分数口径'
    elif any(k in key for k in ['param', 'menu', 'type', 'year', 'getType', 'headers']):
        label = '公开分数查询菜单与字段配置'
    elif 'browser-observation' in key:
        label = '公开页面浏览器核查记录'
    elif any(k in key for k in ['score', 'gx2025', 'gx2026']):
        label = '公开分数查询结果核查'
    elif any(k in key for k in ['js', 'chunk', 'app']):
        label = '公开查询前端字段'
    else:
        label = '招生官网栏目与公开资料核查'
    source = {'id': sid(m['name']), 'title': school + '：' + label + '（' + key + '）',
              'url': m['url'], 'publisher': school,
              'year': 2026 if m['name'] in actual or m['name'] in charters.values() else None,
              'publishedAt': {'10366-2026': '2026-07-14', '10366-pdf': '2026-07-14',
                              '10366-charter': '2026-05-22', '10366-charter-pdf': '2026-05-22',
                              '10542-charter': '2026-05-25', '10589-charter': '2026-05-22',
                              '10511-charter': '2026-05-29',
                              '11414-charter-body-session': '2026-05-29'}.get(m['name']),
              'accessedAt': m['checkedAt'], 'sha256': m['sha256'],
              'responseSha256': m['responseSha256'], 'requestMethod': m['requestMethod'],
              'requestData': m['requestData'], 'httpStatus': m['httpStatus'],
              'evidenceRole': 'actual-major-score-source' if m['name'] in actual else 'source-review',
              'evidenceType': m['evidenceType'], 'archiveFile': m['archiveFile'],
              'notes': [m.get('observation') or definitions[code]['note']]}
    if m.get('accessFailure'):
        source['accessFailure'] = m['accessFailure']
    sources.append(source)

records = []
counts = collections.Counter()
for evidence in facts:
    code = evidence['schoolCode']
    f = evidence['fields']
    src = sid(evidence['file'].rsplit('.', 1)[0])
    charter, header = sid(charters[code]), sid(headers[code])
    if code in ['10589', '11414']:
        source_track, major, minimum = f['klmc'], f['zymc'], f['minScore']
        category = f['zylx']
        batch = f['pcmc'] or ('本科普通批' if category == '本科普通批' else '本科批（精确批次待核）')
        maximum, average = f['maxScore'], f['avgScore']
        rank = f['minOrder'] if isinstance(f['minOrder'], (int, float)) and f['minOrder'] > 0 else None
        admission = '普通类' if category == '本科普通批' else category
    elif code == '10542':
        source_track, major, minimum = f['scienceClass'], f['majorName'], f['lowScore']
        category, admission, batch = f['type'], '普通类', f['batch']
        maximum, average, rank = f['hightScore'], f['avgScore'], None
    else:
        source_track, major, minimum = f['track'], f['major'], f['minimum']
        batch = f['batch']
        category = '普通类' if code == '10366' else ('优师计划' if '优师' in batch else '公费师范')
        admission = category
        maximum, average, rank = f.get('maximum'), f.get('average'), None
    track = '物理' if '物理' in source_track or source_track == '理工' else '历史'
    code_source = 'gxeea-2026-33107' if track == '物理' else 'gxeea-2026-33106'
    refs = [src, charter, header, code_source]
    fields = {k: [src] for k in ['year', 'province', 'track', 'major', 'score', 'admissionType']}
    fields.update(schoolCode=[code_source], scoreBasis=[charter], note=refs)
    if batch != '本科批（精确批次待核）':
        fields['batch'] = [src]
    note = '学校直接发布的具体专业实际录取最低分。广西3位专业组码、广西填报专业代号和首次/征集轮次未列，保持未知。'
    requirement = '首选' + track + '；原分数表未列完整再选科目要求'
    if code in ['10589', '11414']:
        note += '原始专业组/选科名称保留为文字，不能当作广西组码；全国专业代码不当作广西填报代号。'
        if f.get('zyzname'):
            requirement += '；原表' + ('选考科目' if code == '10589' else '专业组名称') + '：' + f['zyzname']
    if code == '10511':
        note += '原表对应省排名为' + f['rankText'] + '区间，未转成单一位次。公费师范或优师资格及履约要求须另行核对。'
    if code == '10366':
        note = '官方PDF第2页广西唯一行，取平行志愿实际最低分列，首轮投档线是独立列。征集栏空白；广西组码及专业代号未列。'
    basis = '750分制普通高考总分（按2026章程专业录取口径，含认可的政策加分）'
    if code in ['11414', '10511', '10542']:
        basis = '750分制普通高考总分（按2026章程投档成绩安排专业，含认可的全国性政策加分）'
    if code == '10589':
        basis = '750分制普通高考总分（依2026章程投档分，含认可加分、不含排位小分）'
    record = {'id': f'major-20260912pilot-c-{code}-{counts[code] + 1:03d}',
              'year': 2026, 'province': '广西', 'schoolCode': code, 'school': targets[code]['school'],
              'sourceSchool': targets[code]['school'], 'track': track, 'sourceTrack': source_track,
              'batch': batch, 'round': '平行志愿（原表口径）' if code == '10366' else '录取汇总（轮次未分）',
              'group': None, 'major': major, 'majorCode': None, 'score': minimum,
              'scoreType': '专业录取最低分', 'rank': rank, 'sourceId': src, 'sourceIds': refs,
              'sourceRow': evidence['sourceRow'], 'sourceTable': evidence['sourceTable'],
              'reviewedAt': DATE, 'evidenceStatus': 'verified', 'scoreComparable': True,
              'scoreBasis': basis, 'scoreScaleMaximum': 750, 'scoreEvidenceGaps': [], 'conflictFields': [],
              'admissionType': admission, 'sourceCategory': category,
              'requiredSubjects': [], 'subjectRule': 'unknown', 'requirementText': requirement,
              'fieldSourceIds': fields, 'sourceMaximumScore': maximum, 'sourceAverageScore': average,
              'sourceScoreHeader': '最低分', 'note': note}
    if maximum is not None:
        fields['sourceMaximumScore'] = [src]
    if average is not None:
        fields['sourceAverageScore'] = [src]
    if rank is not None:
        record['rankType'] = '最低分排名（学校公布）'
        fields['rank'] = [src, header]
    if code in ['10589', '11414']:
        record['sourceMajorCode'] = f['zydm']
        record['sourceGroupName'] = f['zyzname']
        if code == '10589':
            record['admittedCount'] = f['rs']
            fields['admittedCount'] = [src, header]
    if code == '10511':
        record['sourceRankText'] = f['rankText']
        fields['sourceRankText'] = [src]
    if code == '10366':
        record.update(sourcePage=2, plannedCount=1, admittedCount=1, sourceRound='平行志愿')
        for key in ['round', 'plannedCount', 'admittedCount']:
            fields[key] = [src]
    counts[code] += 1
    records.append(record)

audits, observations = [], []
for code, target in targets.items():
    entries = [m for m in manifest if m['schoolCode'] == code]
    urls = list(dict.fromkeys(m['url'] for m in entries))
    ids = [sid(m['name']) for m in entries]
    definition = definitions[code]
    audits.append({'id': sid('review-' + code), 'year': 2026, 'province': '广西',
                   'schoolCode': code, 'school': target['school'], 'auditKind': 'major-scores',
                   'checkedAt': DATE, 'title': '2026广西专业录取分来源核查',
                   'status': definition['status'], 'recordCount': counts[code], 'sourceIds': ids,
                   'checkedUrls': urls, 'note': definition['note'],
                   'scope': '仅列明官方入口、附件及真实查询组合；未取得不等于未招生或所有渠道未发布。'})
    timestamps = sorted(m['checkedAt'] for m in entries if m['checkedAt'] and 'T' in m['checkedAt'])
    elapsed = None
    if len(timestamps) > 1:
        elapsed = round((datetime.datetime.fromisoformat(timestamps[-1]) - datetime.datetime.fromisoformat(timestamps[0])).total_seconds(), 2)
    observations.append({'schoolCode': code, 'school': target['school'], 'checkedOn': DATE,
                         'status': definition['status'], 'newMajorScoreRows': counts[code],
                         'checkedUrls': urls, 'checkedRequestCount': len(entries),
                         'firstRecordedRequestAt': timestamps[0] if timestamps else None,
                         'lastRecordedRequestAt': timestamps[-1] if timestamps else None,
                         'elapsedEvidenceSpanSeconds': elapsed,
                         'timingMethod': '交错执行的首末请求证据时间跨度，含其他学校工作；非独占人工耗时，不能逐校相加。初版采集器未记录单次请求结束时间，仅一次请求时跨度置空。',
                         'failures': [{'sourceId': sid(m['name']), 'kind': m['accessFailure'],
                                       'httpStatus': m['httpStatus']} for m in entries if m.get('accessFailure')],
                         'finding': definition['note'], 'scopeComplete': False,
                         'boundedReviewComplete': True})

identities = [(r['year'], r['schoolCode'], r['track'], r['batch'], r['group'], r['major'], r['round'], r['admissionType']) for r in records]
assert len(records) == 141 and len(set(identities)) == 141
assert counts == {'10589': 65, '11414': 21, '10542': 37, '10511': 17, '10366': 1}
assert len(audits) == 30 and all(a['sourceIds'] for a in audits)
assert all(0 <= r['score'] <= 750 for r in records)
assert all(r['sourceMaximumScore'] is None or r['score'] <= r['sourceMaximumScore'] for r in records)
assert all(r['sourceAverageScore'] is None or r['score'] <= r['sourceAverageScore'] <= r['sourceMaximumScore'] for r in records)
for name, value in [('sources.json', sources), ('major-cutoffs-upsert.json', records),
                    ('school-audit-notes.json', audits), ('observations.json', observations)]:
    save(name, value)
save('QA.json', {'status': 'passed-local-assertions', 'reviewedAt': DATE,
                 'newMajorScoreRows': len(records), 'schoolCounts': dict(counts),
                 'reviewedSchools': 30, 'sources': len(sources),
                 'auditStatusCounts': dict(collections.Counter(a['status'] for a in audits)),
                 'checks': ['2026且广西实际具体专业分，未用组汇总替代', '141条身份无重复',
                            '最低最高平均分范围一致', '5校章程专业分口径已核查',
                            '湖南师范23/14专业菜单与结果完整对应', 'CUP三组合、海南五组合覆盖全部当前广西菜单',
                            '华中师范排名区间未转单点', '安徽医科PDF成绩页及章程页已渲染核对',
                            '30校均实际查过限定范围的官方入口'],
                 'limits': ['院校全渠道完整率不可据本批判断', '广西组码、广西填报代号、完整选科及轮次仍有缺口',
                            '两校当前年有效空表，一校查询入口访问失败', '逐校时间为交错证据跨度而非独占人工耗时'],
                 'importerPreflight': 'pending'})
print('Built', len(records), 'rows;', len(sources), 'sources;', len(audits), 'school audits')
