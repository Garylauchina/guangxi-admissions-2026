"""Read only the public URLs and parameters explicitly listed in a manifest."""
from pathlib import Path
import json, sys, urllib.request, urllib.parse, urllib.error, hashlib, datetime
from concurrent.futures import ThreadPoolExecutor
ROOT=Path(__file__).resolve().parent
RAW=ROOT/'raw'
RAW.mkdir(exist_ok=True)
def clean(value):
    if isinstance(value,dict):
        return {k:clean(v) for k,v in value.items() if k.lower() not in {'token','accesstoken','access_token','authorization','cookie','jessionid','jsessionid','sessionid','seal','csrftoken','csrf_token'}}
    if isinstance(value,list):return [clean(v) for v in value]
    return value
def fetch(job):
    url=job['url'];data=job.get('data');kind=job.get('encoding','form')
    meta={**job,'requestMethod':'POST' if data is not None else 'GET','checkedAt':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()}
    headers={'User-Agent':'Mozilla/5.0','Referer':job.get('referer',url)}
    payload=None
    if data is not None:
        headers['Content-Type']='application/json;charset=utf-8' if kind=='json' else 'application/x-www-form-urlencoded; charset=UTF-8'
        payload=json.dumps(data,ensure_ascii=False).encode() if kind=='json' else urllib.parse.urlencode(data).encode()
    b=None
    try:
        with urllib.request.urlopen(urllib.request.Request(url,data=payload,headers=headers),timeout=35) as r:
            b=r.read();meta.update(httpStatus=r.status,finalUrl=r.url)
    except urllib.error.HTTPError as e:
        b=e.read();meta.update(httpStatus=e.code,error=str(e))
    except Exception as e:meta['error']=str(e)
    if b is not None:
        meta['responseSha256']=hashlib.sha256(b).hexdigest()
        try:
            obj=json.loads(b);safe=clean(obj)
            b=json.dumps(safe,ensure_ascii=False,indent=2).encode()
            meta['archiveMethod']='JSON formatted; session-related fields omitted'
        except (ValueError,UnicodeError):pass
        meta.update(sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
        (RAW/job['name']).write_bytes(b)
    (RAW/(job['name']+'.meta.json')).write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
    print(job['name'],meta.get('httpStatus'),meta.get('bytes'),meta.get('error',''),flush=True)
    return meta
if __name__=='__main__':
    jobs=json.loads((ROOT/(sys.argv[1] if len(sys.argv)>1 else 'requests-1.json')).read_text())
    with ThreadPoolExecutor(max_workers=4) as pool:list(pool.map(fetch,jobs))
