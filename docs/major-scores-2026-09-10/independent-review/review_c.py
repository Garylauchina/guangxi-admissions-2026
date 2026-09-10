"""Independent read-only comparison of batch C against archived official tables.

Does not import the batch collector/parser or modify the website/batch.
Usage: python3 review_c.py [batch-c-directory] [site-data-directory]
"""
import collections
import hashlib
import html
import json
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
BATCH = Path(sys.argv[1]) if len(sys.argv)>1 else HERE.parent/'batch-c'
SITE = Path(sys.argv[2]) if len(sys.argv)>2 else HERE.parents[2]/'guangxi-admissions-2026/site/data'
RAW = BATCH/'raw'
read = lambda p: json.loads(p.read_text())
digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
def table(name):
    text=(RAW/(name+'.html')).read_text()
    # These official responses contain one flat table, no merged/nested cells.
    tables=re.findall(r'<table\b[^>]*>(.*?)</table>',text,re.S|re.I)
    assert len(tables)==1 and not re.search(r'rowspan|colspan',tables[0],re.I)
    rows=[]
    for tr in re.findall(r'<tr\b[^>]*>(.*?)</tr>',tables[0],re.S|re.I):
        cells=re.findall(r'<t[dh]\b[^>]*>(.*?)</t[dh]>',tr,re.S|re.I)
        rows.append([re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]*>','',c))).strip() for c in cells])
    assert rows[0]==['年份','专业名称','批次','投档单位','控制线','最高分','平均分','最低分']
    return rows[1:]

rows=read(BATCH/'major-cutoffs-upsert.json')
sources={s['id']:s for s in read(BATCH/'sources.json')}
cfg=read(RAW/'glmu-2026-select.json')['data']['tddwList']
groups={}
for g in cfg:
    assert g['year']==2026 and g['provinceId']==20 and g['provinceName']=='广西'
    key=(g['batchNo'],g['tddw'],g['kldm'])
    if key in groups:
        assert all(g[k]==groups[key][k] for k in ['batchCNName','tddwName','kldmCNName','year','provinceName'])
    groups[key]=g
expected={}; excluded=[]; raw_group_rows=[]; group_summary=[]
for key,g in groups.items():
    name='glmu-g-'+'-'.join(key); sid='mscore-c-2026-'+name
    meta=read(RAW/(name+'.meta.json')); req=meta['request']
    assert meta['status']==200
    assert req['recruitScore.year']=='2026' and req['recruitScore.provinceId']=='20' and req['recruitScore.provinceName']=='广西'
    assert tuple(req['recruitScore.'+f] for f in ['batchNo','tddw','kldm'])==key
    assert digest(RAW/meta['archiveFile'])==meta['archiveSha256']==sources[sid]['archiveSha256']
    assert sources[sid]['request']==req
    raw=table(name); raw_group_rows+=raw
    page=re.findall(r'class="maxPage"[^>]*value="(\d+)"',(RAW/(name+'.html')).read_text())
    assert not page or page==['1']
    for ri,r in enumerate(raw,2):
        assert r[0]=='2026' and r[2]==g['batchCNName'] and r[3]==g['tddwName']
        if '预科' in r[1] or '预科' in r[3]:
            excluded.append({'sourceId':sid,'sourceRow':ri,'rawRow':r});continue
        admission = ('农村订单定向免费医学生' if r[3]=='国家免费医学生_普通类' else
                     '民族班' if '民族班' in r[3] else
                     '中澳学分互认联合培养项目' if '中澳学分互认联合培养项目' in r[1] else '普通类')
        track={'1':'历史','5':'物理'}[g['kldm']]
        assert g['kldmCNName']==track+'类'
        expected[(sid,ri)]={'year':2026,'province':'广西','schoolCode':'10601','school':'桂林医科大学',
          'track':track,'batch':r[2],'group':g['tddw'],'major':r[1],'score':int(r[7]),
          'sourceMaximumScore':int(r[5]),'sourceAverageScore':float(r[6]),'rawAdmissionType':r[3],
          'admissionType':admission,'round':'录取汇总（轮次未分）','sourceTable':1,'scoreType':'专业录取最低分'}
    group_summary.append({'query':name,'group':g['tddw'],'track':g['kldmCNName'],'batch':g['batchCNName'],'rawCount':len(raw),'includedCount':sum(1 for k in expected if k[0]==sid),'archiveSha256':digest(RAW/(name+'.html'))})
assert len(expected)==57 and len(excluded)==5 and len(raw_group_rows)==62
allrows=[];pages=[]
for i in range(1,8):
    name='glmu-2026-all' if i==1 else f'glmu-all-p{i}'
    r=table(name);allrows+=r;pages.append({'page':i,'rows':len(r)})
assert [p['rows'] for p in pages]==[10,10,10,10,10,10,2]
assert collections.Counter(map(tuple,allrows))==collections.Counter(map(tuple,raw_group_rows))
actual_keys=[]; comparisons=[]
for row in rows:
    k=(row['sourceId'],row['sourceRow']);actual_keys.append(k);e=expected[k]
    assert all(row.get(f)==v for f,v in e.items()),(row['id'],{f:(row.get(f),v) for f,v in e.items() if row.get(f)!=v})
    assert 0<row['score']<=row['sourceAverageScore']<=row['sourceMaximumScore']<=750
    assert row['rank'] is None and row['rankType'] is None
    assert row.get('plannedCount') is None and row.get('admittedCount') is None
    assert row['scoreComparable'] is True and row['conflictFields']==[] and row['scoreEvidenceGaps']==[]
    assert row['fieldSourceIds']['group']==['mscore-c-2026-glmu-2026-select',row['sourceId']]
    for ids in row['fieldSourceIds'].values():
        assert all(sid in sources for sid in ids)
    comparisons.append({'id':row['id'],'sourceId':k[0],'sourceRow':k[1],'matchedFields':list(e),'passed':True})
assert len(set(actual_keys))==57 and set(actual_keys)==set(expected)
actual_excluded=read(BATCH/'excluded-records.json')
assert collections.Counter((r['sourceId'],r['sourceRow'],tuple(r['rawRow'])) for r in actual_excluded)==collections.Counter((r['sourceId'],r['sourceRow'],tuple(r['rawRow'])) for r in excluded)
charter=html.unescape(re.sub(r'<[^>]*>',' ',(RAW/'glmu-charter.html').read_text()))
charter=re.sub(r'\s+',' ',charter)
assert all(s in charter for s in ['桂林医科大学2026','4145010601','加分与降分计入总分','第十八条','第十九条','第二十条','90分'])
joint=[r for r in rows if r['admissionType']=='中澳学分互认联合培养项目']
assert len(joint)==5 and all('90分' in r['note'] and '60%' in r['note'] and 'mscore-c-2026-glmu-charter' in r['fieldSourceIds']['note'] for r in joint)
# Original cells were separately read by the reviewer; pin representative exact readbacks.
manual=[
 ('450','临床医学(定向医学生,柳州市柳城县)',559,555.33,553),
 ('451','临床医学(定向医学生,桂林市平乐县)',574,574.0,574),
 ('101','社会工作(医学方向)',491,475.49,470),
 ('155','生物技术',558,470.50,453),
 ('155','康复治疗学',517,468.40,446),
 ('750','护理学',488,455.40,430),
 ('950','康复治疗学(中澳学分互认联合培养项目)',476,418.67,377),
 ('952','药学(中澳学分互认联合培养项目)',410,407.50,405),
 ('953','医学检验技术(中澳学分互认联合培养项目)',464,423.44,371),
 ('184','护理',424,381.44,366),
]
for group,major,mx,avg,mn in manual:
    hit=[r for r in rows if r['group']==group and r['major']==major]
    assert len(hit)==1 and (hit[0]['sourceMaximumScore'],hit[0]['sourceAverageScore'],hit[0]['score'])==(mx,avg,mn)
filings=read(SITE/'cutoffs.json')
filing_identity=[]
for r in rows:
    hit=[f for f in filings if f['year']==r['year'] and f['schoolCode']==r['schoolCode'] and f['track']==r['track'] and f['batch']==r['batch'] and f['group']==r['group']]
    filing_identity.append({'id':r['id'],'corroboratedByExistingFilingIdentity':bool(hit),'note':None if hit else '本科提前批未包含于本站16个普通批投档表，组码仍有本校2026广西配置及逐组回包直接证明。'})
assert sum(x['corroboratedByExistingFilingIdentity'] for x in filing_identity)==40
report={'checkedAt':'2026-09-10','status':'passed-data-values','batch':'C','batchSha256':digest(BATCH/'major-cutoffs-upsert.json'),
 'reviewMethod':'Independent standard-library flat-table parser; no collector/parser reuse. Full row, request, configuration, pagination and archived-hash comparison; selected original cells separately read by reviewer.',
 'summary':{'rows':len(rows),'configurationEntries':len(cfg),'uniqueQueryGroups':len(groups),'includedGroups':len({(r['batch'],r['track'],r['group']) for r in rows}),'sourceRows':62,'excludedPreparatoryRows':5,'byTrack':dict(collections.Counter(r['track'] for r in rows)),'byAdmissionType':dict(collections.Counter(r['admissionType'] for r in rows))},
 'pages':pages,'groups':group_summary,'rowComparisons':comparisons,'filingIdentityCrossCheck':filing_identity,
 'manualCellReadbacks':[{'group':g,'major':m,'maximum':mx,'average':av,'minimum':mn} for g,m,mx,av,mn in manual],
 'limits':['原始响应哈希的真实性不能独立重构会话脱敏前字节；本次独立核实归档字节哈希及元数据一致。','本次仅按原始官方归档重算逐组分值；实时分数入口独立读取超时，章程实时读取成功。','轮次未分，全部保留录取汇总；不能因为最低分碰巧与某轮组线相同改成首轮或征集。'],
 'recommendations':[{'id':'C-ENGLISH-90','severity':'P2','status':'fixed-and-independently-verified','note':'中澳5条现已补章程第20条英语单科90/150及其他满分60%要求，并具章程字段来源；不影响专业最低总分本身可比性。','sourceUrl':'https://jyw.glmu.edu.cn/zhaosheng/school!articleDetail.htm?recruitArticle.searchArticleId=145'}]}
(HERE/'batch-c-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'status':report['status'],'summary':report['summary'],'sha256':report['batchSha256']},ensure_ascii=False))
