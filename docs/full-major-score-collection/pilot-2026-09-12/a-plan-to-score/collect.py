#!/usr/bin/env python3
"""Fetch declared public statistical sources; raw evidence stays local."""
import argparse, concurrent.futures, datetime, hashlib, html, json, pathlib, re
import urllib.error, urllib.parse, urllib.request
ROOT = pathlib.Path(__file__).resolve().parent
RAW = ROOT / 'raw'
RAW.mkdir(exist_ok=True)
MANIFEST = ROOT / 'fetch-manifest.json'

def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def fetch(item):
    start = now()
    ident, url = item['id'], item['url']
    body = item.get('request')
    headers = {'User-Agent': 'Mozilla/5.0 (research of public admissions statistics)'}
    data = None
    if body is not None:
        if item.get('requestEncoding') == 'json':
            data = json.dumps(body, ensure_ascii=False).encode()
            headers['Content-Type'] = 'application/json'
        else:
            data = urllib.parse.urlencode(body).encode()
            headers['Content-Type'] = 'application/x-www-form-urlencoded'
    status, error, content_type, final_url = None, None, None, url
    try:
        req = urllib.request.Request(url, data=data, headers=headers)
        with urllib.request.urlopen(req, timeout=25) as response:
            raw = response.read()
            status, final_url = response.status, response.url
            content_type = response.headers.get('Content-Type')
    except urllib.error.HTTPError as exc:
        status, error, raw = exc.code, str(exc), exc.read()
        content_type = exc.headers.get('Content-Type')
    except Exception as exc:
        error, raw = str(exc), b''
    ext = '.json' if 'json' in (content_type or '') else '.html'
    if 'pdf' in (content_type or ''): ext = '.pdf'
    if 'image' in (content_type or ''): ext = '.image'
    filename = ident + ext
    (RAW / filename).write_bytes(raw)
    text = raw.decode('utf-8', errors='replace')
    if ext == '.html':
        plain = html.unescape(re.sub('<[^>]+>', ' ', re.sub(r'<(script|style)\b.*?</\1>', '', text, flags=re.S)))
        (RAW / (ident + '.txt')).write_text(re.sub(r'[ \t]+', ' ', plain), encoding='utf-8')
        links = []
        for href, label in re.findall(r'<a\b[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', text, re.S|re.I):
            label = html.unescape(re.sub('<[^>]+>', '', label)).strip()
            if label: links.append({'text': label, 'url': urllib.parse.urljoin(final_url, html.unescape(href))})
        (RAW / (ident + '-links.json')).write_text(json.dumps(links, ensure_ascii=False, indent=2))
    result = dict(item, startedAt=start, finishedAt=now(), httpStatus=status,
                  error=error, finalUrl=final_url, contentType=content_type,
                  bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest(), rawFile='raw/'+filename)
    return result

def run(items):
    # One sequential stream per hostname, at most three hosts at once.
    groups = {}
    for item in items: groups.setdefault(urllib.parse.urlsplit(item['url']).hostname, []).append(item)
    def group_fetch(values): return [fetch(x) for x in values]
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        for batch in pool.map(group_fetch, groups.values()): results.extend(batch)
    old = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else []
    byid = {x['id']: x for x in old}
    for item in results: byid[item['id']] = item
    MANIFEST.write_text(json.dumps(list(byid.values()), ensure_ascii=False, indent=2))
    for item in results:
        print(item['id'], item['httpStatus'], item['bytes'], item.get('error') or '')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('request_file')
    args = parser.parse_args()
    run(json.loads((ROOT / args.request_file).read_text()))
