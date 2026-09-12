"""Download only public source documents; never persist request/response headers."""
from pathlib import Path
from urllib.request import Request,urlopen
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor
import json, hashlib
BASE=Path(__file__).resolve().parent
RAW=BASE/'raw'; RAW.mkdir(exist_ok=True)
def get(item):
    key,url=item['key'],item['url']
    meta={'id':key,'url':url,'checkedAt':datetime.now(timezone.utc).isoformat(),'requestMethod':'GET'}
    try:
        with urlopen(Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=35) as r:
            content=r.read();meta.update(status=r.status,finalUrl=r.url,sha256=hashlib.sha256(content).hexdigest(),bytes=len(content))
        (RAW/item['file']).write_bytes(content)
    except Exception as e:meta.update(error=str(e),status=getattr(e,'code',None))
    (RAW/(key+'.meta.json')).write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
    return key,meta.get('status'),meta.get('bytes'),meta.get('error')
if __name__=='__main__':
    items=json.loads((BASE/'requests.json').read_text())
    with ThreadPoolExecutor(max_workers=6) as pool:
        for result in pool.map(get,items):print(result)
