from fetch import fetch
from public_api import PublicAPI
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
s=(Path(__file__).parent/'raw/uestc-lnfs.js').read_text()
assert all(k in s for k in ['sf:','nf:','zslb:','klmc:','xqmc:'])
def uestc(y,t):
 return fetch('uestc-gx-'+y+'-'+t+'.json','https://chaxun.uestc.edu.cn/lqxx/s/api/front/lqxx/getList',{'type':'lnfs','sf':'广西','nf':y,'zslb':'普通类','klmc':t,'xqmc':'电子科技大学'},'https://chaxun.uestc.edu.cn/public/zsdata/lqxx/','json')
def nankai():
 api=PublicAPI('https://lqcx.nankai.edu.cn','nankai')
 for y,t in [('2026','物理类'),('2026','历史类'),('2025','物理类')]:api.query('gx-'+y+'-'+t,'f/ajax_lnfs',{'ssmc':'广西','zsnf':y,'klmc':t,'zslx':'本科普通批'})
with ThreadPoolExecutor(max_workers=4) as p:
 jobs=[p.submit(uestc,y,t) for y,t in [('2026','物理类'),('2026','历史类'),('2025','物理类')]]+[p.submit(nankai)]
 for j in jobs:j.result()
