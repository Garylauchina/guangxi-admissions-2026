#!/usr/bin/env python3
"""Build only this reviewed nine-school batch from public frozen evidence, offline."""
import collections, datetime, hashlib, json, re
from pathlib import Path
R=Path(__file__).resolve().parent
P='major-20260911-a-'
def read(n):return json.loads((R/n).read_text())
def write(n,v):(R/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
sources=read('evidence/source-snapshots.json'); by={s['id']:s for s in sources}
# Stable review timestamp is derived from the reviewed snapshot, in Beijing time.
checked=max(datetime.datetime.fromisoformat(s['accessedAt']) for s in sources).astimezone(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
assert checked.startswith('2026-09-11')
def ident(code,track,major,kind):
 return 'major26-'+hashlib.sha256('|'.join(['2026','广西',code,track,major,kind,'录取汇总（轮次未分）']).encode()).hexdigest()[:20]
scores=[]
for source in sources:
 if not source['id'].startswith(P+'muc-majors'):continue
 fn=source['archiveFile'];data=read(fn)
 assert hashlib.sha256((R/fn).read_bytes()).hexdigest()==source['sha256']
 assert data['success'] is True and data['total']==len(data['rows'])
 for i,a in enumerate(data['rows'],1):
  assert a['year']==2026 and a['sfmc']=='广西' and a['klmc'] in ('物理类','历史类')
  assert a['zslbdm']==source['queryParameters']['vepd_xslxdm']
  tr=a['klmc'].removesuffix('类');kind=a['zslbmc'];major=a['zymc'];req=[]
  if kind=='民族班':req.append('民族班招生对象为少数民族考生，须符合相应招生资格。')
  if kind=='国家专项':req.append('须符合国家专项招生资格，按教育部相关政策执行。')
  if kind=='合作办学':req.append('数据科学与大数据技术为内地与港澳地区合作办学；只录取填报该专业志愿的考生，入学后不得申请转专业。')
  if major.startswith('中国少数民族语言文学'):req.append('本方向学生入学后不得申请转入其他普通类专业。')
  if major=='外国语言文学类':req.append('应试语种为英语；当地组织外语口试的，须参加且合格。')
  basis='普通高考750分制招生录取分数；章程按投档总分分专业录取并原则上认可省级加分政策（上限20分）；分数表未单列加分处理，不声明为裸分。'
  note='官网分专业录取情况原值；网页说明分数有小数时向下取整。未列省编专业组码、精确批次及分轮次，保留空组码和汇总轮次。'
  if kind=='合作办学':note+='原接口类型为合作办学，章程明确为内地与港澳地区合作办学。'
  row=dict(id=ident('10052',tr,major,kind),year=2026,province='广西',schoolCode='10052',school='中央民族大学',track=tr,batch='本科（批次待核）',group=None,major=major,score=int(a['mincj']),sourceMaximumScore=int(a['maxcj']),sourceAverageScore=int(a['avgcj']),scoreType='专业录取最低分',scoreBasis=basis,scoreScaleMaximum=750,round='录取汇总（轮次未分）',admissionType=kind,sourceCategory=kind,sourceTrack=a['klmc'],scoreComparable=True,evidenceStatus='verified',scoreEvidenceGaps=[],conflictFields=[],rank=int(a['minwc']),rankType='专业最低分排名（学校公布）',sourceId=source['id'],sourceIds=[source['id'],P+'muc-score-entry',P+'muc-charter-2026'],fieldSourceIds={'score':[source['id']],'rank':[source['id'],P+'muc-score-entry'],'scoreBasis':[P+'muc-charter-2026'],'admissionType':[source['id']]},sourceRow=i,sourceTable=f"2026年广西{a['klmc']}/{kind}/分专业录取情况",reviewedAt=checked,note=note,sourceRecord=a)
  if req:row['admissionRequirements']=' '.join(req);row['fieldSourceIds']['admissionRequirements']=[P+'muc-charter-2026']
  scores.append(row)

x=read('evidence/xjtlu-guangxi-table.json')
assert x['year']==2026 and x['province']=='广西' and len(x['rows'])==3
for i,a in enumerate(x['rows'],1):
 tr,subjects,major,planned,admitted,maxs,mins=a
 scores.append(dict(id=ident('16302',tr,major,'中外合作办学'),year=2026,province='广西',schoolCode='16302',school='西交利物浦大学',track=tr,batch='本科批（具体批次待核）',group=None,major=major,majorType='正式招生大类',score=int(mins),sourceMaximumScore=int(maxs),sourceAverageScore=None,plannedCount=int(planned),admittedCount=int(admitted),scoreType='专业录取最低分',scoreBasis='普通高考750分制大类录取最低分；章程按分数优先录取，投档成绩同分时比较不含政策性加分的高考成绩等；本表未单列加分处理，不声明为裸分。',scoreScaleMaximum=750,round='录取汇总（轮次未分）',admissionType='中外合作办学',sourceCategory='高考选拔招生',sourceTrack=tr,sourceSubjectRequirement=subjects,requirementText=subjects,requiredSubjects=['化学'] if subjects=='物理+化学' else [],subjectRule='all' if subjects=='物理+化学' else 'none',scoreComparable=True,evidenceStatus='verified',scoreEvidenceGaps=[],conflictFields=[],rank=None,sourceId=P+'xjtlu-score-2026',sourceIds=[P+'xjtlu-score-2026',P+'xjtlu-charter-2026'],fieldSourceIds={'score':[P+'xjtlu-score-2026'],'admittedCount':[P+'xjtlu-score-2026'],'plannedCount':[P+'xjtlu-score-2026'],'requirementText':[P+'xjtlu-score-2026'],'requiredSubjects':[P+'xjtlu-score-2026'],'subjectRule':[P+'xjtlu-score-2026'],'admissionType':[P+'xjtlu-charter-2026'],'admissionRequirements':[P+'xjtlu-charter-2026'],'scoreBasis':[P+'xjtlu-charter-2026']},sourceRow=i,sourceTable='2026年分省录取数据/广西壮族自治区',reviewedAt=checked,note='正式招生大类最低分，不是大类内各具体专业最低分。原表招生专业组列实际填写选科组合，不能据此生成省编组码；原表未分轮次。章程确定本科批次原则，广西具体批次名称未在该表单列，暂保留待核。',admissionRequirements='按大类填报，招生大类名称与入学后就读专业没有直接关联；完成大一第一学期后选专业，须满足课程及部分专业成绩要求。专业课程全英文教学，学校不设外语单科高考最低线。',sourceRecord=dict(zip(x['headers'],a))))

SCHOOLS=[('10610','四川大学','access-restricted','四川大学招生网及当前分数索引均返回HTTP 412；公开分数查询系统返回HTTP 483，正文提示访问策略禁止访问。学院可读目录链接的是截止2025年的分数统计。未取得2026广西分专业录取数据。'),('10698','西安交通大学','access-restricted','历年录取查询URL正常GET返回HTTP 200，但正文是访问验证/网站正在加载中页面，未取得专业查询表；本次未执行或绕过验证挑战。未取得2026广西分专业录取数据。'),('18213','哈尔滨工业大学(深圳)','current-year-not-listed','公开历年分数前端已读取并实际查询年份接口，仅返回2025和2024，没有2026所需的年份ID。未猜测年份ID，未提交伪造2026参数；本轮没有2026广西专业分可采。'),('10286','东南大学','no-current-year-records','广西官方目录的本年资料为2026招生计划；最新可读分专业录取表虽在2026-01-13发布，正文年份是2025。2026录取进度公告不列专业分。未将计划或旧年分数拼成2026记录。'),('10533','中南大学','no-current-year-records','已读取本科普通类公开前端和接口配置。当前年份选项为2020至2025；使用前端公开字段分别请求2026/广西/物理类、历史类，均成功返回code=200、list=[]、total=0。没有分页遗漏或专业分入库；不能据空结果断言校方所有渠道均未发布。'),('10013','北京邮电大学','access-restricted','本科招生网及检索发现的旧年分数公告入口均返回HTTP 412，未取得可读专业表。旧年检索条目不当作2026录取分；本轮未取得2026广西专业实际录取数据。'),('19246','复旦大学医学院','no-current-year-records','官方分数目录最新可读表为2025年分省录取分数，2026-01-21发布；表中医学院列主要为院校科类汇总，不能当作2026单专业分数。2026章程明确本部与医学院招生分别实施；本包保留医学院独立代码19246。'),('10052','中央民族大学','collected-partial','2026广西物理/历史公开分专业接口采得35条：普通本科28、民族班5、国家专项1、合作办学1。六个科类类别响应均核对total等于rows长度，完整采集本次公开选项下的35条；体育科类未进入采集。保留专业最低分排名与资格限制；仍缺省编组码、精确批次、分轮次及录取人数，不宣称全部招生项目已覆盖。'),('16302','西交利物浦大学','collected-partial','2026年分省录取数据正文的广西表采得3个正式招生大类、实际录取110人（历史21、物理89）。计划数与录取数分别转录。URL含2023但当前h1为2026。学校按大类招生，大类名不等于入学后具体专业；组列是选科组合，省编组码及分轮次仍缺，具体批次名称待核。')]
notes=[]
for code,school,status,note in SCHOOLS:
 ss=[s for s in sources if s['schoolCode']==code]
 notes.append(dict(id='major-score-audit-2026-0911-'+code,year=2026,province='广西',auditKind='major-scores',title='2026广西专业录取分核查',schoolCode=code,school=school,status=status,checkedAt=checked,sourceIds=[s['id'] for s in ss],checkedUrls=list(dict.fromkeys(s.get('entryUrl',s['url']) for s in ss)),recordCount=sum(r['schoolCode']==code for r in scores),note=note))

assert len(scores)==38 and len({r['id'] for r in scores})==38
assert collections.Counter(r['schoolCode'] for r in scores)=={'10052':35,'16302':3}
assert collections.Counter(r['track'] for r in scores)=={'历史':19,'物理':19}
assert sum(r.get('admittedCount',0) for r in scores)==110
for r in scores:
 assert r['score']<=r['sourceMaximumScore']
 if r['sourceAverageScore'] is not None:assert r['score']<=r['sourceAverageScore']<=r['sourceMaximumScore']
 assert all(s in by for s in r['sourceIds']) and r['group'] is None
 if r['rank'] is not None:assert r['fieldSourceIds']['rank']
qa=dict(status='PASS',reviewedAt=checked,scopeSchools=9,scoreRows=38,comparableRows=38,schoolCounts=dict(collections.Counter(r['schoolCode'] for r in scores)),trackCounts=dict(collections.Counter(r['track'] for r in scores)),mucCategoryCounts=dict(collections.Counter(r['admissionType'] for r in scores if r['schoolCode']=='10052')),explicitRankRows=35,unknownGroupRows=38,unknownPreciseBatchRows=38,summaryRoundRows=38,explicitActualAdmittedCountRows=3,actualAdmittedCountSum=110,sourceCount=len(sources),auditNoteCount=9,checks=['2026与广西逐行核验','六个中央民大科类/类别接口total与rows相符，无分页参数','中央民大体育科类未采；录取概况接口未作专业来源','原始最高/平均/最低和最低分排名字段逐项映射','西浦仅提取广西表；3大类共110实际录取人','原表计划人数与录取人数独立字段','中央民大合作为内地与港澳地区合作，未误作普通招生','旧年分数、分组线及招生计划均未冒充专业分','未知组码/精确批次/轮次不推断','原7校逐校真实尝试及可追溯缺口','来源引用与ID唯一性','本地原响应hash与归档hash保存，公开目录不含会话值'],limitations=['中央民大35条与西浦3大类是已读来源覆盖，不代表9校全部招生类别','原7校仍无可入库2026专业分','scoreComparable表示同一高考总分尺度可参考，不能保证录取','未单列政策加分处理，不声称裸分','本轮校外独立审阅由主任务完成'])
write('major-cutoffs-upsert.json',scores);write('sources.json',sources);write('school-audit-notes.json',notes);write('QA.json',qa)
print(json.dumps({k:qa[k] for k in ['status','scoreRows','sourceCount','auditNoteCount']},ensure_ascii=False))
