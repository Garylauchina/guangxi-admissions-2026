#!/usr/bin/env python3
"""Replay public source requests and expand the four official GB18030 tables."""
import pathlib,json,io,sys
from collect import fetch
ROOT=pathlib.Path(__file__).resolve().parent
if '--fetch' in sys.argv:
    for r in json.loads((ROOT/'public-request-manifest.json').read_text()):
        result=fetch(r['id'],r['url'],r.get('request'),r.get('requestEncoding')=='form')
        if result.get('error'):raise RuntimeError(result)
import pandas as pd
for key in ['gxeea-first-history','gxeea-first-physics','gxeea-second-history','gxeea-second-physics']:
    text=(ROOT/'raw'/(key+'.html')).read_bytes().decode('gb18030')
    frame=pd.read_html(io.StringIO(text),header=None,flavor='lxml')[0]
    rows=frame.where(frame.notna(),None).values.tolist()
    (ROOT/'raw'/(key+'.expanded.json')).write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
