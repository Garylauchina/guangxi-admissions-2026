"""Build a public fact-only package from locally archived official responses.
Run fetch.py requests.json first to reproduce network inputs; raw is private.
PDF extraction requires pdfplumber. Nothing outside this batch is modified.
"""
from pathlib import Path
import hashlib,json,re
from collections import Counter
import pdfplumber
ROOT=Path(__file__).resolve().parent
RAW=ROOT/'raw'
def read(name):return json.loads((ROOT/name).read_text())
def write(name,obj):(ROOT/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
def source_id(ref):return 'major-20260920-c-'+ref
D=read('decisions.json');targets=read('targets.json');target={x['schoolCode']:x for x in targets}
assert len(D)==len(target)==30 and {x['schoolCode'] for x in D}==set(target)
refs=list(dict.fromkeys(r for d in D for r in d['refs']))
meta={r:json.loads((RAW/(r+'.meta.json')).read_text()) for r in refs}
for r,m in meta.items():
 if m.get('sha256'):assert hashlib.sha256((RAW/m['archiveFile']).read_bytes()).hexdigest()==m['sha256'],r
 else:assert m.get('error') and m.get('errorSha256'),r
# Only the allowlisted, identity-confirmed requests are public/reproducible.
request_keys=['id','schoolCode','school','url','purpose','referer','data','encoding','publicHeaders']
write('requests.json',[{k:m[k] for k in request_keys if k in m} for m in meta.values()])
sources=[]
for ref,m in meta.items():
 textpath=RAW/(ref+'.text.txt')
 title=''
 if textpath.exists():
  lines=[x.lstrip('\ufeff').strip() for x in textpath.read_text().splitlines()]
  title=next((x for x in lines if x and len(x)<=130),'')
 if ref=='12493-pdf2026':title='2026年全国统一高考各省市各专业录取最低分数线（PDF）'
 elif ref=='12933-results2026-img':title='2026年分省录取分数表（原图）'
 elif ref=='12977-img':title='2023—2025各省第一志愿投档线（原图）'
 elif ref=='12302-pdf2026':title='学校2026年普高招生录取分数情况表（PDF）'
 elif ref.startswith('11828-api-'):title='专业录取分查询公开菜单：'+ref.split('-')[-1]
 elif ref.startswith('11828-control-'):title='学校录取分查询公开菜单对照：'+ref.split('-')[-1]
 elif ref=='11828-app-js':title='招生网公开前端：专业分/学校分查询字段及公开租户配置'
 if not title or m.get('error'):title='官方入口访问记录：'+ref
 s=dict(id=source_id(ref),title=m['school']+'｜'+title,url=m['url'],publisher=m['school'],year=None,publishedAt=None,accessedAt=m['checkedAt'],finishedAt=m['finishedAt'],httpStatus=m.get('httpStatus'),requestMethod='POST' if 'data' in m else 'GET',evidenceRole='source-review',evidenceType='public-response' if m.get('sha256') else 'access-failure',archiveFile=m.get('archiveFile'),notes=['仅公开来源元数据和抽取事实；响应原文、图片/PDF及会话资料不列入发布白名单。'])
 if m.get('sha256'):s.update(sha256=m['sha256'],responseSha256=m['sha256'],bytes=m['bytes'])
 if m.get('error'):s.update(accessError=m['error'],errorSha256=m['errorSha256'])
 if ref in ['12493-results2026','12493-pdf2026']:s.update(year=2026,publishedAt='2026-09-03')
 if ref in ['12933-results2026','12933-results2026-img']:s.update(year=2026,publishedAt='2026-09-15')
 if ref in ['12302-results2026','12302-pdf2026']:s.update(year=2026,publishedAt='2026-08-27')
 if ref=='12679-results2026':s.update(year=2026,publishedAt='2026-09-08')
 sources.append(s)
write('sources.json',sources)
# Extract the two Guangxi columns with assertions against column drift.
with pdfplumber.open(RAW/'12493-pdf2026.pdf') as pdf:
 assert len(pdf.pages)==1
 page=pdf.pages[0];text=page.extract_text();assert '2026' in text and '最低分' in text
 tables=page.extract_tables();assert len(tables)==1
 table=tables[0];col=table[0].index('广西')
 assert table[0][col-2]=='贵州' and table[0][col+2]=='河南'
 assert table[1][col:col+2]==['历史类','物理类']
 cells=[]
 for row_idx,row in enumerate(table[2:],start=3):
  for offset,track in enumerate(['历史','物理']):
   value=row[col+offset]
   if value not in ('',None):cells.append((row[0].replace('\n',''),track,int(value),row_idx,col+offset+1))
assert {(m,t,s) for m,t,s,_,_ in cells}=={('酒店管理与数字化运营','历史',403),('现代家政服务与管理','历史',405),('软件技术','物理',439),('智慧健康养老服务与管理','物理',410)}
pdfsource=source_id('12493-pdf2026');pagesource=source_id('12493-results2026')
scores=[]
for n,(major,track,score,table_row,table_col) in enumerate(cells,1):
 note='原表为2026全国统一高考专业录取最低分，取广西'+track+'类非空单元格；已对照PDF原页。具体批次、录取轮次、广西组码、专业代码、招生类别细分及位次未列，不推断为首轮，空白不作0分。'
 scores.append(dict(id=f'major-20260920-c-12493-{n:03}',year=2026,province='广西',schoolCode='12493',school='上海行健职业学院',sourceSchool='上海行健职业学院',track=track,sourceTrack=track+'类',batch='批次未注明',round='录取汇总（轮次未分）',group=None,major=major,majorCode=None,score=score,scoreType='专业录取最低分',rank=None,sourceId=pdfsource,sourceIds=[pdfsource,pagesource],sourcePage=1,sourceTable='2026年全国统一高考各省市各专业录取最低分数线',sourceRow=f'表格第{table_row}行（含两行表头）｜{major}',sourceColumn=f'第{table_col}列（1起，含专业名称列）｜广西{track}类',sourceScoreHeader='录取最低分数线',reviewedAt='2026-09-20',evidenceStatus='verified',scoreComparable=True,scoreBasis='全国统一高考分数；原表未细分政策加分口径',scoreScaleMaximum=750,scoreEvidenceGaps=[],conflictFields=[],admissionType='普通高考（类别未细分）',requiredSubjects=[],subjectRule='unknown',requirementText='首选'+track+'；原分数表未列完整再选要求',metadataGaps=['广西组码','专业代码','具体批次','具体录取轮次','招生类别细分','录取人数','最低位次','政策加分细分口径'],fieldSourceIds={k:[pdfsource] for k in ['year','province','track','major','score','note']},note=note))
write('major-cutoffs-upsert.json',scores)
notes=[];observations=[]
for d in D:
 code=d['schoolCode'];t=target[code];ms=[meta[r] for r in d['refs']]
 started=min(m['checkedAt'] for m in ms);finished=max(m['finishedAt'] for m in ms)
 count=sum(r['schoolCode']==code for r in scores)
 limitation='核查范围限所列入口、目录和原文；未取得不等于学校未招生或所有渠道均未发布。'
 notes.append(dict(id='review-major-20260920-c-'+code,year=2026,province='广西',schoolCode=code,school=t['school'],auditKind='major-scores',checkedAt='2026-09-20',startedAt=started,finishedAt=finished,title='2026广西高职专业录取分核查',status=d['status'],recordCount=count,sourceIds=[source_id(r) for r in d['refs']],checkedUrls=[m['url'] for m in ms],note=d['note'],scope=d['scope']+' '+limitation,remainingGaps=d['remaining']))
 evidence=[dict(sourceId=source_id(r),url=meta[r]['url'],accessedAt=meta[r]['checkedAt'],finishedAt=meta[r]['finishedAt'],httpStatus=meta[r].get('httpStatus'),responseSha256=meta[r].get('sha256'),errorSha256=meta[r].get('errorSha256'),archiveFile=meta[r].get('archiveFile')) for r in d['refs']]
 observations.append(dict(schoolCode=code,school=t['school'],year=2026,province='广西',auditKind='major-scores',startedAt=started,finishedAt=finished,status=d['status'],scoreRecordCount=count,scope=d['scope'],limitation=limitation,observed=d['note'],remainingGaps=d['remaining'],fieldEvidence=[dict(sourceId=source_id(f['ref']),locator=f['locator'],fact=f['fact']) for f in d['fieldEvidence']],sources=evidence))
write('school-audit-notes.json',notes);write('observations.json',observations)
write('summary.json',dict(schools=30,actualMajorRecords=len(scores),schoolsWithActualMajorRecords=1,statusCounts=dict(Counter(d['status'] for d in D)),officialSourceRecords=len(sources),responseHashes=sum(bool(x.get('sha256')) for x in sources),accessFailureRecords=sum(x['evidenceType']=='access-failure' for x in sources),negativeConclusions='仅对所列入口范围有效，不代表全校全渠道未发布'))
print(json.dumps(read('summary.json'),ensure_ascii=False))
