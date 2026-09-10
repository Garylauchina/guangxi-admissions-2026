"""Supplement HTML parsing with explicitly reviewed official image transcriptions and API data."""
import json

def extend(ROOT, NOW, rows, sources, findings, excluded, checks, base_record, category, tables):
    def read(n): return json.loads((ROOT/n).read_text())
    def source(sid,title,school,count,published=None,method='',parent=None):
        m=read('raw/'+sid+'.meta.json')
        s={'id':sid,'title':title,'url':m['url'],'publisher':school,'year':2026,
           'publishedAt':published,'accessedAt':m['accessedAt'],'sha256':m['sha256'],
           'recordCount':count,'method':method,'rawPath':m['rawFile'],
           'request':m.get('request'),'requestEncoding':m.get('requestEncoding'),'auditAction':'新增已核对专业数据'}
        if parent:s['parentSourceId']=parent
        sources.append(s)
    # Actual admission results: images are manually checked in full, not unreviewed OCR.
    for sid in ['bsuc-lines-normal','bsuc-lines-special']:
        source(sid,'百色学院2026年广西专业录取情况公告','百色学院',0,'2026-07-27','公告正文图片，专业结果以图片源记录为准。')
    for sid,kind,filename in [('bsuc-lines-normal-img-4','普通类','bsuc-normal-transcription.txt'),
          ('bsuc-lines-special-img-1','精准专项','bsuc-lines-special-img-1-transcription.json'),
          ('bsuc-lines-special-img-2','民族班','bsuc-lines-special-img-2-transcription.json'),
          ('bsuc-lines-normal-img-3','公费师范','bsuc-advance-transcription.txt')]:
        if filename.endswith('.json'):
            tab=read(filename)['rows']; tab=[[c[0],c[1],c[2],c[3],c[5],c[6]] for c in tab]
        else:tab=[line.split('|') for line in (ROOT/filename).read_text().splitlines() if line and not line.startswith('#')]
        new=[]
        for i,c in enumerate(tab,1):
            county=None
            if kind=='公费师范': county=c[1];c=[c[0]]+c[2:]
            name,track,score,mean,rank,admitted=c
            assert int(score)<=int(mean) and int(rank)>0 and int(admitted)>0
            r=base_record(sid,'百色学院','10609',track,'本科提前批其它类（公费师范）' if county else '本科普通批',name,score,i,kind)
            r.update(rank=int(rank),rankType='专业最低录取分位次（源表）',admittedCount=int(admitted))
            r['note']='公告逐专业发布录取情况；录取人数不作为招生计划数。位次来自本专业最低分位次列，轮次未分。'
            if county:
                r['major']=name+'（公费师范，定向'+county+'）';r['directedArea']=county
                r['sourceBatch']='本科提前批其它类（公费师范）'
                r['batchDetailGap']='原图未进一步细分其他一类、二类或三类，不能据公费师范名称推定。'
                r['note']+='仅适用于公费师范定向'+county+'；原图分数子列名为投档成绩。'
            new.append(r)
        parent='bsuc-lines-special' if 'special' in sid else 'bsuc-lines-normal'
        source(sid,'百色学院2026年广西'+kind+'专业录取情况原图','百色学院',len(new),'2026-07-27',
               '逐行人工核对原图与转录；普通/精准/民族班列为最低分，提前批列为投档成绩最低分；公告总题为录取情况并给录取人数。',parent)
        rows.extend(new);checks.append({'sourceId':sid,'records':len(new),'result':'PASS','method':'全行原图与转录专业、科类、最低分、最低分位次、录取人数目视核对；最低分<=平均分。'})
    # The API has school summaries in dataSource that misleadingly carry one major name.
    # Only the explicitly separate major_data_source is admissible as major-level evidence.
    sid='gxmu-lines-2026-valid';payload=read('raw/'+sid+'.json');assert payload['code']==0
    data=payload['data'];assert len(data['dataSource'])==6 and len(data['major_data_source'])==77
    for r in data['dataSource']:excluded.append({'sourceId':sid,'reason':'学校汇总dataSource，含代表性专业名仍不是专业行，整批排除。','sourceCells':r})
    new=[]
    for i,c in enumerate(data['major_data_source'],1):
        assert c['year']=='2026' and c['province_name']=='广西' and c['province']=='45'
        if c['level']=='预科':excluded.append({'sourceId':sid,'sourceRow':i,'reason':'预科不当具体本科专业','sourceCells':c});continue
        assert c['subjects'] in ('历史类','物理类') and float(c['min_score'])<=float(c['average'])<=float(c['max_score'])
        kind=category(c['major'])
        if '定向医学生' in c['major']:kind='定向医学生'
        elif '中澳' in c['major']:kind='中澳联合培养项目'
        batch='高职高专普通批' if c['batch']=='专科批' else c['batch'] if '提前' in c['batch'] else '本科普通批'
        r=base_record(sid,'广西医科大学','10598',c['subjects'].replace('类',''),batch,c['major'],c['min_score'],i,kind)
        r.update(rank=int(c['lowest_position']),rankType='专业最低录取分位次（源表）',sourceBatch=c['batch'],sourceCategory=c['enroll_type'])
        r['sourceTable']='major_data_source'
        r['note']='官方分专业录取情况查询；位次为本专业最低分位次，轮次未分。'
        if c['num']:
            r['unclassifiedSourceCount']=int(c['num']);r['note']+='接口人数值未在本次公开列配置标明口径，暂不归入计划数或录取数。'
        if c['major_group']:r['group']=c['major_group']
        if c['xkyq'] not in ('','-'):r['requirementText']=c['xkyq']
        new.append(r)
    source('gxmu-score-portal','广西医科大学官网链接的历年分数查询','广西医科大学',0,method='入口由学校招生网 https://zs.gxmu.edu.cn/list-6u2d8983/linianfenshu/1/10 嵌入。')
    source('gxmu-score-config','广西医科大学历年分数公开列及年份配置','广西医科大学',0,method='公开查询配置确认2026可选；num未在本次公开列标名，不解释人数口径。',parent='gxmu-score-portal')
    source(sid,'广西医科大学2026年广西分专业录取情况公开查询','广西医科大学',len(new),method='严格只取major_data_source专业行；6条dataSource汇总和1条预科不进入实际专业分。人数口径未公布故不反推计划/录取人数；资格从逐条专业原名提取。',parent='gxmu-score-portal')
    rows.extend(new);checks.append({'sourceId':sid,'records':len(new),'result':'PASS','method':'API成功码、每行2026/广西、单列专业表、分数上下界、类别及字段逐项核对。'})
    # Separate professional filing thresholds from actual admission outcomes.
    filing=[]
    for sid,track in [('gxgc-lines-physics','物理'),('gxgc-lines-history','历史')]:
        tabs,text=tables(sid);tab=[t for t in tabs if t[0]==['专业代码','专业名称','批次名称','科类','计划类别','投档最低分']][0]
        for i,c in enumerate(tab[1:],2):
            assert c[3]==track+'类' and c[2]=='高职高专普通批' and c[4] in ('普通类','师范类')
            r=base_record(sid,'广西工程职业学院','14127',track,c[2],c[1],c[5],i)
            r.update(majorCode=c[0],scoreType='专业投档最低分',sourceCategory=c[4])
            r['note']='原文仅称各专业最低投档分数线；尚未据此确认实际专业录取最低分。'
            filing.append(r)
        source(sid,'广西工程职业学院2026年广西普通批'+track+'类各专业最低投档分数线','广西工程职业学院',len(tab)-1,'2026-08-07','逐专业投档线另表保留，不能计入实际录取覆盖。')
    assert len(filing)==81
    return filing
