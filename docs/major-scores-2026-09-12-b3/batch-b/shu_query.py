"""Replay the official public FineUI form. Cookie and hidden state stay in memory.
Selection values and response hashes are archived; no session state is published.
"""
from pathlib import Path
import urllib.request,urllib.parse,http.cookiejar,json,base64,re,hashlib,datetime
from html import unescape
R=Path(__file__).resolve().parent;RAW=R/'raw';URL='https://bks.shu.edu.cn/pub/scores.aspx'
def clean(s):
 s=re.sub(r'^.*?return;;;','[SESSION STATE REDACTED]',s,flags=re.S) if 'F.f_viewState(__VIEWSTATE' in s else s
 return re.sub(r'(<input[^>]+name="(?:__VIEWSTATE|__EVENTVALIDATION|F_STATE)"[^>]+value=")[^"]*',r'\1[REDACTED]',s)
def run(y,category):
 label={'一本':'normal','一本中外':'coop','国家专项':'national','高校专项':'special'}[category];name=f'shu-gx-{y}-{label}'
 m={'id':name,'url':URL,'data':{'year':y,'province':'广西','category':category,'track':'全部'},'checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'accessMethod':'Actual public FineUI form POST with fresh hidden state; state and Cookie values omitted.'}
 try:
  op=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()));h={'User-Agent':'Mozilla/5.0','Referer':URL}
  s=op.open(urllib.request.Request(URL,headers=h),timeout=25).read().decode()
  hidden={k:unescape(v) for k,v in re.findall(r'<input[^>]+name="([^"]+)"[^>]+value="([^"]*)"',s)}
  states={}
  for match in re.finditer(r'var (f\d+)_state=',s):
   i=match.group(1);state=json.JSONDecoder().raw_decode(s[match.end():])[0]
   control=re.search(r'var '+i+r'=new F\.\w+\(\{.*?id:\'([^\']+)\'',s)
   if control:states[control.group(1)]=state
  values={'SC_Year':str(y),'SC_ShengYD':'广西','SC_LeiXing':category,'SC_KeMZ':'全部'}
  for k,v in values.items():
   hidden['Panel1$ctl00$'+k+'$Value']=v
   if 'Panel1_ctl00_'+k in states:states['Panel1_ctl00_'+k]['SelectedValueArray']=[v]
  hidden.update(__EVENTTARGET='Panel1$ctl00$btnOK',__EVENTARGUMENT='',F_STATE=base64.b64encode(json.dumps(states,ensure_ascii=False).encode()).decode())
  hidden['F_TARGET']='Panel1_ctl00_btnOK';h['X-FineUI-Ajax']='true';h['Content-Type']='application/x-www-form-urlencoded; charset=UTF-8'
  with op.open(urllib.request.Request(URL,data=urllib.parse.urlencode(hidden).encode(),headers=h),timeout=25) as resp:raw=resp.read();m['status']=resp.status
  s=clean(raw.decode());body=s.encode();fn=name+'.html';(RAW/fn).write_bytes(body)
  m.update(rawSha256=hashlib.sha256(raw).hexdigest(),archiveSha256=hashlib.sha256(body).hexdigest(),archiveFile=fn,bytes=len(raw))
 except Exception as e:m.update(status=getattr(e,'code',None),error=str(e))
 (RAW/(name+'.meta.json')).write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n');print(name,m.get('status'),m.get('error'),m.get('bytes'))
if __name__=='__main__':
 for y,c in [(2025,'一本'),(2026,'一本'),(2026,'一本中外'),(2026,'国家专项'),(2026,'高校专项')]:run(y,c)
