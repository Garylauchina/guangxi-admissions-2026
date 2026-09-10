"""Normalize the two official, publicly queried 2026 Guangxi ordinary plan responses."""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parent;RAW=R/'raw'
plans=[];sources=[];catalog=[];results=[]
def read(name):return json.loads((RAW/name).read_text())
def dump(name,value):(R/(name+'.json')).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
def source(key,title,file,entry,method):
 m=read(file+'.meta.json' if (RAW/(file+'.meta.json')).exists() else str(Path(file).with_suffix('.meta.json')));row={'id':key,'title':title,'url':entry,'publisher':title.split('2026')[0],'sourceType':'official','year':2026,'accessedAt':'2026-09-10','checkedAt':m['checkedAt'],'sha256':m['sha256'],'method':method,'requestUrl':m['url'],'requestData':m.get('requestData'),'recordCount':0}
 if m.get('archiveSha256'):row['archiveSha256']=m['archiveSha256'];row['redactedFields']=m['redactedFields']
 sources.append(row);return key
charter=source('top20-ustc-charter','中国科学技术大学2026年本科招生章程','ustc-charter.html','https://zsb.ustc.edu.cn/2026/0529/c35550a741990/page.htm','第十二条：所有招生专业物理、化学；第二十五条：4800元/学年。未给出分专业学制。')
for key,code,school,count,seats,kind in [('ustc','10358','中国科学技术大学',12,30,'普通本科'),('ruc','10002','中国人民大学',7,14,'本科一批')]:
 host='https://zsfw.ustc.edu.cn' if key=='ustc' else 'https://rdzs.ruc.edu.cn';entry=host+'/zsw/zsjh.html'
 j=read(key+'-gx-2026-normal.json');params=read(key+'-params-session.json')['data'];rows=j['data']['zsjhList'];total=j['data']['zsjhTotal']
 assert j['state']==1 and len(rows)==count and sum(int(r['zsjhs']) for r in rows)==seats
 assert len(total)==1 and total[0]['nf']=='2026' and total[0]['ssmc']=='广西' and total[0]['klmc']=='物理类' and total[0]['zsjhs']==seats
 assert not j['data']['withZyz'] and not params['withZyz']
 assert any(kind in x.get('广西_2026_物理类_sex_campus',[]) for x in params['ssmc_nf_klmc_sex_campus_zslx_list'])
 sid=source('top20-'+key+'-plans',school+'2026年广西物理类普通招生计划',key+'-gx-2026-normal.json',entry,'遵循公开页面的会话及CSRF查询流程，选择广西、2026、物理类、'+kind+'；核对分专业合计与总计。列表未列年的行按同响应汇总及查询条件确认年、科类；分类为非征集普通计划，不保证是第一发布版或省最终版，以省招办公布为准。正式广西组码为空，不能按唯一组或科目推断。')
 sources[-1]['recordCount']=count
 pid=source('top20-'+key+'-params',school+'2026招生计划查询条件',key+'-params-session.json',entry,'公开筛选条件列有广西_2026_物理类及'+kind+'，withZyz=false；原响应会话字段不公开。')
 for i,r in enumerate(rows,1):
  assert r['ssmc']=='广西' and r['zylx']==kind
  assert not any(r.get(x) for x in ['zyz','zyzdm','zyzname'])
  name=r['zymc'];included=r.get('bhzy') or ''
  plan={'id':'plan26-top20-'+hashlib.sha256((key+'|'+name+'|'+included).encode()).hexdigest()[:16], 'year':2026,'province':'广西','schoolCode':code,'school':school,'track':'物理','batch':r.get('zycc') or '本科（批次待核）','group':None,'major':name,'majorCode':None,'sourceMajorCode':r.get('zydh') or None,'includedMajors':included,'plannedCount':int(r['zsjhs']),'requiredSubjects':['化学'],'subjectRule':'all','requirementText':'物理+化学','tuition':4800 if key=='ustc' else int(r['zyxf']),'duration':r.get('zyxz') or None,'category':'普通类','planStage':'initial','planVersion':'2026高校公开普通招生计划（当前查询版；广西组码待核）','currentGaokaoSeatsKnown':True,'checkedAt':'2026-09-10','sourceId':sid,'sourceRow':i,'fieldSourceIds':{'schoolCode':['gxeea-2026-33107'],'includedMajors':[sid]},'groupMissingReason':'高校查询未公开广西正式专业组代码，不能直接匹配首轮组线。','note':'包含专业：'+included+'。以广西招办公布的计划及正式调整为准。广西正式组码待核；'+('原计划未注明广西批次及学制。'  if key=='ustc' else '高校原文类别：本科一批；原文广西批次：本科普通批。高校专业代号：'+str(r.get('zydh') or '未列')+'（填报专业代码待核）。')}
  if key=='ustc':plan['fieldSourceIds'].update(requiredSubjects=[charter],subjectRule=[charter],requirementText=[charter],tuition=[charter])
  else:assert r['nf']=='2026' and r['klmc']=='物理类' and r['xkkm']=='物+化' and r['zycc']=='本科普通批'
  plans.append(plan)
 note=f'本轮已收录官网2026年广西普通物理类{count}条分专业计划、{seats}人。高校未公开广西正式专业组代码，因此目标物理'+('101' if key=='ustc' else '102')+'组仍未补齐组内计划；可先查看该校已收录计划。'+('中科大同名试验班两行包含专业不同，分别保留；广西批次与学制待核。' if key=='ustc' else '招生人数、物理+化学、学费及学制已按原表收录。')
 catalog.append({'year':2026,'schoolCode':code,'school':school,'status':'collected','checkedAt':'2026-09-10','entryUrl':entry,'sourceIds':[sid,pid]+([charter] if key=='ustc' else []),'note':note})
 results.append({'cutoffId':'gx-2026-33107-'+code+'-'+('101' if key=='ustc' else '102'),'status':'source-found','checkedAt':'2026-09-10','sourceIds':[sid,pid]+([charter] if key=='ustc' else []),'checkedUrls':[entry],'note':note})
dump('plans-upsert',plans);dump('sources',sources);dump('source-catalog',catalog);dump('target-results',results)
dump('qa',{'status':'PASS','records':len(plans),'seats':sum(r['plannedCount'] for r in plans),'strictTargetMatches':0,'schoolCounts':[{'school':s,'records':sum(r['school']==s for r in plans),'seats':sum(r['plannedCount'] for r in plans if r['school']==s)} for s in dict.fromkeys(r['school'] for r in plans)]})
print('Root normalized:',len(plans),'plans /',sum(r['plannedCount'] for r in plans),'seats; zero strict group matches')
