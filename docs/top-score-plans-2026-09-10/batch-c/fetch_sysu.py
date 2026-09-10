"""Replay the official public site's cookie + CSRF handshake; no account needed."""
from pathlib import Path
import urllib.request,urllib.parse,http.cookiejar,json,time,hashlib
from datetime import datetime,timezone
R=Path(__file__).resolve().parent;E=R/'evidence'
base='https://admission.sysu.edu.cn/';entry=base+'zsw/zsjh.html'
jar=http.cookiejar.CookieJar();op=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar));op.addheaders=[('User-Agent','Mozilla/5.0'),('Referer',entry)]
op.open(entry,timeout=25).read()
def request(path,body,token=None):
 now=str(int(time.time()*1000));h={'X-Requested-Time':now,'X-Requested-With':'XMLHttpRequest','Origin':'https://admission.sysu.edu.cn','Content-Type':'application/x-www-form-urlencoded'}
 if token:h['Csrf-Token']=token
 return op.open(urllib.request.Request(base+path+'?ts='+now,urllib.parse.urlencode(body).encode(),h),timeout=25)
r=request('f/ajax_get_csrfToken',{'n':3});token=json.loads(r.read())['data'].split(',')[0]
body={'ssmc':'广西','zsnf':'2026','klmc':'物理类','zslx':'普通录取'}
r=request('f/ajax_zsjh',body,token);raw=r.read();d=json.loads(raw)
removed=[k for k in ['jessionid','jsessionid','csrfToken','token'] if k in d]
for k in removed:d.pop(k)
b=(json.dumps(d,ensure_ascii=False,indent=2)+'\n').encode();(E/'sysu.json').write_bytes(b)
meta={'key':'sysu_session','url':base+'f/ajax_zsjh','entryUrl':entry,'request':body,'checkedAt':datetime.now(timezone.utc).isoformat(),'status':r.status,'file':'sysu.json','bytes':len(b),'rawResponseSha256':hashlib.sha256(raw).hexdigest(),'sanitizedSha256':hashlib.sha256(b).hexdigest(),'redactedFields':removed,'method':'公开tplt.js规定的cookie与CSRF握手；会话和token不落盘'}
(E/'sysu_session.meta.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
j=json.loads(b);rows=j['data']['zsjhList'];print(json.dumps({'status':r.status,'rows':len(rows),'seats':sum(int(x['zsjhs']) for x in rows),'fields':sorted(rows[0]),'first':rows[0]},ensure_ascii=False,indent=2))
