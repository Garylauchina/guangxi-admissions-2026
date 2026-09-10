from pathlib import Path
import json,collections
R=Path(__file__).resolve().parent
read=lambda f:json.loads((R/f).read_text())
a=read('major-cutoffs-upsert.json');s=read('sources.json');n=read('school-audit-notes.json');q=read('QA.json')
checks=[]
def ck(k,v):checks.append({'check':k,'passed':bool(v)});assert v,k
ck('57条且均桂林医科10601',len(a)==57 and all(r['schoolCode']=='10601' and r['school']=='桂林医科大学' for r in a))
ck('51物理6历史',collections.Counter(r['track'] for r in a)=={'物理':51,'历史':6})
ck('34普通17定向1民族5中澳',collections.Counter(r['admissionType'] for r in a)=={'普通类':34,'农村订单定向免费医学生':17,'民族班':1,'中澳学分互认联合培养项目':5})
ck('无错误年份省份或未知分数',all(r['year']==2026 and r['province']=='广西' and isinstance(r['score'],int) for r in a))
ck('最高与平均字段约定一致',all('sourceMaximumScore' in x and 'sourceAverageScore' in x and 'maxScore' not in x and 'averageScore' not in x for x in a))
projects=[x for x in a if x['group'] in ['950','951','952','953','954']]
ck('中澳五项目英语条件和章程来源逐项补齐',len(projects)==5 and all(x['foreignLanguageRequirement']['minimumScore']==90 and x['foreignLanguageRequirement']['scoreScaleMaximum']==150 and x['foreignLanguageRequirement']['minimumRatio']==0.6 and '90分' in x['note'] and '60%' in x['note'] and 'mscore-c-2026-glmu-charter' in x['fieldSourceIds']['note'] and x['fieldSourceIds']['foreignLanguageRequirement']==['mscore-c-2026-glmu-charter'] and x['admissionType']=='中澳学分互认联合培养项目' for x in projects))
ck('组码双来源',all(len(r['fieldSourceIds']['group'])==2 and r['sourceId'] in r['fieldSourceIds']['group'] for r in a))
ck('无预科冒充专业',not any('预科' in r['major'] for r in a))
ck('保留完整查询缺口',len(n)==6 and sum(x['recordCount']>0 for x in n)==1)
ck('五校负面结论限于已查范围',all('不宣称' in x['scope'] for x in n))
ck('公开数据无敏感会话字段',not any('jessionid' in json.dumps(x) or 'jsessionid' in json.dumps(x) for x in a+s+n))
ck('全部原始分数关联表行',all(r['sourceTable']==1 and r['sourceRow']>=2 for r in a))
ck('所有分数来源有原响应和归档哈希',all(next(x for x in s if x['id']==r['sourceId'])['rawSha256'] and next(x for x in s if x['id']==r['sourceId'])['archiveSha256'] for r in a))
ck('满分口径辅助来源归档限制可见',any(x['id']=='mscore-c-2026-gx-scale-policy' and x['rawSha256'] is None and x['accessLimitType']=='web-read-verified-raw-archive-unavailable' for x in s))
q['verificationChecks']=checks;q['passed']=all(x['passed'] for x in q['checks']+checks)
(R/'QA.json').write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'passed':q['passed'],'buildChecks':len(q['checks']),'verificationChecks':len(checks),'rows':len(a)},ensure_ascii=False))
