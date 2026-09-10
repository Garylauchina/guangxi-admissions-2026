import urllib.request,urllib.parse,urllib.error,json,hashlib,datetime,pathlib,concurrent.futures,sys
ROOT=pathlib.Path(__file__).parent/'raw'
ROOT.mkdir(parents=True,exist_ok=True)
def fetch(name,url,data=None,referer=None,encoding="form"):
    meta={'url':url,'method':'POST' if data is not None else 'GET','requestData':data,'requestEncoding':encoding,'checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat()}
    headers={'User-Agent':'Mozilla/5.0','Referer':referer or url}
    if data is not None:headers['Content-Type']='application/json;charset=utf-8' if encoding=='json' else 'application/x-www-form-urlencoded; charset=UTF-8'
    try:
        req=urllib.request.Request(url,data=(json.dumps(data,ensure_ascii=False).encode() if encoding=='json' else urllib.parse.urlencode(data).encode()) if data is not None else None,headers=headers)
        with urllib.request.urlopen(req,timeout=35) as r:
            b=r.read();meta.update(status=r.status,finalUrl=r.url,sha256=hashlib.sha256(b).hexdigest(),bytes=len(b));(ROOT/name).write_bytes(b)
    except Exception as e:meta.update(error=str(e))
    (ROOT/(name+'.meta.json')).write_text(json.dumps(meta,ensure_ascii=False,indent=2))
    print(json.dumps(meta,ensure_ascii=False));return meta
