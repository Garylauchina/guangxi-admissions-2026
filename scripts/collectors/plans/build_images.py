"""Image-based public plan transcription with displayed aggregate checks; no OCR assumptions."""
from pathlib import Path
exec((Path(__file__).parent/'build.py').read_text().split("s=source('gxnu_plan'")[0])
d=json.load(open(BASE/'gxtcm-transcription-2026.json'))
parent='https://www.gxtcmu.edu.cn/zs/zsjh/content_87929'
for key,which in [('gxtcm_plan_img_1','firstImage'),('gxtcm_plan_img_2','secondImage')]:
 s=source(key,'广西中医药大学','2026-06-18',method='逐图手工核读2026分省表广西列，包含预科直升，不能等同普通高考可报总数。两张本科表2470人对账通过。');s['landingUrl']=parent
 for i,r in enumerate(d[which]):
  cats='国家专项计划' if '国家专项' in r[0] else '地方专项计划' if '地方专项' in r[0] else '民族班' if '民族班' in r[0] else '定向医学生' if '定向医学生' in r[0] else '公布计划（含预科直升）'
  combos=[('历史',r[3]),('物理',r[4])] if which=='firstImage' else [('物理',r[3])]
  for tr,n in combos:
   req=tr+'（1门科目必须选考）' if which=='firstImage' else '物理、化学（2门科目均须选考）'
   add(s,'10600','广西中医药大学',tr,r[0],n,batch='本科批次待核',majorCode=r[1],duration=r[2],req=req,category=cats,note='官网注明：广西计划数包含预科直升计划。本表未拆分直升人数，不能作为普通统考实际可填计划数；专业组和批次未列。',rawId=f'{i}-{tr}')
 if which=='secondImage':
  r=d['secondImageOther'][0]
  for tr,n in [('历史',r[3]),('物理',r[4])]:add(s,'10600','广西中医药大学',tr,r[0],n,batch='本科批次待核',majorCode=r[1],duration=r[2],req=tr+'（1门科目必须选考）',category='公布计划（含预科直升）',note='官网注明广西计划数包含预科直升；未拆分，组码和批次未列。',rawId=tr)
assert sum(r['plannedCount'] for r in plans)==2470
checks.append({'school':'广西中医药大学','sumCount':2470,'sourceTotal':2470,'scope':'两张本科图片广西列合计；包含官网说明的预科直升，不用于预测普通高考可填余额。'})
s=source('gxtcm_plan_img_3','广西中医药大学','2026-06-18',method='官方预科表广西历史/物理四行逐图核读，合计132。');s['landingUrl']=parent
for i,r in enumerate(d['prepImage']):
 for tr,n in [('历史',r[1]),('物理',r[2])]:add(s,'10600','广西中医药大学',tr,r[0],n,batch='预科批次待核',duration='1',req=tr+'（1门科目必须选考）' if tr=='历史' else '物理、化学（2门科目均须选考）',category='预科A类' if i==0 else '预科B类',note='原表未列具体批次或专业组。',rawId=f'{i}-{tr}')
s=source('gxtcm_plan_img_5','广西中医药大学','2026-06-18',method='官网正文明确2026年高职分专业招生计划表(广西)；逐图核读合计400。');s['landingUrl']=parent
for i,(ma,code,tr,count,req) in enumerate([('针灸推拿','520403K','历史',54,'历史（1门科目必须选考）'),('针灸推拿','520403K','物理',126,'物理（1门科目必须选考）'),('中药学','520410','物理',70,'物理、化学（2门科目均须选考）'),('药学','520301','物理',70,'物理、化学（2门科目均须选考）'),('护理','520201','物理',80,'物理、化学（2门科目均须选考）')]):add(s,'10600','广西中医药大学',tr,ma,count,batch='高职高专批次待核',majorCode=code,duration='3',req=req,note='官网正文注明广西；图表未列批次、专业组和学费。',rawId=i)
checks.append({'sourceId':s['id'],'sumCount':400,'sourceTotal':400})
# The complete Baise matrix is publicly archived, but only unambiguously single-stream rows are transcribed.
bs=json.load(open(BASE/'bsuc-transcription-2026.json'))
s=source('bsuc_plan_img','百色学院','2026-06-23',method='逐图核读2026分省表，仅单一科类专业；分广西普通类/精准专项/民族班，不含预科直升。历史+物理合计专业未擅自拆分。');s['landingUrl']='https://zs.bsuc.edu.cn/info/1043/3270.htm'
for i,r in enumerate(bs['rows']):
 ma,tr,normal,special,ethnic,fee=r
 for cat,n in [('地方公费师范生' if '公费师范生' in ma else '普通类',normal),('精准专项',special),('民族班',ethnic)]:add(s,'10609','百色学院',tr,ma,n,batch='本科批次待核',tuition=fee,category=cat,note='2026分省表广西对应类别列；不含预科直升；批次、组码、再选科目未列。',rawId=f'{i}-{cat}')
checks.append({'sourceId':s['id'],'selectedMajorRows':len(bs['rows']),'excluded':'未拆分历史+物理的合计专业、艺术体育、预科直升及预科混合科类'})
(BASE/'supplement-images.json').write_text(json.dumps({'plans':plans,'sources':sources,'checks':checks},ensure_ascii=False,indent=2))
print(len(plans),len(sources))
