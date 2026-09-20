"""Build a factual import package from archived official responses, no raw publication."""
import collections, hashlib, json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
RAW=ROOT/'raw'
SITE=ROOT.parents[2]/'guangxi-admissions-2026/site/data'
DATE='2026-09-20'
targets=json.loads((ROOT/'targets.json').read_text())
schools={r['schoolCode']:r['school'] for r in targets}
sources=[]; records=[]; audits=[]; observations=[]; groups=[]
def write(name,value): (ROOT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
def source(key,title=None):
    sid='major-20260920-d-'+key
    if any(x['id']==sid for x in sources):return sid
    p=RAW/(key+'.meta.json')
    if not p.exists():p=RAW/(key+'.json.meta.json')
    m=json.loads(p.read_text())
    s={'id':sid,'title':title or schools[key[:5]]+'：官方专业分来源核查（'+key+'）','url':m['url'],'publisher':schools[key[:5]],'accessedAt':m['checkedAt'],'year':None,'publishedAt':None,'httpStatus':m.get('httpStatus'),'evidenceRole':'source-review'}
    for k in ['sha256','responseSha256','archiveFile']:
        if m.get(k):s[k]=m[k]
    if 'data' in m:s.update(requestMethod='POST',requestData=m['data'])
    else:s['requestMethod']='GET'
    if m.get('error'):s['accessError']=m['error']
    sources.append(s);return sid
def audit(code,status,note,keys):
    refs=[source(k) for k in keys]
    row={'id':'major-20260920-d-review-'+code,'year':2026,'province':'广西','schoolCode':code,'school':schools[code],'auditKind':'major-scores','checkedAt':DATE,'title':'2026广西专业录取分来源核查','status':status,'recordCount':sum(r['schoolCode']==code for r in records),'sourceIds':refs,'checkedUrls':list(dict.fromkeys(next(s['url'] for s in sources if s['id']==x) for x in refs)),'note':note,'scope':'结论仅覆盖本轮列明入口和真实查询；未取得不等于未招生或所有渠道未发布。'}
    audits.append(row)

filing=json.loads((SITE/'cutoffs.json').read_text())
for code,files,entry,charter in [
 ('10536',['10536-2026-physics','10536-2026-history'],'10536-entry-1','10536-charter'),
 ('11117',['11117-2026-physics-ordinary','11117-2026-physics-national','11117-2026-history-ordinary','11117-2026-history-national'],'11117-entry','11117-charter-browser')]:
    entryId=source(entry);charterId=source(charter);menuId=source(code+'-menu-session')
    if code=='11117':
        menu=json.loads((RAW/'11117-menu-session.json').read_text())
        assert any(f['fieldName']=='minOrder' and f['label']=='最低分排名' for f in menu['data']['showField']['showField3'])
    for file in files:
        raw=json.loads((RAW/(file+'.json')).read_text());assert raw['state']==1
        body=raw['data']; allrows=body['sszygradeList']; kept=[]
        sid=source(file,schools[code]+'：2026广西分专业录取最低分（'+file.split('2026-')[1]+'）')
        request=json.loads((RAW/(file+'.json.meta.json')).read_text())['data']
        for i,r in enumerate(allrows,1):
            if str(r.get('nf'))!='2026' or r.get('ssmc')!='广西':continue
            assert r['klmc']==request['klmc'] and r['zslx']==request['zslx']
            assert r['minScore']<=r['avgScore']<=r['maxScore'] and (r['rs']!=1 or r['maxScore']==r['minScore'])
            track=r['klmc'].replace('类','');schoolRef=next(x['sourceId'] for x in filing if x['schoolCode']==code and x['track']==track)
            rid=f'major-20260920-d-{code}-{len([x for x in records if x["schoolCode"]==code])+1:03}'
            refs=[sid,entryId,charterId,schoolRef,menuId]
            fields={k:[sid] for k in ['year','province','track','major','score','sourceMaximumScore','sourceAverageScore','sourceReportedCount','admissionType']}
            fields.update(schoolCode=[schoolRef],scoreBasis=[charterId],note=refs)
            # National major code is not the Guangxi application code.
            row={'id':rid,'year':2026,'province':'广西','schoolCode':code,'school':schools[code],'sourceSchool':schools[code],'track':track,'sourceTrack':r['klmc'],'batch':r.get('pcmc') or '批次未注明','round':'录取汇总（轮次未分）','group':None,'major':r['zymc'],'majorCode':None,'sourceMajorCode':r.get('zydm'),'score':r['minScore'],'scoreType':'专业录取最低分','rank':None,'sourceId':sid,'sourceIds':refs,'sourceRow':i,'sourceTable':'分专业录取情况 sszygradeList','reviewedAt':DATE,'evidenceStatus':'verified','scoreComparable':True,'scoreBasis':'750分制普通高考总分（高校专业录取口径，含其认可的政策加分）','scoreScaleMaximum':750,'scoreEvidenceGaps':[],'conflictFields':[],'admissionType':r['zslx'],'sourceCategory':r['zslx'],'requiredSubjects':[],'subjectRule':'unknown','requirementText':'首选'+track+'；完整再选科目要求待核','fieldSourceIds':fields,'sourceMaximumScore':r['maxScore'],'sourceAverageScore':r['avgScore'],'sourceScoreHeader':'最低分','sourceReportedCount':r['rs'],'sourceCountField':'rs','note':'仅选取API逐行标明2026年、广西的专业录取记录；响应同时含往年记录，已排除。广西专业组码、填报专业代号及录取轮次未列，保持未知。API rs 字段未见公开人数表头，仅保留原始值，不解释为录取或计划人数。'}
            if r.get('pcmc'):fields['batch']=[sid]
            if r.get('minOrder'):
                assert r['minRank']==r['minOrder']
                row.update(rank=r['minOrder'],sourceMinimumRank=r['minRank'],sourceRankField='minOrder',rankType='专业最低分排名（学校公布）');fields['rank']=[sid,entryId,menuId]
            elif r.get('minRank'):
                row['sourceMinimumRank']=r['minRank'];row['sourceRankHeader']='API minRank（专业表列示范围仍待核）';fields['sourceMinimumRank']=[sid]
            records.append(row);kept.append(r)
        aggregate=[r for r in body['zsSsgradeList'] if str(r.get('nf'))=='2026' and r.get('ssmc')=='广西']
        assert len(aggregate)==1 and sum(r['rs'] for r in kept)==aggregate[0]['rs']
        observations.append({'schoolCode':code,'query':request,'sourceId':sid,'responseRows':len(allrows),'accepted2026Rows':len(kept),'excludedOtherYearRows':len(allrows)-len(kept),'sourceRsSum':sum(r['rs'] for r in kept),'sourceAggregateRs':aggregate[0]['rs'],'minimum':min(r['minScore'] for r in kept),'maximum':max(r['maxScore'] for r in kept),'numericConflicts':0})

audit('10536','collected-partial','取得2026广西物理类61条、历史类6条具体专业录取分；两科专业行 API rs 数值合计分别210、16，与省级汇总行相符；该字段未见公开表头，不作人数语义解释。当前普通类菜单仅这两科组合。API同时返回2025/2024，已逐行排除。公开新闻所列投档分不进入专业录取库。专业组码和轮次仍缺。',['10536-menu-session','10536-2026-physics','10536-2026-history','10536-entry-1','10536-charter','10536-2026'])
audit('11117','collected-partial','沿新招生主页进入zstong官方系统，取得2026广西51条：物理普通36、物理国家专项3、历史普通10、历史国家专项2。四组合 API rs 数值和均与省级汇总行相符；该字段未见公开表头，不作人数语义解释，保留专项类型，排除响应内往年记录。API未给批次、广西组码和轮次，均不推定。旧ASP仍显示2025，不作本年证据。',['11117-menu-session','11117-2026-physics-ordinary','11117-2026-physics-national','11117-2026-history-ordinary','11117-2026-history-national','11117-entry','11117-charter-browser'])
audit('10009','entry-only-year-gap','实际读取招生首页和历年分数目录，最新条目为2025年录取分数线（2025-09-12发布），其后依次2024、2023等；本轮未取得2026广西专业分。',['10009-home','10009-entry-1'])
audit('11664','entry-only-year-gap','从旧查询页沿官方链接进入zsdata新系统，真实历年分数getType(type=lnfs)菜单仅2025、2024、2023；广西分支也不含2026。个人录取进程getAllNf空列表不作为专业分缺口依据。',['11664-scores','11664-entry-1','11664-type'])
audit('10439','entry-only-year-gap','完成官网匿名会话查询，实际专业分菜单广西最高年份2025（物理类、历史类本科普通批）；未见2026广西选项。直接无会话请求403已由正常匿名流程解决，不能误记为学校无数据。',['10439-entry-1','10439-menu-session'])
audit('10126','entry-only-year-gap','招生官网分数公示目录共0条；继续从官方历年分数入口完成匿名查询，真实菜单广西仅2025物理类/历史类普通类。未将空目录单独解释为全校未发布。',['10126-entry-1','10126-entry-2','10126-menu-session'])
audit('11075','entry-only-year-gap','实际读取官网动态历年分数表单配置：专业录取数据（2023年-2025年），年份选择2025/2024/2023，省份含广西；needLogin=N、msgCode=N。未提供2026年专业分选项。',['11075-admissions','11075-scores','11075-form'])
audit('10631','group-only','官网2026各省各批次录取表提供广西物理101/102/103组最低录取分581/551/519，已另存为组级录取分，不冒充专业分。独立历年专业查询浏览器实际年份菜单仍为2025—2021。',['10631-home','10631-2026','10631-scores','10631-embed','10631-browser'])
audit('10674','entry-only-year-gap','核查本科招生目录最新页及紧邻旧页，2026录取查询是个人结果入口；当前公开分专业分数为2025年数据，2026-04-15发布。2026年报考文章同样明确列2025年分数，未按文章年份误收。',['10674-admissions','10674-earlier','10674-article'])
audit('10063','entry-only-year-gap','历年分数栏目最新为2025年各省招生录取情况，发布日2026-04-23，后续为2024各省统计；本轮未取得2026广西实际专业分。',['10063-home','10063-entry-1'])
sid=source('10631-2026')
for group,score,high in [('101',581,606),('102',551,561),('103',519,575)]:
    identity=next(r for r in filing if r['schoolCode']=='10631' and r['group']==group and r['track']=='物理' and r['round']=='首轮')
    groups.append({'id':'group-admission-20260920-10631-'+group,'year':2026,'province':'广西','schoolCode':'10631','school':schools['10631'],'track':'物理','batch':identity['batch'],'group':group,'score':score,'scoreType':'专业组录取最低分','scoreComparable':True,'scoreScaleMaximum':750,'evidenceScope':'official-group-summary','roundScope':'annual','round':'录取汇总（轮次未分）','sourceId':sid,'sourceIds':[sid,identity['sourceId']],'sourceMaximumScore':high,'sourceLocator':'广西 / 普通本科批'+group+'组 / 物理类 / 最低分','reviewedAt':DATE,'note':'校方直接公布的本组录取汇总最低分；原表未区分首次和征集轮次。与考试院投档线独立保存。','fieldSourceIds':{k:[sid] for k in ['year','province','track','batch','group','score']}})

write('major-cutoffs-upsert.json',records);write('sources.json',sources);write('school-audit-notes.json',audits);write('group-admission-candidates.json',groups);write('observations.json',observations)
write('qa.json',{'checkedAt':DATE,'schools':10,'newMajorScores':len(records),'newComparableScores':len(records),'directGroupAdmissions':len(groups),'allQuerySourceRsTotalsReconciled':True,'allNumericChecksPassed':True,'counts':dict(collections.Counter(r['school'] for r in records))})
print('Built',len(records),'major scores,',len(audits),'audits,',len(groups),'group outcomes')
