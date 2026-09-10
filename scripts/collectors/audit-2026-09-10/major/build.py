#!/usr/bin/env python3
"""Rebuild the audited 2026 Guangxi major outcomes from public evidence; stdlib only."""
import collections, datetime, hashlib, json, re
from pathlib import Path
from html_tables import NestedTables, expand
ROOT=Path(__file__).resolve().parent
NOW=datetime.datetime.now(datetime.timezone.utc).isoformat()
def read(name):return json.loads((ROOT/name).read_text())
def dump(name,obj):(ROOT/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
def tables(key):
    b=(ROOT/'raw'/f'{key}.html').read_bytes()
    text=b.decode('gbk' if key.startswith('cqie') else 'utf-8-sig')
    p=NestedTables();p.feed(text)
    return [expand(x) for x in p.tables if x],text
def number(x):
    v=float(x);return int(v) if v.is_integer() else v
def normalize(x):return re.sub(r'\s+','',x).replace('（','(').replace('）',')')
def category(name,source='普通类'):
    for term in ['精准专项','国家专项','地方专项','民族班','中外合作办学','公费师范']:
        if term in name or term in source:return term
    return source
def base_record(sid,school,code,track,batch,major,score,row,kind='普通类',round_name='录取汇总（轮次未分）'):
    return {'id':f'audit-major26-{sid}-{row}-{track}','year':2026,'school':school,'schoolCode':code,
            'track':track,'batch':batch,'group':None,'major':major,'score':number(score),
            'scoreType':'专业录取最低分','plannedCount':None,'admittedCount':None,'rank':None,
            'rankType':None,'requiredSubjects':[],'subjectRule':'unknown','requirementText':None,
            'sourceId':sid,'sourceRow':row,'round':round_name,'admissionType':kind,
            'note':'原文未公布专业组，未据学校或组最低分推定专业线。',
            'reviewedAt':NOW,'evidenceStatus':'verified','scoreComparable':True,'scoreEvidenceGaps':[],'conflictFields':[]}
def main():
    rows=read('baseline-major-cutoffs.json');old_sources=read('baseline-sources.json')
    findings=[];checks=[];excluded=[];sources=[]
    by_source={s['id']:tables(s['id']) for s in old_sources}
    for r in rows:
        tabs,text=by_source[r['sourceId']];assert '2026' in text
        if r['sourceId'].startswith('ylu'):
            cell=tabs[r['sourceTable']-1][r['sourceRow']-1]
            assert r['group']==cell[0] and r['score']==number(cell[-1])
            assert r['plannedCount']==int(cell[-3]) and r['admittedCount']==int(cell[-2])
        elif r['sourceId'].startswith('nepu'):
            cell=tabs[0][r['sourceRow']-1]
            assert cell[0]=='广西' and cell[4]==r['major'] and number(cell[8])==r['score']
            assert (int(cell[5]),int(cell[6]))==(r['plannedCount'],r['admittedCount'])
        elif r['sourceId'].startswith('qqhru'):
            cell=tabs[0][r['sourceRow']-1];assert cell[1]==r['major'] and number(cell[3])==r['score']
        elif r['sourceId'].startswith('cqie'):
            cell=tabs[0][r['sourceRow']-1];assert cell[0]=='广西' and cell[4]==r['major'] and number(cell[5])==r['score']
            plan=[x for x in by_source['cqie-plan-2026-78111'][0][0] if len(x)>8 and x[7]==r['track'] and normalize(x[2])==normalize(r['major'])]
            assert len(plan)==1 and int(plan[0][6])==r['plannedCount'] and plan[0][4]==r['group']
        else:
            tab=[t for t in tabs if t[0][:3]==['省份','批次','计划性质']][0]
            cell=tab[r['sourceRow']-1];assert cell[0]=='广西' and cell[6]==r['major'] and number(cell[9])==r['score']
            assert int(cell[7])==r['admittedCount'] and r['plannedCount'] is None
        r.update(reviewedAt=NOW,rank=None,rankType=None,evidenceStatus='source-conflict' if '【原文' in r['note'] else 'verified',scoreComparable=True,scoreEvidenceGaps=[],conflictFields=[])
        if '【原文出档分冲突】' in r['note']:r['conflictFields'].append('filingScoreInSource')
        if '【原文分列待核实】' in r['note']:r['conflictFields'].append('planIdentity')
        if r['evidenceStatus']=='source-conflict':findings.append({'type':'existing-source-conflict','school':r['school'],'schoolCode':r['schoolCode'],'recordIds':[r['id']],'sourceIds':[r['sourceId']],'detail':r['note'],'action':'保留专业分数和源行，显式标注；不静默更正原文。'})
    checks.append({'scope':'existing-five-schools','records':len(rows),'check':'每条专业最低分及源人数列与本轮重新获取原页完全一致','result':'PASS'})
    for s in old_sources:
        meta=read('raw/'+s['id']+'.meta.json');sources.append(dict(s,accessedAt=meta['accessedAt'],sha256=meta['sha256'],rawPath=meta['rawFile'],auditAction='本轮重新下载并逐记录核对；旧源说明保留'))
    specs=[('ncwu-lines','华北水利水电大学','10078','2026-07-20'),('sxyyc-lines','重庆三峡医药高等专科学校','14008','2026-08-10'),('lngpi-lines','辽宁轨道交通职业学院','12896','2026-08-08'),('bsu-lines-normal','北京体育大学','10043',None),('bsu-lines-cooperation','北京体育大学','10043',None),('guat-lines','桂林航天工业学院','11825','2026-09-07'),('glut-lines-2026','桂林理工大学','10596',None)]
    for sid,school,code,published in specs:
        ts,text=tables(sid);assert '2026' in text
        new=[]
        if sid=='ncwu-lines':
            tab=[t for t in ts if t[0][:3]==['批次','科类','专业']][0]
            for i,c in enumerate(tab[1:],2):
                assert number(c[6])<=number(c[7])<=number(c[5])
                r=base_record(sid,school,code,'历史' if c[1]=='文/历史' else '物理','本科普通批',c[2],c[6],i,category(c[2]))
                r.update(plannedCount=int(c[3]),admittedCount=int(c[4]),rank=int(c[10]),rankType='专业最低录取分位次（源表）',sourceBatch=c[0])
                r['note']+='计划与录取人数分列；rank来自本专业最低分位次列，不是专业组位次。原文未说明轮次与位次加分口径。'
                new.append(r)
        elif sid=='sxyyc-lines':
            tab=[t for t in ts if t[0][0]=='专业' and len(t[0])==9][0]
            for i,c in enumerate(tab[2:],3):
                for track,start in [('历史',1),('物理',5)]:
                    if not c[start+2]:continue
                    assert number(c[start+2])<=number(c[start+3])
                    r=base_record(sid,school,code,track,'高职高专普通批',c[0],c[start+2],i)
                    r.update(plannedCount=int(c[start]),admittedCount=int(c[start+1]))
                    r['note']+='招生录取工作截至8月10日结束；轮次未拆分。计划数与录取数分别照录。'
                    if r['admittedCount']==1 and c[start+2]!=c[start+3]:
                        detail='原表录取数为1，但最低分与最高分不相同；不能同时视为已解决。'
                        r.update(evidenceStatus='source-conflict',sourceMaximumScore=number(c[start+3]),scoreComparable=False,scoreEvidenceGaps=['录取人数与分数区间不自洽，无法独立确认最低分可用于比较。'],conflictFields=['admittedCount','scoreRange']);r['note']+='【原文人数冲突】'+detail
                        findings.append({'type':'source-internal-conflict','school':school,'schoolCode':code,'recordIds':[r['id']],'sourceIds':[sid],'detail':detail,'action':'保留官方原值并警示，不用该行人数反推计划或概率。'})
                    new.append(r)
        elif sid=='lngpi-lines':
            tab=[t for t in ts if '广西分专业最低分数线' in t[0][0]][0]
            for i,c in enumerate(tab[3:],4):
                r=base_record(sid,school,code,'物理','高职高专普通批',c[1],c[3],i);r['plannedCount']=int(c[2]);r['note']+='原文有计划数，无录取人数，轮次未分。';new.append(r)
        elif sid.startswith('bsu'):
            tab=[t for t in ts if '2026年我校在广西壮族自治区普通类专业录取分数线' in t[0][0]][0]
            for i,c in enumerate(tab[3:],4):
                assert number(c[3])<=number(c[5])<=number(c[4])
                r=base_record(sid,school,code,c[0].replace('类',''),'本科普通批',c[1],c[3],i,category(c[1]))
                r.update(requirementText=c[2],requiredSubjects=[x for x in ['化学','生物','政治','地理'] if x in c[2]],subjectRule='none' if '不提科目' in c[2] or c[2].startswith('物理(1门') else 'all')
                r['note']+='招生官网分专业录取表，数值表头为投档成绩。原文未公布人数或录取轮次。';r['sourceScoreLabel']='投档成绩最低分';new.append(r)
        elif sid=='guat-lines':
            tab=[t for t in ts if t[0][:2]==['选考科目','录取专业']][0]
            for i,c in enumerate(tab[1:],2):
                if c[1]=='最低分' or '预科' in c[1]:excluded.append({'sourceId':sid,'sourceRow':i,'sourceCells':c,'reason':'分组汇总/预科不是具体本科专业线；其位次不能复制给组内专业。'});continue
                assert number(c[2])<=number(c[3])<=number(c[4])
                r=base_record(sid,school,code,'历史' if '历史' in c[0] else '物理','本科普通批',c[1],c[2],i,category(c[1]),'首轮')
                r.update(requirementText=c[0],requiredSubjects=['化学'] if '化学' in c[0] else [],subjectRule='all' if '化学' in c[0] else 'none' if '不限' in c[0] or '历史' in c[0] else 'unknown')
                r['note']+='原文标题明确为正投；未公布人数与专业组；分段汇总位次不作为专业位次。';new.append(r)
        elif sid=='glut-lines-2026':
            tab=[t for t in ts if t[0][:4]==['年份','省份','科类','专业']][0]
            assert len(tab)==175
            for i,c in enumerate(tab[1:],2):
                assert c[0]=='2026' and c[1]=='广西'
                if c[2] not in ('历史类','物理类') or '预科' in c[3] or '预科' in c[4]:
                    excluded.append({'sourceId':sid,'sourceRow':i,'sourceCells':c,'reason':'艺术或预科不混入普通本科专业录取线。'});continue
                assert number(c[7])<=number(c[8])<=number(c[6])
                r=base_record(sid,school,code,c[2].replace('类',''),'本科普通批',c[3],c[7],i,category(c[3],c[5]))
                r['sourceBatch']=c[4];r['sourceCategory']=c[5]
                r['note']+='公开查询逐行标明2026、广西；批次按广西规范名称整理。原表没有专业组或人数，轮次未分。'+('原备注：'+c[9] if c[9] else '')
                new.append(r)
        meta=read('raw/'+sid+'.meta.json')
        title=re.search(r'<title[^>]*>(.*?)</title>',text,re.S|re.I)
        sources.append({'id':sid,'title':re.sub('<[^>]+>','',title.group(1)).strip() if title else school+'2026年广西专业录取分数查询','url':meta['url'],'publisher':school,'year':2026,'publishedAt':published,'accessedAt':meta['accessedAt'],'sha256':meta['sha256'],'recordCount':len(new),'method':'从本轮官方原始HTML独立展开合并单元格，限定广西2026、专业级和普通科类；人数和位次口径分列。','rawPath':meta['rawFile'],'request':meta.get('request'),'requestEncoding':meta.get('requestEncoding'),'auditAction':'新增专业实际录取数据'})
        if sid in ('guat-lines','glut-lines-2026'):
            sources[-1]['method']+='原表专业名或独立类别中的精准专项、国家/地方专项、民族班、中外合作分别标记；方法说明不写入每条普通记录的备注。'
        if sid.startswith('bsu'):
            sources[-1]['method']+='学校官网普通类/中外合作专栏明确列为普通类专业录取分数线，分数子列标题是投档成绩，非体育综合分。'
        checks.append({'sourceId':sid,'records':len(new),'result':'PASS','samples':[new[0],new[len(new)//2],new[-1]]})
        rows.extend(new)
    from audit_extra import extend
    filing=extend(ROOT,NOW,rows,sources,findings,excluded,checks,base_record,category,tables)
    assert len(set(r['id'] for r in rows))==len(rows)
    assert all(r['year']==2026 and 0<=r['score']<=750 and r['track'] in ('历史','物理') for r in rows)
    sources.extend(read('baseline-qualification-sources.json'))
    source_ids={s['id'] for s in sources};assert len(source_ids)==len(sources)
    for r in rows:
        assert r['sourceId'] in source_ids
        for key in ['planSourceId','qualificationSourceId']:
            if key in r:assert r[key] in source_ids
    for r in rows:
        for key in ['plannedCount','admittedCount']:assert r[key] is None or isinstance(r[key],int) and r[key]>=0
    negatives=read('negative-findings.json') if (ROOT/'negative-findings.json').exists() else []
    for item in negatives:
        for sid in item['sourceIds']:
            if sid in source_ids:continue
            m=read('raw/'+sid+'.meta.json')
            sources.append({'id':sid,'title':item['school']+'专业录取数据检索证据：'+sid,'url':m['url'],
                            'publisher':item['school'],'publishedAt':None,'accessedAt':m['accessedAt'],
                            'sha256':m.get('sha256'),'recordCount':0,'method':item['result'],
                            'request':m.get('request'),'requestEncoding':m.get('requestEncoding'),
                            'accessLimitType':item['accessLimitType'],'rawPath':m.get('rawFile'),
                            'auditAction':'负面检索或访问限制证据，不代表全站无数据'})
            source_ids.add(sid)
    supplement=[]
    for r in rows:
        for key,value in [('requiredSubjects',[]),('subjectRule','unknown'),('requirementText',None)]:r.setdefault(key,value)
        if r['sourceId'] not in ('ncwu-lines','lngpi-lines'):continue
        assert r['plannedCount'] is not None
        supplement.append({'id':r['id'].replace('audit-major26','audit-plan26'),'year':2026,'school':r['school'],
                           'schoolCode':r['schoolCode'],'track':r['track'],'batch':r['batch'],'group':None,
                           'major':r['major'],'majorCode':None,'plannedCount':r['plannedCount'],
                           'tuition':None,'duration':None,'requiredSubjects':[],'subjectRule':'unknown',
                           'requirementText':None,'category':r['admissionType'],'sourceId':r['sourceId'],
                           'planVersion':'录取结果公告所列计划人数（非征集剩余计划；未确认是否为最初发布版）',
                           'note':'来自录取结果公告明确的计划人数列，未用录取人数替代；未证实与最初计划版本完全相同。'})
    dump('corrected-major-cutoffs.json',rows);dump('sources.json',sources)
    dump('major-filing-cutoffs.json',filing);dump('new-plan-supplement.json',supplement)
    dump('findings.json',{'checkedAt':NOW,'findings':findings,'negativeSearches':negatives,'excludedRows':excluded})
    dump('quality-report.json',{'checkedAt':NOW,'baselineCount':253,'recordCount':len(rows),'newRecordCount':len(rows)-253,'schoolCount':len({r['schoolCode'] for r in rows}),'bySchool':dict(collections.Counter(r['school'] for r in rows)),'sourceConflictCount':sum(r['evidenceStatus']=='source-conflict' for r in rows),'scoreNonComparableCount':sum(not r['scoreComparable'] for r in rows),'checks':checks,'uniqueIds':'PASS','sourceReferences':'PASS','yearAndNumericBounds':'PASS','limitations':['限定公开已取得的专业结果；学校和专业组最低线不替代专业线。','未分轮次的专业录取汇总不标为首轮。','rank仅取华北水利水电大学、百色学院、广西医科大学源表逐专业明确列出的最低分位次；其他位次不推断。']})
    print(json.dumps({'records':len(rows),'new':len(rows)-253,'bySchool':dict(collections.Counter(r['school'] for r in rows))},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
