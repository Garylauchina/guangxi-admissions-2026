#!/usr/bin/env python3
"""Freeze reviewed public summaries. Requires local raw; no network or repository access."""
from pathlib import Path
import collections,datetime,hashlib,html,json,re
R=Path(__file__).resolve().parent
P='major-20260912b2-a-'
SCHOOLS={'sdu':('10422','山东大学'),'shutcm':('10268','上海中医药大学'),'szu':('10590','深圳大学'),'shufe':('10272','上海财经大学'),'jnu':('10559','暨南大学'),'swupl':('10652','西南政法大学'),'cau':('10019','中国农业大学')}
def read(n):return json.loads((R/n).read_text())
def write(n,d):(R/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def text(n):return (R/'raw'/n).read_text()
metas=[json.loads(f.read_text()) for f in sorted((R/'raw').glob('*.meta.json'))]
assert len(metas)==60, 'Source inventory changed; re-review before replacing this snapshot.'
sources=[];manifest=[]
for m in metas:
 k=m['id'];prefix=k.split('-')[0];code,name=SCHOOLS[prefix]
 raw=R/m['rawFile'];assert hashlib.sha256(raw.read_bytes()).hexdigest()==m['sha256']
 role='公开入口或前端字段'
 if 'params' in k:role='公开历年分数查询选项'
 if '-gx-' in k:role='广西分专业查询响应'
 if 'old' in k:role='广西旧年分数表（排除）'
 if 'summary' in k:role='2026各类别录取汇总（非专业分）'
 if m['httpStatus']!=200:role='公开访问失败记录（不是空分数结果）'
 if k=='shufe-query-entry':role='历年分数表查询入口（必填验证码）'
 count=None
 if m.get('ext')=='json' and m['httpStatus']==200:
  d=json.loads(raw.read_text())
  if isinstance(d.get('data'),dict) and 'sszygradeList' in d['data']:count=len(d['data']['sszygradeList'])
 year=2026 if ('-2026-' in k or '2026-summary' in k or k=='cau-summary') else (2025 if '-2025-' in k or k in ['szu-gx-old','jnu-gx-old','jnu-year-directory'] else None)
 s=dict(id=P+k,schoolCode=code,title=name+'：'+role+' ['+k+']',url=m['url'],entryUrl=m.get('entryUrl'),year=year,publishedAt=None,accessedAt=datetime.datetime.fromisoformat(m['accessedAt']).astimezone(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),httpStatus=m['httpStatus'],sha256=m['sha256'],archiveSha256=m['sha256'],responseSha256=m['responseSha256'],archiveFile=m['rawFile'],recordCount=count,queryParameters=m.get('request'),method='根据官方入口和已读前端字段正常 GET/POST。会话仅在内存使用；归档 JSON 已移除会话字段，原响应仅保存 hash。')
 if m.get('finalUrl'):s['finalUrl']=m['finalUrl']
 if m.get('accessError'):s['accessError']=m['accessError']
 sources.append(s)
 j={a:b for a,b in m.items() if a in ['id','url','method','encoding','request','path','host','entryUrl','csrf','ext']}
 j.update(expectedHttpStatus=m['httpStatus'],expectedArchiveSha256=m['sha256']);manifest.append(j)
e={'scopeYear':2026,'recordCount':0,'schools':{},'manualReview':{'sdu-summary-table':'原图列为省市代码、省市、科类名称、统计类型、录取人数、最低分、最高分、平均分；没有专业名称列，不把类别汇总转专业分。','szu-current-entry':'主入口正文备注为按第一次投档统计。广西分专业表体年份为2025/2024，全部排除。'}}
for prefix,pk,current_prefix,current_n,old_n in [('sdu','sdu-params','sdu-gx-2026-',9,[24,11]),('cau','cau-params-https','cau-gx-session-2026-',6,[21,6])]:
 d=read('raw/'+pk+'.json');assert d['state']==1
 config=d['data']['ssmc_nf_klmc_sex_campus_zslx_list'];opts=[x for x in config if next(iter(x)).startswith('广西_')]
 years=sorted({next(iter(x)).split('_')[1] for x in opts});assert years==['2023','2024','2025']
 queries=[];controls=[]
 for m in metas:
  if m['id'].startswith(current_prefix):
   q=read(m['rawFile']);assert m['httpStatus']==200 and q['state']==1 and q['data']['sszygradeList']==[]
   queries.append(dict(sourceId=P+m['id'],parameters=m['request'],state=1,majorRows=0,summaryRows=len(q['data']['zsSsgradeList'])))
  if (m['id'].startswith('sdu-gx-2025-') if prefix=='sdu' else m['id'].startswith('cau-gx-session-2025-')):
   q=read(m['rawFile']);a=q['data']['sszygradeList'];assert m['httpStatus']==200 and q['state']==1
   assert all(x['nf']=='2025' and x['ssmc']=='广西' and x['klmc']==m['request']['klmc'] for x in a)
   controls.append(dict(sourceId=P+m['id'],parameters=m['request'],state=1,majorRows=len(a)))
 assert len(queries)==current_n and sorted(x['majorRows'] for x in controls)==sorted(old_n)
 e['schools'][SCHOOLS[prefix][0]]=dict(availableGuangxiYears=years,menuOptions=opts,queries=queries,oldYearControls=controls)
assert '2025年在广西录取分数线' in text('jnu-gx-old.html')
assert '2025年各省普通类专业录取分' in text('jnu-entry.html')
assert '2025' in text('szu-gx-old.html') and '2024' in text('szu-gx-old.html')
assert '2026' in text('shufe-query-entry.html') and '广西' in text('shufe-query-entry.html') and 'validateCodeImg' in text('shufe-query-entry.html')
assert '专业名称' in text('shufe-query-entry.html') and '最低分' in text('shufe-query-entry.html')
for code,files,statuses in [('10268',['shutcm-home','shutcm-home-retry','shutcm-school'],[504,504,403]),('10652',['swupl-home','swupl-admissions','swupl-entry'],[200,412,412])]:
 actual={m['id']:m['httpStatus'] for m in metas};assert [actual[k] for k in files]==statuses
 e['schools'][code]=dict(accessChecks=[dict(sourceId=P+k,httpStatus=actual[k]) for k in files],actualScoreQueriesRun=False)
e['schools']['10590']=dict(sourceIds=[P+'szu-directory',P+'szu-current-entry',P+'szu-gx-old'],tableYears=[2025,2024],currentActualRows=0,reason='广西表体为旧年；当前入口的第一次投档口径另需审查，不与实际专业录取汇总混淆。')
e['schools']['10559']=dict(sourceIds=[P+'jnu-entry',P+'jnu-directory',P+'jnu-year-directory',P+'jnu-gx-old'],latestScoreYear=2025,publishedYear=2026,currentActualRows=0)
e['schools']['10272']=dict(sourceId=P+'shufe-query-entry',menuYears=[2026,2025,2024],provinceOption='广西',tableFields=['年份','省市','科类名称','专业名称','最高分','最低分','备注'],captchaRequired=True,actualScoreQueriesRun=False)
checked=max(s['accessedAt'] for s in sources)
write('review-context.json',dict(reviewDate=checked[:10],checkedAt=checked,scopeYear=2026,sourceCount=len(sources),schoolCount=7,scoreRows=0,baselineCommit='5e742e9296767c0abec242531549f5c884cdb4b9',baselineMajorRows=1058))
write('source-snapshots.json',sources);write('query-evidence.json',e);write('public-fetch-manifest.json',manifest)
print('Frozen',len(sources),'sources; 15 successful current empty queries; 4 positive old-year controls.')
