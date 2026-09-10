#!/usr/bin/env python3
"""Independent read-only source-value audit. Requires pdfplumber; never calls collector parsers."""
from pathlib import Path
from html.parser import HTMLParser
from html import unescape
from collections import Counter
import re,json,hashlib,datetime
import pdfplumber
HERE=Path(__file__).resolve().parent
BASE=HERE.parent
checks=[]; row_results=[]; inputs={}; totals={}
def load(p):
 inputs[str(p.relative_to(BASE))]=hashlib.sha256(p.read_bytes()).hexdigest()
 return json.loads(p.read_text())
def read(p):
 inputs[str(p.relative_to(BASE))]=hashlib.sha256(p.read_bytes()).hexdigest()
 return p.read_text()
def norm(s):return re.sub(r'\s+','',str(s or '')).replace('（','(').replace('）',')')
def num(s):return float(norm(s)) if norm(s) else None
def check(name,ok,detail=None):
 checks.append({'name':name,'pass':bool(ok),**({'detail':detail} if detail is not None else {})})
class Tables(HTMLParser):
 def __init__(self):super().__init__();self.stack=[];self.done=[]
 def handle_starttag(self,tag,attrs):
  if tag=='table': self.stack.append({'rows':[],'row':None,'cell':None})
  if not self.stack:return
  t=self.stack[-1]
  if tag=='tr':t['row']=[]
  if tag in ('td','th') and t['row'] is not None:t['cell']={'text':'','attrs':dict(attrs)}
 def handle_data(self,s):
  if self.stack and self.stack[-1]['cell'] is not None:self.stack[-1]['cell']['text']+=s
 def handle_endtag(self,tag):
  if not self.stack:return
  t=self.stack[-1]
  if tag in ('td','th') and t['cell'] is not None:
   t['row'].append(t['cell']);t['cell']=None
  if tag=='tr' and t['row'] is not None:t['rows'].append(t['row']);t['row']=None
  if tag=='table':self.done.append(self.stack.pop()['rows'])
def tables(s):
 p=Tables();p.feed(s);out=[]
 for rows in p.done:
  expanded=[];carry={}
  for raw in rows:
   row={};new={}
   for c,(v,left) in carry.items():
    row[c]=v
    if left>1:new[c]=(v,left-1)
   c=0
   for cell in raw:
    while c in row:c+=1
    colspan=int(cell['attrs'].get('colspan',1)); rowspan=int(cell['attrs'].get('rowspan',1));v=cell['text'].strip()
    for j in range(colspan):
     row[c+j]=v
     if rowspan>1:new[c+j]=(v,rowspan-1)
    c+=colspan
   if row:expanded.append([row.get(i,'') for i in range(max(row)+1)])
   carry=new
  out.append(expanded)
 return out
def verify_row(r,expected,raw_file):
 fields=[]
 for field,value in expected.items():
  actual=r.get(field)
  ok=norm(actual)==norm(value) if isinstance(value,str) else actual==value
  fields.append({'field':field,'pass':ok,'actual':actual,'sourceValue':value})
 row_results.append({'id':r['id'],'school':r['school'],'sourceId':r['sourceId'],'rawFile':raw_file,'pass':all(x['pass'] for x in fields),'fields':fields})
