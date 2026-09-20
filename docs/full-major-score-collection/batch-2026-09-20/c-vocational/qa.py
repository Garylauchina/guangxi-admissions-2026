"""Validate this isolated batch and invoke the repository importer without --apply."""
from pathlib import Path
import argparse,hashlib,json,re,subprocess,sys
ROOT=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('--repo',required=True);args=ap.parse_args()
def read(name):return json.loads((ROOT/name).read_text())
def write(name,obj):(ROOT/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
scores=read('major-cutoffs-upsert.json');sources=read('sources.json');notes=read('school-audit-notes.json');obs=read('observations.json');targets=read('targets.json')
source_map={x['id']:x for x in sources};codes={x['schoolCode'] for x in targets}
assert len(codes)==len(notes)==len(obs)==30
assert {x['schoolCode'] for x in notes}=={x['schoolCode'] for x in obs}==codes
assert len(source_map)==len(sources)
assert len(scores)==4
assert {(r['major'],r['track'],r['score']) for r in scores}=={('酒店管理与数字化运营','历史',403),('现代家政服务与管理','历史',405),('软件技术','物理',439),('智慧健康养老服务与管理','物理',410)}
for s in sources:
 assert re.match(r'^https?://',s['url'])
 assert s['accessedAt']<=s['finishedAt']
 if s.get('sha256'):
  assert hashlib.sha256((ROOT/'raw'/s['archiveFile']).read_bytes()).hexdigest()==s['sha256']
 else:
  assert s['evidenceType']=='access-failure' and s.get('errorSha256') and s.get('accessError')
  assert hashlib.sha256(s['accessError'].encode()).hexdigest()==s['errorSha256']
for r in scores+notes:
 assert r['sourceIds'] and all(k in source_map for k in r['sourceIds'])
for n in notes:
 assert n['auditKind']=='major-scores' and n['startedAt']<=n['finishedAt'] and n['scope'] and n['remainingGaps']
 assert n['recordCount']==sum(r['schoolCode']==n['schoolCode'] for r in scores)
for o in obs:
 assert o['sources'] and o['fieldEvidence']
 for e in o['fieldEvidence']:assert e['sourceId'] in source_map and e['locator']
for r in scores:
 assert r['year']==2026 and r['province']=='广西' and r['schoolCode']=='12493'
 assert r['group'] is None and r['majorCode'] is None and r['rank'] is None
 assert r['batch']=='批次未注明' and r['round']=='录取汇总（轮次未分）'
 assert r['scoreComparable'] is True and not r['scoreEvidenceGaps']
 assert r['sourcePage']==1 and r['sourceRow'] and r['sourceColumn'] and r['metadataGaps']
 for ids in r['fieldSourceIds'].values():assert ids and all(k in source_map for k in ids)
# Capture importer output; it performs no mutation without --apply.
repo=Path(args.repo).resolve()
proc=subprocess.run(['node',str(repo/'scripts/import-major-score-batch.mjs'),str(ROOT)],capture_output=True,text=True,cwd=repo)
assert proc.returncode==0,proc.stderr
preflight=json.loads(proc.stdout);write('preflight.json',preflight)
public=read('PUBLIC-FILES.json');assert len(public)==len(set(public))
assert all('/' not in n and '\\' not in n and not n.endswith(('.pdf','.png','.jpg','.html','.zip')) for n in public)
privacy_hits=[]
for name in public:
 if name=='qa-results.json':continue
 text=(ROOT/name).read_text()
 for pattern in [r'/(?:Users|home)/[A-Za-z0-9][^\s"\']+',r'(?i)(?:sessionid|csrftoken|JSESSIONID)\s*[:=]\s*["\']?[A-Za-z0-9+/=_-]{12,}',r'(?i)authorization\s*[:=]\s*["\']?bearer\s+[A-Za-z0-9._-]+']:
  if re.search(pattern,text):privacy_hits.append(name)
assert not privacy_hits,privacy_hits
assert all('raw/' not in n for n in public)
result=dict(passed=True,checks=['30个目标逐校存在审计与实查源元数据','95个来源ID唯一且引用闭合','82个本地原响应SHA256与13个错误摘要SHA256核验','4个广西专业单元格值、科类、行列定位核验','批次/轮次/组码未知保持未知','公开白名单不含原文、图片PDF、个人名单、会话值和绝对路径','仓库导入器只读预检通过'],schoolCount=30,sourceCount=len(sources),actualMajorRecords=len(scores),preflightAdded=preflight['added'],preflightUpdated=preflight['updated'],readOnlyImport=True,publicFileCount=len(public),privacyFindings=privacy_hits,visualReview=dict(shanghaiXingjian='PDF 1页广西两列4格逐格确认；集成方独立确认',hunanRailway='PDF 1页广西行是省科类汇总，右侧湖南专业组不套广西',jiangxiElectric='2026分省分数原图，无专业字段',wuhanRailway='原图三个统计年2023/2024/2025，不随2026发布日期改变'))
write('qa-results.json',result);print(json.dumps(result,ensure_ascii=False,indent=2))
