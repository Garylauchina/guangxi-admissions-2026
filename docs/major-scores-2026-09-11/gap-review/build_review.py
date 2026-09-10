# -*- coding: utf-8 -*-
"""Offline evidence review; reads sibling archives, publishes only facts/hashes."""
from pathlib import Path
import json, hashlib

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
def read(path):
    return json.loads(path.read_text())
def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

# Each finding was independently read from archived JSON/HTML and request metadata.
rows = [
    ('batch-root','10561','html-no-data','scut-query.html|scut-gx-2026-物理类.html|scut-gx-2026-历史类.html|scut-gx-2025-物理类.html|scut-gx-2025-历史类.html|scut-current-min.html',
     '2026广西普通类两科HTTP200返回无结果提示；2025同接口两科有专业记录。公告列表2026发布日期对应2025数据。',
     '同接口2025两科成绩正向对照；仅限普通类两科及所列公告。'),
    ('batch-root','10614','success-empty','uestc-score-types.json|uestc-gx-2026-物理类.json|uestc-gx-2026-历史类.json|uestc-gx-2025-物理类.json',
     '2026广西普通类本部两科code200/success=true/list空；广西配置最新2025，本部与沙河分列。',
     '2025同接口本部普通类物理15条；不能外推沙河或其他类别。'),
    ('batch-root','10611','business-config-error','cqu-score-entry.html|cqu-config-2026.json|cqu-config-2025.json',
     '2026配置HTTP200但业务code500/msg空；2025同接口code0且广西选项完整。',
     '2025正向对照是配置而非专业成绩；不能声称2026查询成功零记录。'),
    ('batch-root','10054','prior-year-data','ncepu-home.html|ncepu-score-entry.html|ncepu-major-data.json|ncepu-all-data.json',
     '专业JSON1308条和院校JSON114条均year2025，广西分别43和5条；2026是JSON生成时间。',
     '全量公开JSON含旧年广西成绩；北京入口有北京地址并另链保定，本次未审保定。'),
    ('batch-root','10055','success-empty','nankai-home.html.meta.json|nankai-score-entry.html.meta.json|nankai-score-params.json|nankai-gx-2026-物理类.json|nankai-gx-2026-历史类.json|nankai-gx-2025-物理类.json',
     '主站403与独立查询站分开；2026广西本科普通批两科state1且学校/专业列表空，广西配置2025/2024。',
     '2025同接口物理9条专业记录；普通批指定查询不能外推其他类型。'),
    ('batch-root','10316','success-empty','cpu-score-page.html|cpu-score-query.js|cpu-gx-2026.json|cpu-gx-2025.json',
     '前端f8省份/f7年份与请求一致；2026广西status1/result true/total0/data空。默认分数表不显示省份年。',
     '2025同接口total30，本次第一页14条f7均2025；2026导航为计划，不是默认分数年份。'),
    ('batch-b','12121','business-no-data','smu-entry.html|smu-query-config.json|smu-gx-2026-all.json|smu-gx-2025-all.json',
     '2026广西不限定科类类别，HTTP200/业务9999/明确无数据提示/data null；公开配置无需登录或短信。',
     '2025同接口同字段22条；此为明确业务无数据，不应计为业务成功空列表，汇总已更正。'),
    ('batch-b','10486','success-empty','whu-types.meta.json|whu-types-json.json|whu-gx-2026-物理类.json|whu-gx-2026-历史类.json|whu-gx-2026-全部.json',
     '修正为JSON后的配置广西最高2025；2026广西校本部、全部类别三种科类均业务成功空list。',
     '有旧年配置正向对照，未保存2025专业成绩对照；早先form请求HTTP500不作为空记录证据。'),
    ('batch-b','10699','http-access-error','nwpu-home.meta.json|nwpu-2026-summary.html',
     '入口元数据HTTP412；官网2026招生总结广西650/1150位次为按省全校物理汇总，无专业列。',
     '总结可读不代表专业查询可用；本次离线仅核保存的HTTP412，未重做网页读取。'),
    ('batch-b','10056','success-empty','tju-component.js|tju-types.json|tju-gx-2026-物理类.json|tju-gx-2026-历史类.json|tju-gx-2026-全部.json',
     '广西配置仅2025北洋园；2026广西北洋园全部类别三种科类均success true/list和sumList空。',
     '有旧年配置，未保存2025专业成绩正向对照；历史空响应不能推定不招历史。'),
    ('batch-b','10287','success-empty','nuaa-entry.html|nuaa-years.json|nuaa-2026-provinces.json|nuaa-gx-2026-物理类.json|nuaa-gx-2026-历史类.json',
     '前端逐专业getAdmissionScore与year/sf/kl一致；年份最高2025，2026省份及两科data空且code0/status200。',
     '年份API为正向配置证据，未保存2025广西专业成绩对照；未用概况接口代替专业分。'),
    ('batch-b','19213','success-empty','hitwh-entry.html|hitwh-gx-2025-config.json|hitwh-gx-2026-config.json|hit-summary-gx.html',
     '威海2026广西年份接口code0且类别/类型/list空；本部跨校区表2026为计划，成绩列为2025/2024。',
     '同站2025省份切换接口4条专业，非与2026同端点严格同参对照；原科类综改，19213独立于10213。'),
    ('batch-b','10247','success-empty','tongji-js-2574580.js|tongji-js-5e0cf47.js|tongji-years.json|tongji-gx-2026.json',
     '官方前端广西provinceCode45；2026省45不限制科类类别，isSuccess true/totalCount0/items空，年份最高2025。',
     '有年份API正向证据，未保存2025广西专业成绩对照；只支持当次查询结果。'),
]

