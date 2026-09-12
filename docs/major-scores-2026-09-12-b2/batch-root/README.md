# 对外经贸30条专业录取分及另外5校缺口核查

核查日期：2026-09-12（北京时间，同日第二批）。纳入对外经济贸易大学30条广西专业/正式大类实际最低分，历史16、物理14，对应83名实际录取。均附学校专业表直接公布的最低分排名；专业组和轮次未公开，保持未知。另2行少数民族预科汇总排除。

[官方历年分数查询](https://aeo.uibe.edu.cn/lqcx/static/front/uibe/basic/html_web/lnfs.html) · [2026招生章程](https://aeo.uibe.edu.cn/front/showContent.jspa?contentId=109396) · [逐条增量](major-cutoffs-upsert.json) · [六校审查](school-audit-notes.json) · [QA](QA.json)

本科批18、提前批4、国家专项4、高校专项2、中外合作2。原名称的选拔项目及分流说明保留；达到专业分不等于取得选拔项目资格。章程认可规定的全国性政策加分，按投档成绩录取至专业；语言类英语要求、专项资格、合作专业志愿与转专业限制及保险学10万元/学年学费单列。

华南师范、广东工业、浙江大学医学院本轮所读材料仍是旧年或汇总；山东大学威海分校4组正确GET和苏州大学当前查询没有专业表，均有2025正对照。威海最初POST中文乱码的失败结果不作为有效空表。苏大参数自动生成的2026标题不代表已发布2026分数。逐校范围见审查JSON，不认定全渠道均未发布。

## 离线重建

仅复制公开白名单即可在任何目录重建。冻结的统计事实不包含原网页、PDF、完整接口响应或会话值。

```sh
python3 build.py
```

`evidence-rows.json` 保存专业统计事实及来源行号，`review-evidence.json` 保存已执行的来源核对结果，`source-manifest.json` 保存公开查询参数、抓取时间、响应及归档哈希。离线重建复现本轮冻结版本，并不代表重新访问了官网。

## 重新访问来源

在本目录执行（`freeze.py` 需安装 pdfplumber）：

```sh
python3 collect.py requests-1.json
python3 collect.py requests-2.json
python3 collect.py requests-3.json
python3 collect.py requests-4.json
python3 collect.py requests-5.json
python3 collect.py requests-6.json
python3 collect.py requests-7.json
python3 collect.py requests-8.json
python3 session_query.py session-requests-1.json
python3 session_query.py session-requests-2.json
python3 freeze.py
python3 build.py
```

采集脚本只走官网匿名访问与公开防伪流程。请求清单保留最初失败尝试供审计；有效证据由 `freeze.py` 分开验证。`raw/` 留在本地；原文保存前删除接口会话字段，原始响应哈希与处理后归档哈希分列。重采可能遇到网站更新，断言失败时须重新核实；不能静默修改旧批次的审核日期和结论。
