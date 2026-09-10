# 2026广西专业录取分补采与复查

核查日期：2026-09-10。范围为上一批15个高分院校代码、6所广西高校，追加3个有新来源的区外高校，并复查重庆三峡医药旧冲突，共25个院校条目。这里的“录取分”专指具体专业实际录取最低分；普通批院校专业组投档线已另有11,448条，本次保持不变。

## 本轮结果

新增4校96条专业分，其中95条可按高校公布的高考成绩口径参考，1条存在原表数值冲突。专业录取分由13校720条增至17校816条；累计3条冲突记录仍展示原文，在分数筛选、排序分差和导出分数中禁用比较。[前后统计及未改数据摘要](summary.json)

| 院校 | 新增记录 | 物理 | 历史 | 可比较 | 尚待核实 |
|---|---:|---:|---:|---:|---|
| 桂林医科大学 | 57 | 51 | 6 | 57 | 按汇总统计；定向、民族班、中澳项目分别保留 |
| 重庆师范大学 | 11 | 6 | 5 | 11 | 10条轮次未分，食品质量与安全1条明确征集但次数未分；组码未公布 |
| 河南城建学院 | 16 | 15 | 1 | 15 | 1条原文矛盾；精确批次、组码和轮次未明 |
| 浙江经贸职业技术学院 | 12 | 6 | 6 | 12 | 精确批次、组码、轮次和计划数未明；12条对应实际录取20人 |

记录数包括同专业不同科类、类别和轮次，不能当作独立专业数量。桂林医科57条有来自当前查询配置和逐组结果的广西组码，涉及26个组；其余39条不猜补组码。95条记录为轮次未分的汇总，不能称为首次录取。

## 数据边界与发现

- 上一批15个高分院校条目，本轮均未取得可确认的2026广西单专业实际最低分。官网页面、年度菜单、公开接口和实际查询结果逐校记录；不据此宣称学校在所有渠道均未发布。
- 桂林医科：全量7页62条与31个批次/投档单位逐组返回的62条多重集完全一致，保留57条专业结果，排除5条预科。17条为订单定向免费医学生、1条民族班、5条中澳学分互认联合培养项目，其余34条普通类。定向的服务地区、签约及6年服务要求保留；中澳5专业按学校章程标明英语单科90/150（其他满分按60%）门槛，不称为中外合作办学。
- 重庆师范：通读完整370行表，广西19条中采集11条，排除3条艺术和5条多专业合计。“社会工作等专业”“工商管理类、旅游管理”等合计最低分不拆给各专业。食品质量与安全547分明确属于征集。
- 河南城建：城市地下空间工程原表最低418、最高423、平均428.2，平均超过最高。原数字不改，单独标记冲突并禁止比较。其余15条的最低/最高/平均范围检查通过。
- 浙江经贸：官方图表由两人独立逐格转录，12条一致；历史、物理各10人，分科最高/最低与合计行一致。空格不变成0分，合计行不作专业。正文日期为2026-08-13，不用URL中的0817推定日期。
- 重庆三峡医药：本轮页面摘要与前轮相同，2条“录取1人但最高不等于最低”冲突仍未修正，继续禁用比较。
- 年份必须从内容核定：浙江大学在2026发布的文章实际是2025投档线；哈工大显式2026参数返回的是2025页面；中大等学校2026查询成功但专业列表为空。旧年数据、成功HTTP响应和空列表均不作为新增专业分。
- 分数是学校公布的普通高考成绩口径，不能一律理解为剔除加分的裸分；政策加分处理按校方说明。录取人数不转成计划人数，不以专业组线填补专业线。

## 页面与校验

详情新增“该校专业录取分数”入口，按同院校代码、同科类查询，并明确含不同批次、类别与轮次，不暗示已与点击的专业组完全匹配。没有数据时展示本轮实际查过的来源与缺口。专业详情显示已公布的最高分、平均分和成绩口径，中澳项目名称在结果条目中可见。

同时补强增量导入：拒绝错误省份/年份、投档线混入、明确非750分制综合成绩、无证据组码/位次、征集冒充首轮、重复新ID及无证据改分；原文分数冲突必须禁用比较。实际专业分不会被额外专业组参考分覆盖。招生类别待核条目在“全部类别”可查，不自动列入一般计划。

