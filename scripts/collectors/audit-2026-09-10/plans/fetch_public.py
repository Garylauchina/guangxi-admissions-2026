#!/usr/bin/env python3
"""Replay the explicit public-source manifest; no login or private inputs."""
import json
from collect import BASE,fetch
if __name__=='__main__':
    result=[]
    for request in json.loads((BASE/'public-request-manifest.json').read_text()):
        result.append(fetch(request['id'],request['url'],request.get('request'),request.get('requestEncoding')=='form'))
    (BASE/'fetch-results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
