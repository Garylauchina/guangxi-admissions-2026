#!/usr/bin/env python3
"""Replay only explicit public requests; never silently replace reviewed conclusions."""
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
  row=dict(id=job['id'],httpStatus=result.get('httpStatus'),statusUnchanged=result.get('httpStatus')==job['expectedHttpStatus'],archiveUnchanged=result.get('sha256')==job['expectedArchiveSha256'])
  results.append(row);print(row['id'],row['httpStatus'],row['archiveUnchanged'])
 (R/'replay-results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
 if any(not x['statusUnchanged'] or not x['archiveUnchanged'] for x in results):
  raise SystemExit('Some responses changed. Review raw and source-year boundaries before refreshing reviewed evidence.')
if __name__=='__main__':main()
