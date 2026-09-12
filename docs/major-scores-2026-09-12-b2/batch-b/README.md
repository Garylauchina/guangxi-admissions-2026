# 2026-09-12 第二批：七校专业实际录取分核查

本包核查指定七校，**新增实际专业录取分 0 条**，新增 7 条有来源的学校核查记录。空结果没有转成 0 分；旧年分数、专业组线、预科和名单没有转成本年专业记录。未修改网站或 Git。

| 学校 | 已核实结果 | 正对照及限制 |
|---|---|---|
| 中国传媒大学 10033 | [官方分数查询](https://zszx.cuc.edu.cn/static/front/cuc/basic/html_web/lnfs.html)广西菜单最新 2025；2026 两科普通类及类别留空查询均成功空表。 | 2025 广西物理普通类有 15 条专业记录。未混海南办学或艺术校考数据。 |
| 江南大学 10295 | [官方分数前端](http://admission1.jiangnan.edu.cn/pc/historyScore/nonArt)公开 RSA-CSRF 流程已跑通；年份仅 2025/2024/2023，2026 省份及科类菜单为空。 | 使用已核实的广西、两科和类别 ID 查询 2026，六组请求成功空表；2025 物理 9 条、历史 1 条专业正对照。 |
| 兰州大学 10730 | [官网首页](https://zsb.lzu.edu.cn/index.html)可读，但其链接的分数入口在本轮无法取得页面。 | HTTPS、HTTP、curl 均失败；网页读取工具返回 412，无可用浏览器备用。没有菜单或旧年正对照，不计作成功空表。 |
| 香港城市大学(东莞) 14851 | [本科招生公开信息](https://uga.cityu-dg.edu.cn/public-information)、政策和问答已读；2026 章程直接核实独立校码。 | 分数问答仅概述 2025 成绩，公开目录旧年录取名单不读取个人内容；未取得 2026 广西专业最低分。 |
| 北京化工大学 10010 | [官方分数查询](https://goto.buct.edu.cn/static/front/buct/basic/html_web/lnfs.html)广西菜单最新 2025；2026 两科普通类均成功空表。 | 2025 物理 16 条、历史 2 条专业正对照。 |
| 中央财经大学 10034 | [官方分数查询](https://zs.cufe.edu.cn/static/front/cufe/basic/html_web/lnfs.html)广西菜单最新 2025；2026 两科统招及类别留空查询均成功空表。 | 2025 物理 13 条、历史 8 条专业正对照。 |
| 广州医科大学 10570 | [外省分数目录](https://zs.gzhmu.edu.cn/wnlqfs/lnfs_ws_/a2025n.htm)和原图均明确 2025 年。 | 全图目视确认广西物理临床医学 614、临床药学 596 两条为旧年分，未采进 2026。 |

统计为 **4 校本年查询成功空表、2 校所读材料仅有旧年分数或概述、1 校分数入口访问受限**。这些结论只涵盖列明入口和实际请求，不断言学校所有渠道都没有发布，也不代表不招生。江南前几次缺公开 CSRF 或 Content-Type 不符产生的业务错误保留在本地证据及来源记录中，最终正常请求已成功，不能把先前错误算作无数据。

江南的本年省份菜单为空，诊断请求使用的是旧年菜单中直接核实的广西 ID 20、物理 ID 3、历史 ID 2 和类别 ID，明确发送 year=2026，并记录参数配置来自 2025。这是受限空结果验证，不是声称本年类别配置存在。两条预科组合只用来检验公开入口，不能生成普通专业分。

## 文件与检查

- `major-cutoffs-upsert.json`：空数组，未增加未经证实的分数。
- `sources.json`：73 条本轮来源或访问尝试，原响应 SHA256 与脱敏归档 SHA256 分开；69 份有内容归档、4 次传输失败。HTTP 200 与业务成功分开记录。
- `school-audit-notes.json`：7 校记录，保留原入口、实际查询 URL、来源、参数结果与限制类型；记录 ID 使用本批 `20260912b2-b` 标识。
- `QA.json`：108 项检查通过。`verification.json`：另读原始响应和来源哈希的 101 项检查通过。
- `audit-context.json`：固定实际审核时间，静态重建不会变成运行当天，也不会把旧结论自动刷新。
- `additional-access-evidence.json`：工具侧兰大入口失败和无浏览器的补充记录；它不伪造为已取得的官网原文。

原始页面、图片、JSON 及请求元数据均在 `raw/` 留本地。公开只使用白名单文件，不发布原文中的公开联系电话、名单或任何会话值。查询仅走官网公开前端流程，没有使用考生姓名、证件或个人账户。

## 复现

静态重建和校验仅需 Python 3 标准库，在本目录执行：

```sh
python3 build.py
python3 verify.py
```

重新采集需要网络，并须依次阅读实际前端条件。已固定的请求清单按编号重放：

```sh
python3 collect.py requests.json
python3 collect.py requests-2.json
python3 collect.py requests-3.json
python3 collect.py requests-4.json
python3 collect.py requests-5.json
python3 collect.py requests-6.json
python3 collect.py requests-7.json
python3 collect.py requests-8.json
python3 session_query.py session-requests.json
python3 session_query.py session-requests-2.json
python3 session_query.py session-requests-3.json
python3 session_query.py session-requests-4.json
python3 session_query.py session-requests-5.json
python3 jnu_query.py jnu-requests.json
python3 jnu_query.py jnu-requests-2.json
python3 jnu_query.py jnu-requests-3.json
python3 jnu_query.py jnu-requests-4.json
python3 jnu_query.py jnu-requests-5.json
python3 jnu_query.py jnu-requests-6.json
python3 retry_transport.py
```

江南脚本另需 `cryptography`，兰大备用传输需 `curl`；没有私人绝对路径。公开前端的 RSA 公钥和固定待加密串由脚本从本地原始 app.js 读取；生成的 CSRF 请求头只在内存中，不保存。中传、北化、中财的 Cookie 与 CSRF 同样仅在内存中。若线上版本变化，先重新审阅前端和参数，不可猜 ID 或只改审核日期继续沿用结论。

本包基线为提交 `5e742e9296767c0abec242531549f5c884cdb4b9`：1058 条实际录取记录、26 校。本包并非网站页面验证报告。
