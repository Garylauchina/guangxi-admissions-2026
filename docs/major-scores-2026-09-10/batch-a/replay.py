#!/usr/bin/env python3
"""Replay only the explicit public request allowlist. Changed responses require review."""
import json
from pathlib import Path
from collector import PublicAPI,fetch,error

R=Path(__file__).resolve().parent

def main():
    jobs=json.loads((R/'public-fetch-manifest.json').read_text());apis={};results=[]
    for job in jobs:
        if job.get('path'):
            key=(job['host'],job['entryUrl'])
            try:
                if key not in apis:apis[key]=PublicAPI(*key)
                result=apis[key].query(job)
            except Exception as exc: result=error(job,exc)
        else: result=fetch(job)
        results.append({'id':job['id'],'httpStatus':result.get('httpStatus'),
            'archiveUnchanged':result.get('sha256')==job['expectedArchiveSha256'],
            'accessError':result.get('accessError')})
        print(job['id'],results[-1]['httpStatus'],results[-1]['archiveUnchanged'])
    (R/'replay-results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
    if any(x['httpStatus']!=200 or not x['archiveUnchanged'] for x in results):
        raise SystemExit('Source failed or changed; inspect raw and re-review before building.')

if __name__=='__main__':main()
