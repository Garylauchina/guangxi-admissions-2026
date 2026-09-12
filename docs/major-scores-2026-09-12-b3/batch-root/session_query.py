"""Replay the official anonymous Cookie/CSRF workflow; never save session values."""
from pathlib import Path
import json,sys,time,hashlib,datetime,http.cookiejar,urllib.request,urllib.parse
from collect import clean

ROOT=Path(__file__).resolve().parent
RAW=ROOT/'raw';RAW.mkdir(exist_ok=True)
def run(config):
    opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
    entry=config['entryUrl'];base=config['baseUrl'];tokens=[]
    opener.open(urllib.request.Request(entry,headers={'User-Agent':'Mozilla/5.0'}),timeout=30).read()
    def request(path,data,token=None):
        stamp=str(int(time.time()*1000))
        headers={'User-Agent':'Mozilla/5.0','Referer':entry,'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8','X-Requested-With':'XMLHttpRequest','X-Requested-Time':stamp}
        if token:headers['Csrf-Token']=token
        with opener.open(urllib.request.Request(base+'/'+path+'?ts='+stamp,data=urllib.parse.urlencode(data).encode(),headers=headers),timeout=30) as r:
            b=r.read();new=r.headers.get('Csrf-Token')
            if new:tokens.append(new)
            return b,r.status
    for q in config['queries']:
        meta={'name':q['name'],'url':base+'/'+q['path'],'entryUrl':entry,'data':q['data'],'requestMethod':'POST','checkedAt':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),'method':'Official anonymous Cookie and public CSRF exchange; no session values saved.'}
        try:
            if not tokens:
                b,_=request('f/ajax_get_csrfToken',{'n':3})
                tokens.extend(json.loads(b)['data'].split(','))
            b,status=request(q['path'],q['data'],tokens.pop(0))
            safe=json.dumps(clean(json.loads(b)),ensure_ascii=False,indent=2).encode()
            (RAW/q['name']).write_bytes(safe)
            meta.update(httpStatus=status,sha256=hashlib.sha256(safe).hexdigest(),responseSha256=hashlib.sha256(b).hexdigest(),bytes=len(safe))
        except Exception as e:meta.update(httpStatus=getattr(e,'code',None),error=str(e))
        (RAW/(q['name']+'.meta.json')).write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
        print(q['name'],meta.get('httpStatus'),meta.get('bytes'),meta.get('error',''),flush=True)
if __name__=='__main__':
    for config in json.loads((ROOT/sys.argv[1]).read_text()):run(config)
