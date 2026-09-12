"""Optional ordinary HTTPS transport retry for the LZU entry; no TLS override."""
from pathlib import Path
import subprocess,json,hashlib,datetime
R=Path(__file__).resolve().parent;raw=R/'raw';name='lzu-entry-curl';url='https://zsdata.lzu.edu.cn/zsdata/lqxx/'
p=raw/(name+'.html')
r=subprocess.run(['curl','-L','--max-time','20','--silent','--show-error','--output',str(p),'--write-out','%{http_code} %{size_download}',url],capture_output=True,text=True)
m={'id':name,'url':url,'checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':None,'accessMethod':'Public curl HTTPS GET with certificate verification; no session headers archived.'}
if r.returncode==0:
 m.update(status=int(r.stdout.split()[0]),archiveFile=p.name,rawSha256=hashlib.sha256(p.read_bytes()).hexdigest(),archiveSha256=hashlib.sha256(p.read_bytes()).hexdigest())
else:m['error']='curl exit '+str(r.returncode)+': '+r.stderr.strip()
(raw/(name+'.meta.json')).write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'id':name,'status':m['status'],'error':m.get('error')},ensure_ascii=False))