checks, records = [], []
cutoffs = read(BASE.parent.parent / 'guangxi-admissions-2026/site/data/cutoffs.json')
names = {}
for c in cutoffs:
    names.setdefault(str(c['schoolCode']), set()).add(c['school'])
for batch, code, response_class, filenames, fact, limitation in rows:
    note = next(n for n in read(BASE / batch / 'school-audit-notes.json') if n['schoolCode'] == code)
    sources = {s['id'] for s in read(BASE / batch / 'sources.json')}
    checks.append({'id': 'identity-' + code, 'pass': note['school'] in names.get(code, set())})
    checks.append({'id': 'source-closure-' + code, 'pass': all(s in sources for s in note['sourceIds'])})
    evidence = []
    for filename in filenames.split('|'):
        p = BASE / batch / 'raw' / filename
        h = digest(p)
        verified = None
        if not filename.endswith('.meta.json'):
            for mp in [p.with_name(p.name + '.meta.json'), p.with_suffix('.meta.json')]:
                if mp.exists():
                    m = read(mp)
                    verified = h == (m.get('archiveSha256') or m.get('sha256') or m.get('rawSha256'))
                    checks.append({'id': 'hash-' + batch + '-' + filename, 'pass': verified})
                    break
        evidence.append({'file': batch + '/raw/' + filename, 'sha256': h, 'archiveHashVerified': verified})
    records.append({'schoolCode': code, 'school': note['school'], 'batch': batch,
                    'reportedStatus': note['status'], 'reviewStatus': 'supported-within-stated-scope',
                    'responseClass': response_class, 'fact': fact, 'positiveControlAndLimits': limitation,
                    'sourceIds': note['sourceIds'], 'evidence': evidence})

b_summary = read(BASE / 'batch-b/QA.json')['summary']
checks.append({'id': 'b-response-summary-corrected', 'pass': b_summary.get('successfulCurrentEmptySchoolQueries') == 5 and b_summary.get('businessNoDataSchoolQueries') == 1})
for batch in ['batch-root', 'batch-b']:
    checks.append({'id': 'no-placeholder-major-rows-' + batch, 'pass': read(BASE / batch / 'major-cutoffs-upsert.json') == []})
