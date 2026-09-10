from fetch import fetch
from concurrent.futures import ThreadPoolExecutor
JOBS=[('scut-score-entry.html','https://admission.scut.edu.cn/30821/list.htm'),('scut-current-min.html','https://admission.scut.edu.cn/lqzdfstj/list.htm'),('uestc-query.html','https://chaxun.uestc.edu.cn/public/zsdata/lqxx/'),('cqu-score-entry.html','https://zhaosheng.cqu.edu.cn/pub/desktopend/queryadmitline'),('ncepu-score-entry.html','https://goto.ncepu.edu.cn/wnfs/index.htm'),('nankai-score-entry.html','https://zsb.nankai.edu.cn/Baokao/fenshu.html'),('cpu-score-page.html','https://zb.cpu.edu.cn/fs/listm.htm'),('cpu-score-query.js','https://zb.cpu.edu.cn/_upload/tpl/03/37/823/template823/search_lqfs.js')]
with ThreadPoolExecutor(max_workers=4) as p:list(p.map(lambda j:fetch(*j),JOBS))
