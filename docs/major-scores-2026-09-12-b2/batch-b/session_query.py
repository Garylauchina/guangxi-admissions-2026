"""Official public Cookie/CSRF workflow; all session values remain only in memory."""
from pathlib import Path
import urllib.request,urllib.parse,http.cookiejar,time,json,hashlib,datetime,concurrent.futures,sys
from collect import redact
R=Path(__file__).resolve().parent;RAW=R/'raw'
def run(item):
 host=item['host'];entry=item['entryUrl'];opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()));tokens=[]
 opener.open(urllib.request.Request(entry,headers={'User-Agent':'Mozilla/5.0'}),timeout=25).read()
 def req(path,data,token=None):
  stamp=str(int(time.time()*1000));headers={'User-Agent':'Mozilla/5.0','Referer':entry,'X-Requested-Time':stamp,'X-Requested-With':'XMLHttpRequest','Content-Type':'application/x-www-form-urlencoded; charset=UTF-8'}
  if token:headers['Csrf-Token']=token
  with opener.open(urllib.request.Request(host+'/'+path+'?ts='+stamp,data=urllib.parse.urlencode(data).encode(),headers=headers),timeout=25) as response:
   raw=response.read();fresh=response.headers.get('Csrf-Token')
   if fresh:tokens.append(fresh)
   return raw
 for q in item['queries']:
  meta={'id':q['id'],'url':host+'/'+q['path'],'entryUrl':entry,'data':q['data'],'checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'accessMethod':'Official frontend Cookie and public CSRF exchange; no session values archived.'}
  try:
   if not tokens:tokens.extend(json.loads(req('f/ajax_get_csrfToken',{'n':3}))['data'].split(','))
   raw=req(q['path'],q['data'],tokens.pop(0));parsed=redact(json.loads(raw));archive=json.dumps(parsed,ensure_ascii=False,indent=2).encode();fn=q['id']+'.json';(RAW/fn).write_bytes(archive)
   meta.update(status=200,rawSha256=hashlib.sha256(raw).hexdigest(),archiveSha256=hashlib.sha256(archive).hexdigest(),archiveFile=fn,bytes=len(raw))
  except Exception as e:meta.update(status=getattr(e,'code',None),error=str(e))
  (RAW/(q['id']+'.meta.json')).write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'id':q['id'],'status':meta.get('status'),'bytes':meta.get('bytes'),'error':meta.get('error')},ensure_ascii=False))
if __name__=='__main__':
 p=Path(sys.argv[1]) if len(sys.argv)>1 else R/'session-requests.json'
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:list(ex.map(run,json.loads(p.read_text())))