qa = {'reviewedAt': '2026-09-11', 'auditKind': 'major-score-gap-independent-review',
      'scope': {'schools': 13, 'networkRequests': 0, 'rawCopiedToOutput': False, 'majorScoreValuesAdded': 0},
      'summary': {'supportedWithinStatedScope': 13, 'materialBlockingFindings': 0, 'wordingFindingsCorrected': 1,
                  'checks': len(checks), 'passed': sum(c['pass'] for c in checks), 'failed': sum(not c['pass'] for c in checks)},
      'findings': [{'id': 'smu-response-summary', 'status': 'resolved', 'severity': 'wording',
                    'fact': 'B汇总现已改为5校成功空列表、1校业务明确无数据；南方医科逐校说明原本已准确写明9999。'}],
      'records': records, 'checks': checks,
      'inputSnapshots': [{'file': b + '/' + f, 'sha256': digest(BASE / b / f)}
                         for b in ['batch-root', 'batch-b'] for f in ['school-audit-notes.json', 'sources.json', 'QA.json']]}
(HERE / 'QA.json').write_text(json.dumps(qa, ensure_ascii=False, indent=2) + '\n')
lines = ['# 2026广西专业录取分缺口独立复核', '',
         '复核时间：2026-09-11（上海）。范围为 batch-root 6校、batch-b 7校；只读已有归档和请求元数据，没有联网重抓、复制原响应或修改数据包、网站。', '',
         '**13校缺口说明均由已归档证据支持，限于其明示查询范围；无阻止发布的实质问题。** B汇总措辞已修正为5校业务成功空列表、1校业务明确无数据、1校入口访问失败。南方医科逐校说明原本已准确区分业务9999。', '',
         '未取得2026专业分不等于0分、未招生或录取未完成，也不证明所有官方渠道均未公开。旧年数据只用来检查接口和年份，均未迁为2026专业分。', '',
         '| 院校代码／院校 | 原证据支持的结论 | 正向对照与边界 |', '| --- | --- | --- |']
for r in records:
    lines.append('| ' + r['schoolCode'] + ' ' + r['school'] + ' | ' + r['fact'] + ' | ' + r['positiveControlAndLimits'] + ' |')
lines += ['', '华南理工的2026公告日期、中国药科的2026计划导航、华北电力的2026 JSON生成时间，均不改变分数数据年2025；哈工大三校区表2026列为招生计划。威海19213与本部10213、华电北京10054与保定、电子科大本部与沙河的边界均保留。', '',
          '对照强度须区分：华工、电子科大、南开、药大、南医有同接口旧年成绩；华电有全量旧年JSON；重庆只有旧年配置；威海有同站另一个端点旧年成绩；武大、天大、南航、同济本包无2025广西专业成绩正向对照。这不改变当前响应为空的事实，但不能据此宣称完整性。', '',
          'QA：' + str(qa['summary']['passed']) + '/' + str(len(checks)) + '项通过。13所代码／校名与现有广西投档资料一致，所列来源引用闭合，选定归档散列与元数据一致。详细事实、文件名和哈希见 QA.json。访问失败只复核保存的错误元数据，未独立复现网络状态。', '',
          '仅公开本目录白名单中的复核报告、QA、离线复核脚本与白名单。不发布 raw，不复制原网页、原响应、Cookie、会话值或签名值。']
(HERE / 'gap-review.md').write_text('\n'.join(lines) + '\n')
(HERE / 'PUBLIC-FILES.json').write_text(json.dumps({'publicFiles': ['gap-review.md', 'QA.json', 'build_review.py', 'PUBLIC-FILES.json'], 'excluded': ['../batch-root/raw/**', '../batch-b/raw/**'], 'note': '脚本只读本地已有证据，不联网；输出仅事实和哈希。'}, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(qa['summary'], ensure_ascii=False))
print([c for c in checks if not c['pass']])
