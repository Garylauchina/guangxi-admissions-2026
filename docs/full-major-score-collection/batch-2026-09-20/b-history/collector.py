"""Fetch only public official pages and documented query endpoints.

Python standard library. `python3 collect.py [manifest.json]`.
Requests never contain saved cookies/authentication; JSON session fields are removed.
"""
import concurrent.futures,datetime,hashlib,http.cookiejar,json,re,threading,time,urllib.request,urllib.parse,gzip
from contextlib import contextmanager
from pathlib import Path
import sys
R=Path(__file__).resolve().parent; RAW=R/'raw';RAW.mkdir(exist_ok=True)
HOST_REQUEST_GAP_SECONDS = 1.0
_host_registry_lock = threading.Lock()
_host_locks = {}
_host_last_finished = {}

@contextmanager
def host_request_slot(url):
 """Serialize requests to each entry hostname within this process.

 Keep a minimum quiet interval after completion, including failed requests.
 Different hostnames retain independent locks and can run concurrently.
 """
 hostname = (urllib.parse.urlsplit(url).hostname or '').lower()
 with _host_registry_lock:
  host_lock = _host_locks.setdefault(hostname, threading.Lock())
 with host_lock:
  remaining = _host_last_finished.get(hostname, 0) + HOST_REQUEST_GAP_SECONDS - time.monotonic()
  if remaining > 0:
   time.sleep(remaining)
  try:
   yield
  finally:
   _host_last_finished[hostname] = time.monotonic()

def redact(x):
 if isinstance(x,list):return [redact(v) for v in x]
 if isinstance(x,dict):return {k:redact(v) for k,v in x.items() if k.lower() not in ['jessionid','jsessionid','sessionid','csrf-token','csrftoken','access_token','seal','randomkey','randomcode']}
 return x
def fetch(item):
 name=item['id'];meta={**item,'checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat()};body=None
 headers={'User-Agent':'Mozilla/5.0','Referer':item.get('referer',item['url'])}
 headers.update(item.get('publicHeaders',{}))
 if 'data' in item:
  if item.get('encoding')=='json':body=json.dumps(item['data']).encode();headers['Content-Type']='application/json;charset=UTF-8'
  else:body=urllib.parse.urlencode(item['data']).encode();headers['Content-Type']='application/x-www-form-urlencoded; charset=UTF-8'
 try:
  opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
  with host_request_slot(item['url']):
   with opener.open(urllib.request.Request(item['url'],data=body,headers=headers),timeout=25) as response:
    raw=response.read();meta.update(status=response.status,finalUrl=response.url,rawSha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw));encoding=item.get('responseEncoding') or response.headers.get_content_charset() or 'utf-8'
  if raw.startswith(b'\x1f\x8b'):
   raw=gzip.decompress(raw);meta['contentDecoding']='gzip'
  if raw.startswith((b'%PDF',b'\x89PNG',b'\xff\xd8',b'PK\x03\x04')):
   ext='pdf' if raw.startswith(b'%PDF') else ('png' if raw.startswith(b'\x89PNG') else ('xlsx' if raw.startswith(b'PK\x03\x04') else 'jpg'))
   filename=name+'.'+ext;(RAW/filename).write_bytes(raw);meta.update(archiveFile=filename,archiveSha256=hashlib.sha256(raw).hexdigest());(RAW/(name+'.meta.json')).write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n');return {'id':name,'status':meta['status'],'bytes':len(raw),'archiveFile':filename}
  text=raw.decode(encoding,errors='replace');extension='html'
  try:parsed=json.loads(text);archive=json.dumps(redact(parsed),ensure_ascii=False,indent=2).encode();extension='json'
  except (ValueError,TypeError):
   text=re.sub(r'(<input[^>]+name="(?:__VIEWSTATE|__EVENTVALIDATION|F_STATE)"[^>]+value=")[^"]*',r'\1[REDACTED]',text)
   text=re.sub(r'(?i)(;jsessionid=)[A-Za-z0-9._-]+',r'\1[REDACTED]',text)
   archive=text.encode();extension='js' if '.js' in urllib.parse.urlparse(item['url']).path else 'html'
  filename=name+'.'+extension;(RAW/filename).write_bytes(archive)
  meta.update(archiveFile=filename,archiveSha256=hashlib.sha256(archive).hexdigest())
 except Exception as e:meta.update(status=getattr(e,'code',None),error=str(e))
 (RAW/(name+'.meta.json')).write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n');return {'id':name,'status':meta.get('status'),'bytes':meta.get('bytes'),'error':meta.get('error'),'archiveFile':meta.get('archiveFile')}
if __name__=='__main__':
 manifest=Path(sys.argv[1]) if len(sys.argv)>1 else R/'requests.json'
 with concurrent.futures.ThreadPoolExecutor(max_workers=7) as pool:
  for r in pool.map(fetch,json.loads(manifest.read_text())):print(json.dumps(r,ensure_ascii=False))
