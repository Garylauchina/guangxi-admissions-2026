#!/usr/bin/env python3
"""Read-only independent source review. Requires pdfplumber and local raw evidence.
Usage: python3 review.py [path/to/batch-root]
Writes only QA.json beside this script. It never changes the reviewed package.
"""
from pathlib import Path
import sys,json,re,hashlib,html
from urllib.parse import urlparse,parse_qs
import pdfplumber
HERE=Path(__file__).resolve().parent
P=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else HERE.parent/'batch-root'
RAW=P/'raw'
def read(n): return (RAW/n).read_text()
def js(n): return json.loads(read(n))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def plain(n): return re.sub(r'\s+',' ',html.unescape(re.sub('<[^>]+>',' ',read(n))))
checks=[]
def check(k,b): checks.append({'check':k,'passed':bool(b)})
rows=json.loads((P/'major-cutoffs-upsert.json').read_text())
sources=json.loads((P/'sources.json').read_text()); sm={s['id']:s for s in sources}
notes=json.loads((P/'school-audit-notes.json').read_text())
check('8 unique records, 6 school reviews, 55 unique sources',len(rows)==len({r['id'] for r in rows})==8 and len(notes)==6 and len(sm)==len(sources)==55)
field_count=0
for r in rows:
 for field,value in {'year':2026,'province':'广西','track':'物理','sourceTrack':'物理类','group':None,'majorCode':None,'rank':None,'round':'录取汇总（轮次未分）','scoreType':'专业录取最低分','scoreScaleMaximum':750,'requiredSubjects':[],'subjectRule':'unknown'}.items():
  check(r['id']+': '+field,r.get(field)==value);field_count+=1
 check(r['id']+': no invented counts',r.get('plannedCount') is None and r.get('admittedCount') is None)
 check(r['id']+': valid source references',r['sourceId'] in sm and all(s in sm for s in r['sourceIds']) and all(s in sm for v in r['fieldSourceIds'].values() for s in v))
 check(r['id']+': critical field provenance',all(r['fieldSourceIds'].get(f) for f in ['year','province','track','major','score','admissionType','schoolCode','scoreBasis','admissionRequirements']))
 check(r['id']+': score range',0<r['score']<=750)
raw_rows=js('ccmu-gx-2026-0.json')['list']; cc=[r for r in rows if r['schoolCode']=='10025']
check('CCMU exactly six original rows and complete menu',len(raw_rows)==len(cc)==6 and set(js('ccmu-params-majors.json')['majorList'])=={x['majorName'] for x in raw_rows})
for r,a in zip(cc,raw_rows):
 for field,key in {'year':'year','province':'cityName','sourceTrack':'scienceClass','major':'majorName','score':'lowScore','sourceMaximumScore':'hightScore','sourceAverageScore':'avgScore','batch':'batch','admissionType':'type','sourceCategory':'type','group':'majorGroup','rank':'lowScoreRank'}.items():
  check(r['id']+': original '+field,r.get(field)==a.get(key));field_count+=1
 check(r['id']+': source row locator',raw_rows[r['sourceRow']-1]==a)
 check(r['id']+': source null count',a['enrollNum'] is None and a['enrollPlan'] is None)
 check(r['id']+': source score interval',a['lowScore']<=a['avgScore']<=a['hightScore'])
 check(r['id']+': verified raw-exam score basis',r['scoreComparable'] is True and '实考分' in r['scoreBasis'] and r['evidenceStatus']=='verified')
 check(r['id']+': unknown reselected subjects independent of xkkm',a['xkkm'] in ['5+3','五年','四年'] and r['subjectRule']=='unknown')
meta=js('ccmu-gx-2026-0.json.meta.json');qp=parse_qs(urlparse(meta['url']).query)
check('CCMU exact live GET parameters',all(qp.get(k)==[v] for k,v in {'sCode':'DEWVJI','cityName':'广西','year':'2026','scienceClass':'物理类','type':'普通类','batch':'本科普通批'}.items()))
check('CCMU current province menu exposes physics only',js('ccmu-params-2026.json')['scienceList']==['物理类'])
check('CCMU type and batch menus exact',js('ccmu-params-types.json')['typeList']==['普通类'] and js('ccmu-params-batches.json')['batchList']==['本科普通批'])
form=read('ccmu-major-form.html');jst=read('ccmu-major.js')
check('CCMU original HTML binds xkkm to duration caption',bool(re.search(r'data-key="xkkm"[^>]*>年制</th>',form)))
check('CCMU original JS exposes both used API routes',all(x in jst for x in ['findMajorScoreCompareList','getMajorSelectChange']))
check('CCMU official link chain', 'zhsh.ccmu.edu.cn' in read('ccmu-main.html') and 'https://admin.zhinengdayi.com' in read('ccmu-major.html') and '/front/info/form/majorScore?' in read('ccmu-major.html') and "sCode = 'DEWVJI'" in read('ccmu-major.html') and 'majorEnrollForm2.js' in form)
cchar=plain('ccmu-charter.html')
check('CCMU charter professional raw-exam basis and bonus tie-break',all(x in cchar for x in ['2026','第十一条','以高考实考分和专业志愿为录取依据','分数志愿均相同','优先录取有政策性加分的考生']))
check('CCMU charter language and health requirements',all(x in cchar for x in ['非英语语种','改学英语','4.8','800度','色盲','色弱','3米','嗅觉迟钝','口吃','肝功能异常']))
pdfs={}
for name in ['snnu-current.pdf','njmu-old.pdf','njucm-gx-2025.pdf','bjut-old.pdf']:
 with pdfplumber.open(RAW/name) as pdf: pdfs[name]=[page.extract_text() or '' for page in pdf.pages]
