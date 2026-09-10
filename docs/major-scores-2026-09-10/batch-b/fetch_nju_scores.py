import urllib.request,urllib.parse,http.cookiejar,time,json,hashlib,datetime,pathlib,concurrent.futures
ROOT=pathlib.Path(__file__).parent/'raw'
class PublicAPI:
 def __init__(self,host,prefix):
  self.host=host;self.prefix=prefix;self.opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()));self.tokens=[]
  self.opener.open(urllib.request.Request(host+'/static/front/nju/basic/html_web/lnfs.html',headers={'User-Agent':'Mozilla/5.0'}),timeout=30).read()
 def req(self,path,data,token=False):
  stamp=str(int(time.time()*1000));url=self.host+'/'+path+'?ts='+stamp
  headers={'User-Agent':'Mozilla/5.0','Referer':self.host+'/static/front/nju/basic/html_web/lnfs.html','X-Requested-Time':stamp,'X-Requested-With':'XMLHttpRequest','Content-Type':'application/x-www-form-urlencoded; charset=UTF-8'}
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
 parser=argparse.ArgumentParser();parser.add_argument('--all-current',action='store_true');parser.add_argument('--probe-current-missing',action='store_true');args=parser.parse_args()
 api=PublicAPI('https://bkzs.nju.edu.cn','nju')
 api.query('score-params-session','f/ajax_lnfs_param',{})
 if args.all_current:
  params=json.loads((ROOT/'nju-score-params-session.json').read_text())['data']
  gx=params['ssmc_nf_klmc_sex_campus_zslx_Map'].get('\u5e7f\u897f',[])
  candidates=[x for x in gx if x.get('nf')=='2026' and x.get('klmc') in ['\u7269\u7406\u7c7b','\u5386\u53f2\u7c7b']]
  for i,x in enumerate(candidates,1):
   name='scores-gx-2026-'+str(i).zfill(2)
   api.query(name,'f/ajax_lnfs',{'ssmc':'\u5e7f\u897f','zsnf':'2026','klmc':x['klmc'],'zslx':x['zslx']})
 if args.probe_current_missing:
  params=json.loads((ROOT/'nju-score-params-session.json').read_text())['data']
  gx=params['ssmc_nf_klmc_sex_campus_zslx_Map'].get('\u5e7f\u897f',[])
  for i,track in enumerate(['\u7269\u7406\u7c7b','\u5386\u53f2\u7c7b'],1):
   assert any(x.get('klmc')==track and x.get('zslx')=='\u666e\u901a\u6279\u6b21' for x in gx)
   api.query('scores-gx-2026-probe-'+str(i),'f/ajax_lnfs',{'ssmc':'\u5e7f\u897f','zsnf':'2026','klmc':track,'zslx':'\u666e\u901a\u6279\u6b21'})
 for f in ROOT.glob('nju-*.meta.json'):
  m=json.loads(f.read_text())
  if 'archiveSha256' not in m:continue
  m['accessedAt']=m['checkedAt'];m['id']=f.name[:-10];m['request']=m['requestData'];m['requestEncoding']='form';m['ext']='json'
  if 'responseSha256' not in m:m['responseSha256']=m['sha256']
  m['sha256']=m['archiveSha256'];m['rawFile']='raw/'+m['id']+'.json';m['byteCount']=(ROOT/(m['id']+'.json')).stat().st_size
  f.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
