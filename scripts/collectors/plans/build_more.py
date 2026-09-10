from pathlib import Path
exec((Path(__file__).parent/'build.py').read_text().split("s=source('gxnu_plan'")[0])
for key in ['gxu_plan_0','gxu_plan_1']:
 s=source(key,'广西大学','2026-06-22');d=load(key)['data'];rs=d['dataSource'];assert all(r['year']=='2026' and r['province']=='45' for r in rs)
 checks.append({'sourceId':s['id'],'rowCount':len(rs),'sumCount':sum(int(r['jhsgf']) for r in rs),'sourceTotal':sum(int(r['jhsgf']) for r in d['overview'])})
 for r in rs:add(s,'10593','广西大学',track(r['subjects']),r['major']+('（'+r['exam_direction']+'）' if r['exam_direction'] else ''),r['jhsgf'],batch=r['batch'],group=r['major_group'],majorCode=r['major_num'] or r['major_code'],req=r['kskmyqzwgf'],tuition=r['fee_standard'],duration=r['educational_code'],category=r['plan_type'] if r['plan_nature']=='非定向' else r['plan_nature'],note='；'.join(str(r.get(k,'')) for k in ['major_remark','school_location','wyyzgf','remark'] if r.get(k)),rawId=r['id'])
s=source('ylu_plan','玉林师范学院','2026-06-23',method='官网2026广西计划表：按普通、精准专项、民族班及历史/物理独立列提取；不混入预科直升。选科要求从同页表按专业名称精确关联')
t=load('ylu_plan.tables');reqs={r[0]:r[1:] for r in t[3][1:]};omit=[]
for i,r in enumerate(t[0][1:]):
 if r[3] in ['艺术类','体育类']:omit.append(r[2]);continue
 rr=reqs.get(r[2],['',''])
 for col,tr,cat in [(4,'历史','普通类'),(5,'物理','普通类'),(6,'历史','精准专项'),(7,'物理','精准专项'),(8,'历史','民族班'),(9,'物理','民族班')]:
  add(s,'10606','玉林师范学院',tr,r[2],r[col],majorCode=r[1],req=rr[0],note='；'.join(x for x in [r[3],rr[1]] if x),category=cat,rawId=f'{i}-{col}')
checks.append({'sourceId':s['id'],'omittedTypes':'艺术体育及预科直升','omittedMajors':omit,'sourceTableRows':len(t[0])-1})
# North Gulf public matrix separates single-stream majors only; combined 文史理工 not duplicated.
s=source('bbgu_plan_pdf','北部湾大学','2026-06-18',method='校方2026分省计划PDF的区内计划数列；只纳入招生科类单一的理工或文史专业。文史理工合计未拆分，不擅自分配。学费列明确参照2025标准。')
tables=load('bbgu_plan_pdf.tables');om=[]
for pi,page in enumerate(tables):
 for ti,t in enumerate(page):
  for i,r in enumerate(t):
   if len(r)!=33 or r[1]!='本科':continue
   if r[-2] not in ['理工类','文史类']:
    om.append(r[0]);continue
   tr='物理' if r[-2]=='理工类' else '历史';cat='地方公费师范生' if '公费师范' in r[0] else '中外合作办学' if '中外合作' in r[0] else '分省计划汇总（专项未拆分）'
   # Province matrix does not state batch; retain an explicit unknown instead of guessing.
   batch='本科批次待核'
   add(s,'11607','北部湾大学',tr,r[0],r[4],batch=batch,tuition=r[-1],category=cat,note=f'区内计划数；PDF第{pi+1}页。科类原文：{r[-2]}。学费原文注明为2025年标准，仅参考；组码/再选要求未列。计划可能含专项但本表未拆分。',rawId=f'{pi}-{ti}-{i}')
