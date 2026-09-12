"""Independent read-only comparison of B3 OUC actual-major rows against official response archives."""
from pathlib import Path
import json,hashlib,re
from collections import Counter
BASE=Path(__file__).resolve().parent
PACKAGE=BASE.parent/'batch-b'
def load(f):return json.loads((PACKAGE/f).read_text())
def digest(f):return hashlib.sha256((PACKAGE/f).read_bytes()).hexdigest()
checks=[]
def check(name,ok):checks.append({'check':name,'passed':bool(ok)})
records=load('major-cutoffs-upsert.json');sources=load('sources.json');byid={s['id']:s for s in sources};metadata=[]
params=load('raw/ouc-params.json')
combos={}
for d in params['data']['ssmc_nf_klmc_sex_campus_zslx_list']:
 for k,v in d.items():
  if k.startswith('\u5e7f\u897f_2026_'):combos[k]=v
check('\u5f53\u5e74\u5e7f\u897f\u524d\u7aef\u914d\u7f6e\u4e1a\u52a1\u6210\u529f',params['state']==1)
check('\u5e7f\u897f\u672c\u5e74\u516c\u5f00\u7ec4\u54089\u9879',sum(map(len,combos.values()))==9)
raw_rows=[];excluded=[]
code_html=(PACKAGE/'raw/gx-code-source.html').read_text()
check('school-code direct official row',bool(re.search(r'10423</td><td[^>]*>\u4e2d\u56fd\u6d77\u6d0b\u5927\u5b66</td>',code_html)))
for n in range(1,10):
 key='ouc-gx-2026-'+str(n);body=load('raw/'+key+'.json');meta=load('raw/'+key+'.meta.json');query=meta['data'];source=byid['major-20260912b3-b-'+key]
 check(key+'\u8bf7\u6c42\u5e74\u4efd\u7701\u4efd',query['ssmc']=='\u5e7f\u897f' and query['zsnf']=='2026')
 ck='\u5e7f\u897f_2026_'+query['klmc']+'_sex_campus';check(key+'\u7ec4\u5408\u6765\u81ea\u672c\u5e74\u914d\u7f6e',query['zslx'] in combos.get(ck,[]))
 check(key+'HTTP\u548c\u4e1a\u52a1\u6210\u529f',meta['status']==200 and body['state']==1)
 check(key+'\u8bf7\u6c42\u6765\u6e90\u5143\u4fe1\u606f\u4e00\u81f4',source['requestParams']==query and source['httpStatus']==200 and source['url']==meta['url'])
 check(key+'\u6570\u7ec4\u660e\u786e\u4e13\u4e1a\u8868','sszygradeList' in body['data'] and isinstance(body['data']['sszygradeList'],list))
 for i,r in enumerate(body['data']['sszygradeList'],1):
  check(key+'\u884c'+str(i)+'\u7701\u5e74\u79d1\u7c7b',r['nf']=='2026' and r['ssmc']=='\u5e7f\u897f' and r['klmc']==query['klmc'])
  check(key+'\u884c'+str(i)+'\u7c7b\u522b',r['zslx']==r['zylx']==query['zslx'])
  identity=(source['id'],i)
  if '\u9884\u79d1' in r['zymc']:excluded.append({'sourceId':identity[0],'sourceRow':i,'major':r['zymc']});continue
  raw_rows.append((identity,r))
 aggregate=body['data']['zsSsgradeList']; detail=body['data']['sszygradeList']
 check(key+' source aggregate extrema',len(aggregate)==1 and min(x['minScore'] for x in detail)==aggregate[0]['minScore'] and max(x['maxScore'] for x in detail)==aggregate[0]['maxScore'])
 expected_count=sum(1 for r in body['data']['sszygradeList'] if '\u9884\u79d1' not in r['zymc'])
 check(key+'\u5b8c\u6574\u8303\u56f4\u5bfc\u5165',sum(x['sourceId']==source['id'] for x in records)==expected_count)
 metadata.append({'key':key,'track':query['klmc'],'category':query['zslx'],'rawMajorRows':len(body['data']['sszygradeList']),'includedMajorRows':expected_count,'requestParams':query,'archiveSha256':digest('raw/'+key+'.json')})