自动数据与页面交互检查共16个测试通过。页面交互使用真实数据在jsdom中验证同校专业分入口、科类保持、定向排除、中澳标签、征集筛选以及冲突分明细/排除；不是截图视觉检查。[独立来源审阅与防错复验](independent-review/REVIEW.md)确认新增桂林医科57条的数值及26组对应关系，8项实现或条件遗漏已修正并复验。原有720条专业分逐条保持不变；计划、投档线、一分一档、强基/竞赛及征集计划文件与基线完全一致。

## 逐校核查结果

### 北京大学（10001）

官方分数入口重定向到当前分数表，年份最高2025；广西行按省份/招生类别列文理分数，未取得2026广西分专业实际录取信息。此结论仅覆盖列出的公开栏目和本轮定向检索，不声称已遍查全校网站。

来源：[官方查询或公告1](https://bkzs.pku.edu.cn/xxgk/lqfsx/index.htm) · [官方查询或公告2](https://bkzs.pku.edu.cn/xxgk/lqfsx/2f23dc2f47ae4f46a90d39efd06c7b1a.htm)

### 北京大学医学部（19001）

官方历年分数栏目列2025、2024、2023；已打开最新各专业分数公告核实其标题和表格属于2025，未作为2026资料导入。医学部19001与北大本部10001分开审计。此结论仅覆盖列出的公开栏目和本轮定向检索，不声称已遍查全校网站。

来源：[官方查询或公告1](https://bkzs.bjmu.edu.cn/) · [官方查询或公告2](https://bkzs.bjmu.edu.cn/zsxx/lnfs/index.htm) · [官方查询或公告3](https://bkzs.bjmu.edu.cn/zsxx/lnfs/824ff31b4cd64f299143feeb899d76c8.htm)

### 清华大学（10003）

官方高考统招页所链接的历年录取分数栏目最新可读公告为2024各省各批次分数；不是2026广西分专业实际录取表，未导入。个人录取查询入口需要考生信息，不用于搜集个人数据。此结论仅覆盖列出的公开栏目和本轮定向检索，不声称已遍查全校网站。

来源：[官方查询或公告1](https://www.join-tsinghua.edu.cn/gnxs/gktz.htm) · [官方查询或公告2](https://www.join-tsinghua.edu.cn/xxgk/lnlqfsx.htm) · [官方查询或公告3](https://www.join-tsinghua.edu.cn/info/1032/1945.htm)

### 中国人民大学（10002）

已核对官方历年分数页面及公开接口；广西年份选项最高为2025。实际提交2026年广西本科一批查询，接口成功响应但专业和院校汇总列表均为空。这表示本轮查询没有得到本年记录，不代表学校未招生或穷尽性证明未发布。

来源：[官方查询或公告1](https://rdzs.ruc.edu.cn/zsw/lnfs.html) · [官方查询或公告2](https://rdzs.ruc.edu.cn/f/ajax_lnfs_param) · [官方查询或公告3](https://rdzs.ruc.edu.cn/static/front/ruc/basic/js/tplt.js) · [官方查询或公告4](https://rdzs.ruc.edu.cn/f/ajax_lnfs)

### 中国科学技术大学（10358）

已核对官方历年分数页面及公开接口；广西年份选项最高为2025。实际提交2026年广西普通本科查询，接口成功响应但专业和院校汇总列表均为空。另检索到的2026强基公告使用综合成绩，已排除；查询配置只展示省份投档线，showField3为空，不能假设存在分专业实际录取分。这表示本轮查询没有得到本年记录，不代表学校未招生或穷尽性证明未发布。

来源：[官方查询或公告1](https://zsfw.ustc.edu.cn/zsw/lnfs.html) · [官方查询或公告2](https://zsfw.ustc.edu.cn/f/ajax_lnfs_param) · [官方查询或公告3](https://zsfw.ustc.edu.cn/static/front/ustc/basic/js/tplt.js) · [官方查询或公告4](https://zsfw.ustc.edu.cn/f/ajax_lnfs) · [官方查询或公告5](https://zsb.ustc.edu.cn/2026/0626/c35499a745702/page.htm)

### 北京理工大学（10007）

已核对官方历年分数页面及公开接口；广西年份选项最高为2025。实际提交2026年广西统招查询，接口成功响应但专业和院校汇总列表均为空。这表示本轮查询没有得到本年记录，不代表学校未招生或穷尽性证明未发布。

来源：[官方查询或公告1](https://admission.bit.edu.cn/static/front/bit/basic/html_web/lnfs.html) · [官方查询或公告2](https://admission.bit.edu.cn/f/ajax_lnfs_param) · [官方查询或公告3](https://admission.bit.edu.cn/static/front/bit/basic/js/tplt.js) · [官方查询或公告4](https://admission.bit.edu.cn/f/ajax_lnfs)

### 北京航空航天大学（10006）

已核对官方历年分数页面及公开接口；广西年份选项最高为2025。实际提交2026年广西统招查询，接口成功响应但专业和院校汇总列表均为空。另一个官网省份地图的广西链接只提供2018/2017年；该地图数据为旧年，不能作为2026专业录取分。这表示本轮查询没有得到本年记录，不代表学校未招生或穷尽性证明未发布。

来源：[官方查询或公告1](https://lqcx.buaa.edu.cn/static/front/buaa/basic/html_web/lnfs.html) · [官方查询或公告2](https://lqcx.buaa.edu.cn/f/ajax_lnfs_param) · [官方查询或公告3](https://lqcx.buaa.edu.cn/static/front/buaa/basic/js/tplt.js) · [官方查询或公告4](https://lqcx.buaa.edu.cn/f/ajax_lnfs) · [官方查询或公告5](https://zs.buaa.edu.cn/bkzn/lnfs.htm) · [官方查询或公告6](https://zs.buaa.edu.cn/info/1082/1247.htm)

### 河南城建学院（11765）

官网2026年8月14日外省本科录取表的广西段16条，物理15、历史1。15条常规数值可按普通高考总分口径参考；学校章程认可政策加分，原表未单列加分处理方式，不称裸分。城市地下空间工程最高423、最低418、平均428.2，保留原值并关闭该条分数比较。未列广西正式批次、专业组、最低位次、录取人数及轮次。

来源：[官方查询或公告1](https://zs.huuc.edu.cn/info/1179/4818.htm) · [官方查询或公告2](https://zs.huuc.edu.cn/list201506.jsp?urltype=tree.TreeTempUrl&wbtreeid=1103) · [官方查询或公告3](https://zs.huuc.edu.cn/info/1103/4769.htm) · [官方查询或公告4](https://www.gxeea.cn/view/content_624_33106.htm)

### 上海交通大学（10248）

官方分数栏目最新数据年2025；未取得2026广西两科普通或明确资格类别的单专业实际最低分。仅能确认本轮未找到，不能宣称学校不招生。

来源：[官方查询或公告1](https://admissions.sjtu.edu.cn/) · [官方查询或公告2](https://admissions.sjtu.edu.cn/rnapi/newsList)

### 上海交通大学医学院（19248）

官方最新可读分数文章为2025普通批次；未取得2026广西专业最低分。独立校码，不与交大本部混用。

来源：[官方查询或公告1](https://www.shsmu.edu.cn/ygzs/zsxx/lnfs.htm) · [官方查询或公告2](https://www.shsmu.edu.cn/ygzs/info/1025/1206.htm)

### 复旦大学（10246）

官方分数栏目最新为2025分省录取分数，未取得2026广西专业最低分；未采用搜索中的旧年参考、预测或其他省综评成绩。

来源：[官方查询或公告1](https://ao.fudan.edu.cn/36333/list.htm)

### 浙江大学（10335）

2026-06-17发布文章实际是2025年分省投档线，年度和分数层级都不符合2026广西专业实际最低分；未将医学院等独立代码并入本部。

来源：[官方查询或公告1](https://zdzsc.zju.edu.cn/87260/list.htm) · [官方查询或公告2](https://zdzsc.zju.edu.cn/2026/0617/c87260a3179915/page.htm)

### 南京大学（10284）

正常公开流程已跑通；分数菜单广西只有2025/2024/2023。对2026物理与历史普通批次分别作明确标注的缺年探查，两次均state1且省/专业列表为空。未见2026资格类别选项，未猜测专项参数。

来源：[官方查询或公告1](https://bkzs.nju.edu.cn/static/front/nju/basic/html_web/lnfs.html) · [官方查询或公告2](https://bkzs.nju.edu.cn/static/front/nju/basic/js/tplt.js) · [官方查询或公告3](https://bkzs.nju.edu.cn/f/ajax_lnfs_param) · [官方查询或公告4](https://bkzs.nju.edu.cn/f/ajax_lnfs)

### 重庆师范大学（10637）

本轮实际录入11条2026广西专业最低分，历史5/物理6，其中征集1。排除艺术3和多专业合计5；这是可明确到单一专业/正式大类的部分覆盖，其他专业仍有缺口。

来源：[官方查询或公告1](https://zsb.cqnu.edu.cn/info/10438/88323.htm) · [官方查询或公告2](https://www.gxeea.cn/view/content_624_33107.htm)

### 广西大学（10593）

已重读官方录取分数栏目；最新普通本科结果标题为2025年，发布于2026年的条目是2025少数民族预科。未得到2026专业实际录取分。

来源：[官方查询或公告1](https://zs.gxu.edu.cn/child/xinxichaxun.jsp?urltype=tree.TreeTempUrl&wbtreeid=1232)

### 广西师范大学（10602）

已读官方分数栏目及当前查询页JS；年份接口仅2025/2024/2023。2026广西不限专业类别的JSON查询返回空数组。最初form请求415已用前端JSON编码纠正；不把415作为未发布证据。

来源：[官方查询或公告1](https://bkzs.gxnu.edu.cn/lnfs_12177/list.htm) · [官方查询或公告2](https://ibkzs.gxnu.edu.cn/RobotSys/pScorePage) · [官方查询或公告3](https://ibkzs.gxnu.edu.cn/RobotSys/selectYear) · [官方查询或公告4](https://ibkzs.gxnu.edu.cn/RobotSys/GetScoreData)

### 广西民族大学（10608）

已从首页进入历年分数完整当前列表；普通、国家专项、地方专项、民族班、公费师范、中外合作和学分互认等最新表均为2025，未取得2026专业实际最低分。

来源：[官方查询或公告1](https://zs.gxmzu.edu.cn/) · [官方查询或公告2](https://zs.gxmzu.edu.cn/list.jsp?urltype=tree.TreeTempUrl&wbtreeid=1101)

### 南宁师范大学（10603）

当前官网链接的前端位于/zsdata/lqxx/，但其JS明确API仍为/lqxx/s/；因此不能将先前API空结果归因于路径错误。当前lnfs/getType仅含2025等既有年份，无2026；按真实字段查询2026/广西/物理类、历史类、全部及类别全部，均成功空列表。

来源：[官方查询或公告1](https://zs.nnnu.edu.cn/) · [官方查询或公告2](https://zsw.nnnu.edu.cn/zsdata/lqxx/) · [官方查询或公告3](https://zsw.nnnu.edu.cn/zsdata/lqxx/js/app.4fa9fdca.js) · [官方查询或公告4](https://zsw.nnnu.edu.cn/zsdata/lqxx/js/lqcxjg.e6efaaac.js) · [官方查询或公告5](https://zsw.nnnu.edu.cn/lqxx/s/api/front/lqxx/getType) · [官方查询或公告6](https://zsw.nnnu.edu.cn/lqxx/s/api/front/lqxx/getList) · [官方查询或公告7](https://zsw.nnnu.edu.cn/) · [官方查询或公告8](https://zsw.nnnu.edu.cn/lqxx/#/lnfs)

### 桂林医科大学（10601）

取得2026广西全部7页62行；31个唯一批次/投档单位筛选合计62行与分页多重集一致。收录57条具体专业实录分，5条预科班单独排除。当前官方查询没有区分首轮/征集，标录取汇总；排名和选科要求未列，保留未知。

来源：[官方查询或公告1](https://jyw.glmu.edu.cn/zhaosheng/school!homeIndex.htm) · [官方查询或公告2](https://jyw.glmu.edu.cn/zhaosheng/school!admissionScore.htm) · [官方查询或公告3](https://jyw.glmu.edu.cn/zhaosheng/school!ajaxGetScoreSelectInfo.htm) · [官方查询或公告4](https://jyw.glmu.edu.cn/zhaosheng/school!articleDetail.htm?recruitArticle.searchArticleId=145) · [官方查询或公告5](https://jyw.glmu.edu.cn/zhaosheng/school!admissionScoreSel.htm)

### 右江民族医学院（10599）

已核对校部代码10599并重读官网及历年分数栏目；最新广西专业、区外专业、定向医学生录取分统计均为2025。首页2026征集公告是余额，不用于专业实录分。

来源：[官方查询或公告1](https://yyzs.ymun.edu.cn/) · [官方查询或公告2](https://yyzs.ymun.edu.cn/list.jsp?urltype=tree.TreeTempUrl&wbtreeid=1048)

### 华中科技大学（10487）

官方分省分专业分数页面的实际年份数据只有2025、2024、2023，未取得2026广西专业实际最低分；2026计划及强基分数不能补代普通专业录取分。

来源：[官方查询或公告1](https://zsb.hust.edu.cn/bkzn/fsfzyfsx.htm)

### 哈尔滨工业大学（10213）

官方分数查询当前提供2025/2024；显式请求广西2026后实际页面仍显示2025广西，因此不将该返回误记为2026。未取得本轮所查2026普通专业最低分。

来源：[官方查询或公告1](https://zsb.hit.edu.cn/information/score) · [官方查询或公告2](https://zsb.hit.edu.cn/information/score?province=%E5%B9%BF%E8%A5%BF&year=2026)

### 中山大学（10558）

正常公开查询流程已跑通。广西菜单最新为2025；2026物理、历史普通录取均成功响应但学校/专业列表为空，2025物理正向对照有专业数据。只记录本轮未取得，不断言学校尚未公布；不猜补其他招生类别。

来源：[官方查询或公告1](https://admission.sysu.edu.cn/f/ajax_lnfs_param) · [官方查询或公告2](https://admission.sysu.edu.cn/f/ajax_lnfs)

### 重庆三峡医药高等专科学校（14008）

重新取得的官网内容摘要与前轮一致，2条冲突未修正：物理医学检验技术录取1人却记最低335/最高411；物理预防医学录取1人却记最低283/最高424。保留原文并继续排除分数比较，不以专业组线猜改。

来源：[官方查询或公告1](https://www.sxyyc.net/zsb/info/1015/2257.htm)

### 浙江经贸职业技术学院（12864）

官方广西录取图表新增12条专业分（历史6、物理6），对应20名实际录取考生。双人读图与两科合计均一致。9个专业名称按科类分列；空白格不作0分、合计行不作为专业。仍缺专业组、精确批次和轮次，以及分专业计划人数。

来源：[官方查询或公告1](https://zs.zjiet.edu.cn/2026/0817/c1030a71607/pagem.htm) · [官方查询或公告2](https://zs.zjiet.edu.cn/_upload/article/images/d3/d0/2f45bca2432097a3305865280ad0/47dacf98-54ea-476d-ac7d-7e1bafb91ce3_d.png)

## 复现与归档

- [增量记录](major-cutoffs-upsert.json)、[来源台账](sources.json)、[25校复查记录](school-audit-notes.json)。来源台账新增121个页面/接口请求记录；接口同址不同参数分别保留，不等于121个独立网页。
- [A包](batch-a/README.md)、[B包](batch-b/README.md)、[C包](batch-c/核验说明.md)、[root包](batch-root/README.md)保留各自生成与复核程序、来源参数和内容摘要。仅发布明确白名单，不上传raw目录、会话或个人资料。C包引用的750分省方案已读正文但原HTML后续下载失败，归档限制单列，不冒填哈希；分数本体、组码与学校章程均有实际响应证据。
- 汇总包给各校核查笔记补上稳定ID及auditKind=major-scores，用于区分分数核查和计划来源状态；不改原始来源事实。
- 在仓库根目录执行 `node scripts/import-major-score-batch.mjs docs/major-scores-2026-09-10` 预览；确认差异后加 `--apply`。相同ID重复导入应为0增量，不删除旧记录。
- `node scripts/report-major-score-batch.mjs` 验证基线720条专业分和8个未修改数据文件，并更新前后统计；再运行 `npm test`、`npm run check`、`node scripts/validate-data.mjs --write-report`。
- 发布通过同一提交的GitHub Actions检查后，再对线上18个运行文件逐一校验HTTP状态与SHA-256。成功构建只证明程序检查通过，不消除本报告列出的资料缺口。
