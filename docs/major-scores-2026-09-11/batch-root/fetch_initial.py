from fetch import fetch
from concurrent.futures import ThreadPoolExecutor
JOBS=[('scut-plan-entry.html','https://admission.scut.edu.cn/30820/list.htm'),('uestc-home.html','https://zs.uestc.edu.cn/'),('cqu-home.html','https://zhaosheng.cqu.edu.cn/'),('ncepu-home.html','https://goto.ncepu.edu.cn/'),('nankai-home.html','https://zsb.nankai.edu.cn/'),('cpu-home.html','https://zb.cpu.edu.cn/mainm.htm'),('cpu-score-entry.html','https://zb.cpu.edu.cn/fs/listm40.psp')]
with ThreadPoolExecutor(max_workers=4) as p:list(p.map(lambda j:fetch(*j),JOBS))
