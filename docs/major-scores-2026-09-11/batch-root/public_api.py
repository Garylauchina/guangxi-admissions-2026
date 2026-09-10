import urllib.request,urllib.parse,http.cookiejar,time,json,hashlib,datetime,pathlib,concurrent.futures
ROOT=pathlib.Path(__file__).parent/'raw'
ROOT.mkdir(parents=True,exist_ok=True)
class PublicAPI:
 def __init__(self,host,prefix):
  self.host=host;self.prefix=prefix;self.opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()));self.tokens=[]
  self.opener.open(urllib.request.Request(host+'/zsw/lnfs.html',headers={'User-Agent':'Mozilla/5.0'}),timeout=30).read()
 def req(self,path,data,token=False):
  stamp=str(int(time.time()*1000));url=self.host+'/'+path+'?ts='+stamp
  headers={'User-Agent':'Mozilla/5.0','Referer':self.host+'/zsw/lnfs.html','X-Requested-Time':stamp,'X-Requested-With':'XMLHttpRequest','Content-Type':'application/x-www-form-urlencoded; charset=UTF-8'}
  if token: headers['Csrf-Token']=self.tokens.pop(0)
  with self.opener.open(urllib.request.Request(url,data=urllib.parse.urlencode(data).encode(),headers=headers),timeout=30) as r:
   b=r.read();nexttoken=r.headers.get('Csrf-Token')
   if nexttoken:self.tokens.append(nexttoken)
   return b
 def query(self,name,path,data):
  meta={'url':self.host+'/'+path,'method':'POST','requestData':data,'checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'access':'公开页面原有会话及CSRF流程；不存储会话值'}
  try:
   if not self.tokens:
    r=json.loads(self.req('f/ajax_get_csrfToken',{'n':3}));self.tokens+=r['data'].split(',')
   b=self.req(path,data,True);meta.update(status=200,sha256=hashlib.sha256(b).hexdigest(),bytes=len(b));parsed=json.loads(b);parsed.pop('jessionid',None);archived=json.dumps(parsed,ensure_ascii=False,indent=2).encode();meta['archiveSha256']=hashlib.sha256(archived).hexdigest();meta['redactedFields']=['jessionid'];(ROOT/(self.prefix+'-'+name+'.json')).write_bytes(archived)
  except Exception as e:meta['error']=str(e)
  (ROOT/(self.prefix+'-'+name+'.meta.json')).write_text(json.dumps(meta,ensure_ascii=False,indent=2));print(json.dumps(meta,ensure_ascii=False))
  return meta

if __name__=='__main__':
 api=PublicAPI('https://lqcx.nankai.edu.cn','nankai');api.query('score-params','f/ajax_lnfs_param',{})
