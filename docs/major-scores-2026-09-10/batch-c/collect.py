"""Bounded official public-page collector; no session values are archived."""
import urllib.request,urllib.parse,http.cookiejar,json,hashlib,datetime,concurrent.futures
from pathlib import Path
R=Path(__file__).resolve().parent;RAW=R/'raw';RAW.mkdir(exist_ok=True)
def fetch(job):
 key,url,*tail=job;body=tail[0] if tail else None;encoding=tail[1] if len(tail)>1 else 'form'
 m={'id':key,'url':url,'request':body,'requestEncoding':encoding if body is not None else None,'checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 try:
  payload=None if body is None else (json.dumps(body).encode() if encoding=='json' else urllib.parse.urlencode(body).encode())
  headers={'User-Agent':'Mozilla/5.0','Content-Type':'application/json' if encoding=='json' else 'application/x-www-form-urlencoded'}
  with urllib.request.urlopen(urllib.request.Request(url,payload,headers),timeout=25) as r:b=r.read();m.update(status=r.status,finalUrl=r.url)
  m['rawSha256']=hashlib.sha256(b).hexdigest();ext='json' if b.lstrip().startswith((b'{',b'[')) else 'html'
  if ext=='json':
   d=json.loads(b)
   if isinstance(d,dict):
    m['redactedFields']=[k for k in ['jessionid','jsessionid','token','csrfToken'] if k in d]
    for k in m['redactedFields']:d.pop(k)
   b=(json.dumps(d,ensure_ascii=False,indent=2)+'\n').encode()
  fn=key+'.'+ext;(RAW/fn).write_bytes(b);m.update(archiveFile=fn,archiveSha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
 except Exception as e:m['error']=str(e)
 (RAW/(key+'.meta.json')).write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n');return m
if __name__=='__main__':
 jobs=json.loads((R/'requests.json').read_text())
 with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
  for m in pool.map(fetch,jobs):print(json.dumps(m,ensure_ascii=False))
