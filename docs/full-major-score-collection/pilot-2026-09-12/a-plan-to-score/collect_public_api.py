#!/usr/bin/env python3
"""Repeat public score-menu requests using the frontend's anonymous CSRF flow."""
import concurrent.futures, hashlib, http.cookiejar, json, time
import urllib.parse, urllib.request
from collect import ROOT, RAW, MANIFEST, now

def strip_session(value):
    sensitive = {'jessionid','jsessionid','sessionid','session','token','csrftoken','csrf-token','cookie','set-cookie'}
    if isinstance(value, dict):
        return {k:strip_session(v) for k,v in value.items() if k.lower() not in sensitive}
    if isinstance(value, list): return [strip_session(v) for v in value]
    return value

class PublicAPI:
    def __init__(self, school):
        self.school = school
        self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
        self.tokens = []
        self.opener.open(urllib.request.Request(school['entry'], headers={'User-Agent':'Mozilla/5.0'}), timeout=25).read()

    def request(self, path, data, csrf=False):
        stamp = str(int(time.time()*1000))
        headers = {'User-Agent':'Mozilla/5.0','Referer':self.school['entry'],
                   'X-Requested-Time':stamp,'X-Requested-With':'XMLHttpRequest',
                   'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8'}
        if csrf: headers['Csrf-Token'] = self.tokens.pop(0)
        req = urllib.request.Request(self.school['host']+'/'+path+'?ts='+stamp,
                                     data=urllib.parse.urlencode(data).encode(),headers=headers)
        with self.opener.open(req,timeout=25) as response:
            body = response.read()
            if response.headers.get('Csrf-Token'): self.tokens.append(response.headers['Csrf-Token'])
            return body,response.status

    def query(self, suffix, path, request):
        s = self.school
        item = {'id':'p100a-'+s['code']+'-'+suffix,'schoolCode':s['code'],
                'school':s['school'],'url':s['host']+'/'+path,
                'request':request,'requestEncoding':'form','startedAt':now(),
                'purpose':'public-score-menu-or-statistics','entryUrl':s['entry']}
        try:
            if not self.tokens:
                raw,_ = self.request('f/ajax_get_csrfToken',{'n':3})
                self.tokens.extend(json.loads(raw)['data'].split(','))
            raw,status = self.request(path,request,True)
            parsed = strip_session(json.loads(raw))
            archive = (json.dumps(parsed,ensure_ascii=False,indent=2)+'\n').encode()
            filename = 'raw/'+item['id']+'.json'
            (ROOT/filename).write_bytes(archive)
            item.update(httpStatus=status,error=None,bytes=len(raw),rawFile=filename,
                        sha256=hashlib.sha256(archive).hexdigest(),
                        responseSha256=hashlib.sha256(raw).hexdigest(),
                        redactedFields=['session and CSRF fields if present'])
        except Exception as exc:
            item.update(httpStatus=getattr(exc,'code',None),error=str(exc),bytes=0,
                        sha256=hashlib.sha256(str(exc).encode()).hexdigest())
            parsed = None
        item['finishedAt'] = now()
        return item,parsed

def collect_school(school):
    results = []
    try:
        api = PublicAPI(school)
        item, params = api.query('params','f/ajax_lnfs_param',{})
        results.append(item)
        if not params or params.get('state') != 1: return results
        # Conditions are selected from this school's returned Guangxi menu.
        menu = params.get('data',{}).get('ssmc_nf_klmc_sex_campus_zslx_Map',{}).get('广西',[])
        (RAW/('p100a-'+school['code']+'-gx-menu.json')).write_text(json.dumps(menu,ensure_ascii=False,indent=2))
        for year in ['2026','2025']:
            rows = [r for r in menu if str(r.get('nf',r.get('zsnf'))) == year]
            if not rows and year == '2026':
                # Explicit missing-year probes retain known categories from 2025.
                rows = [r for r in menu if str(r.get('nf',r.get('zsnf'))) == '2025']
            seen = set()
            for row in rows:
                track = row.get('klmc','')
                if track not in ['物理类','历史类','物理','历史']: continue
                category = row.get('zslx','')
                key = (track,category)
                if key in seen: continue
                seen.add(key)
                request = {'ssmc':'广西','zsnf':year,'klmc':track,'zslx':category}
                for field in ['sex','campus']:
                    if row.get(field): request[field] = row[field]
                item,data = api.query('scores-'+year+'-'+str(len(seen)),'f/ajax_lnfs',request)
                item['missingYearProbe'] = year=='2026' and not any(str(r.get('nf',r.get('zsnf')))=='2026' for r in menu)
                results.append(item)
                if year == '2025': break
    except Exception as exc:
        results.append({'id':'p100a-'+school['code']+'-session-error','schoolCode':school['code'],
                        'school':school['school'],'url':school['entry'],
                        'startedAt':now(),'finishedAt':now(),'error':str(exc),
                        'httpStatus':getattr(exc,'code',None),'bytes':0,
                        'sha256':hashlib.sha256(str(exc).encode()).hexdigest()})
    return results

if __name__=='__main__':
    schools = json.loads((ROOT/'api-schools.json').read_text())
    results=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        for batch in pool.map(collect_school,schools): results.extend(batch)
    byid = {r['id']:r for r in json.loads(MANIFEST.read_text())}
    for r in results:byid[r['id']]=r
    MANIFEST.write_text(json.dumps(list(byid.values()),ensure_ascii=False,indent=2))
    for r in results: print(r['id'],r.get('httpStatus'),r.get('bytes'),r.get('error') or '')