checks.append({'sourceId':s['id'],'omittedCombinedStreams':om})
# GXMU interface explicitly has province/year/stream and level, but no batch or group.
for key in ['gxmu_plan_0','gxmu_plan_1']:
 s=source(key,'广西医科大学',method='官方计划页面链接的公开查询接口；年度2026、省份45独立校验。原接口未给批次/组码，保留待核。含高职专科。')
 d=load(key)['data'];rs=d['dataSource'];assert all(r['year']=='2026' and r['province']=='45' for r in rs)
 checks.append({'sourceId':s['id'],'rowCount':len(rs),'sumCount':sum(int(r['jhsgf']) for r in rs),'sourceTotal':sum(int(r['jhsgf']) for r in d['overview'])})
 for r in rs:
  batch=r['batch'] or ('高职高专批次待核' if r['level']=='高职(专科)' else '本科批次待核')
  add(s,'10598','广西医科大学',track(r['subjects']),r['major'],r['jhsgf'],batch=batch,group=r['major_group'],majorCode=r['major_num'] or r['major_code'],req=r['kskmyqzwgf'],tuition=r['fee_standard'],duration=r['educational_code'],category=r['plan_type'] or r['level'],note='；'.join(str(r.get(k,'')) for k in ['major_remark','school_location','wyyzgf','remark'] if r.get(k))+'；层次：'+r['level']+'；接口未公布批次、组码与选科要求。',rawId=r['id'])
s=source('gxnun_plan','广西民族师范学院','2026-06-13',method='官方2026分省计划HTML展开rowspan/colspan后，提取广西历史与物理两列；保留普通/专项/民族班/公费师范分类。不混入艺术体育。原表未给批次与组码。')
t=load('gxnun_plan.expanded-0');assert t[0][6:8]==['广西','广西'] and t[1][6:8]==['历史','物理']
assert sum(int(r[x] or 0) for r in t[2:78] for x in (6,7))==int(t[78][6])
checks.append({'sourceId':s['id'],'sumCount':sum(int(r[x] or 0) for r in t[2:78] for x in (6,7)),'sourceTotal':int(t[78][6]),'scope':'全表广西3065含艺术体育；本站提取普通历史/物理，不混入艺术体育。'})
for i,r in enumerate(t[2:78]):
 if r[1] in ['艺术学院','体育学院']:continue
 for col,tr in [(6,'历史'),(7,'物理')]:
  add(s,'10604','广西民族师范学院',tr,r[3],r[col],batch='本科批次待核',majorCode=r[2],tuition=r[31],duration=r[0],category=r[30] or '普通类',note='；'.join(x for x in [r[1],'师范类' if r[4]=='是' else '',r[30],'原分省计划表未列批次、专业组或选科要求。'] if x),rawId=f'{i}-{col}')
for key in ['gxufe_plan_0','gxufe_plan_1','gxufe_plan_2','gxufe_plan_3']:
 s=source(key,'广西财经学院','2026-06-18',method='官方招生网2026更新的计划链接公开查询；参数及返回数据均独立限定2026和广西。')
 d=load(key)['data'];rs=d['dataSource'];assert all(r['year']=='2026' and r['province']=='45' for r in rs)
 checks.append({'sourceId':s['id'],'rowCount':len(rs),'sumCount':sum(int(r['jhsgf']) for r in rs),'sourceTotal':sum(int(r['jhsgf']) for r in d['overview'])})
 for r in rs:
  add(s,'11548','广西财经学院',track(r['subjects']),r['major']+('（'+r['exam_direction']+'）' if r['exam_direction'] else ''),r['jhsgf'],batch=r['batch'] or '本科批次待核',group=r['major_group'],majorCode=r['major_num'] or r['major_code'],req=r['kskmyqzwgf'],tuition=r['fee_standard'],duration=r['educational_code'],category=r['plan_type'] or '普通类',note='；'.join(str(r.get(k,'')) for k in ['major_remark','school_location','wyyzgf','remark'] if r.get(k)),rawId=r['id'])
s=source('gxgc_plan','广西工程职业学院','2026-06-23',method='官方2026广西普通高考分专业计划HTML，批次、科类、代码、人数逐列提取；艺术体育未混入普通科类。')
t=load('gxgc_plan.expanded-0');assert t[0][0]=='省份' and all(r[0]=='广西' and r[1]=='14127' for r in t[1:-1])
for i,r in enumerate(t[1:-1]):add(s,r[1],'广西工程职业学院',track(r[5]),r[3],r[9],batch=r[4],majorCode=r[2],tuition=r[8],duration=r[7],category=r[6],note=r[10] or '',rawId=i)
for c in checks:
 if 'sourceTotal' in c:assert c['sumCount']==c['sourceTotal']
(BASE/'supplement-fresh-more.json').write_text(json.dumps({'plans':plans,'sources':sources,'checks':checks},ensure_ascii=False,indent=2))
print(len(plans),len(sources))
