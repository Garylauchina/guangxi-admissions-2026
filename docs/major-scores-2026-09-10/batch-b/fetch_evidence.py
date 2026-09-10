#!/usr/bin/env python3
"""Download an explicit manifest of public aggregate admissions sources. Stdlib only."""
import argparse, concurrent.futures, datetime, hashlib, json, urllib.request, urllib.parse
from pathlib import Path
ROOT=Path(__file__).resolve().parent
def fetch(job):
    key=job['id']; headers={'User-Agent':'Mozilla/5.0'}; data=None
    if job.get('request') is not None:
        form=job.get('requestEncoding')=='form'
        data=(urllib.parse.urlencode(job['request']) if form else json.dumps(job['request'],ensure_ascii=False)).encode()
        headers['Content-Type']='application/x-www-form-urlencoded' if form else 'application/json'
    meta=dict(job,accessedAt=datetime.datetime.now(datetime.timezone.utc).isoformat())
    try:
        response=urllib.request.urlopen(urllib.request.Request(job['url'],data,headers),timeout=30)
        raw=response.read(); ext=job.get('ext','html')
        filename=f'raw/{key}.{ext}';(ROOT/filename).write_bytes(raw)
        meta.update(status=response.status,finalUrl=response.geturl(),sha256=hashlib.sha256(raw).hexdigest(),rawFile=filename,byteCount=len(raw))
        if job.get('expectedSha256') and job['expectedSha256']!=meta['sha256']:
            meta['status']='changed';meta['error']='Official response hash changed; re-review before rebuilding published facts.'
    except Exception as e:meta.update(status='error',error=str(e))
    (ROOT/'raw'/f'{key}.meta.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
    print(key,meta['status'],meta.get('byteCount',meta.get('error')))
    return meta
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--manifest',default='fetch-manifest.json');args=parser.parse_args()
    jobs=json.loads((ROOT/args.manifest).read_text());(ROOT/'raw').mkdir(exist_ok=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:results=list(pool.map(fetch,jobs))
    (ROOT/'fetch-results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
    if any(r['status']!='200' and r['status']!=200 for r in results):raise SystemExit('Some source requests failed or changed; inspect fetch-results.json.')
if __name__=='__main__':main()
