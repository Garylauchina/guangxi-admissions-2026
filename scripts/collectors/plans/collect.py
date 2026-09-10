#!/usr/bin/env python3
"""Read-only downloads of public university admissions evidence; never login or student records."""
import urllib.request, urllib.parse, json, re, hashlib, concurrent.futures, datetime
from pathlib import Path
from html.parser import HTMLParser
BASE=Path(__file__).resolve().parent
class Tables(HTMLParser):
 def __init__(self):
  super().__init__();self.tables=[];self.table=None;self.row=None;self.cell=None
 def handle_starttag(self,t,a):
  if t=='table':self.table=[]
  if t=='tr':self.row=[]
  if t in ('td','th'):self.cell=[]
 def handle_data(self,d):
  if self.cell is not None:self.cell.append(d)
 def handle_endtag(self,t):
  if t in ('td','th') and self.cell is not None:
   if self.row is not None:self.row.append(re.sub(r'\s+',' ',''.join(self.cell)).strip())
   self.cell=None
  if t=='tr' and self.row is not None:
   if self.table is not None:self.table.append(self.row)
   self.row=None
  if t=='table' and self.table is not None:self.tables.append(self.table);self.table=None

def fetch(key,url,body=None,form=False):
 headers={'User-Agent':'Mozilla/5.0'};data=None
 if body is not None:
  data=(urllib.parse.urlencode(body) if form else json.dumps(body,ensure_ascii=False)).encode()
  headers['Content-Type']='application/x-www-form-urlencoded' if form else 'application/json'
 try:
  r=urllib.request.urlopen(urllib.request.Request(url,data,headers),timeout=25);b=r.read()
  ext='png' if b[:8]==b'\x89PNG\r\n\x1a\n' else 'jpg' if b[:2]==b'\xff\xd8' else 'pdf' if b[:4]==b'%PDF' else 'json' if b[:1] in (b'{',b'[') else 'html'
  (BASE/'raw'/f'{key}.{ext}').write_bytes(b)
  meta={'id':key,'url':url,'finalUrl':r.geturl(),'request':body,'accessedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sha256':hashlib.sha256(b).hexdigest(),'rawFile':f'raw/{key}.{ext}','status':r.status,'method':'POST' if body is not None else 'GET','requestEncoding':'form' if form else 'json' if body is not None else None}
  (BASE/'raw'/f'{key}.meta.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2))
  if ext=='json':
   d=json.loads(b);print(key,'JSON',str(d)[:300])
  elif ext=='html':
   s=b.decode('utf-8-sig',errors='replace');p=Tables();p.feed(s)
   (BASE/'raw'/f'{key}.tables.json').write_text(json.dumps(p.tables,ensure_ascii=False,indent=2))
   print(key,'HTML',len(b),'tables',[(len(t),t[:2]) for t in p.tables][:4])
  else: print(key,ext.upper(),len(b))
  return meta
 except Exception as e: print(key,type(e).__name__,str(e));return {'id':key,'url':url,'error':str(e)}

