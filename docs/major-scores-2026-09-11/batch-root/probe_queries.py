from fetch import fetch
from concurrent.futures import ThreadPoolExecutor
import json,urllib.parse
JOBS=[]
for y in ['2026','2025']:
 JOBS.append(('cqu-config-'+y+'.json','https://zhaosheng.cqu.edu.cn/pub/share/getQueryConditionByAdmitLine',{'year':y}))
 fields=['f1','f2','f3','f4','f5','f6','f7','f10','f9']
 data={'siteId':225,'columnId':10209,'pageIndex':1,'rows':14,'orders':'[]','returnInfos':json.dumps([{'name':f} for f in fields]),'conditions':json.dumps([{'orConditions':[{'field':'f8','value':'广西','judge':'='}]},{'orConditions':[{'field':'f7','value':y,'judge':'='}]}],ensure_ascii=False)}
 JOBS.append(('cpu-gx-'+y+'.json','https://zb.cpu.edu.cn/_wp3services/generalQuery?queryObj=articles',data,'https://zb.cpu.edu.cn/fs/listm.htm'))
 for track in ['理工/物理类','文史/历史类']:
  data={'cq16s188':y,'cq16s189':'广西','cq16s190':'普通类','cq16s191':track}
  JOBS.append(('scut-gx-'+y+'-'+track.split('/')[1]+'.html','https://admission.scut.edu.cn/_web/_apps/commonquery/commonquery/api/commonqueryCacheResult/16.rst?_p=YXM9MzQ4JnQ9MTcyMyZwPTEmbT1OJg__&mobileTemplate=false',data))
JOBS.append(('uestc-score-types.json','https://chaxun.uestc.edu.cn/lqxx/s/api/front/lqxx/getType',{'type':'lnfs'},'https://chaxun.uestc.edu.cn/public/zsdata/lqxx/','json'))
with ThreadPoolExecutor(max_workers=4) as p:list(p.map(lambda j:fetch(*j),JOBS))
