# 2026 广西专业招生计划公开数据

截至 2026-09-10，收录 14 所高校、1584 条物理/历史科类计划，30 个来源。293 条记录具备来源明确给出的专业组码，其余保持 null。计划数量合计 56992，但包括专项、预科等不同类型，不能视为普通统考可填余额。学校名单、分校人数及记录数见 `coverage.json`。

**这是部分覆盖。** 尚未取得全区完整专业计划库。未收录不表示该校或专业不在广西招生；最终须核验官方系统、当年招生计划篇与高校章程。普通组投档线与专业实际录取线是不同数据，不得混用。

广西阳光志愿的计划入口在未登录时确实重定向至登录页面；本次公开检索未找到可免费下载的完整 2026 官方计划册 PDF。访问证据、检索范围和谨慎表述见 `province-plan-access-audit.json`、`PROVINCE_PLAN_ACCESS.md`。未注册、登录、提交验证码或访问受限接口。

## 重要字段说明

- `year` 固定为 2026，所有数据来自当年公开来源，未用旧年度替代。
- `requiredSubjects` 只列再选科目；首选科目见 `track`。政治统一写“政治”，原文保存在 `requirementText`。`subjectRule=unknown` 表示要求待核，不等于不限。
- 来源未给批次时使用“本科批次待核”“高职高专批次待核”或“预科批次待核”，不得擅自关联组投档线。
- `category` 保留专项、民族班、中外合作等分类。广西财经 19 条精准专项取自官方 `exam_direction`；不是普通类。类别变更后记录 ID 随规范化结果变化。
- 广西中医药本科图片明确说明广西人数包含预科直升，原表没有拆分直升人数。已加分类及备注；公布人数不能当作普通统考实际可填人数。
- 北部湾、百色的文史理工或历史+物理合计行没有擅自拆分，仅提取明确单一科类。百色分别提取普通、精准专项和民族班，未含预科直升。
- 北部湾 2026 计划表的学费列明示参照 2025 标准，已保留提醒；不是把 2025 计划改名为 2026。
- 艺术、体育等需要额外资格或综合成绩的计划不混入普通文化科类。

## 交付文件

网站接入数据位于仓库 `site/data/`；在此目录重建会生成 `plans.json`、`sources.json`、`coverage.json`。`majorCutoffs.json` 为空，专业实际线由独立数据集提供。

核验：`validation.json`（来源合计与覆盖）、`QA.json`（结构、哈希与类别核验）、上述访问缺口文件。

可公开复现的文件：

```
collect.py
fetch_public.py
fetch_2026.py
extract_public.py
build.py
build_more.py
build_images.py
validate_public.py
requirements.txt
public-request-manifest.json
gxtcm-transcription-2026.json
bsuc-transcription-2026.json
```

这些文件只使用自身目录的相对位置，没有旧私人研究目录、学生背景文件或 2025 采集脚本依赖。查询 URL 中的 key 是学校官网公开链接所含的发布标识，不是账号凭证。原始网页、JSON、PDF、PNG 保存在本地 `raw/`，公开仓库可只发布清单与校验哈希，不必上传原文件。

## 从公开来源复现

在一个干净目录放入上述可复现文件，使用 Python 3.10 或以上，按顺序执行：

```sh
python3 -m pip install -r requirements.txt
python3 fetch_public.py
python3 extract_public.py
python3 build_more.py
python3 build_images.py
python3 build.py
python3 validate_public.py
```

`fetch_2026.py` 是 `fetch_public.py` 的兼容入口。采集程序只执行清单中公开页面及招生查询所用的 GET/POST，不含登录步骤。图片转录文件来自直接看图核读；它们不会因抓取而自动更新。来源页面发生变化时，须对照 `replay-report.json` 重新核读，不可仅凭构建通过就自动发布。

`supplement-fresh-more.json` 和 `supplement-images.json` 为构建中间结果，由脚本在新目录生成，无须从旧研究复制。校验报告明确区分结构通过与完整数据覆盖；完整覆盖当前仍为 false。

## 独立复现验收

已在仅含上述12个公开复现文件的新目录中，重新执行37个公开网络请求并从头提取、构建、校验，重建的1584条计划与交付 plans.json 逐项完全一致。未使用旧私人研究目录或2025采集程序。结果见 REPRODUCTION_QA.json。
