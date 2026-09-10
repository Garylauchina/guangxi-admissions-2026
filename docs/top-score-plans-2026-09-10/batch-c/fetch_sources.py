from pathlib import Path
from datetime import datetime,timezone
import urllib.request,urllib.parse,json,hashlib,concurrent.futures
R=Path(__file__).resolve().parent;E=R/'evidence';E.mkdir(exist_ok=True)
JOBS=[
('bit','https://admission.bit.edu.cn/f/ajax_zsjh',{'ssmc':'广西','nf':'2026','klmc':'物理类','zslx':'普通类'}),
('bit_entry','https://admission.bit.edu.cn/static/front/bit/basic/html_web/zsjh.html',None),
('buaa','https://lqcx.buaa.edu.cn/f/ajax_zsjh',{'ssmc':'广西','zsnf':'2026','klmc':'物理类','zslx':'统招'}),
('buaa_entry','https://lqcx.buaa.edu.cn/static/front/buaa/basic/html_web/zsjh.html',None),
('hit','https://zsb.hit.edu.cn/information/plan?province=%E5%B9%BF%E8%A5%BF&year=2026',None),
('hust','https://zsb.hust.edu.cn/bkzn/zsjh.htm',None),
('sysu_entry','https://admission.sysu.edu.cn/zsw/zsjh.html',None),
('buaa-charter','https://zs.buaa.edu.cn/info/1003/3583.htm',None),
('hit-charter','https://zsb.hit.edu.cn/article/read/c6615f467530827fb19246dce601b931',None),
('hit-major-directory','https://zsb.hit.edu.cn/article/read/35766a7f35b60e5737b4ab426ee28103',None),
('sysu-charter','https://admission.sysu.edu.cn/f/newsCenter/article/8b565b6ba01a4d568cf370680f8338d4',None),
('hust-charter','https://zsb.hust.edu.cn/info/1006/3065.htm',None),
]
def fetch(job):
 key,url,body=job;m={'key':key,'url':url,'request':body,'checkedAt':datetime.now(timezone.utc).isoformat()}
 try:
  req=urllib.request.Request(url,urllib.parse.urlencode(body).encode() if body is not None else None,headers={'User-Agent':'Mozilla/5.0','Content-Type':'application/x-www-form-urlencoded'})
  with urllib.request.urlopen(req,timeout=25) as r:b=r.read();m.update(status=r.status,finalUrl=r.url)
  raw_hash=hashlib.sha256(b).hexdigest()
  ext='json' if b.lstrip().startswith((b'{',b'[')) else 'html'
  if ext=='json':
   j=json.loads(b); removed=[k for k in ['jessionid','jsessionid','csrfToken','token'] if k in j]
   for k in removed:j.pop(k)
   b=(json.dumps(j,ensure_ascii=False,indent=2)+'\n').encode();m['redactedFields']=removed
  f=f'{key}.{ext}';(E/f).write_bytes(b);m.update(file=f,bytes=len(b),rawResponseSha256=raw_hash,sanitizedSha256=hashlib.sha256(b).hexdigest())
 except Exception as e:m['error']=str(e)
 (E/f'{key}.meta.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n');print(json.dumps(m,ensure_ascii=False),flush=True)
 return m
if __name__=='__main__':
 with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:r=list(pool.map(fetch,JOBS))
 (R/'fetch-log.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
