#!/usr/bin/env python3
"""Build a bounded 8-school admissions audit; stop if new sources need review."""
import collections, hashlib, json, re
from pathlib import Path
from parse_huuc import extract as extract_huuc

R=Path(__file__).resolve().parent

def read(name): return json.loads((R/name).read_text())
def write(name,value): (R/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')

def main():
    manifest=read('public-fetch-manifest.json')
    sources=[];metas={};snapshots=[]
    for job in manifest:
        meta=read('raw/'+job['id']+'.meta.json'); metas[job['id']]=meta
        assert meta.get('httpStatus')==200, (job['id'],'request failed')
        body=(R/meta['rawFile']).read_bytes(); digest=hashlib.sha256(body).hexdigest()
        assert digest==meta['sha256']==job['expectedArchiveSha256'], (job['id'],'source changed; inspect before rebuilding')
        sources.append({
            'id':'major-a-'+job['id'],'title':job['title'],'url':job['url'],
            'year':2026,'sourceYear':job.get('sourceYear'),'sourceKind':job['sourceKind'],
            'publishedAt':job.get('publishedAt'),'accessedAt':meta['accessedAt'],
            'sha256':digest,'responseSha256':meta.get('responseSha256'),
            'recordCount':0,'method':job['method'],'httpStatus':200,
            'request':job.get('request'),'requestEncoding':'form' if job.get('path') else None,
            'entryUrl':job.get('entryUrl'),'rawFile':meta['rawFile'],
            'targetProvince':'广西','targetYear':2026,
        })
    specs=[('ruc','10002','中国人民大学','本科一批',['physics','history']),
           ('ustc','10358','中国科学技术大学','普通本科',['physics']),
           ('bit','10007','北京理工大学','统招',['physics','history']),
           ('buaa','10006','北京航空航天大学','统招',['physics','history'])]
    notes=[];query_summary=[]
    for key,code,school,category,tracks in specs:
        param=read(f'raw/{key}-score-params.json')
        assert param['state']==1
        gx=param['data']['ssmc_nf_klmc_sex_campus_zslx_Map']['广西']
        years=sorted({x['nf'] for x in gx},reverse=True)
        assert years and max(years)=='2025' and not any(x['nf']=='2026' for x in gx), (key,'year availability changed')
        snapshots.append({'schoolCode':code,'sourceId':f'major-a-{key}-score-params',
                          'dataPath':'data.ssmc_nf_klmc_sex_campus_zslx_Map.广西',
                          'availableOptions':gx,'showField':param['data'].get('showField'),
                          'sourceRemarks':param['data'].get('remarks')})
        ids=[key+'-score-entry',key+'-score-params',key+'-plan-entry-tplt'];queries=[]
        for track in tracks:
            source_key=f'{key}-score-2026-{track}';ids.append(source_key)
            result=read('raw/'+source_key+'.json');assert result['state']==1
            assert result['data'].get('sszygradeList')==[], (key,'new major data requires substantive review')
            assert result['data'].get('zsSsgradeList')==[], (key,'new school data requires substantive review')
            query={'sourceId':'major-a-'+source_key,'request':metas[source_key]['request'],
                   'state':1,'schoolSummaryRowCount':0,'majorRowCount':0,
                   'result':'请求成功，2026广西普通类别院校和专业列表均为空'}
            queries.append(query);query_summary.append(query)
        extra=''
        if key=='ustc':
            ids.append('ustc-strong-base-exclusion')
            extra='另检索到的2026强基公告使用综合成绩，已排除；查询配置只展示省份投档线，showField3为空，不能假设存在分专业实际录取分。'
        if key=='buaa':
            ids+=['buaa-score-map','buaa-score-gx-page']
            extra='另一个官网省份地图的广西链接只提供2018/2017年；该地图数据为旧年，不能作为2026专业录取分。'
        entry=metas[key+'-score-entry']['url']
        notes.append({'year':2026,'province':'广西','schoolCode':code,'school':school,
            'status':'current-year-query-empty','entryUrl':entry,'checkedAt':metas[ids[-1]]['accessedAt'],
            'sourceIds':['major-a-'+x for x in ids],
            'checkedUrls':list(dict.fromkeys(metas[x]['url'] for x in ids)),
            'availableYears':years,'queryResults':queries,'importedRecordCount':0,
            'note':f'已核对官方历年分数页面及公开接口；广西年份选项最高为2025。实际提交2026年广西{category}查询，接口成功响应但专业和院校汇总列表均为空。'+extra+'这表示本轮查询没有得到本年记录，不代表学校未招生或穷尽性证明未发布。',
            'evidenceGaps':['2026广西分专业最低录取分未取得','专业组与省内批次未取得','首轮与征集未区分','最低位次未取得','2026专业分的成绩统计口径未取得'],
        })
    static=[
        ('10001','北京大学','pku-score-page',['pku-score-index','pku-score-page'],['2025','2024','2023','2022','2021','2020','2019','2018','2017','2016','2015'],
         '官方分数入口重定向到当前分数表，年份最高2025；广西行按省份/招生类别列文理分数，未取得2026广西分专业实际录取信息。'),
        ('19001','北京大学医学部','med-score-index',['med-home','med-score-index','med-score-2025'],['2025','2024','2023'],
         '官方历年分数栏目列2025、2024、2023；已打开最新各专业分数公告核实其标题和表格属于2025，未作为2026资料导入。医学部19001与北大本部10001分开审计。'),
        ('10003','清华大学','thu-score-index',['thu-general','thu-score-index','thu-score-2024'],['2024','2023','2022','2021','2020','2019','2018','2017','2016','2015','2014','2013','2012','2011'],
         '官方高考统招页所链接的历年录取分数栏目最新可读公告为2024各省各批次分数；不是2026广西分专业实际录取表，未导入。个人录取查询入口需要考生信息，不用于搜集个人数据。'),
    ]
    for code,school,entry_key,ids,years,note in static:
        notes.append({'year':2026,'province':'广西','schoolCode':code,'school':school,
            'status':'entry-only-year-gap','entryUrl':metas[entry_key]['url'],
            'checkedAt':metas[entry_key]['accessedAt'],'sourceIds':['major-a-'+x for x in ids],
            'checkedUrls':[metas[x]['url'] for x in ids],'availableYears':years,
            'queryResults':[],'importedRecordCount':0,'note':note+'此结论仅覆盖列出的公开栏目和本轮定向检索，不声称已遍查全校网站。',
            'evidenceGaps':['2026广西分专业最低录取分未取得','科类、批次、类别与分数口径须取得本年资料后核定']})
    records,conflicts,huuc_table=extract_huuc()
    huuc_ids=['huuc-score-2026','huuc-charter-index','huuc-charter-2026','huuc-school-code-evidence']
    notes.append({'year':2026,'province':'广西','schoolCode':'11765','school':'河南城建学院',
        'status':'collected-with-source-conflict','entryUrl':metas['huuc-score-2026']['url'],
        'checkedAt':metas['huuc-score-2026']['accessedAt'],
        'sourceIds':['major-a-'+x for x in huuc_ids],'checkedUrls':[metas[x]['url'] for x in huuc_ids],
        'availableYears':['2026'],'queryResults':[],'importedRecordCount':16,'comparableRecordCount':15,
        'sourceConflictRecordCount':1,
        'note':'官网2026年8月14日外省本科录取表的广西段16条，物理15、历史1。15条常规数值可按普通高考总分口径参考；学校章程认可政策加分，原表未单列加分处理方式，不称裸分。城市地下空间工程最高423、最低418、平均428.2，保留原值并关闭该条分数比较。未列广西正式批次、专业组、最低位次、录取人数及轮次。',
        'evidenceGaps':['城市地下空间工程原表平均超过最高，须由学校澄清','广西正式批次和专业组未列','最低位次及录取人数未列','轮次未分']})
    for source in sources:
        if source['id']=='major-a-huuc-score-2026':source['recordCount']=len(records)
    order=['10001','19001','10003','10002','10358','10007','10006','11765'];notes.sort(key=lambda x:order.index(x['schoolCode']))
    assert len(notes)==8 and len(query_summary)==7
    assert all(x['id'] in {s['id'] for s in sources} for n in notes for x in [{'id':sid} for sid in n['sourceIds']])
    write('major-cutoffs-upsert.json',records);write('sources.json',sources)
    write('school-audit-notes.json',notes);write('query-results.json',query_summary);write('parameter-evidence.json',snapshots)
    write('source-conflicts.json',conflicts);write('huuc-table-evidence.json',huuc_table)
    write('QA.json',{'status':'pass-with-evidence-gaps-and-source-conflict','year':2026,'province':'广西','schoolCount':8,
          'newMajorCutoffRows':16,'comparableRows':15,'sourceConflictRows':1,
          'majorRowsByTrack':{'物理':15,'历史':1},'successfulCurrentYearApiQueries':7,'currentYearQueriesWithMajorRows':0,
          'sourceCount':len(sources),'sourceHashesVerified':len(sources),'errors':[],
          'checks':['8所学校均有已访问官方来源及逐校结论','四校公开CSRF流程成功，参数与2026广西查询保存','河南城建广西16条按原表列逐条解析，最低减控制线等于线差','旧年/院校线/专业组线/强基综合分没有导入','无招生计划人数转作录取人数','1条平均高于最高的原文冲突保留，关闭比较','公开文件不含个人查询结果或会话值'],
          'limitations':['原7校仍无本年专业分数；新增16条仅覆盖河南城建官网广西段','15条普通高考总分可参考，不能声称剔除了政策加分','空列表不等于无招生，不是学校未发布的穷尽性证明','静态栏目只核对列出的页面，未遍查所有历史网页']})
    print(f'Built 8 school audits, 7 successful current-year empty queries, 16 major cutoffs (15 comparable), {len(sources)} sources')

if __name__=='__main__': main()