sn=pdfs['snnu-current.pdf'][1]
check('SNNU original PDF 2026 ordinary score header',len(pdfs['snnu-current.pdf'])==11 and '2026年全国各省份普通类录取最低分' in sn)
# Independent original PDF table extraction (not collector evidence-rows).
with pdfplumber.open(RAW/'snnu-current.pdf') as pdf: tables=pdf.pages[1].extract_tables()
flat=[row for table in tables for row in table]
province=None;track=None; gx=[]
for row in flat:
 if len(row)!=5: continue
 if row[0]: province=row[0].replace('\n','')
 if row[1]: track=row[1].replace('\n','')
 if province=='广西': gx.append((track,(row[3] or '').replace('\n',''),row[4]))
check('SNNU Guangxi merged cells contain 14 records',len(gx)==14)
expected=[(track,major,int(score)) for track,major,score in gx if '中外合作办学' in major]
check('SNNU only two named majors, other 12 aggregates excluded',expected==[('物理类','电子信息技术（中外合作办学）',563),('物理类','物理学（中外合作办学）',517)])
snr=[r for r in rows if r['schoolCode']=='10718']
for r,(track,major,score) in zip(snr,expected):
 for field,value in {'sourceTrack':track,'major':major,'score':score,'admissionType':'中外合作办学','sourceCategory':'中外合作办学','batch':'本科批（精确批次待核）','sourceMaximumScore':None,'sourceAverageScore':None,'sourcePage':2}.items():
  check(r['id']+': original PDF '+field,r.get(field)==value);field_count+=1
 check(r['id']+': PDF row locator',gx[r['sourceRow']-1][1]==major)
schar=plain('snnu-charter.html')
check('SNNU charter distinct professional name', '电子信息科学与技术（中外合作办学）' in schar and '电子信息技术（中外合作办学）' not in schar)
conf=[r for r in snr if r['score']==563][0];phys=[r for r in snr if r['score']==517][0]
check('SNNU naming conflict retained and excluded',conf['scoreComparable'] is False and conf['evidenceStatus']=='source-conflict' and conf['conflictFields']==['major'] and bool(conf['scoreEvidenceGaps']))
check('SNNU physical major comparable',phys['scoreComparable'] is True and phys['evidenceStatus']=='verified')
check('SNNU charter score and cooperation requirements',all(x in schar for x in ['全国性高考加分','20分','按照投档成绩','3+1','匈牙利塞格德大学','第四学年','只录取有志愿考生','部分课程采用英语授课','不得申请转专业']))
check('SNNU sports table excluded', '体育类录取最低分' in pdfs['snnu-current.pdf'][9] and all('体育' not in r['major'] for r in rows))
neg=[]
for school,tracks,oldcounts in [('sisu',['物理类','历史类'],[6,5]),('snnu',['理工','文史'],[11,7])]:
 for track,oldcount in zip(tracks,oldcounts):
  for year in [2026,2025]:
   n=f'{school}-gx-{year}-{track}.json';d=js(n);m=js(n+'.meta.json');params=m['data']
   if school=='sisu':
    a=d['data']['sszygradeList'];ok=d['state']==1;pk='ssmc';yk='zsnf'
   else: a=d['list'];ok=d['code']==200 and d['success'] is True;pk='sf';yk='nf'
   check(n+': business success and expected count',ok and len(a)==(oldcount if year==2025 else 0))
   check(n+': exact province and year request',params[pk]=='广西' and params[yk]==str(year) and ('普通类' in params.values()))
   if a: check(n+': raw positive response year province class',all(str(x['nf'])==str(year) and x[pk]=='广西' and x['klmc']==params['klmc'] for x in a))
   neg.append({'query':n,'year':year,'count':len(a),'state':'success-empty' if not a else 'positive-control'})
