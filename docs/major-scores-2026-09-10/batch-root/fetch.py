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
    jobs=[['hit-home.html', 'https://zsb.hit.edu.cn/', None, None], ['hit-scores-2026.html', 'https://zsb.hit.edu.cn/information/score?province=%E5%B9%BF%E8%A5%BF&year=2026', None, None], ['hit-scores-entry.html', 'https://zsb.hit.edu.cn/information/score', None, None], ['hust-scores.html', 'https://zsb.hust.edu.cn/bkzn/fsfzyfsx.htm', None, None], ['sxyyc-scores.html', 'https://www.sxyyc.net/zsb/info/1015/2257.htm', None, None], ['sysu-scores.html', 'https://admission.sysu.edu.cn/zsw/lnfs.html', None, None], ['sysu-tplt.js', 'https://admission.sysu.edu.cn/static/front/sysu/basic/js/tplt.js', None, None], ['zjiet-gx-scores.html', 'https://zs.zjiet.edu.cn/2026/0817/c1030a71607/pagem.htm', None, None], ['zjiet-gx-scores.png', 'https://zs.zjiet.edu.cn/_upload/article/images/d3/d0/2f45bca2432097a3305865280ad0/47dacf98-54ea-476d-ac7d-7e1bafb91ce3_d.png', None, None], ['zjiet-news.html', 'https://zs.zjiet.edu.cn/zsdt/listm.htm', None, None]]
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:list(pool.map(lambda j:fetch(*j),jobs))