raw_map=dict(raw_rows);check('\u6e9060\u6761\u4e0e\u5bfc\u516560\u6761\u4e00\u4e00\u5bf9\u5e94',len(raw_map)==len(raw_rows)==len(records)==60 and len({(r['sourceId'],r['sourceRow']) for r in records})==60)
field_map={'major':'zymc','score':'minScore','sourceMaximumScore':'maxScore','sourceAverageScore':'avgScore','sourceCategory':'zslx','sourceTrack':'klmc'}
for record in records:
 identity=(record['sourceId'],record['sourceRow']);r=raw_map[identity];rid=record['id']
 for out,source in field_map.items():check(rid+'-'+out,record[out]==r[source])
 check(rid+'schema\u5e74\u4efd\u7701\u4efd\u5b66\u6821',record['year']==2026 and record['province']=='\u5e7f\u897f' and record['schoolCode']=='10423' and record['school']=='\u4e2d\u56fd\u6d77\u6d0b\u5927\u5b66')
 check(rid+'\u79d1\u7c7b\u51c6\u786e',record['track']==r['klmc'][:2])
 check(rid+'\u65e0\u539f\u8868\u4e0d\u5b58\u5728\u4eba\u6570\u4f4d\u6b21\u7ec4',record['group'] is None and record['rank'] is None and record['admittedCount'] is None and 'rs' not in r)
 check(rid+'\u7cbe\u786e\u6279\u6b21\u4e0e\u8f6e\u6b21\u672a\u77e5',not r.get('pcmc') and record['sourceBatch'] is None and record['round']=='\u5f55\u53d6\u6c47\u603b\uff08\u8f6e\u6b21\u672a\u5206\uff09')
 check(rid+'\u5206\u6570\u8303\u56f4\u548c\u5747\u503c',0<=r['minScore']<=r['avgScore']<=r['maxScore']<=750)
 check(rid+'\u539f\u59cb\u5b9e\u9645\u5206\u53ef\u6bd4',record['scoreComparable'] is True and record['scoreType']=='\u4e13\u4e1a\u5f55\u53d6\u6700\u4f4e\u5206' and record['scoreScaleMaximum']==750 and record['conflictFields']==[])
 check(rid+'\u6765\u6e90\u5b57\u6bb5\u95ed\u5408',set(record['sourceIds'])<=set(byid) and all(set(s)<=set(record['sourceIds']) for s in record['fieldSourceIds'].values()))
 if r['zslx']=='\u666e\u901a\u7c7b-\u63d0\u524d\u6279':check(rid+'\u63d0\u524d\u7c7b\u522b',record['admissionType']=='\u666e\u901a\u7c7b\uff08\u63d0\u524d\u6279\uff09' and record['batch']=='\u672c\u79d1\u63d0\u524d\u6279\uff08\u5177\u4f53\u6279\u6b21\u5f85\u6838\uff09')
 else:check(rid+'\u62db\u751f\u7c7b\u522b\u4fdd\u7559',record['admissionType']==r['zslx'])
 if '\u4e13\u9879' in r['zslx']:check(rid+'\u4e13\u9879\u8d44\u683c\u8bf4\u660e','\u8d44\u683c' in record['admissionRequirements'])
 if r['zslx']=='\u4e2d\u5916\u5408\u4f5c\u529e\u5b66':
  check(rid+'\u5408\u4f5c\u72ec\u7acb\u8d44\u683c\u4e0e\u82f1\u8bed\u5efa\u8bae','\u4e0d\u80fd\u8c03\u6574\u81f3\u975e\u4e2d\u5916\u5408\u4f5c' in record['admissionRequirements'] and '\u5efa\u8bae\u975e\u82f1\u8bed' in record['admissionRequirements'])
  check(rid+'\u5408\u4f5c\u76f4\u63a5\u9009\u79d1',record['requiredSubjects']==['\u5316\u5b66'] and record['subjectRule']=='all' and '\u7269\u7406\u3001\u5316\u5b66' in record['requirementText'])
  money={'\u8ba1\u7b97\u673a\u79d1\u5b66\u4e0e\u6280\u672f\uff08\u4e2d\u5916\u5408\u4f5c\u529e\u5b66\uff09':'70000','\u6d77\u6d0b\u79d1\u5b66\uff08\u4e2d\u5916\u5408\u4f5c\u529e\u5b66\uff09':'52000','\u7269\u7406\u5b66\uff08\u4e2d\u5916\u5408\u4f5c\u529e\u5b66\uff09':'75000'}[r['zymc']]
  check(rid+'\u5408\u4f5c\u5b66\u8d39\u4e0e\u4e13\u4e1a\u6a21\u5f0f',money in record['admissionRequirements'])
  if r['zymc']!='\u6d77\u6d0b\u79d1\u5b66\uff08\u4e2d\u5916\u5408\u4f5c\u529e\u5b66\uff09':check(rid+'\u7b2c\u56db\u5e74\u82f1\u56fd\u5fc5\u4fee','\u7b2c\u56db\u5e74\u987b\u8d74\u82f1\u56fd' in record['admissionRequirements'] and '\u6ce8\u518c\u8d39' in record['admissionRequirements'])