for b in ['batch-a','batch-c']:
 folder=BASE/b;rows=load(folder/'major-cutoffs-upsert.json');sources=load(folder/'sources.json');notes=load(folder/'school-audit-notes.json');ids={s['id'] for s in sources}
 check(f'{b}:unique-row-ids',len({r['id'] for r in rows})==len(rows))
 check(f'{b}:source-ids-resolve',all(set([r['sourceId']]+r.get('sourceIds',[])+[s for v in r.get('fieldSourceIds',{}).values() for s in v])<=ids for r in rows))
 check(f'{b}:year-province-score-scope',all(r['year']==2026 and r['province']=='广西' and r['track'] in ['物理','历史'] and r['scoreType']=='专业录取最低分' and 0<r['score']<=750 and r['scoreScaleMaximum']==750 for r in rows))
 check(f'{b}:unseparated-round-preserved',all(r['round']=='录取汇总（轮次未分）' for r in rows))
 check(f'{b}:min-max-average-consistent',all(r['score']<=r['sourceMaximumScore'] and (r.get('sourceAverageScore') is None or r['score']<=r['sourceAverageScore']<=r['sourceMaximumScore']) for r in rows))
 check(f'{b}:positive-admitted-count',all(r.get('admittedCount') is None or r['admittedCount']>0 for r in rows))
 check(f'{b}:no-unproven-group-or-rank',all((r['group'] is None or r.get('fieldSourceIds',{}).get('group')) and (r['rank'] is None or r.get('fieldSourceIds',{}).get('rank')) for r in rows))
 check(f'{b}:audit-local-date',all(str(r['checkedAt']).startswith('2026-09-11') for r in notes))
 hash_count=0
 for s in sources:
  p=folder/s.get('archiveFile','__none__')
  if not p.is_file():
   key=s['id'].removeprefix('major-20260911-a-').removeprefix('major-c-20260911-')
   candidates=[q for q in (folder/'raw').glob(key+'.*') if not q.name.endswith('.meta.json')]
   if len(candidates)==1:p=candidates[0]
  if p.is_file():
   actual=hashlib.sha256(p.read_bytes()).hexdigest();expected=s.get('archiveSha256') or s.get('sha256');check(f'{b}:source-hash:{s["id"]}',actual==expected);hash_count+=1
 totals[b]={'rows':len(rows),'sources':len(sources),'notes':len(notes),'sourceArchivesHashChecked':hash_count,'schools':dict(Counter(r['school'] for r in rows))}
 if b=='batch-a':
  muc=[r for r in rows if r['schoolCode']=='10052'];count=0
  for file in sorted((folder/'raw').glob('muc-majors-2026-gx-*.json')):
   if file.name.endswith('.meta.json'):continue
   raw=load(file);meta=load(file.with_suffix('.meta.json'));sid='major-20260911-a-'+file.stem
   check(file.stem+':successful-complete',raw['success'] is True and raw['total']==len(raw['rows']))
   check(file.stem+':actual-query-2026-gx',meta['request']['vepd_year']=='2026' and meta['request']['vepd_sf']=='450000')
   rs=[r for r in muc if r['sourceId']==sid];check(file.stem+':count',len(rs)==len(raw['rows']))
   for i,x in enumerate(raw['rows'],1):
    match=[r for r in rs if norm(r['major'])==norm(x['zymc'])]
    check(file.stem+':unique-'+str(i),len(match)==1)
    if not match:continue
    verify_row(match[0],{'year':x['year'],'province':x['sfmc'],'sourceTrack':x['klmc'],'track':x['klmc'][:2],'major':x['zymc'],'score':num(x['mincj']),'sourceMaximumScore':num(x['maxcj']),'sourceAverageScore':num(x['avgcj']),'rank':num(x['minwc']),'admissionType':x['zslbmc'],'sourceCategory':x['zslbmc'],'group':None,'admittedCount':None,'plannedCount':None,'sourceRow':i},str(file.relative_to(BASE)));count+=1
  entry=read(folder/'raw/muc-score-entry.html')
  segment=entry[entry.find('分专业录取情况'):]
  check('MUC:major-table-rank-header-and-binding','最低分排名' in segment and 'data[i].minwc' in segment and 'findAdmissionScore.json' in segment)
  check('MUC:decimal-floor-note','如果分数为小数，则向下取整' in entry)
  html=read(folder/'raw/xjtlu-score-2026.html');pos=html.find('<h4>广西壮族自治区')
  table=tables(html[pos:html.find('</table>',pos)+8])[0]
  check('XJTLU:page-title-2026',bool(re.search(r'<h1[^>]*>\s*2026年分省录取数据',html)))
  check('XJTLU:GX-three-formal-classes',len(table)==4 and norm(table[0][2])=='大类')
  for t,r in zip(table[1:],[r for r in rows if r['schoolCode']=='16302']):
   verify_row(r,dict(year=2026,province='广西',track=t[0],sourceTrack=t[0],sourceSubjectRequirement=t[1],major=t[2],plannedCount=num(t[3]),admittedCount=num(t[4]),sourceMaximumScore=num(t[5]),score=num(t[6]),sourceAverageScore=None,rank=None,group=None,majorType='正式招生大类',admissionType='中外合作办学',requiredSubjects=['化学'] if '化学' in t[1] else [],subjectRule='all' if '化学' in t[1] else 'none',requirementText=t[1]),f'{b}/raw/xjtlu-score-2026.html')
 else:
  for stem in ['juwp-gx-6212','juwp-gx-6502','sctu-gx-2267','sxdt-admission']:
   html=read(folder/f'raw/{stem}.html');tabs=tables(html);sid='major-c-20260911-'+stem;rs=[r for r in rows if r['sourceId']==sid]
   check(stem+':year-title',bool(re.search(r'<title>[^<]*2026',html,re.I)))
   if stem.startswith('juwp'):
    table=[t for t in tabs if t and len(t[0])==8 and '专业名称' in norm(t[0][1])][0]
    check(stem+':complete-major-row-count',len(table)-1==len(rs))
    for t in table[1:]:
     match=[r for r in rs if norm(r['major'])==norm(t[1])];check(stem+':unique-'+norm(t[1]),len(match)==1)
     if not match:continue
     r=match[0];category='定向培养军士' if stem.endswith('6502') else ('中外合作办学' if '中外合作' in t[1] else '普通类')
     verify_row(r,dict(year=2026,province='广西',track=norm(t[0])[:2],sourceTrack=t[0],major=t[1],admittedCount=num(t[2]),sourceMaximumScore=num(t[4]),score=num(t[5]),sourceAverageScore=num(t[6]),sourceMinimumRank=num(t[7]),rank=None,rankComparable=False,group=None,admissionType=category,batch='高职高专提前批定向类' if stem.endswith('6502') else '本科普通批'),f'{b}/raw/{stem}.html')
   elif stem.startswith('sctu'):
    table=[t for t in tabs if t and len(t[0])==9 and '专业组' in t[0]][0]
    check('SCTU:five-table-rows',len(table)-1==len(rs)==5)
    for t in table[1:]:
     r=[r for r in rs if r['group']==norm(t[2])][0]
     verify_row(r,dict(year=2026,province=t[0],track='物理' if '物理' in t[1] else '历史',sourceTrack=t[1],major=t[3],group=norm(t[2]),admittedCount=num(t[5]),sourceMaximumScore=num(t[6]),score=num(t[7]),sourceAverageScore=num(t[8]),rank=None,admissionType='中外合作办学' if norm(t[2])=='301' else '普通类',batch='本科普通批'),f'{b}/raw/{stem}.html')
     if r.get('plannedCount') is not None:check('SCTU:explicit-plan-'+r['id'],r['plannedCount']==num(t[4]))
   else:
    table=[t for t in tabs if t and len(t[0])==6 and norm(t[0][0])=='省市名称'][0]
    gx=[t for t in table[1:] if t[0]=='广西'];check('SXDT:GX-eight-rows',len(gx)==len(rs)==8)
    for t in gx:
     r=[r for r in rs if norm(r['major'])==norm(t[2])][0]
     verify_row(r,dict(year=2026,province=t[0],track=t[1][:2],sourceTrack=t[1],major=t[2],admittedCount=num(t[3]),sourceMaximumScore=num(t[4]),score=num(t[5]),sourceAverageScore=None,rank=None,group=None,admissionType='普通类'),f'{b}/raw/{stem}.html')
  pdf_file=folder/'raw/fjbu-pdf.pdf';inputs[str(pdf_file.relative_to(BASE))]=hashlib.sha256(pdf_file.read_bytes()).hexdigest();pdfrows=[]
  with pdfplumber.open(pdf_file) as pdf:
   check('FJBU:two-pages',len(pdf.pages)==2)
   check('FJBU:2026-GX-title','2026' in pdf.pages[0].extract_text() and '广西-143' in norm(pdf.pages[0].extract_text()))
   for pi,page in enumerate(pdf.pages,1):
    ts=page.extract_tables();check(f'FJBU:p{pi}-column-headers',len(ts)==1 and [norm(x) for x in ts[0][0]][:8]==['序号','专业名称','科类(组别)','计划数','录取数','最高分','最低分','平均分'])
    for t in ts[0][1:]:
     r=[r for r in rows if r['schoolCode']=='11313' and r['sourceRow']==int(t[0])][0];pdfrows.append(t)
     verify_row(r,dict(year=2026,province='广西',track=t[2][:2],sourceTrack=t[2],major=t[1],admittedCount=num(t[4]),sourceMaximumScore=num(t[5]),score=num(t[6]),sourceAverageScore=num(t[7]),rank=None,group=None,admissionType='普通类',sourcePage=pi,requiredSubjects=['化学'] if '化学' in t[2] else [],subjectRule='all' if '化学' in t[2] else 'none'),f'{b}/raw/fjbu-pdf.pdf')
     check('FJBU:control-line-difference-'+t[0],num(t[6])-num(t[8])==num(t[9]))
     if r.get('plannedCount') is not None:check('FJBU:explicit-plan-'+r['id'],r['plannedCount']==num(t[3]))
  check('FJBU:all-63-sequential-rows',[int(t[0]) for t in pdfrows]==list(range(1,64)))
  totals['fjbu']={'planned':sum(int(t[3]) for t in pdfrows),'admitted':sum(int(t[4]) for t in pdfrows),'byTrack':{k:{'rows':len([t for t in pdfrows if t[2].startswith(k)]),'planned':sum(int(t[3]) for t in pdfrows if t[2].startswith(k)),'admitted':sum(int(t[4]) for t in pdfrows if t[2].startswith(k))} for k in ['历史','物理']}}