sp=js('sisu-params.json')['data']['ssmc_nf_klmc_sex_campus_zslx_list'];gy=[int(k.split('_')[1]) for x in sp for k in x if k.startswith('广西_')]
check('SISU current menu latest Guangxi year 2025',max(gy)==2025)
st=js('snnu-types.json')['typeMap'];gy=[int(k.split('_')[1]) for k in st if k.startswith('广西_')]
check('SNNU current menu latest Guangxi year 2025',max(gy)==2025)
check('SISU actual front endpoint chain', 'aopress.shisu.edu.cn' in read('sisu-home.html') and 'ajax_lnfs' in read('sisu-query.html'))
check('SNNU actual front API', 'getList' in read('snnu-app.js') or 'getList' in read('snnu-query.js'))
check('NJMU old PDF 33 pages, Guangxi 2025 on page19',len(pdfs['njmu-old.pdf'])==33 and '广西壮族自治区' in pdfs['njmu-old.pdf'][18] and '2025' in pdfs['njmu-old.pdf'][18] and '2026-05-12' in read('njmu-old.html'))
check('NJUCM source is 2025 filing, 14 Guangxi rows', '2025年本科招生专业平行志愿投档线' in pdfs['njucm-gx-2025.pdf'][0] and pdfs['njucm-gx-2025.pdf'][0].count('广西壮族自治区')==14)
check('BJUT source is 2025 ordinary professional PDF',len(pdfs['bjut-old.pdf'])==5 and '2025年北京工业大学' in pdfs['bjut-old.pdf'][0] and '广西' in pdfs['bjut-old.pdf'][0])
check('Old-year-only schools have no imported rows',not ({r['schoolCode'] for r in rows}&{'10312','10315','10005','10271'}))
for n in notes:
 check(n['schoolCode']+': review identity and source references',n['id'].startswith('review-major-20260912b3-root-') and n['auditKind']=='major-scores' and n['year']==2026 and n['province']=='广西' and n['checkedAt']=='2026-09-12' and all(s in sm for s in n['sourceIds']))
 check(n['schoolCode']+': accurate partial count and limitation',n['recordCount']==sum(r['schoolCode']==n['schoolCode'] for r in rows) and '未取得不等于' in n['scope'])
archives=[]
for s in sources:
 f=s.get('archiveFile')
 if f and s.get('sha256'):
  check(f+': original archive SHA',sha(RAW/f)==s['sha256']);archives.append(f)
 elif f: check(f+': failed response distinguished',s.get('httpStatus') is None and not (RAW/f).exists())
 else: check('existing filing reference not treated as new raw',s['id']=='gxeea-2026-33107')
public=json.loads((P/'PUBLIC-FILES.json').read_text())['publicFiles']
for f in public:
 check(f+': safe public path',Path(f).name==f and (P/f).is_file())
 text=(P/f).read_text()
 check(f+': no stored secret or private path',not re.search(r'"(?:Cookie|Csrf-Token|jessionid|sessionid)"\s*:\s*"(?!\[)[^"\s]{12,}',text,re.I) and not re.search(r'/(?:Users|home)/[A-Za-z]',text))
result={'status':'passed' if all(c['passed'] for c in checks) else 'failed','reviewedAt':'2026-09-12','reviewer':'independent batch-b agent','scope':'Root B3 eight actual-major records and six school source reviews; read-only original JSON/HTML/PDF and rendered PDF pages. No new network requests.','recordCount':len(rows),'comparableRecords':sum(r['scoreComparable'] for r in rows),'conflictRecords':sum(not r['scoreComparable'] for r in rows),'directAndBoundaryFieldComparisons':field_count,'originalArchivesVerified':len(archives),'reusedSourceReferences':1,'failedAccessRecords':1,'publicFilesReviewed':len(public),'visualReview':['snnu-current.pdf page2 Guangxi merged cells and named majors','snnu-current.pdf page10 sports exclusions','njmu-old.pdf page19 Guangxi 2025 header','njucm-gx-2025.pdf page1 2025 filing header','bjut-old.pdf pages1-2 2025 header and Guangxi continuation'],'queryReview':neg,'frozenHashes':{f:sha(P/f) for f in ['major-cutoffs-upsert.json','sources.json','school-audit-notes.json','QA.json']},'sourceValueSamples':[{'major':r['major'],'score':r['score'],'sourceMaximumScore':r.get('sourceMaximumScore'),'sourceAverageScore':r.get('sourceAverageScore'),'scoreComparable':r['scoreComparable']} for r in rows],'blockingFindings':[],'checksPassed':sum(c['passed'] for c in checks),'checksTotal':len(checks),'checks':checks}
(HERE/'QA.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:result[k] for k in ['status','recordCount','directAndBoundaryFieldComparisons','originalArchivesVerified','checksPassed','checksTotal','frozenHashes']},ensure_ascii=False))
if result['status']!='passed':
 print(json.dumps([c for c in checks if not c['passed']],ensure_ascii=False));sys.exit(1)
