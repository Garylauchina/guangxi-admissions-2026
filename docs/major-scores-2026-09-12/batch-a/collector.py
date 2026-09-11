#!/usr/bin/env python3
"""Fetch public admissions pages and anonymous front-end score APIs; no account login."""
import argparse, concurrent.futures, datetime, hashlib, http.cookiejar, json, re, time
import urllib.parse, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RAW = ROOT / 'raw'
RAW.mkdir(exist_ok=True)

def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def strip_session(obj):
    sensitive = {'jessionid','jsessionid','sessionid','session','token','csrftoken','csrf-token','cookie','set-cookie'}
    if isinstance(obj,dict):
        return {k:strip_session(v) for k,v in obj.items() if k.lower() not in sensitive}
    if isinstance(obj,list):
        return [strip_session(v) for v in obj]
    return obj

def save(job, body, status=200, final_url=None):
    meta = dict(job, accessedAt=now(), httpStatus=status)
    meta['responseSha256'] = hashlib.sha256(body).hexdigest()
    ext = job.get('ext','html')
    if ext=='json':
        body = (json.dumps(strip_session(json.loads(body)),ensure_ascii=False,indent=2)+'\n').encode()
        meta['redactedFields'] = ['session and CSRF fields if present']
    name = f"raw/{job['id']}.{ext}"
    (ROOT/name).write_bytes(body)
    meta.update(rawFile=name,sha256=hashlib.sha256(body).hexdigest(),byteCount=len(body))
    if final_url: meta['finalUrl']=final_url
    (RAW/f"{job['id']}.meta.json").write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
    return meta

def error(job,exc):
    meta=dict(job,accessedAt=now(),httpStatus=getattr(exc,'code',None),accessError=str(exc))
    if hasattr(exc,'read'):
        body=exc.read()
        if body:
            # Preserve failed public response evidence locally, without publishing its body.
            name=f"raw/{job['id']}.error.html"; (ROOT/name).write_bytes(body)
            digest=hashlib.sha256(body).hexdigest()
            meta.update(rawFile=name,sha256=digest,responseSha256=digest,byteCount=len(body))
    (RAW/f"{job['id']}.meta.json").write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
    return meta

def fetch(job):
    try:
        headers={'User-Agent':'Mozilla/5.0'}
        data=None
        if job.get('request') is not None and job.get('method')=='POST':
            if job.get('encoding')=='json':
                headers['Content-Type']='application/json;charset=utf-8';data=json.dumps(job['request'],ensure_ascii=False).encode()
            else:
                headers['Content-Type']='application/x-www-form-urlencoded;charset=utf-8';data=urllib.parse.urlencode(job['request']).encode()
        if job.get('entryUrl'):headers['Referer']=job['entryUrl']
        with urllib.request.urlopen(urllib.request.Request(job['url'],headers=headers,data=data,method=job.get('method','GET')),timeout=35) as r:
            return save(job,r.read(),r.status,r.geturl())
    except Exception as exc:return error(job,exc)

class PublicAPI:
    def __init__(self,host,entry):
        self.host=host;self.entry=entry;self.tokens=[]
        self.opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
        self.opener.open(urllib.request.Request(entry,headers={'User-Agent':'Mozilla/5.0'}),timeout=35).read()
    def req(self,path,data,token=False):
        stamp=str(int(time.time()*1000));url=self.host+'/'+path+'?ts='+stamp
        headers={'User-Agent':'Mozilla/5.0','Referer':self.entry,'X-Requested-Time':stamp,'X-Requested-With':'XMLHttpRequest','Content-Type':'application/x-www-form-urlencoded; charset=UTF-8'}
        if token:headers['Csrf-Token']=self.tokens.pop(0)
        request=urllib.request.Request(url,data=urllib.parse.urlencode(data).encode(),headers=headers)
        with self.opener.open(request,timeout=35) as r:
            body=r.read();next_token=r.headers.get('Csrf-Token')
            if next_token:self.tokens.append(next_token)
            return body,r.status
    def query(self,job):
        try:
            if job.get('csrf') and not self.tokens:
                body,_=self.req('f/ajax_get_csrfToken',{'n':3})
                tokens=json.loads(body)['data'];self.tokens.extend(tokens.split(','))
            body,status=self.req(job['path'],job['request'],bool(job.get('csrf')))
            return save(job,body,status)
        except Exception as exc:return error(job,exc)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('manifest');args=parser.parse_args()
    jobs=json.loads((ROOT/args.manifest).read_text())
    if jobs and 'path' in jobs[0]:
        api=PublicAPI(jobs[0]['host'],jobs[0]['entryUrl'])
        result=[api.query(job) for job in jobs]
    else:
        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool: result=list(pool.map(fetch,jobs))
    for row in result:print(row['id'],row.get('httpStatus'),row.get('byteCount'),row.get('accessError',''))

if __name__=='__main__': main()