check('\u4e24\u6761\u9884\u79d1\u5747\u6392\u9664',len(excluded)==2 and not any('\u9884\u79d1' in r['major'] for r in records))
check('\u79d1\u7c7b46\u7269\u740614\u5386\u53f2',Counter(r['track'] for r in records)=={'\u7269\u7406':46,'\u5386\u53f2':14})
check('\u7c7b\u522b47\u666e\u901a1\u63d0\u524d7\u56fd\u5bb62\u9ad8\u68213\u5408\u4f5c',Counter(r['admissionType'] for r in records)=={'\u666e\u901a\u7c7b':47,'\u666e\u901a\u7c7b\uff08\u63d0\u524d\u6279\uff09':1,'\u56fd\u5bb6\u4e13\u9879\u8ba1\u5212':7,'\u9ad8\u6821\u4e13\u9879\u8ba1\u5212':2,'\u4e2d\u5916\u5408\u4f5c\u529e\u5b66':3})
# Direct table bindings and charter facts were read separately; retain concise replay checks.
html=(PACKAGE/'raw/ouc-scores.html').read_text();segment=html[html.index('id="sszygradeList"'):];segment=segment.split('</script>',1)[0]
for f in ['minScore','avgScore','maxScore','zymc','nf','klmc','zylx']:check('\u4e13\u4e1a\u8868\u5b57\u6bb5\u7ed1\u5b9a '+f,f in segment)
for h in ['\u6700\u4f4e\u5206','\u5e73\u5747\u5206','\u6700\u9ad8\u5206']:check('\u4e13\u4e1a\u8868\u5217\u540d '+h,h in segment)
charter=(PACKAGE/'raw/ouc-charter.html').read_text()
for word in ['2026\u5e74\u672c\u79d1\u62db\u751f\u7ae0\u7a0b','\u4e0d\u5f97\u8d85\u8fc720\u5206','\u542b\u653f\u7b56\u6027\u52a0\u5206','\u5176\u4ed6\u8bed\u79cd','\u4e0d\u80fd\u8c03\u6574\u81f3\u975e\u4e2d\u5916\u5408\u4f5c']:check('\u7ae0\u7a0b\u5173\u952e\u8bc1\u636e '+word,word in re.sub('<[^>]+>','',charter))
# Only review evidence relevant to OUC, including a read-only old-year control (never admitted as current).
archive_checks=[]
for source in sources:
 if '-ouc-' in source['id'] or source['id'].endswith('gx-code-source'):
  actual=digest(source['archiveFile']);expected=source.get('archiveSha256') or source['sha256'];check('\u539f\u6863hash '+source['id'],actual==expected)
  archive_checks.append({'id':source['id'],'archiveSha256':actual})
