"""Freeze only source metadata and statistical browser observations for publication."""
import datetime, hashlib, json, re, urllib.parse
from pathlib import Path
ROOT = Path(__file__).resolve().parent
RAW = ROOT / 'raw'
def save(name, value):
    (ROOT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
def safe_url(value):
    p = urllib.parse.urlsplit(value)
    query = [(k, v) for k, v in urllib.parse.parse_qsl(p.query, keep_blank_values=True)
             if not re.search('token|session|cookie', k, re.I)]
    return urllib.parse.urlunsplit((p.scheme, p.netloc, p.path, urllib.parse.urlencode(query), p.fragment))
browser = [
    ('19145', 'https://zslq.neuq.edu.cn/release-page/OverYears?key=r%2BkqhCVU%2FPpgPn8%2FnHJ2',
     '浏览器选择2025广西历史类本科批；年份菜单2025/2024/2023，具体专业结果3条。'),
    ('10112', 'https://zhaolu.zjzw.cn/release-page/overyears?key=23a0a115af2262c7b0398b88',
     '浏览器选择2025广西物理类本科批；年份菜单2025/2024/2023，具体专业结果43条。'),
    ('10357', 'https://zsb.ahu.edu.cn/',
     '正常浏览器读取官方招生首页，历年录取真实链接指向http://bkzs.ahu.edu.cn/static/front/ahu/basic/html_web/lnfs.html。'),
    ('10357', 'https://bkzs.ahu.edu.cn/static/front/ahu/basic/html_web/lnfs.html',
     '正常浏览器访问HTTP与HTTPS均呈现资源访问错误502；没有读到分数菜单。'),
    ('10357', 'https://zsb.ahu.edu.cn/13317/list.htm',
     '招生快讯首页列15条，总30条、2页；最新2026-09-08，页尾2025-09-11；本轮该页未提供2026广西专业分表。'),
    ('10030', 'https://joinus.bfsu.edu.cn/',
     '正常浏览器恢复招生首页，历年分数链接指向https://zhaosheng.bfsu.edu.cn/static/front/bfsu/basic/html_web/lnfs.html?20220331。')
]
# These are analyst observations of actual DOM, not downloaded response bodies.
for i, (code, url, note) in enumerate(browser, 1):
    name = f'{code}-browser-observation-{i}'
    obj = {'schoolCode': code, 'url': url, 'observation': note,
           'observedOn': '2026-09-12', 'evidenceType': 'browser-dom-observation'}
    body = (json.dumps(obj, ensure_ascii=False, indent=2) + '\n').encode()
    (RAW / (name + '.json')).write_bytes(body)
    meta = {'id': name, 'schoolCode': code, 'url': url, 'checkedAt': '2026-09-12',
            'archiveFile': name + '.json', 'archiveSha256': hashlib.sha256(body).hexdigest(),
            'evidenceType': 'browser-dom-observation', 'observation': note}
    (RAW / (name + '.meta.json')).write_text(json.dumps(meta, ensure_ascii=False, indent=2) + '\n')

manifest = []
targets = {r['schoolCode'] for r in json.loads((ROOT / 'targets.json').read_text())}
for path in sorted(RAW.glob('*.meta.json')):
    m = json.loads(path.read_text())
    code = m.get('schoolCode') or m['id'][:5]
    if code not in targets:
        continue
    file = m.get('archiveFile') or m.get('rawFile', '').rsplit('/', 1)[-1]
    request = m.get('data', m.get('request'))
    # Public query fields only. Neither cookies nor CSRF values enter the manifest.
    if isinstance(request, dict):
        request = {k: v for k, v in request.items()
                   if not re.search('token|session|cookie|password|seal', k, re.I)}
    record = {'name': m['id'], 'schoolCode': code, 'url': safe_url(m['url']),
              'checkedAt': m.get('checkedAt', m.get('accessedAt')),
              'requestMethod': m.get('method', 'POST' if request is not None else 'GET'),
              'requestData': request, 'httpStatus': m.get('status', m.get('httpStatus')),
              'archiveFile': file or None,
              'sha256': m.get('archiveSha256', m.get('sha256')),
              'responseSha256': m.get('rawSha256', m.get('responseSha256')),
              'evidenceType': m.get('evidenceType', 'public-response')}
    if m.get('error') or m.get('accessError'):
        error = m.get('error', m.get('accessError'))
        record['accessFailure'] = 'http-error' if record['httpStatus'] else (
            'incomplete-response' if 'IncompleteRead' in error else 'transport-error')
    if m.get('observation'):
        record['observation'] = m['observation']
    manifest.append(record)
save('source-manifest.json', manifest)
print('Frozen source metadata:', len(manifest))
