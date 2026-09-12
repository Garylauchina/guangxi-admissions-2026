"""Freeze bounded facts and metadata from local original responses. Raw files stay local."""
from pathlib import Path
from html.parser import HTMLParser
import json,hashlib,re
from urllib.parse import urlsplit,parse_qs
import pdfplumber
ROOT=Path(__file__).resolve().parent;RAW=ROOT/'raw';checks=[]
def load(n):return json.loads((RAW/n).read_text())
def read(n):return (RAW/n).read_text()
def save(n,x):(ROOT/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def check(n,c):
 assert c,n
 checks.append({'check':n,'passed':True})
class Table(HTMLParser):
 def __init__(self):super().__init__();self.rows=[];self.row=None;self.cell=None
 def handle_starttag(self,t,a):
  if t=='tr':self.row=[]
  if t in ['td','th']:self.cell=[]
 def handle_endtag(self,t):
  if t in ['td','th'] and self.cell is not None:
   if self.row is not None:self.row.append(''.join(self.cell).strip())
   self.cell=None
  if t=='tr' and self.row is not None:self.rows.append(self.row);self.row=None
 def handle_data(self,d):
  if self.cell is not None:self.cell.append(d)
def rows(n):
 p=Table();p.feed(read(n));return p.rows
params=load('uibe-params.json');check('UIBE parameter response success',params['state']==1)
check('UIBE professional minOrder label',any(x.get('fieldName')=='minOrder' and x.get('label')=='最低分排名' for x in params['data']['showField']['showField3']))
categories=[('历史类','提前批',4),('历史类','本科批',7),('历史类','中外合作办学',1),('历史类','少数民族预科',1),('历史类','国家专项',3),('历史类','高校专项',1),('物理类','本科批',11),('物理类','中外合作办学',1),('物理类','少数民族预科',1),('物理类','国家专项',1),('物理类','高校专项',1)]
evidence=[]
fields=['ssmc','nf','klmc','zymc','minScore','maxScore','avgScore','minOrder','minRank','rs','zydm','zyzname','pcmc','zslx','zylx','zycc']
for i,(track,category,count) in enumerate(categories,1):
 name=f'uibe-gx-2026-{i}.json';d=load(name);m=load(name+'.meta.json');q=m['data'];rr=d['data']['sszygradeList']
 check(name+' exact successful selected query',d['state']==1 and q=={'ssmc':'广西','zsnf':'2026','klmc':track,'sex':'','campus':'','zslx':category} and len(rr)==count)
 for j,r in enumerate(rr,1):
  check(name+f' row{j} direct identity and rank',r['nf']=='2026' and r['ssmc']=='广西' and r['klmc']==track and r['zslx']==category and r['minOrder']==r['minRank'] and r['zyzname']=='')
  evidence.append({'file':name,'sourceRow':j,'included':category!='少数民族预科','exclusionReason':'预科汇总不作为具体本科专业录取分' if category=='少数民族预科' else None,'fields':{k:r.get(k) for k in fields}})
for track,count in [('history',7),('physics',9)]:
 d=load(f'uibe-gx-2025-{track}.json');check('UIBE prior '+track+' positive',d['state']==1 and len(d['data']['sszygradeList'])==count and all(str(x['nf'])=='2025' for x in d['data']['sszygradeList']))
check('UIBE 30 majors 83 admissions',sum(e['included'] for e in evidence)==30 and sum(e['fields']['rs'] for e in evidence if e['included'])==83)
check('UIBE charter2026 and score/selection conditions','2026年全日制普通本科招生章程' in read('uibe-charter.html') and '不得' in read('uibe-charter.html') and '全国性政策加分' in read('uibe-charter.html'))
for kind,count in [('physics',4),('history',3)]:
 n=f'sduwh-get-2025-{kind}.html';check('SDUWH old '+kind+' positive',len([r for r in rows(n) if len(r)==10 and r[0] not in ['专业类','专业']])==count and '2025年广西壮族自治区普通类' in read(n))
for kind in ['physics','history','physics-national','history-national']:
 n=f'sduwh-get-2026-{kind}.html';m=load(n+'.meta.json');q=parse_qs(urlsplit(m['url']).query)
 check('SDUWH current GET '+kind+' correct empty',m['httpStatus']==200 and q['nf']==['2026'] and q['sf']==['广西壮族自治区'] and '该项选择无数据' in read(n) and 'value="广西壮族自治区"' in read(n) and len(rows(n))==0)
for year in [2025,2026]:
 for kind in ['physics','history']:
  check(f'SDUWH malformed POST excluded {year} {kind}','value="???????"' in read(f'sduwh-gx-{year}-{kind}.html'))
check('SUDA old table 38',len([r for r in rows('suda-gx-2025.html') if len(r)==6 and r[2] in ['物理类','历史类']])==38)
check('SUDA 2026 selected route no professional table',len([r for r in rows('suda-gx-2026.html') if len(r)==6 and r[2] in ['物理类','历史类']])==0 and parse_qs(urlsplit(load('suda-gx-2026.html.meta.json')['url']).query)['ay']==['2026'])
check('SUDA menu latest2025','value="2025"' in read('suda-scores.html') and 'value="2026"' not in read('suda-scores.html'))
with pdfplumber.open(RAW/'scnu-prior-scores.pdf') as pdf:
 p1=pdf.pages[0].extract_text();p7=pdf.pages[6].extract_text()
 check('SCNU PDF is2025 and GX physical page7','2025' in p1 and '华南师范大学' in p1 and '广西' in p7 and len(pdf.pages)==11)
check('GDUT official selectedyear2025','n2025' in load('gdut-gx-2025.html.meta.json')['url'] and '2025' in read('gdut-scores.html'))
check('ZJU latest2026publication actually2025 groupfiling','2025年浙江大学各省份普通本一批投档分数线' in read('zju-latest.html') and '广西' in read('zju-latest.html'))
metas=[]
for p in sorted(RAW.glob('*.meta.json')):
 m=json.loads(p.read_text())
 if m.get('sha256'):check(m['name']+' original archive digest',hashlib.sha256((RAW/m['name']).read_bytes()).hexdigest()==m['sha256'])
 metas.append(m)
save('evidence-rows.json',evidence);save('review-evidence.json',{'reviewedAt':'2026-09-12','checks':checks,'manualReview':[{'file':'scnu-prior-scores.pdf','page':7,'note':'已渲染核对广西历史6、物理7专业，合计行另计；PDF第一页明确2025。'},{'file':'gdut-gx-2025.png','note':'已目视核对广西专业录取数/max/avg/min/排名，来源上级页面2025，不能改写年份。'}]});save('source-manifest.json',metas)
print('PASS frozen',len(evidence),'statistical rows,',len(metas),'sources,',len(checks),'checks')
