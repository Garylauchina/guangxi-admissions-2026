# 9月12日第三批：6校专业分来源核查

新增首都医科大学6条、陕西师范大学2条，其中1条专业名称冲突退出分数比较。首医6条与本年广西完整专业菜单一致；陕师只有两条中外合作专业明确到专业，其他类别汇总和体育分不纳入。

[逐行统计事实](evidence-rows.json) · [来源与请求](source-manifest.json) · [缺口结论](school-audit-notes.json) · [83项检查](QA.json)

首医真实入口为[招生官网](https://zhsh.ccmu.edu.cn/) → [专业录取信息](https://zhsh.ccmu.edu.cn/page/detail/DEWVJI/1653/3627)。公开表单的xkkm在这里表示年制；人数、位次、专业组和轮次均未公开。按2026章程，高考实考分用于专业录取，政策加分只用于后续同分排序。

陕师[2026公告](https://zsb.snnu.edu.cn/info/1192/5432.htm)附件第2页广西区块，物理学（中外合作办学）517；原表电子信息技术（中外合作办学）563，与[章程](https://zsb.snnu.edu.cn/info/1235/5172.htm)的电子信息科学与技术名称不一致，原样保留并待核。没有用普通类/专项/公费师范类别汇总填充其下专业。

上海外国语新入口与陕西师范真实专业查询均取得本年两科普通类成功空结果，并有旧年正对照；南京医科、南京中医药、北京工业的当前附件明确是旧年。完整边界见逐校note，不代表全部发布渠道未公布。

## 复现

离线：在本目录执行 `python3 build.py`，依赖冻结事实及元数据，不访问官网。

重新获取：按编号运行 `python3 collect.py requests-1.json` 至 `requests-13.json`；分别运行 `python3 session_query.py session-requests-1.json` 和 `session-requests-2.json`。请求文件只含公开URL和统计查询参数。`freeze.py`需pdfplumber；原文下载及人工逐页复核后再执行freeze和build。重读可能获得变化后的数据，不应覆盖本次冻结证据后仍称本次已复核。

只发布PUBLIC-FILES所列文件；raw网页/脚本/图片/PDF及会话信息不入公开仓库。根目录代码来源文件仅复用现有广西考试院记录证明校码，未将组分转成专业分。
