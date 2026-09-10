"""Reproduce public official enrollment queries, without website writes."""
from pathlib import Path
import urllib.request,json,hashlib
R=Path(__file__).resolve().parent;E=R/'evidence';E.mkdir(exist_ok=True)
manifest=json.loads((R/'request-manifest.json').read_text());log=[]
for k,m in manifest.items():
 req=urllib.request.Request(m['url'],data=b'' if m['httpMethod']=='POST' else None,headers={'User-Agent':'Mozilla/5.0','Content-Type':'application/x-www-form-urlencoded'})
 with urllib.request.urlopen(req,timeout=25) as resp:
  b=resp.read();f='csu.json' if k=='csu' else 'scut.html';(E/f).write_bytes(b)
  log.append({'id':k,'status':resp.status,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
(E/'csu-entry.html').write_bytes(urllib.request.urlopen(manifest['csu']['entryUrl'],timeout=25).read())
(E/'fetch-log.json').write_text(json.dumps(log,indent=2)+'\n')
