"""Replay only public 2026 admissions evidence requests, with no credentials or login.

The manifest contains exact public GET/POST requests observed on university websites.
Install pandas, lxml, and pdfplumber for extract_public.py; downloading uses stdlib.
"""
from collect import BASE, fetch
import json
from concurrent.futures import ThreadPoolExecutor

def main():
    (BASE / 'raw').mkdir(exist_ok=True)
    manifest = json.load(open(BASE / 'public-request-manifest.json'))
    def one(m):
        result = fetch(m['id'], m['url'], m['request'], m['requestEncoding'] == 'form')
        result['previousSha256'] = m['sha256']
        result['sameRawBytes'] = result.get('sha256') == m['sha256']
        return result
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(one, manifest))
    (BASE / 'replay-report.json').write_text(json.dumps(results, ensure_ascii=False, indent=2))
    failures = [r for r in results if 'error' in r]
    if failures:
        raise RuntimeError(f'{len(failures)} public sources could not be downloaded; see replay-report.json')

if __name__ == '__main__':
    main()
