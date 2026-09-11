#!/usr/bin/env python3
"""Summarize reviewed public responses. Full raw bodies are never publication outputs."""
import collections,datetime,hashlib,json,re
from pathlib import Path
from urllib.parse import parse_qs,urlparse
R=Path(__file__).resolve().parent
def read(n):return json.loads((R/n).read_text())
def write(n,v):(R/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
schools={'dlut':('10141','大连理工大学'),'cupl':('10053','中国政法大学'),'bjtu':('10004','北京交通大学'),'ustb':('10008','北京科技大学'),'bnu':('10027','北京师范大学'),'jlu':('10183','吉林大学'),'uestc':('19614','电子科技大学(沙河校区)')}
titles={'dlut-score-entry':'大连理工大学录取分数入口','cupl-home':'中国政法大学本科招生网访问记录','bjtu-home':'北京交通大学本科招生网','ustb-home':'北京科技大学本科招生网','bnu-home':'北京师范大学本科生招生网','jlu-home':'吉林大学本科招生网','uestc-query':'电子科技大学公开招生数据查询入口','bjtu-score-entry':'北京交通大学历年分数查询','ustb-score-entry':'北京科技大学历年分数查询','bnu-score-index':'北京师范大学招生计划及历年分数目录','bnu-plan-scores-2026':'北京师范大学2026年分省招生计划及近年录取分数','bnu-gx-2026-brochure':'北京师范大学2026年在广西本科招生计划及2025年各专业录取分数','jlu-score-data':'吉林大学公开历年专业录取分数整表','jlu-score-config':'吉林大学公开历年分数配置','dlut-years':'大连理工大学主校区录取分数年份查询','dlut-provinces':'大连理工大学公开省份字典','uestc-shahe-types':'电子科技大学历年分数选项（区分沙河校区）'}
sources=[];manifest=[];by={}
for f in sorted((R/'raw').glob('*.meta.json')):
 m=json.loads(f.read_text());key=m['id'];prefix=key.split('-')[0];code,school=schools[prefix]
 assert m.get('sha256') and hashlib.sha256((R/m['rawFile']).read_bytes()).hexdigest()==m['sha256']
 title=titles.get(key)
 if not title:
  suffix=key[len(prefix)+1:]
  title=school+('2026广西公开专业分查询：'+suffix.split('2026-gx-',1)[1] if '2026-gx-' in suffix else '公开前端/配置：'+suffix)
 s=dict(id='major-20260912-a-'+key,title=title,url=m['url'],schoolCode=code,accessedAt=datetime.datetime.fromisoformat(m['accessedAt']).astimezone(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),publishedAt=None,sha256=m['sha256'],responseSha256=m['responseSha256'],httpStatus=m['httpStatus'],recordCount=0,method='正常匿名公开POST查询' if m.get('path') or m.get('method')=='POST' else '公开GET',year=2026 if '2026-gx' in key else None)
 if m.get('request') is not None:s['queryParameters']=m['request']
 elif m.get('queryParameters'):s['queryParameters']=m['queryParameters']
 elif urlparse(m['url']).query:s['queryParameters']={k:v[0] for k,v in parse_qs(urlparse(m['url']).query).items()}
 if m.get('entryUrl'):s['entryUrl']=m['entryUrl']
 if key=='bnu-plan-scores-2026':s.update(publishedAt='2026-06-18',note='本年计划入口，附件的录取分数为2025年。')
 if key=='bnu-gx-2026-brochure':s.update(year=2025,note='单页表头分别为2026年招生计划与2025年录取分数；本包分数全部排除。')
 if key=='cupl-home':s['note']='HTTP 200但仅访问验证页；没有取得招生或录取数据正文。未执行验证挑战。'
 if key.startswith('jlu-score-'):s['note']='公开专业分数库的年份只有2022、2023、2024、2025。'
 sources.append(s);by[key]=s
 manifest.append({**{k:v for k,v in m.items() if k in ['id','url','ext','host','path','entryUrl','request','csrf','method','encoding','queryParameters']},'expectedArchiveSha256':m['sha256'],'expectedHttpStatus':m['httpStatus']})

# Direct assertions against all independently fetched evidence, not search snippets.
assert 'challengeId' in (R/'raw/cupl-home.html').read_text() and '/dynamic_challenge' in (R/'raw/cupl-home.html').read_text()
assert '2026 年在广西本科招生计划' in (R/'raw/bnu-gx-2026-brochure.txt').read_text()
assert '2025 年各专业录取分数' in (R/'raw/bnu-gx-2026-brochure.txt').read_text()
j=read('raw/jlu-score-data.json')['data'];assert len(j['list'])==j['total']==1704
years=dict(collections.Counter(str(r['C']) for r in j['list']));assert set(years)=={'2022','2023','2024','2025'}
gx=[r for r in j['list'] if any(float(r.get(k,0) or 0)>0 for k in ['CY','CZ','DA','DB','DC'])]
assert len(gx)==231
for code in ['bjtu','ustb']:
 param=read(f'raw/{code}-score-params.json');assert param['state']==1 and '2026' not in json.dumps(param['data'],ensure_ascii=False)
 for f in sorted((R/'raw').glob(f'{code}-2026-gx-*.json')):
  if '.meta.' in f.name:continue
  q=json.loads(f.read_text());assert q['state']==1 and q['data']['sszygradeList']==[]
for tr in ['物理类','历史类']:
 q=read('raw/uestc-shahe-2026-gx-'+tr+'.json');assert q['code']==200 and q['success'] and q['list']==[]
for tr in ['20','21']:
 for suffix in ['types','majors']:
  q=read('raw/dlut-2026-gx-'+tr+'-'+suffix+'.json');assert q['code']==200 and q['data']==[]
q=read('raw/dlut-years.json');assert q['code']==200 and q['data']==[]
types=read('raw/uestc-shahe-types.json')['typeMap'];shahe={k:v for k,v in types.items() if k.startswith('广西_') and '沙河校区' in k};assert shahe and not any('_2026_' in k for k in shahe)
campus=read('raw/dlut-dict-campus.json')['data'];assert any(r['dictValue']==1 and r['dictLabel']=='主校区（含开发区校区）' for r in campus)
obs={'scopeYear':2026,'province':'广西','sourceCount':len(sources),'recordCount':0,'evidenceBoundary':'以下仅为事实核对摘要。完整原始HTML/JS/PDF/JSON及请求元信息均保留raw，不公开发布。','schools':{
 '10141':{'campus':{'value':1,'label':'主校区（含开发区校区）'},'provinceCode':'450000','trackCodes':{'20':'物理类','21':'历史类'},'yearListResult':[],'queries':[{'year':2026,'track':tr,'typeOptions':[],'majorRows':0,'categoryFilter':'未限定；源允许的所有类型'} for tr in ['物理类','历史类']],'sourceIds':[by[k]['id'] for k in by if k.startswith('dlut-')]},
 '10053':{'httpStatus':200,'bodyKind':'浏览器访问验证页','dataQueriesExecuted':False,'reason':'未取得可读查询前端字段，未猜造接口或执行挑战','sourceIds':[by['cupl-home']['id']]},
 '10004':{'availableGuangxiYears':['2024','2025'],'queriedYear':2026,'queriedTracks':['物理','历史'],'queriedCategories':['普通类','国家专项','民族班'],'groupLabelQueries':['物化','物化-詹天佑信息类','物化-詹天佑智能类','历史','物化组','民族班'],'note':'2026未出现在配置。对照当前公开字典参数做本年空结果验证；标签取自既有公开选项，不证明2026组码或类别不变。未将威海中外类别合入本部。','majorRows':0,'sourceIds':[by[k]['id'] for k in by if k.startswith('bjtu-')]},
 '10008':{'availableGuangxiYears':['2023','2024','2025'],'queriedYear':2026,'queries':[{'track':'物理类','category':'普通类'},{'track':'物理类','category':'国家专项'},{'track':'历史类','category':'普通类'}],'majorRows':0,'sourceIds':[by[k]['id'] for k in by if k.startswith('ustb-')]},
 '10027':{'latestDirectoryEntryPublishedAt':'2026-06-18','brochurePageCount':1,'brochureTitle':'2026年在广西本科招生计划及2025年各专业录取分数','planYear':2026,'scoreYear':2025,'campusTableHeaders':['北京校区','珠海校区'],'importedRows':0,'sourceIds':[by[k]['id'] for k in by if k.startswith('bnu-')]},
 '10183':{'total':j['total'],'rows':len(j['list']),'yearCounts':years,'guangxiOldYearRows':len(gx),'guangxiYearCounts':dict(collections.Counter(str(r['C']) for r in gx)),'guangxiTracks':sorted(set(r['E'] for r in gx)),'guangxiCategories':sorted(set(r['F'] for r in gx)),'currentYearRows':0,'headMapping':{k:j['head'][0][k] for k in ['C','D','E','F','CY','CZ','DA','DB','DC']},'note':'主页面/配置/公开JS指定完整CDN表；一次下载全部1704行，total一致，无遗漏分页；数据年从C/nf逐行判定，整表没有2026。旧年数值不导入。','sourceIds':[by[k]['id'] for k in by if k.startswith('jlu-')]},
 '19614':{'sourceCampusName':'电子科技大学（沙河校区）','siteSchoolName':'电子科技大学(沙河校区)','guangxiMenu':shahe,'queries':[{'nf':'2026','sf':'广西','klmc':tr,'zslb':'普通类','xqmc':'电子科技大学（沙河校区）','code':200,'success':True,'majorRows':0} for tr in ['物理类','历史类']],'note':'本次重新请求沙河校区，未沿用昨日本部查询；没有推断未在本年菜单出现的其他类别。','sourceIds':[by[k]['id'] for k in by if k.startswith('uestc-')]}}}
write('source-snapshots.json',sources);write('query-evidence.json',obs);write('public-fetch-manifest.json',manifest)
print('Frozen',len(sources),'sources; 7 schools; 0 eligible current-year major scores.')
