"""Re-fetch the two adopted public official HTML tables; no login or private endpoints."""
from pathlib import Path
import urllib.request,json,hashlib,datetime
R=Path(__file__).resolve().parent;E=R/'evidence';E.mkdir(exist_ok=True)
urls={'jnu':'https://zsb.jnu.edu.cn/2026/0622/c4288a857512/page.htm','jxpu':'https://zsw.jxpu.edu.cn/info/1187/17992.htm'}
log=[]
for k,u in urls.items():
 with urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'}),timeout=30) as resp:
  b=resp.read();(E/f'{k}.html').write_bytes(b)
  log.append({'id':k,'url':u,'status':resp.status,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat()})
(E/'fetch-log.json').write_text(json.dumps(log,ensure_ascii=False,indent=2)+'\n')
print('Fetched 2 official public initial plan tables')