# Independent charter/header semantics; these checks supplement raw numeric equality.
a_rows=load(BASE/'batch-a/major-cutoffs-upsert.json');c_rows=load(BASE/'batch-c/major-cutoffs-upsert.json')
muc_charter=norm(unescape(re.sub('<[^>]+>','',read(BASE/'batch-a/raw/muc-charter-2026.html'))))
check('MUC:charter-policy-score-basis','学校录取专业时原则上认可省级招办有关加分' in muc_charter and '最大分值不超过20分' in muc_charter)
xfile=BASE/'batch-a/raw/xjtlu-charter-2026.pdf';inputs[str(xfile.relative_to(BASE))]=hashlib.sha256(xfile.read_bytes()).hexdigest()
with pdfplumber.open(xfile) as pdf:xt=norm(''.join(page.extract_text() or '' for page in pdf.pages))
check('XJTLU:charter-2026-formal-class-and-cooperation','2026年中国内地本科招生章程' in xt and '办学性质：中外合作办学' in xt and '按照专业大类进行招生' in xt)
check('XJTLU:charter-score-order','不含政策性加分' in xt and '投档成绩相同' in xt)
for stem in ['juwp','sctu','sxdt','fjbu']:
 charter=norm(unescape(re.sub('<[^>]+>','',read(BASE/f'batch-c/raw/{stem}-charter.html'))))
 check(stem+':2026-charter-policy-score-basis','2026' in charter and '加分' in charter)
 if stem=='sctu':
  coop=[r for r in c_rows if r['schoolCode']=='11552' and r['group']=='301'][0]
  cook=[r for r in c_rows if r['schoolCode']=='11552' and r['group']=='101'][0]
  check('SCTU:English85-explicit-restriction','85分及以上' in charter and '85' in str(coop))
  check('SCTU:voluntary-major-and-transfer-restriction','不录取未填报本专业志愿的考生' in charter and '不得转入其他专业' in charter and '不得转' in str(coop))
  check('SCTU:culinary-vision-restriction','4.8及以上且无色盲' in charter and '4.8' in str(cook) and '色盲' in str(cook))
 if stem=='juwp':
  check('JUWP:military-qualification-not-general','定向培养军士报考条件、政审、体检' in charter and all(r['admissionType']=='定向培养军士' and '政审' in r['note'] for r in c_rows if r['batch']=='高职高专提前批定向类'))
check('all-132-row-values',len(row_results)==132 and all(r['pass'] for r in row_results))
result={'reviewedAt':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),'status':'PASS' if all(x['pass'] for x in checks) else 'FAIL','method':'Independent raw JSON/HTMLParser and PDF pdfplumber extraction. Collector-derived evidence and sourceRecord fields are not comparison inputs. Two PDF page images visually reviewed separately.','totals':totals,'rowCount':len(row_results),'fieldCount':sum(len(r['fields']) for r in row_results),'checks':checks,'rows':row_results,'inputSha256':inputs}
(HERE/'QA.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:result[k] for k in ['status','rowCount','fieldCount','totals']},ensure_ascii=False,indent=2))
print('failed checks',json.dumps([x for x in checks if not x['pass']],ensure_ascii=False))
print('failed rows',json.dumps([x for x in row_results if not x['pass']],ensure_ascii=False))
