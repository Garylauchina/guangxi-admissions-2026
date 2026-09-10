"""Replay the public Tongji frontend's read-only admission API signing flow.

Derives the public signature constant from the fetched official frontend bundle.
No user account/token is used or stored. All session/signature headers remain in memory.
"""
import datetime,hashlib,http.cookiejar,json,re,urllib.request
from pathlib import Path
from collect import redact
R=Path(__file__).resolve().parent;RAW=R/'raw'
bundle=(RAW/'tongji-js-5e0cf47.js').read_text()
key=re.search(r'ld\(e\.url,e\.data,"([^"]+)"\)',bundle).group(1)
host=re.search(r'f\.defaults\.baseURL="(https://ag-tongji-pc[^"]+)"',bundle).group(1)
assert 'provinceCode:45' in bundle and 'name:"广西"' in bundle
opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
def query(name,path,data=None):
 body=json.dumps(data,ensure_ascii=False,separators=(',',':')) if data else ''
 signature=hashlib.md5((body+'&'+key).lower().encode()).hexdigest()
 item={'id':name,'schoolCode':'10247','url':host+path,'method':'POST','data':data,'encoding':'json','entryUrl':'https://bkzs.tongji.edu.cn/luqu/admission','checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'methodNote':'按官方前端公开签名流程；未使用登录令牌，不归档签名或会话值。'}
 headers={'User-Agent':'Mozilla/5.0','Content-Type':'application/json','Referer':item['entryUrl'],'u-sign':signature,'u-dfs':'pc.tongji','u-token':''}
 try:
  with opener.open(urllib.request.Request(item['url'],data=body.encode(),headers=headers),timeout=25) as response: raw=response.read();item['status']=response.status
  parsed=redact(json.loads(raw));archive=json.dumps(parsed,ensure_ascii=False,indent=2).encode();filename=name+'.json';(RAW/filename).write_bytes(archive)
  item.update(rawSha256=hashlib.sha256(raw).hexdigest(),archiveSha256=hashlib.sha256(archive).hexdigest(),archiveFile=filename,bytes=len(raw))
 except Exception as e:item.update(status=getattr(e,'code',None),error=str(e));parsed=None
 (RAW/(name+'.meta.json')).write_text(json.dumps(item,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'id':name,'status':item.get('status'),'result':parsed},ensure_ascii=False));return parsed
if __name__=='__main__':
 query('tongji-years','/youzy.youz.cc.enrolldata.enterdata.year.getall')
 query('tongji-gx-2026','/youzy.youz.cc.enrolldata.enterdata.query',{'year':2026,'provinceCode':45,'pageIndex':1,'pageSize':50})
