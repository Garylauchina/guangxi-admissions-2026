"""Reproduce Jiangnan's public frontend RSA CSRF header; no account/session saved.
Requires cryptography; values are read from the archived public app script.
"""
from pathlib import Path
import re,json,base64,hashlib,datetime,urllib.request,urllib.parse,sys
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from collect import redact
R=Path(__file__).resolve().parent;RAW=R/'raw'
def run(item):
 script=(RAW/'jnu-app.js').read_text()
 match=re.search(r'var e="([a-f0-9]+)",t="([A-Za-z0-9+/=]+)",n=new a\["a"\]',script)
 if not match:raise ValueError('Public frontend CSRF helper changed; reread before retrying')
 key=serialization.load_der_public_key(base64.b64decode(match[2]))
 token=base64.b64encode(key.encrypt(match[1].encode(),padding.PKCS1v15())).decode()
 meta={**item,'checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'accessMethod':'Public frontend RSA CSRF header, derived in memory from app.js; no token archived.'}
 try:
  is_json=item.get('encoding')=='json'
  headers={'User-Agent':'Mozilla/5.0','Referer':'http://admission1.jiangnan.edu.cn/pc/historyScore/nonArt','Content-Type':'application/json' if is_json else 'application/x-www-form-urlencoded','csrf':token}
  body=json.dumps(item.get('data',{})).encode() if is_json else urllib.parse.urlencode(item.get('data',{})).encode()
  req=urllib.request.Request(item['url'],data=body,headers=headers)
  with urllib.request.urlopen(req,timeout=25) as r:raw=r.read();meta.update(status=r.status,bytes=len(raw))
  obj=redact(json.loads(raw));archive=json.dumps(obj,ensure_ascii=False,indent=2).encode();filename=item['id']+'.json';(RAW/filename).write_bytes(archive)
  meta.update(rawSha256=hashlib.sha256(raw).hexdigest(),archiveSha256=hashlib.sha256(archive).hexdigest(),archiveFile=filename)
 except Exception as e:meta.update(status=getattr(e,'code',None),error=str(e))
 (RAW/(item['id']+'.meta.json')).write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'id':item['id'],'status':meta.get('status'),'bytes':meta.get('bytes'),'error':meta.get('error')},ensure_ascii=False))
if __name__=='__main__':
 for item in json.loads(Path(sys.argv[1]).read_text()):run(item)