for key in ['ouc-gx-2025-physics','ouc-gx-2025-history']:
 body=load('raw/'+key+'.json');rr=body['data']['sszygradeList'];check(key+'\u65e7\u5e74\u5bf9\u7167\u672a\u5165\u5f53\u5e74',all(r['nf']=='2025' for r in rr) and not any(r['sourceId'].endswith(key) for r in records))
public_count=0
manifest=PACKAGE/'PUBLIC-FILES.json'
if manifest.exists():
 allow=json.loads(manifest.read_text());allow=allow['files'] if isinstance(allow,dict) else allow
 for file in allow:
  file=file['path'] if isinstance(file,dict) else file
  content=(PACKAGE/file).read_text();public_count+=1
  check('\u767d\u540d\u5355\u6587\u4ef6\u8def\u5f84\u5b89\u5168 '+file,not file.startswith('raw/') and not re.search(r'/(?:Users|private|var/folders)/[A-Za-z0-9_.-]+/',content))
  check('\u767d\u540d\u5355\u65e0\u4f1a\u8bdd\u5e38\u91cf '+file,not re.search(r'"(?:jessionid|poc_token|cap_sid)"\s*:\s*"[^"\s]+"',content,re.I))
else:check('\u6700\u7ec8\u516c\u5f00\u767d\u540d\u5355\u5b58\u5728',False)
result={'status':'PASS' if all(c['passed'] for c in checks) else 'NEEDS-REVIEW','reviewedAt':'2026-09-12','scope':'\u72ec\u7acb\u53ea\u8bfb\u6838\u67e5B3\u4e2d\u56fd\u6d77\u6d0b\u5927\u5b6660\u6761\u5b9e\u9645\u4e13\u4e1a\u5206\u30019\u7ec4\u5408\u8bf7\u6c42\u30012\u9884\u79d1\u6392\u9664\u3001\u914d\u5957\u7ae0\u7a0b/\u5408\u4f5c\u8981\u6c42\u53ca\u767d\u540d\u5355\uff1b\u672a\u590d\u6838B\u5176\u4ed66\u6821\u8d1f\u9762\u7ed3\u8bba\u3002','records':60,'numericFieldsCompared':180,'sourceFieldsCompared':360,'sourceArchivesCompared':len(archive_checks),'sourceArchiveHashes':archive_checks,'queryCoverage':metadata,'excluded':excluded,'publicFilesChecked':public_count,'inputHashes':{f:digest(f) for f in ['major-cutoffs-upsert.json','sources.json','school-audit-notes.json']},'checked':len(checks),'passed':sum(c['passed'] for c in checks),'failed':sum(not c['passed'] for c in checks),'checks':checks,'manualReview':'\u5df2\u5b8c\u6574\u9605\u8bfb\u672c\u8f6e\u5f52\u6863\u62db\u751f\u7ae0\u7a0b\u4e0e\u5408\u4f5c\u9879\u76ee\u4ecb\u7ecd\uff1b\u4fdd\u7559\u82f1\u8bed\u5efa\u8bae\u3001\u539f\u5219\u4e0a\u4e0d\u5f55\u53d6\u7684\u8272\u89c9\u6761\u4ef6\u3001\u4e13\u9879\u8d44\u683c\u3001\u5408\u4f5c\u4e09\u4e13\u4e1a\u5b66\u8d39/\u57f9\u517b\u6a21\u5f0f/\u7b2c\u56db\u5e74\u8d74\u82f1\u6761\u4ef6\uff0c\u4e0d\u5c06\u5efa\u8bae\u6539\u6210\u786c\u7981\u3002\u516c\u5f00\u8868\u6570\u5b57\u5b57\u6bb5\u4e3a\u4e13\u4e1a\u6700\u4f4e/\u5e73\u5747/\u6700\u9ad8\uff0c\u7701\u7ea7\u6c47\u603b\u53e6\u8868\u672a\u62c6\u3002'}
(BASE/'QA.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:result[k] for k in ['status','records','checked','passed','failed','publicFilesChecked','inputHashes']},ensure_ascii=False))
for c in checks:
 if not c['passed']:print(c)
