#!/usr/bin/env python3
"""Fetch declared public GET pages / read-only POST queries; never authenticate or disable TLS verification."""
import concurrent.futures
import hashlib
import html
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def fetch(item):
    key, url = item['id'], item['url']
    out = dict(item, checkedAt=datetime.now(timezone.utc).isoformat())
    try:
        body = item.get('body')
        headers = {'User-Agent': 'Mozilla/5.0'}
        if body is not None:
            headers['Content-Type'] = 'application/x-www-form-urlencoded; charset=UTF-8'
        with urllib.request.urlopen(urllib.request.Request(url, data=body.encode() if body is not None else None, headers=headers), timeout=25) as response:
            raw = response.read()
            out.update(status=response.status, finalUrl=response.url, contentType=response.headers.get('Content-Type'))
        ext = item.get('extension', 'html')
        target = ROOT / 'raw' / f'{key}.{ext}'
        target.parent.mkdir(exist_ok=True)
        target.write_bytes(raw)
        out.update(file=str(target.relative_to(ROOT)), sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw))
        if ext == 'html':
            charset = re.search(rb'charset=[\"\']?([a-zA-Z0-9_-]+)', raw[:4000], re.I)
            encoding = charset[1].decode() if charset else 'utf-8'
            out['encoding'] = encoding
            text = raw.decode(encoding, errors='replace')
            title = re.search(r'<title[^>]*>(.*?)</title>', text, re.S | re.I)
            out['title'] = html.unescape(re.sub('<[^>]+>', '', title[1])).strip() if title else None
            out['links'] = [{'text': html.unescape(re.sub('<[^>]+>', '', m[2])).strip(), 'url': urllib.parse.urljoin(url, m[1])} for m in re.finditer(r'<a\b[^>]*href=[\"\']([^\"\']+)[\"\'][^>]*>(.*?)</a>', text, re.S | re.I)]
    except Exception as error:
        out['error'] = str(error)
    return out

if __name__ == '__main__':
    manifest = ROOT / (sys.argv[1] if len(sys.argv) > 1 else 'request-manifest.json')
    requests = json.loads(manifest.read_text())
    results = list(concurrent.futures.ThreadPoolExecutor(max_workers=6).map(fetch, requests))
    (ROOT / f'{manifest.stem}-results.json').write_text(json.dumps(results, ensure_ascii=False, indent=2) + '\n')
    for row in results:
        print(json.dumps(row, ensure_ascii=False))
