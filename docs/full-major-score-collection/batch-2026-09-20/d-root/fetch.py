"""Archive explicit public URLs, with serial requests per host. Raw files stay local."""
from pathlib import Path
import concurrent.futures, datetime, hashlib, html, json, re, sys, threading, time
from html.parser import HTMLParser
from urllib.parse import urlparse, urljoin, urlencode
from urllib.request import Request, urlopen

ROOT=Path(__file__).resolve().parent
RAW=ROOT/'raw'
RAW.mkdir(exist_ok=True)
LOCKS={}
GUARD=threading.Lock()
class Page(HTMLParser):
    def __init__(self):
        super().__init__(); self.parts=[]; self.links=[]; self.active=None; self.hidden=0
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag in ['script','style']: self.hidden+=1
        if tag=='a' and a.get('href'): self.active={'href':a['href'],'text':''}
        if tag in ['p','div','tr','br','li','h1','h2','h3']: self.parts.append('\n')
        if tag=='img' and a.get('src'):self.links.append({'href':a['src'],'text':a.get('alt',''),'type':'image'})
    def handle_endtag(self,tag):
        if tag in ['script','style']:self.hidden=max(0,self.hidden-1)
        if tag=='a' and self.active: self.links.append(self.active);self.active=None
        if tag in ['p','div','tr','li']:self.parts.append('\n')
    def handle_data(self,text):
        if not self.hidden:self.parts.append(text)
        if self.active:self.active['text']+=text
def fetch(item):
    key=item['id']; path=RAW/(key+'.meta.json')
    if path.exists() and not item.get('refresh'):
        return {'id':key,'cached':True,**{k:v for k,v in json.loads(path.read_text()).items() if k in ['httpStatus','bytes','error','archiveFile']}}
    host=urlparse(item['url']).netloc
    with GUARD: lock=LOCKS.setdefault(host,threading.Lock())
    with lock:
        started=time.monotonic(); meta={**item,'checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat()}
        headers={'User-Agent':'Mozilla/5.0','Referer':item.get('referer',item['url'])};body=None
        if 'data' in item:
            is_json=item.get('encoding')=='json'
            body=(json.dumps(item['data']) if is_json else urlencode(item['data'])).encode()
            headers['Content-Type']='application/json;charset=UTF-8' if is_json else 'application/x-www-form-urlencoded;charset=UTF-8'
        try:
            with urlopen(Request(item['url'],data=body,headers=headers),timeout=25) as response:
                raw=response.read();meta.update(httpStatus=response.status,finalUrl=response.url,contentType=response.headers.get('Content-Type',''))
                enc=response.headers.get_content_charset()
            meta.update(bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())
            ext='pdf' if raw.startswith(b'%PDF') else 'png' if raw.startswith(b'\x89PNG') else 'jpg' if raw.startswith(b'\xff\xd8') else 'zip' if raw.startswith(b'PK\x03\x04') else 'html'
            if ext=='html':
                declared=re.search(br'charset\s*=\s*["\']?([\w-]+)',raw[:10000],re.I)
                enc=enc or (declared.group(1).decode() if declared else 'utf-8')
                try: text=raw.decode(enc)
                except (UnicodeDecodeError,LookupError):text=raw.decode('utf-8',errors='replace')
                try: json.loads(text);ext='json'
                except ValueError:pass
                if ext=='html':
                    page=Page();page.feed(text)
                    plain='\n'.join(re.sub(r'\s+',' ',s).strip() for s in ''.join(page.parts).splitlines() if s.strip())
                    (RAW/(key+'.text.txt')).write_text(plain)
                    links=[{**l,'url':urljoin(meta['finalUrl'],l['href'])} for l in page.links]
                    (RAW/(key+'.links.json')).write_text(json.dumps(links,ensure_ascii=False,indent=2)+'\n')
            meta['archiveFile']=key+'.'+ext
            (RAW/meta['archiveFile']).write_bytes(raw)
        except Exception as e:meta.update(httpStatus=getattr(e,'code',None),error=str(e))
        meta['elapsedSeconds']=round(time.monotonic()-started,3)
        path.write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
        time.sleep(0.5)
        return {k:meta.get(k) for k in ['id','httpStatus','bytes','archiveFile','error']}
if __name__=='__main__':
    items=json.loads(Path(sys.argv[1]).read_text())
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        for r in pool.map(fetch,items):print(json.dumps(r,ensure_ascii=False),flush=True)
