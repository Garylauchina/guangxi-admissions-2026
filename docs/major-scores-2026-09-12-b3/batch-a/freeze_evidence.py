#!/usr/bin/env python3
"""Freeze bounded public-source findings from local raw archives; no network/repository access."""
import collections,datetime,hashlib,json,re
from pathlib import Path
R=Path(__file__).resolve().parent;P='major-20260912b3-a-'
SCHOOLS={'swu':('10635','西南大学'),'hfut':('10359','合肥工业大学'),'nwafu':('10712','西北农林科技大学'),'gzhu':('11078','广州大学'),'ncepu':('10079','华北电力大学(保定)'),'ncu':('10403','南昌大学'),'dmu':('10161','大连医科大学')}
def read(n):return json.loads((R/n).read_text())
def write(n,d):(R/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
metas=[json.loads(f.read_text()) for f in sorted((R/'raw').glob('*.meta.json'))]
assert len(metas)==51,'Inventory changed; review before refreshing.'
sources=[];manifest=[]
for m in metas:
 k=m['id'];code,name=SCHOOLS[k.split('-')[0]];body=(R/m['rawFile']).read_bytes();assert hashlib.sha256(body).hexdigest()==m['sha256']
 role='公开入口、导航或前端字段';count=None;year=None
 if 'param' in k or 'types' in k or 'config' in k:role='公开查询条件配置'
 if '-gx-' in k:role='广西分专业查询响应';year=2026 if '-2026-' in k else 2025
 if m['httpStatus']!=200:role='请求失败证据（不是成功空表）'
 if k=='nwafu-types':role='初次请求未携带JSON体的失败记录（已用有效参数重查）'
 if k=='nwafu-old-entry':role='旧入口重定向身份认证页面（另有公开新入口）'
 if k=='dmu-old-pdf':role='2025附件链接返回验证码HTML（未取得PDF）'
 if k=='dmu-old':role='2025分专业录取分公告目录（附件未读）';year=2025
 if k=='ncepu-major-data':role='保定各专业分数公开JSON（仅2025）';year=2025
 if k=='ncepu-summary-data':role='保定录取汇总JSON（非专业分）'
 if m['httpStatus']==200 and m.get('ext')=='json':
  d=json.loads(body)
  if isinstance(d.get('data'),dict) and 'sszygradeList' in d['data']:count=len(d['data']['sszygradeList'])
  elif 'list' in d:count=len(d['list'])
  elif k=='ncepu-major-data':count=len(d['data'])
  elif isinstance(d.get('data'),dict) and 'dataList' in d['data']:count=len(d['data']['dataList'])
  # Application code 9999 is an explicit no-match message, not a successful array response.
 s=dict(id=P+k,schoolCode=code,title=name+'：'+role+' ['+k+']',url=m['url'],entryUrl=m.get('entryUrl'),year=year,publishedAt=None,accessedAt=datetime.datetime.fromisoformat(m['accessedAt']).astimezone(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),httpStatus=m['httpStatus'],sha256=m['sha256'],archiveSha256=m['sha256'],responseSha256=m['responseSha256'],archiveFile=m['rawFile'],recordCount=count,queryParameters=m.get('request'),method='按官方入口及已读前端字段正常GET/POST；原响应hash与脱敏归档hash分别保存；匿名会话仅在内存使用。')
 if m.get('accessError'):s['accessError']=m['accessError']
 # Do not export redirect state or session query values from university SSO pages.
 if m.get('finalUrl') and '?' not in m['finalUrl'] and '#' not in m['finalUrl']:s['finalUrl']=m['finalUrl']
 sources.append(s)
 j={a:b for a,b in m.items() if a in ['id','url','method','encoding','request','path','host','entryUrl','csrf','ext','publicHeaders']};j.update(expectedHttpStatus=m['httpStatus'],expectedArchiveSha256=m['sha256']);manifest.append(j)
e={'scopeYear':2026,'recordCount':0,'schools':{}}
for prefix,ncur,nold in [('ncu',3,[30,8]),('hfut',3,[27,3]),('nwafu',5,[44,6])]:
 key=prefix+'-params' if prefix!='nwafu' else 'nwafu-types-valid';d=read('raw/'+key+'.json')
 if prefix=='nwafu':opts={k:v for k,v in d['typeMap'].items() if k.startswith('广西_')};assert d['success'];years=sorted({k.split('_')[1] for k in opts})
 else:opts=[x for x in d['data']['ssmc_nf_klmc_sex_campus_zslx_list'] if next(iter(x)).startswith('广西_')];assert d['state']==1;years=sorted({next(iter(x)).split('_')[1] for x in opts})
 assert '2026' not in years
 queries=[];controls=[]
 for m in metas:
  if not m['id'].startswith(prefix+'-gx-'):continue
  q=read(m['rawFile']);a=q['list'] if prefix=='nwafu' else q['data']['sszygradeList'];valid=q.get('success') is True if prefix=='nwafu' else q.get('state')==1
  assert m['httpStatus']==200 and valid
  if '-2026-' in m['id']:
   assert a==[];queries.append(dict(sourceId=P+m['id'],parameters=m['request'],applicationSuccess=True,majorRows=0))
  else:
   assert all(x['nf']=='2025' and x.get('sf',x.get('ssmc'))=='广西' and x['klmc']==m['request']['klmc'] for x in a)
   if prefix=='hfut':assert all(x.get('campus')=='合肥校区' for x in a)
   controls.append(dict(sourceId=P+m['id'],parameters=m['request'],applicationSuccess=True,majorRows=len(a)))
 assert len(queries)==ncur and sorted(x['majorRows'] for x in controls)==sorted(nold)
 e['schools'][SCHOOLS[prefix][0]]=dict(availableGuangxiYears=years,menuOptions=opts,queries=queries,oldYearControls=controls)
 if prefix=='hfut':
  assert '所有分数均为第一次投档数据' in d['data']['remarks']['remark1'];e['schools']['10359']['sourceScopeWarning']='所有分数均为第一次投档数据';e['schools']['10359']['campus']='合肥校区'
# Guangzhou query columns come directly from public configuration, needLogin=N/msgCode=N.
g=read('raw/gzhu-config-public.json');assert g['code']=='0000' and g['data']['needLogin']=='N' and g['data']['msgCode']=='N'
g=read('raw/gzhu-gx-2025-control.json');a=g['data']['dataList'];assert g['code']=='0000' and g['data']['total']==len(a)==17
fields={'province':'Item-1746001468596-3612-value','year':'Item-1746001468596-3907-value','track':'Item-1746001468596-6833-value','category':'Item-1746001468596-5295-value'}
assert all(x[fields['year']]=='2025' and x[fields['province']]=='广西' for x in a)
gq=[]
for k in ['gzhu-gx-2026-all','gzhu-gx-2026-1','gzhu-gx-2026-2']:
 d=read('raw/'+k+'.json');assert d['code']=='9999' and d['msg']=='未查询到相关数据' and d['data'] is None
 m=next(m for m in metas if m['id']==k);gq.append(dict(sourceId=P+k,parameters=m['request'],applicationCode='9999',message=d['msg'],successfulArrayResponse=False))
e['schools']['11078']=dict(needLogin=False,requiresCaptcha=False,currentQueries=gq,oldYearControl=dict(sourceId=P+'gzhu-gx-2025-control',year=2025,province='广西',totalRows=17,receivedRows=17,tracks=dict(collections.Counter(x[fields['track']] for x in a)),categories=sorted({x[fields['category']] for x in a})),initialOldRequestFailed=True)
a=read('raw/ncepu-major-data.json')['data'];gx=[x['properties'] for x in a if x['properties']['province']=='广西'];assert len(a)==1166 and {x['properties']['year'] for x in a}=={'2025'} and len(gx)==41
assert '华北电力大学（保定）' in re.sub(r'\s+','',(R/'raw/ncepu-home.html').read_text())
e['schools']['10079']=dict(sourceId=P+'ncepu-major-data',tableYears=[2025],fullRows=1166,guangxiRows=41,tracks=dict(collections.Counter(x['scienceCategory'] for x in gx)),categories=sorted({x['type'] for x in gx}),campusEvidence='保定官网页尾及major_bd_json.json独立前端路径',currentActualRows=0)
assert all(next(m for m in metas if m['id']==k)['httpStatus']==412 for k in ['swu-entry','swu-entry-https'])
e['schools']['10635']=dict(sourceIds=[P+'swu-home',P+'swu-entry',P+'swu-entry-https'],accessStatus=412,actualScoreQueriesRun=False)
s=(R/'raw/dmu-directory.html').read_text();assert '2023-2025' in s and '2025年分省市区' in s
assert '验证码' in (R/'raw/dmu-old-pdf.pdf').read_text()
e['schools']['10161']=dict(sourceIds=[P+'dmu-directory',P+'dmu-old',P+'dmu-old-pdf'],latestListedScoreYear=2025,attachmentAccess='captcha-html',attachmentBodyVerified=False,actualScoreQueriesRun=False)
checked=max(s['accessedAt'] for s in sources);assert checked.startswith('2026-09-12')
write('review-context.json',dict(reviewDate='2026-09-12',checkedAt=checked,scopeYear=2026,sourceCount=51,schoolCount=7,scoreRows=0,baselineCommit='89383ef',baselineMajorRows=1120))
write('source-snapshots.json',sources);write('query-evidence.json',e);write('public-fetch-manifest.json',manifest)
print('PASS: 51 source archives; 11 valid empty arrays, 3 explicit no-match messages, 7 old-year positive controls.')
