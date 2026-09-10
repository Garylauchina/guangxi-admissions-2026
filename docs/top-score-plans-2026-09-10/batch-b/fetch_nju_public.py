import urllib.request,urllib.parse,http.cookiejar,time,json,hashlib,datetime,pathlib,concurrent.futures
ROOT=pathlib.Path(__file__).parent/'raw'
class PublicAPI:
 def __init__(self,host,prefix):
  self.host=host;self.prefix=prefix;self.opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()));self.tokens=[]
  self.opener.open(urllib.request.Request(host+'/static/front/nju/basic/html_web/zsjh.html',headers={'User-Agent':'Mozilla/5.0'}),timeout=30).read()
 def req(self,path,data,token=False):
  stamp=str(int(time.time()*1000));url=self.host+'/'+path+'?ts='+stamp
  headers={'User-Agent':'Mozilla/5.0','Referer':self.host+'/static/front/nju/basic/html_web/zsjh.html','X-Requested-Time':stamp,'X-Requested-With':'XMLHttpRequest','Content-Type':'application/x-www-form-urlencoded; charset=UTF-8'}
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
 import argparse
 parser=argparse.ArgumentParser();parser.add_argument('--normal',action='store_true');args=parser.parse_args()
 api=PublicAPI('https://bkzs.nju.edu.cn','nju')
 api.query('params-session','f/ajax_zsjh_param',{})
 if args.normal:
  params=json.loads((ROOT/'nju-params-session.json').read_text())['data']
  gx=params['ssmc_nf_klmc_sex_campus_zslx_Map']['\u5e7f\u897f']
  candidates=[x for x in gx if x.get('nf')=='2026' and x.get('klmc')=='\u7269\u7406\u7c7b' and x.get('zslx')=='\u666e\u901a\u6279\u6b21']
  assert len(candidates)==1, 'Expected exact public filter option; inspect params before changing scope'
  api.query('gx-2026-normal','f/ajax_zsjh',{'ssmc':'\u5e7f\u897f','zsnf':'2026','klmc':'\u7269\u7406\u7c7b','zslx':'\u666e\u901a\u6279\u6b21'})
 for name in ['nju-params-session','nju-gx-2026-normal']:
  f=ROOT/(name+'.meta.json')
  if not f.exists():continue
  m=json.loads(f.read_text());m['accessedAt']=m['checkedAt'];m['id']=name;m['request']=m['requestData'];m['requestEncoding']='form';m['ext']='json'
  if m.get('archiveSha256'):
   m['responseSha256']=m['sha256'];m['sha256']=m['archiveSha256'];m['rawFile']='raw/'+name+'.json';m['byteCount']=(ROOT/(name+'.json')).stat().st_size
  f.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
