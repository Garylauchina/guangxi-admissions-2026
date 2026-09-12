#!/usr/bin/env python3
"""Independent archive review; needs batch-c raw re-fetched first. Never imports its parser."""
from pathlib import Path
from html.parser import HTMLParser
import collections,csv,hashlib,html,json,re,sys
R=Path(__file__).resolve().parent;B=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else R.parent/'batch-c'
EXPECTED_DATA_SHA='a6295b04eda4377ce127471a6725b5911c845c413302d3d5a8c03b663375480e'
def read(n):return json.loads((B/n).read_text())
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def plain(n):
 t=(B/'raw'/n).read_text();t=re.sub('<script[^>]*>.*?</script>',' ',t,flags=re.S|re.I);return re.sub(r'\s+',' ',html.unescape(re.sub('<[^>]*>',' ',t)))
assert digest(B/'major-cutoffs-upsert.json')==EXPECTED_DATA_SHA,'Input changed; re-review new version.'
rows=read('major-cutoffs-upsert.json');sources=read('sources.json');notes=read('school-audit-notes.json');assert len(rows)==32
class Tables(HTMLParser):
 def __init__(self):super().__init__();self.tables=[];self.depth=0;self.table=[];self.row=[];self.cell=None
 def handle_starttag(self,t,a):
  if t=='table':
   if self.depth==0:self.table=[]
   self.depth+=1
  elif t=='tr' and self.depth:self.row=[]
  elif t in ['td','th'] and self.depth:self.cell=[]
 def handle_data(self,d):
  if self.cell is not None:self.cell.append(d)
 def handle_endtag(self,t):
  if t in ['td','th'] and self.cell is not None:self.row.append(re.sub(r'\s+','', ''.join(self.cell)));self.cell=None
  elif t=='tr' and self.depth and self.row:self.table.append(self.row)
  elif t=='table':
   self.depth-=1
   if not self.depth:self.tables.append(self.table)
p=Tables();p.feed((B/'raw/cqc-gx.html').read_text());tables=[t for t in p.tables if t and t[0]==['科类','录取专业','录取最低分数','录取数']];assert len(tables)==1 and len(tables[0])==10
expected=[]
for n,x in enumerate(tables[0][1:],2):expected.append(dict(sourceKey='cqc-gx',sourceRow=n,track=x[0][:2],major=x[1],score=int(x[2]),admittedCount=int(x[3])))
for x in csv.DictReader((R/'c-image-transcription.tsv').open(),delimiter='\t'):
 expected.append(dict(sourceKey=x['sourceKey'],sourceRow=int(x['sourceRow']),track=x['track'],major=x['major'],score=int(x['minimum']),admittedCount=int(x['admittedCount']),sourceMaximumScore=int(x['maximum']),**({'sourceAverageScore':float(x['average'])} if x['average'] else {})))
index={(x['sourceId'].removeprefix('major-20260912b2-c-'),x['sourceRow']):x for x in rows};assert len(index)==32
comparisons=0
for e in expected:
 r=index[e['sourceKey'],e['sourceRow']]
 for k in ['track','major','score','admittedCount','sourceMaximumScore','sourceAverageScore']:
  if k in e:assert r.get(k)==e[k],(e['sourceKey'],e['sourceRow'],k,r.get(k),e[k]);comparisons+=1
for r in rows:
 assert r['province']=='广西' and r['year']==2026 and r['scoreType']=='专业录取最低分'
 assert r['rank'] is None and r['group'] is None and r['round']=='录取汇总（轮次未分）'
 assert r['admissionType']=='普通类' and r['scoreComparable'] is True and r['scoreEvidenceGaps']==r['conflictFields']==[]
 assert r.get('plannedCount') is None and not r.get('matchedGroupId') and not r.get('referenceScore')
 assert r['scoreScaleMaximum']==750 and '裸分' not in r['scoreBasis']
 if r['schoolCode']=='10383':assert r['batch']=='本科批' and r['requiredSubjects']==['化学'] and r['subjectRule']=='all'
 elif r['schoolCode']=='10723':assert r['batch']=='本科（批次待核）' and r['subjectRule']=='unknown' and r['sourceScoreHeader']=='文化分投档 录取最高/最低分' and r['sourceScoreNote']=='文化分录取'
 else:assert r['schoolCode']=='12758' and r['batch']=='高职专科批次' and r['subjectRule']=='unknown'
assert comparisons==153 and sum(x['admittedCount'] for x in rows)==96
cqc=plain('cqc-gx.html');tlu=plain('tlu-gx.html');wnu=plain('wnu-gx.html')
assert '2026年广西普通高校招生高职专科批次普通类录取情况' in cqc
assert '2026年广西壮族自治区普通本科批次录取工作圆满完成' in re.sub(r'\s+','',tlu)
assert '2026年录取快讯' in wnu and '2026-07-21' in wnu and '广西壮族自治区普通类' in wnu
qc=plain('cqc-charter.html');tc=plain('tlu-charter.html');wc=plain('wnu-charter-mirror.html')
assert '4150012758' in qc and '婴幼儿托育服务与管理' in qc and '不招收色盲、色弱考生' in qc and '加降分政策' in qc
assert '物联网应用技术' in cqc and '其余专业学生大一年级在荣昌校区就读' in qc
child=[r for r in rows if r['major']=='婴幼儿托育服务与管理'];assert len(child)==2
assert all(r['eligibility']['colorBlindnessExcluded'] and r['eligibility']['colorWeaknessExcluded'] and '色盲、色弱' in r['note'] for r in child)
assert '录取时以投档分为准' in tc and '英语作为第一外语安排教学' in tc
assert '按加分(或降分)后的成绩排序录取' in wc and '2026' in wc
archive_checks=[]
for s in sources:
 if s.get('archiveFile'):
  actual=digest(B/s['archiveFile']);assert actual==s['sha256'];archive_checks.append(s['id'])
assert len(archive_checks)==18
public=read('PUBLIC-FILES.json')['publicFiles']
for f in public:
 p=Path(f);assert not p.is_absolute() and '..' not in p.parts and p.parts[0]!='raw'
 t=(B/f).read_text()
 assert ('/'+'Users/') not in t and ('/'+'home/') not in t
 assert not re.search(r'Bearer\s+[A-Za-z0-9._-]{16,}|JSESSIONID=[A-Za-z0-9]{8,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',t)
summary=dict(status='PASS',reviewedAt='2026-09-12',inputHashes={f:digest(B/f) for f in ['major-cutoffs-upsert.json','sources.json','school-audit-notes.json']},summary=dict(rows=32,admitted=96,independentSourceValueComparisons=comparisons,archiveHashesChecked=len(archive_checks),publicFilesScanned=len(public)),schools=[dict(schoolCode=code,rows=sum(r['schoolCode']==code for r in rows),admitted=sum(r['admittedCount'] for r in rows if r['schoolCode']==code)) for code in ['12758','10383','10723']],findings=[],limits=['Independent read of archived official HTML and original images; no fresh network queries.','School-code filing source original hashes were not re-downloaded; three charter identities and imported code metadata checked.','Manual image interpretation remains part of evidence; rerunning numeric comparisons is not a replacement for viewing images.','This review covers C 32 new records, qualifications and six excluded WNU images; it does not review unrelated school gaps.'])
(R/'review-c.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n');print(json.dumps(summary['summary'],ensure_ascii=False))
