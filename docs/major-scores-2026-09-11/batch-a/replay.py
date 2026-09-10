#!/usr/bin/env python3
"""Replay the explicit public request list; never silently refresh reviewed evidence."""
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
   except Exception as exc:result=error(job,exc)
  else:result=fetch(job)
  results.append(dict(id=job['id'],httpStatus=result.get('httpStatus'),statusUnchanged=result.get('httpStatus')==job['expectedHttpStatus'],archiveUnchanged=result.get('sha256')==job['expectedArchiveSha256']))
  print(job['id'],results[-1]['httpStatus'],results[-1]['archiveUnchanged'])
 (R/'replay-results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
 if any(not x['statusUnchanged'] or not x['archiveUnchanged'] for x in results):
  raise SystemExit('Some public responses changed. Read and review new raw responses; do not overwrite reviewed evidence automatically.')
if __name__=='__main__':main()
