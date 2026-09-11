# 2026-09-12 广西专业实际录取分 · B 包

已实查指定七校，取得华东师范大学 **32 条**单专业或正式招生大类录取分，实际录取人数 **88 人**。其余六校保留有边界的缺口说明。本包是来源研究成果，未修改网站或发布。

| 学校 | 本次结果 | 来源及口径 |
|---|---|---|
| 厦门大学 10384 | 2026 查询成功空列表 | [官方历年分数入口](https://zsdata.xmu.edu.cn/public/zsdata/lqxx/#/lnfs)的广西年份最新 2025；2026 物理、历史、全部科类及全部类别查询均成功空列表，2025 正对照 50 行。 |
| 北京师范大学(珠海校区) 19027 | 已读材料仅有旧年分数 | [官方计划分数目录](https://admission.bnu.edu.cn/zsjhlnfs/index.html)当前广西折页明确“2026 计划及 2025 各专业录取分数”。北京/珠海表头均已目视核对，珠海未混入北京本部。 |
| 南京理工大学 10288 | 已读材料仅有旧年分数 | [官方查询页面](https://zsb.njust.edu.cn/lqjh_fsx)分数列 year1、year2、year3 对应 2023、2024、2025；广西返回 21 行，未当成 2026 分数。 |
| 湖南大学 10532 | 2026 返回空表及空汇总 | [官方入口](https://admi2.hnu.edu.cn/lnlqqk)选项含 2026，实际查询返回 `[null,[]]`。2025 正对照有 10 行类别汇总，当前无专业名称/人数且类别字样为问号；不纳入专业分。 |
| 哈尔滨工程大学 10217 | 2026 查询成功空列表 | [官方分数入口](https://zsb.hrbeu.edu.cn/static/front/hrbeu/basic/html_web/lnfs.html)正常 Cookie/公开 CSRF 流程可读；广西配置最新 2025。2026 物理普通、历史普通、物理国家专项均成功空表；2025 物理普通正对照 16 行。 |
| 华东师范大学 10269 | 新增 32 行、88 人 | [官方分数入口](https://zsbcx.ecnu.edu.cn/static/front/ecnu/basic/html_web/lnfs.html)当前配置中的广西两科八种类别/选科组合均已采集。 |
| 武汉理工大学 10497 | 2026 查询成功空列表 | [官方分专业入口](https://zs.whut.edu.cn/bkcx/bklqqk/)广西配置最新 2025；2026 科类仅“全部”，实际查询专业/省份总表均空。2025 正对照 37 行（含旧年艺术，仅作对照）。 |

空返回不代表 0 分、不招生或所有官方渠道均未发布。本轮统计为 1 校取得记录、4 校正常返回空数据、2 校已读资料只有往年分数，未出现最终传输失败；湖南空汇总保留 null，不作业务码解释。

## 华东师范大学记录范围

| 类别 | 记录数 | 实际录取人数 |
|---|---:|---:|
| 普通本科 | 18 | 55 |
| 公费师范提前批 | 6 | 11 |
| 国家专项 | 6 | 20 |
| 高校专项 | 2 | 2 |
| 合计 | 32 | 88 |

物理 19 条、历史 13 条。仅采响应 `data.sszygradeList`，排除八条 `sszyzgradeList` 组汇总和体育配置；专业最低、最高、平均分别保留，不使用 `avgScoreIntValue` 替代公布的小数平均分。

全部组码为空，因为 `zyzname` 原值是“化学”或“不限”，属于选科文字。全部 rank 为空，因为原专业行没有位次；同响应的组最低位次不能挪到专业。科类和招生性质逐条照原响应。公费师范单独归类并保留签约要求；英语语种、适用专业体检条件及高校专项资格参照[2026 招生章程](https://zsb.ecnu.edu.cn/a3/50/c37582a762704/page.htm)。分数为普通高考 750 分制口径，章程认可最高一项、最多 20 分政策性加分并用于安排专业，原表没有单列加分分值。

原表没有分首轮/征集，全部使用“录取汇总（轮次未分）”。提前批未列广西细分类，国家专项与高校专项未列精确批次，分别保留待核，不以既有专业组分数反推归组。32 行人数均为实际录取人数，plannedCount=null；没有生成计划补录。

## 验证与公开边界

- `QA.json`：180 项构建检查，包含八种查询配置覆盖、每响应专业人数与组汇总人数一致、分数上下界、旧年对照、引用闭合、49 份本轮归档哈希及北京时间日期。
- `verification.json`：独立读取主数据与原响应，逐条复比 320 个来源字段，另核空组码/位次、轮次、资格与归档；全部通过。
- `importer-preflight.json`：仅执行导入预检，948 → 980，新增 32、更新 0、原有 3 条不可比较记录不变。未执行 apply。
- 原响应哈希与归档哈希分别保留在 sources 和原始抓取元数据；JSON 中会话相关字段递归脱敏，Cookie/CSRF 值仅在内存传递。北师折页含公开咨询联系方式，原文不公开复制。没有考生个人记录。

仅发布 `PUBLIC-FILES.json` 列出的文件；`raw/`（包括原始 PDF、页面、接口响应、截图）与 `__pycache__/` 留本地。`code-sources.json` 为两份既有考试院来源元数据，供复现校码证据，不是重新采集投档线。

## 复现

在本目录执行，采集及构建只需要 Python 标准库：

```sh
python3 collect.py requests.json
python3 collect.py requests-2.json
python3 collect.py requests-3.json
python3 collect.py requests-4.json
python3 collect.py requests-5.json
python3 collect.py requests-6.json
python3 collect.py requests-7.json
python3 collect.py requests-8.json
python3 collect.py requests-9.json
python3 session_query.py session-requests.json
python3 session_query.py session-requests-2.json
python3 build.py
python3 verify.py
```

所有路径相对本包，无私人绝对路径。公开接口仍需正常获取访客 Cookie 和公开 CSRF；脚本不使用个人账户。前端参数、真实 URL 和查询条件已入清单。若以后配置或分数变化，断言可能失败，须重新审阅，不能将本次缺口结论继续沿用。北师单页 PDF 的人工表头核验已完成；如需重看，可用任意 PDF 阅读器打开 `raw/bnu-gx-brochure.pdf`。

本包重建使用固定的已审阅日期，不取运行当天作为核查日期。重新下载后如需形成新结论，应另建新日期批次重新审阅，不能只改日期沿用本包。
