import urllib.request,urllib.parse,urllib.error,json,hashlib,datetime,pathlib,concurrent.futures,sys
ROOT=pathlib.Path(__file__).parent/'raw'
ROOT.mkdir(parents=True,exist_ok=True)
def fetch(name,url,data=None,referer=None):
    meta={'url':url,'method':'POST' if data is not None else 'GET','requestData':data,'checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat()}
    headers={'User-Agent':'Mozilla/5.0','Referer':referer or url}
    if data is not None:headers['Content-Type']='application/x-www-form-urlencoded; charset=UTF-8'
    try:
        req=urllib.request.Request(url,data=urllib.parse.urlencode(data).encode() if data is not None else None,headers=headers)
        with urllib.request.urlopen(req,timeout=35) as r:
            b=r.read();meta.update(status=r.status,finalUrl=r.url,sha256=hashlib.sha256(b).hexdigest(),bytes=len(b));(ROOT/name).write_bytes(b)
    except Exception as e:meta.update(error=str(e))
    (ROOT/(name+'.meta.json')).write_text(json.dumps(meta,ensure_ascii=False,indent=2))
    print(json.dumps(meta,ensure_ascii=False));return meta
if __name__=='__main__':
    jobs=[('ustc-charter.html','https://zsb.ustc.edu.cn/2026/0529/c35550a741990/page.htm',None,None),('ustc-common.js','https://zsfw.ustc.edu.cn/static/front/ustc/basic/js/common.js',None,'https://zsfw.ustc.edu.cn/zsw/zsjh.html'),('ustc-params.json','https://zsfw.ustc.edu.cn/f/ajax_zsjh_param',{},'https://zsfw.ustc.edu.cn/zsw/zsjh.html'),('ruc-init.js','https://rdzs.ruc.edu.cn/static/front/ruc/basic/js/init.js',None,'https://rdzs.ruc.edu.cn/'),('ruc-common.js','https://rdzs.ruc.edu.cn/static/front/ruc/basic/js/common.js',None,'https://rdzs.ruc.edu.cn/')]
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:list(pool.map(lambda j:fetch(*j),jobs))
