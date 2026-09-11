# 2026 广西专业录取分缺口续查

核查日期：2026-09-12（北京时间）。本轮实查23个院校条目，其中20校按分数优先续查，另查3校公开材料。[前后统计与既有数据保护检查](summary.json) · [20校优先目标](targets.json)

## 本轮结果

新增3校110条专业或正式招生大类的实际录取最低分，覆盖原表205名实际录取人数。全站由23校948条增至26校1,058条；原有3条分数冲突继续保留原值并停用比较。记录数包括同专业的不同科类、招生类别及定向服务县区，不等于110个独立专业。

| 院校 | 新增记录 | 物理 | 历史 | 实际人数 | 主要边界 |
|---|---:|---:|---:|---:|---|
| 华东师范大学 | 32 | 19 | 13 | 88 | 普通本科18、公费师范6、国家专项6、高校专项2；组码和专业位次未公布 |
| 广西中医药大学 | 72 | 44 | 28 | 111 | 仅中医学定向医学生，按具体服务县区保留；再选科目和位次未明 |
| 浙江工商职业技术学院 | 6 | 3 | 3 | 6 | 官方表广西段完整6行；具体专科批次、组码、再选科目和位次未明 |

110条全部保留“录取汇总（轮次未分）”，不能理解为首轮。38条组码为空；华东师范14条提前批或专项、浙江工商6条专科未列精确批次，保留待核。全部新增记录没有明确的专业最低分位次，未借用同响应的专业组位次。原表录取人数没有转写成招生计划。

广西中医药72条定向记录使用原专业名，单列服务市县，并以县区区分招生类别，避免同组同专业互相覆盖。农村户籍、连续3年、设区市生源、签约及完成规定培训或专硕后至少6年服务等条件留在详情；普通类筛选排除这些定向记录。两张原图中宜州区的合并单元格边界已独立复核：历史407组、物理457组，贵港从下一行桂平市开始。

## 仍未取得的资料

20所优先院校按各校符合条件的首轮专业组最高分排序，本轮范围642至627分；这个分数只安排核查顺序，不能理解为学校最低分。华东师范取得专业明细，其余19校本轮未取得合格的本年广西专业分。另查北京联合大学的广西表只有专业组分，未当作专业分。合计20个核查条目没有新增实际专业分。

典型缺口包括：北师大本部及珠海折页是2026计划与2025分数；天津医科最新公告附件实际为2023—2025；吉林整表1,704行全部属于2022—2025。当前公开查询成功空表、配置未含2026、业务返回失败、传输失败和访问验证分别记载，不据此宣称学校所有渠道都没有发布。

广西中医药普通本科两张图40行（含2条预科）及专科5行明确写“首次投档最高/最低/平均分”。这些表虽列录取人数，仍不能改变其分数性质；本轮仅保留官方来源和排除说明，未混入实际专业录取分，也未改写既有81条专业投档分。提前批定向表则明确为专业录取情况，列最高分、最低分和实际人数，按原文分别处理。

## 校验与页面验证

华东师范32条由另一采集者对八份原响应逐行独立复核；广西中医药72条从原图独立重录关键字段，与正式包比对；浙江工商6条逐行核对原HTML。来源年份、广西科类、专业名、分数、录取人数、选科、县区和组码按原表验证。

17项自动测试、数据检查及真实数据页面交互验证通过。新增页面检查包括华东师范普通类筛选不混入公费/专项、未知组码不冒充选科文字，以及定向记录县区和资格条件可见、普通筛选排除定向。交互验证使用jsdom，不声称完成浏览器截图视觉检查。

原有948条实际专业分及552条既有来源逐条未改。投档线、计划、一分一档、强基与竞赛、政策、征集计划、计划来源目录及专业投档分等8个数据文件与上次发布基线逐字节一致。

[华东师范独立复核](batch-a/independent-review-b.md) · [广西中医药与浙江工商独立复核](independent-review/REVIEW.md) · [六校缺口独立核查](root-gap-review.md)。各采集包保留公开白名单；原始网页、PDF、图片和任何会话内容不发布。

## 逐校核查记录

### 大连理工大学（10141）

公开分数前端及API已核查。字典确认主校区（含开发区）=1、广西=450000、物理类=20、历史类=21。主校区年份接口为空；请求2026广西两科分类和分专业接口均成功返回空数组，未取得本年专业分。未限定招生类型，不把盘锦校区数据合入本部；入口/API空结果不等于学校所有发布渠道均无数据。

来源：[大连理工大学2026广西公开专业分查询：20-majors](https://zs.dlut.edu.cn/apiV2025/portal/recruitmentInfo/admissionScore/admissionScoreList?zsCampusType=1&recruitmentYear=2026&provinceCode=450000&recruitmentSubjectType=20) · [大连理工大学2026广西公开专业分查询：20-types](https://zs.dlut.edu.cn/apiV2025/portal/recruitmentInfo/admissionScore/selectRecruitmentTypeList?zsCampusType=1&recruitmentYear=2026&provinceCode=450000&recruitmentSubjectType=20) · [大连理工大学2026广西公开专业分查询：21-majors](https://zs.dlut.edu.cn/apiV2025/portal/recruitmentInfo/admissionScore/admissionScoreList?zsCampusType=1&recruitmentYear=2026&provinceCode=450000&recruitmentSubjectType=21) · [大连理工大学2026广西公开专业分查询：21-types](https://zs.dlut.edu.cn/apiV2025/portal/recruitmentInfo/admissionScore/selectRecruitmentTypeList?zsCampusType=1&recruitmentYear=2026&provinceCode=450000&recruitmentSubjectType=21) · [大连理工大学公开前端/配置：api-chunk](https://zs.dlut.edu.cn/assets/index-480b452d.js) · [大连理工大学公开前端/配置：app](https://zs.dlut.edu.cn/assets/index-a85f3f00.js) · [大连理工大学公开前端/配置：campus-chunk](https://zs.dlut.edu.cn/assets/zsCampusType-f008d741.js) · [大连理工大学公开前端/配置：dict-campus](https://zs.dlut.edu.cn/apiV2025/portal/common/getDictData/zs_campus_type) · [大连理工大学公开前端/配置：dict-track](https://zs.dlut.edu.cn/apiV2025/portal/common/getDictData/recruitment_subject_type) · [大连理工大学公开前端/配置：dict-type](https://zs.dlut.edu.cn/apiV2025/portal/common/getDictData/recruitment_type) · [大连理工大学公开省份字典](https://zs.dlut.edu.cn/apiV2025/portal/common/provinceList) · [大连理工大学公开前端/配置：score-chunk](https://zs.dlut.edu.cn/assets/index-6433af1e.js) · [大连理工大学录取分数入口](https://zs.dlut.edu.cn/admissionScore) · [大连理工大学主校区录取分数年份查询](https://zs.dlut.edu.cn/apiV2025/portal/recruitmentInfo/admissionScore/admissionScoreYearList?zsCampusType=1)

### 中国政法大学（10053）

本科招生官网本次HTTP 200，但正文仅浏览器访问验证页，未取得可读录取查询字段或分数表。未执行验证挑战或猜造查询接口；未能按两科和类别进一步核查2026广西专业分，保留访问缺口。

来源：[中国政法大学本科招生网访问记录](https://zs.cupl.edu.cn/)

### 北京交通大学（10004）

已读公开历年分数前端和参数，广西选项仅2024、2025。实际请求2026广西物理/历史普通类，并查物理国家专项、民族班，分专业数组均空；对当前字典中的6个专业组名称逐一请求本年仍空。此举只记录查询结果，不证明旧年组标签或类别适用于2026；未将威海中外单列校区合入本部。

来源：[北京交通大学2026广西公开专业分查询：历史-普通类-历史](https://zsw.bjtu.edu.cn/f/ajax_lnfs) · [北京交通大学2026广西公开专业分查询：历史-普通类](https://zsw.bjtu.edu.cn/f/ajax_lnfs) · [北京交通大学2026广西公开专业分查询：物理-国家专项-物化组](https://zsw.bjtu.edu.cn/f/ajax_lnfs) · [北京交通大学2026广西公开专业分查询：物理-国家专项](https://zsw.bjtu.edu.cn/f/ajax_lnfs) · [北京交通大学2026广西公开专业分查询：物理-普通类-物化-詹天佑信息类](https://zsw.bjtu.edu.cn/f/ajax_lnfs) · [北京交通大学2026广西公开专业分查询：物理-普通类-物化-詹天佑智能类](https://zsw.bjtu.edu.cn/f/ajax_lnfs) · [北京交通大学2026广西公开专业分查询：物理-普通类-物化](https://zsw.bjtu.edu.cn/f/ajax_lnfs) · [北京交通大学2026广西公开专业分查询：物理-普通类](https://zsw.bjtu.edu.cn/f/ajax_lnfs) · [北京交通大学2026广西公开专业分查询：物理-民族班-民族班](https://zsw.bjtu.edu.cn/f/ajax_lnfs) · [北京交通大学2026广西公开专业分查询：物理-民族班](https://zsw.bjtu.edu.cn/f/ajax_lnfs) · [北京交通大学本科招生网](https://zsw.bjtu.edu.cn/) · [北京交通大学历年分数查询](https://zsw.bjtu.edu.cn/zsw/lnfs.html) · [北京交通大学公开前端/配置：score-params](https://zsw.bjtu.edu.cn/f/ajax_lnfs_param)

### 北京科技大学（10008）

已读公开历年分数前端和参数，广西选项仅2023至2025。实际请求2026广西物理类普通类、国家专项及历史类普通类，均返回state=1且sszygradeList=[]。未将学校录取概况数组替代专业分；其他本年招生类别仍无直接记录。

来源：[北京科技大学2026广西公开专业分查询：历史类-普通类](https://zhaoshengyunzhi.ustb.edu.cn/f/ajax_lnfs) · [北京科技大学2026广西公开专业分查询：物理类-国家专项](https://zhaoshengyunzhi.ustb.edu.cn/f/ajax_lnfs) · [北京科技大学2026广西公开专业分查询：物理类-普通类](https://zhaoshengyunzhi.ustb.edu.cn/f/ajax_lnfs) · [北京科技大学本科招生网](https://zhaosheng.ustb.edu.cn/) · [北京科技大学历年分数查询](https://zhaoshengyunzhi.ustb.edu.cn/zsw/lnfs.html) · [北京科技大学公开前端/配置：score-params](https://zhaoshengyunzhi.ustb.edu.cn/f/ajax_lnfs_param)

### 北京师范大学（10027）

当前计划分数目录最新为2026-06-18发布的本年计划与近年分数。广西单页附件表体明确2026招生计划及2025各专业录取分数，北京/珠海校区各自表头相同；全部旧年分数排除，未取得2026广西本部专业实际录取分。保持10027与19027校区身份独立。

来源：[北京师范大学2026年在广西本科招生计划及2025年各专业录取分数](https://admission.bnu.edu.cn/docs//2026-06/bf4044bdab3c45099fe724ce5650c45f.pdf) · [北京师范大学本科生招生网](https://admission.bnu.edu.cn/) · [北京师范大学2026年分省招生计划及近年录取分数](https://admission.bnu.edu.cn/zsjhlnfs/579650127d9e4120be2044b08d71da55.html) · [北京师范大学招生计划及历年分数目录](https://admission.bnu.edu.cn/zsjhlnfs/index.html)

### 吉林大学（10183）

官网公开JS直接指定的历年专业分CDN整表已完整下载，total与行数均为1704；逐行年份仅2022/2023/2024/2025，没有2026。广西有旧年记录231行，也全部排除；页面一次读取整表，没有漏采分页。本年物理/历史及各类别专业分仍缺。

来源：[吉林大学公开前端/配置：app](https://zsb.jlu.edu.cn/js/app-ec3771fad27ccda1a3cd.js) · [吉林大学公开前端/配置：common](https://zsb.jlu.edu.cn/js/common-ec3771fad27ccda1a3cd-chunk.js) · [吉林大学公开前端/配置：config](https://zsb.jlu.edu.cn/ipcofig.js) · [吉林大学公开前端/配置：details](https://zsb.jlu.edu.cn/js/details-ec3771fad27ccda1a3cd-chunk.js) · [吉林大学本科招生网](https://zsb.jlu.edu.cn/) · [吉林大学公开历年分数配置](https://study-cdn2.jobpi.cn/formal/38147/enroll/lqfsConfig.json) · [吉林大学公开历年专业录取分数整表](https://study-cdn2.jobpi.cn/formal/38147/enroll/lqfsDataMin.json)

### 电子科技大学(沙河校区)（19614）

本轮重新读取电子科大公开查询前端与选项，广西沙河校区菜单年份仅2021至2025，没有2026。以学校原文xqmc=电子科技大学（沙河校区）分别请求2026广西物理类、历史类普通类，均code=200、success=true、list=[]。本部和沙河代码保持独立，不把本部查询结果当沙河证据，其他本年类别未取得。

来源：[电子科技大学(沙河校区)公开前端/配置：app](https://chaxun.uestc.edu.cn/public/zsdata/lqxx/js/app.b9fb24b1.js) · [电子科技大学(沙河校区)公开前端/配置：lnfs](https://chaxun.uestc.edu.cn/public/zsdata/lqxx/js/lqcxjg.7ac4330b.js) · [电子科技大学公开招生数据查询入口](https://chaxun.uestc.edu.cn/public/zsdata/lqxx/) · [电子科技大学(沙河校区)2026广西公开专业分查询：历史类](https://chaxun.uestc.edu.cn/lqxx/s/api/front/lqxx/getList) · [电子科技大学(沙河校区)2026广西公开专业分查询：物理类](https://chaxun.uestc.edu.cn/lqxx/s/api/front/lqxx/getList) · [电子科技大学历年分数选项（区分沙河校区）](https://chaxun.uestc.edu.cn/lqxx/s/api/front/lqxx/getType)

### 厦门大学（10384）

官方分数查询广西配置最新2025。按真实前端参数查询2026广西、全部类别，物理类/历史类/全部均success=true且list为空；2025同口径正对照50条。2026广西报考指南另表列的是2026计划和2025/2024录取分，未挪作本年实际分。查询包含官方类别中的马来西亚分校，当前无2026结果，未产生本部/分校混码。

来源：[厦门大学：公开查询配置或前端页面 [xmu-app]](https://zsdata.xmu.edu.cn/public/zsdata/lqxx/js/app.aa9f5572.js) · [厦门大学：公开查询配置或前端页面 [xmu-component]](https://zsdata.xmu.edu.cn/public/zsdata/lqxx/js/lqcxjg.610f706a.js) · [厦门大学：公开查询配置或前端页面 [xmu-entry]](https://zsdata.xmu.edu.cn/public/zsdata/lqxx/#/lnfs) · [厦门大学：公开查询配置或前端页面 [xmu-guide]](https://zs.xmu.edu.cn/zsdt/info/1021/1046.htm) · [厦门大学：2025广西正向对照（不纳入2026） [xmu-gx-2025-全部]](https://zsdata.xmu.edu.cn/lqxx/s/api/front/lqxx/getList) · [厦门大学：2026广西公开分数查询响应 [xmu-gx-2026-全部]](https://zsdata.xmu.edu.cn/lqxx/s/api/front/lqxx/getList) · [厦门大学：2026广西公开分数查询响应 [xmu-gx-2026-历史类]](https://zsdata.xmu.edu.cn/lqxx/s/api/front/lqxx/getList) · [厦门大学：2026广西公开分数查询响应 [xmu-gx-2026-物理类]](https://zsdata.xmu.edu.cn/lqxx/s/api/front/lqxx/getList) · [厦门大学：公开查询配置或前端页面 [xmu-types]](https://zsdata.xmu.edu.cn/lqxx/s/api/front/lqxx/getType)

### 北京师范大学(珠海校区)（19027）

官方计划分数目录当前有2026招生计划及近年分数、2025及更旧实际分数入口。本年广西折页已核对主标题与珠海校区表头：2026为计划年，最低/最高分属2025；未找到本次可核实的2026珠海校区单专业实际分。珠海19027独立记账，未使用北京本部10027数据。

来源：[北京师范大学(珠海校区)：公开查询配置或前端页面 [bnu-guide]](https://admission.bnu.edu.cn/zsjhlnfs/579650127d9e4120be2044b08d71da55.html) · [北京师范大学(珠海校区)：2026广西计划与2025专业录取分数折页 [bnu-gx-brochure]](https://admission.bnu.edu.cn/docs//2026-06/bf4044bdab3c45099fe724ce5650c45f.pdf) · [北京师范大学(珠海校区)：公开查询配置或前端页面 [bnu-home]](https://admission.bnu.edu.cn/) · [北京师范大学(珠海校区)：公开查询配置或前端页面 [bnu-index]](https://admission.bnu.edu.cn/zsjhlnfs/index.html)

### 南京理工大学（10288）

官方2026招生计划及近三年分数入口中的分数表，year1/year2/year3前端表头分别为2023/2024/2025。广西接口成功返回21条旧年专业记录，未提供2026分数列；未将招生计划年份套到旧分数上。本次未取得可确认的2026专业实际分。

来源：[南京理工大学：公开查询配置或前端页面 [njust-entry]](https://zsb.njust.edu.cn/lqjh_fsx) · [南京理工大学：广西2023至2025各专业历年分数 [njust-lines]](https://zsb.njust.edu.cn/lqScore/initDateWebCon)

### 湖南大学（10532）

官方前端年份选项包含2026；按year=2026、sf=广西壮族自治区正常GET，HTTP200返回[null,[]]。同样2025返回汇总及10条类别行，当前原响应不含专业名称/录取人数、类别文字为问号，仅证明接口响应。前端按月份在类别/专业表头间切换，本次未将类别汇总冒充专业分。

来源：[湖南大学：公开查询配置或前端页面 [hnu-entry]](https://admi2.hnu.edu.cn/lnlqqk) · [湖南大学：2025广西正向对照（不纳入2026） [hnu-gx-2025-control]](https://admi2.hnu.edu.cn/lnlqqkSearch?year=2025&sf=%E5%B9%BF%E8%A5%BF%E5%A3%AE%E6%97%8F%E8%87%AA%E6%B2%BB%E5%8C%BA) · [湖南大学：2026广西公开分数查询响应 [hnu-gx-2026]](https://admi2.hnu.edu.cn/lnlqqkSearch?year=2026&sf=%E5%B9%BF%E8%A5%BF%E5%A3%AE%E6%97%8F%E8%87%AA%E6%B2%BB%E5%8C%BA) · [湖南大学：公开查询配置或前端页面 [hnu-home]](https://admi.hnu.edu.cn/) · [湖南大学：公开查询配置或前端页面 [hnu-js]](https://admi2.hnu.edu.cn/add210531/js/lnlqqk.js)

### 哈尔滨工程大学（10217）

依官方Cookie与公开CSRF流程读取配置，广西分数年份最新2025，校区/性别筛选未启用。2026广西物理普通类、历史普通类、物理国家专项均state=1但专业与总表为空；2025广西物理普通类正对照16条专业记录。未把配置缺少年份等同于所有渠道均未发布。

来源：[哈尔滨工程大学：公开查询配置或前端页面 [hrbeu-entry]](https://zsb.hrbeu.edu.cn/static/front/hrbeu/basic/html_web/lnfs.html) · [哈尔滨工程大学：2025广西正向对照（不纳入2026） [hrbeu-gx-2025-物理类-普通类]](https://zsb.hrbeu.edu.cn/f/ajax_lnfs) · [哈尔滨工程大学：2026广西公开分数查询响应 [hrbeu-gx-2026-历史类-普通类]](https://zsb.hrbeu.edu.cn/f/ajax_lnfs) · [哈尔滨工程大学：2026广西公开分数查询响应 [hrbeu-gx-2026-物理类-国家专项]](https://zsb.hrbeu.edu.cn/f/ajax_lnfs) · [哈尔滨工程大学：2026广西公开分数查询响应 [hrbeu-gx-2026-物理类-普通类]](https://zsb.hrbeu.edu.cn/f/ajax_lnfs) · [哈尔滨工程大学：公开查询配置或前端页面 [hrbeu-home]](https://zsb.hrbeu.edu.cn/) · [哈尔滨工程大学：公开查询配置或前端页面 [hrbeu-init]](https://zsb.hrbeu.edu.cn/static/front/hrbeu/basic/js/init.js) · [哈尔滨工程大学：公开查询配置或前端页面 [hrbeu-params]](https://zsb.hrbeu.edu.cn/f/ajax_lnfs_param) · [哈尔滨工程大学：公开查询配置或前端页面 [hrbeu-tplt]](https://zsb.hrbeu.edu.cn/static/front/hrbeu/basic/js/tplt.js)

### 华东师范大学（10269）

已采官方配置中2026广西物理/历史8种类别与选科组合，共32条、88名实际录取：普通本科18条、公费师范提前6条、国家专项6条、高校专项2条。已排除体育配置及8条组汇总。原专业行未公布省编组码/专业位次/校区/轮次；国家专项与高校专项精确批次待核。范围仅为当前官方查询配置，不宣称全校全部招生渠道完备。

来源：[华东师范大学：2026年本科招生章程 [ecnu-charter]](https://zsb.ecnu.edu.cn/a3/50/c37582a762704/page.htm) · [华东师范大学：公开查询配置或前端页面 [ecnu-entry]](https://zsb.ecnu.edu.cn/_redirect?siteId=799&columnId=37612&articleId=444126) · [华东师范大学：2026广西公开分数查询响应 [ecnu-gx-2026-1]](https://zsbcx.ecnu.edu.cn/f/ajax_lnfs) · [华东师范大学：2026广西公开分数查询响应 [ecnu-gx-2026-2]](https://zsbcx.ecnu.edu.cn/f/ajax_lnfs) · [华东师范大学：2026广西公开分数查询响应 [ecnu-gx-2026-3]](https://zsbcx.ecnu.edu.cn/f/ajax_lnfs) · [华东师范大学：2026广西公开分数查询响应 [ecnu-gx-2026-4]](https://zsbcx.ecnu.edu.cn/f/ajax_lnfs) · [华东师范大学：2026广西公开分数查询响应 [ecnu-gx-2026-5]](https://zsbcx.ecnu.edu.cn/f/ajax_lnfs) · [华东师范大学：2026广西公开分数查询响应 [ecnu-gx-2026-6]](https://zsbcx.ecnu.edu.cn/f/ajax_lnfs) · [华东师范大学：2026广西公开分数查询响应 [ecnu-gx-2026-7]](https://zsbcx.ecnu.edu.cn/f/ajax_lnfs) · [华东师范大学：2026广西公开分数查询响应 [ecnu-gx-2026-8]](https://zsbcx.ecnu.edu.cn/f/ajax_lnfs) · [华东师范大学：公开查询配置或前端页面 [ecnu-home]](https://zsb.ecnu.edu.cn/) · [华东师范大学：公开查询配置或前端页面 [ecnu-init]](https://zsbcx.ecnu.edu.cn/static/front/ecnu/basic/js/init.js) · [华东师范大学：公开查询配置或前端页面 [ecnu-params]](https://zsbcx.ecnu.edu.cn/f/ajax_lnfs_param) · [华东师范大学：公开查询配置或前端页面 [ecnu-tplt]](https://zsbcx.ecnu.edu.cn/static/front/ecnu/basic/js/tplt.js)

### 武汉理工大学（10497）

官方分专业查询广西年份最新2025，2026科类配置仅返回“全部”；按2026广西全部科类实际查询success=true，专业表和省份汇总表均为空。2025同口径正对照37条专业记录（含艺术旧分，仅作对照，不纳入）。本次空返回未当作0分或不招生。

来源：[武汉理工大学：公开查询配置或前端页面 [whut-entry]](https://zs.whut.edu.cn/bkcx/bklqqk/) · [武汉理工大学：2025广西正向对照（不纳入2026） [whut-gx-2025-control]](https://zs.whut.edu.cn/enroll-info/recruitByMajor/selRecruitByProvinceAndYearAndSubjectType.do) · [武汉理工大学：2026广西公开分数查询响应 [whut-gx-2026-all]](https://zs.whut.edu.cn/enroll-info/recruitByMajor/selRecruitByProvinceAndYearAndSubjectType.do) · [武汉理工大学：公开查询配置或前端页面 [whut-query-js]](https://zs.whut.edu.cn/material/static/js/loaddata_lqqk.js) · [武汉理工大学：公开查询配置或前端页面 [whut-tracks-2026]](https://zs.whut.edu.cn/enroll-info/recruitByMajor/selSubjectTypeByProvinceAndYear.do) · [武汉理工大学：公开查询配置或前端页面 [whut-years]](https://zs.whut.edu.cn/enroll-info/recruitByMajor/selYearbyProvince.do)

### 浙江工商职业技术学院（12789）

取得2026官方六省专科录取表完整广西段6条，历史3、物理3，录取6人。只明示高职专科层次，具体批次未核；未明示轮次、组码和再选科目，均保留未知/汇总。其他省及非普通高考不采。

来源：[浙江工商职业技术学院2026年六省高职（专科）录取情况：广西段](https://zs.zbti.edu.cn/a/202687/5547.shtml) · [浙江工商职业技术学院2026年普通高校招生章程](https://zs.zbti.edu.cn/a/2026522/5357.shtml)

### 广西中医药大学（10600）

取得提前批中医学定向医学生72条县区科类记录（历史28条36人、物理44条75人），均有实际最高/最低分和录取数。普通本科两图40行含2预科，高职5行均写首次投档分，不能当作实际专业录取分；本批仅保留其来源和口径说明，不更新实际分库或既有投档分库。

来源：[广西中医药大学2026年广西本科提前批录取情况](https://www.gxtcmu.edu.cn/zs/zsjz/content_88515) · [广西中医药大学2026年中医学定向医学生历史类录取分数原图](https://www.gxtcmu.edu.cn/upload/zs/contentmanage/article/image/2026/07/13/%E6%8F%90%E5%89%8D%E6%89%B9%E5%8E%86%E5%8F%B2%282%29.png) · [广西中医药大学2026年中医学定向医学生物理类录取分数原图](https://www.gxtcmu.edu.cn/upload/zs/contentmanage/article/image/2026/07/13/%E6%8F%90%E5%89%8D%E6%89%B9%E7%89%A9%E7%90%86.png) · [广西中医药大学2026年广西本科普通批情况：原图分数口径为首次投档](https://www.gxtcmu.edu.cn/zs/zsjz/content_88882) · [广西中医药大学2026年本科首次投档专业分原图1](https://www.gxtcmu.edu.cn/upload/zs/contentmanage/article/image/2026/07/30/2cd33541-41f5-46ca-b147-7ccb77df7382.png) · [广西中医药大学2026年本科首次投档专业分原图2](https://www.gxtcmu.edu.cn/upload/zs/contentmanage/article/image/2026/07/30/7f2ca361-8f6a-4bc0-8986-e8b162198d66%282%29.png) · [广西中医药大学2026年广西高职高专普通批情况：原图为首次投档分](https://www.gxtcmu.edu.cn/zs/zsjz/content_89174) · [广西中医药大学2026年高职高专首次投档专业分原图](https://www.gxtcmu.edu.cn/upload/zs/contentmanage/article/image/2026/08/07/c716ba8c-99e7-49f4-9415-ab18963bd920.png) · [广西中医药大学2026年普通本科、高职招生章程](https://www.gxtcmu.edu.cn/zs/zszc/content_87648) · [广西2026年普通高校招生政策百问百答（桂林学院官方转载）](https://www.glc.edu.cn/zsw/info/1008/2891.htm)

### 北京联合大学（11417）

实际读取2026各省普通本科录取最低分页面，广西段第15表只有科类、选考要求及专业组、录取最低分，12行均为专业组口径，无具体专业列；不采入实际专业分。页面其他省的专业分不能迁至广西。

来源：[北京联合大学2026年各省普通本科录取最低分：广西段只有专业组分](https://zs.buu.edu.cn/news/show-1309.html)

### 福建福耀科技大学（14896）

读取本科招生首页、招生政策栏目及2026本科计划正文，明确广西9人、按智能制造工程招生，但所读页面没有2026广西专业实际录取最低分。计划数和入学后可选专业不作为录取分；本轮未覆盖全部官方公众号历史文章，不据此认定学校全渠道未发布。

来源：[福建福耀科技大学：招生官网](https://zsc.fyust.edu.cn/) · [福建福耀科技大学：招生政策栏目](https://zsc.fyust.edu.cn/index/zszc.htm) · [福建福耀科技大学：2026招生计划](https://zsc.fyust.edu.cn/info/1009/2321.htm)

### 大湾区大学（14942）

本科招生页和2026章程明确面向广西，以计算机科学与技术统一招生、后续可选专业；所读页面没有2026广西专业实际最低分。未把其他培养方向分别赋予院校专业组分数，未访问考生个人录取查询，也不宣称遍查了全部官方渠道。

来源：[大湾区大学：2026招生章程](https://www.gbu.edu.cn/tzgg2_details/16.html) · [大湾区大学：招生官网](https://www.gbu.edu.cn/undergraduate.html)

### 北京中医药大学（10026）

现官网链接的公开分数系统菜单最高2025；2026省份和广西科类配置成功返回空列表。按真实省码450000及历史11/物理12查询：历史返回success=false且list=null，物理HTTPS两次及官网原HTTP路径均连接关闭/协议失败，不能说两科专业查询成功为空。2025同接口历史4、物理22条正向对照；响应中的planYear=2026只是计划年份，成绩字段仍为2025。旧静态栏目为2022—2024。

来源：[北京中医药大学：广西 2025 历史类](https://www.51gzb.com/api/zb/score/list.json?sid=33347946-2ced-11e8-a80e-00163e002f0f&year=2025&type=11&province=450000&levelType=01) · [北京中医药大学：广西 2025 物理类](https://www.51gzb.com/api/zb/score/list.json?sid=33347946-2ced-11e8-a80e-00163e002f0f&year=2025&type=12&province=450000&levelType=01) · [北京中医药大学：广西 2026 历史类](https://www.51gzb.com/api/zb/score/list.json?sid=33347946-2ced-11e8-a80e-00163e002f0f&year=2026&type=11&province=450000&levelType=01) · [北京中医药大学：广西 2026 物理类（官网HTTP路径重试）](http://www.51gzb.com/api/zb/score/list.json?sid=33347946-2ced-11e8-a80e-00163e002f0f&year=2026&type=12&province=450000&levelType=01) · [北京中医药大学：广西 2026 物理类（HTTPS重试）](https://www.51gzb.com/api/zb/score/list.json?sid=33347946-2ced-11e8-a80e-00163e002f0f&year=2026&type=12&province=450000&levelType=01) · [北京中医药大学：广西 2026 物理类](https://www.51gzb.com/api/zb/score/list.json?sid=33347946-2ced-11e8-a80e-00163e002f0f&year=2026&type=12&province=450000&levelType=01) · [北京中医药大学：招生官网](https://bkzs.bucm.edu.cn/) · [北京中医药大学：广西2022至2024分数页](https://bkzs.bucm.edu.cn/fsjh/lnfs/13336c7a19a343ba880de3ef2637447b.htm) · [北京中医药大学：省份配置 2025](https://www.51gzb.com/api/zb/score/province.json?sid=33347946-2ced-11e8-a80e-00163e002f0f&year=2025) · [北京中医药大学：省份配置 2026](https://www.51gzb.com/api/zb/score/province.json?sid=33347946-2ced-11e8-a80e-00163e002f0f&year=2026) · [北京中医药大学：公开分数查询页（HTTPS）](https://www.51gzb.com/bucm/zb/bucmScore) · [北京中医药大学：当前公开分数查询页](http://www.51gzb.com/bucm/zb/bucmScore) · [北京中医药大学：历年分数栏目](https://bkzs.bucm.edu.cn/fsjh/lnfs/index.htm) · [北京中医药大学：初始科类查询（后已更正省码） 2025](https://www.51gzb.com/api/zb/score/type.json?sid=33347946-2ced-11e8-a80e-00163e002f0f&year=2025&pro=%E5%B9%BF%E8%A5%BF%E5%A3%AE%E6%97%8F%E8%87%AA%E6%B2%BB%E5%8C%BA) · [北京中医药大学：初始科类查询（后已更正省码） 2026](https://www.51gzb.com/api/zb/score/type.json?sid=33347946-2ced-11e8-a80e-00163e002f0f&year=2026&pro=%E5%B9%BF%E8%A5%BF%E5%A3%AE%E6%97%8F%E8%87%AA%E6%B2%BB%E5%8C%BA) · [北京中医药大学：广西科类配置 2025](https://www.51gzb.com/api/zb/score/type.json?sid=33347946-2ced-11e8-a80e-00163e002f0f&year=2025&pro=450000) · [北京中医药大学：广西科类配置 2026](https://www.51gzb.com/api/zb/score/type.json?sid=33347946-2ced-11e8-a80e-00163e002f0f&year=2026&pro=450000) · [北京中医药大学：年份菜单](https://www.51gzb.com/api/zb/score/year.json?sid=33347946-2ced-11e8-a80e-00163e002f0f)

### 天津医科大学（10062）

录取分数栏目最新文章发布于2026-05-27，标题及PDF实际为2023—2025。已渲染目视核对附件第7页（印刷页6）的广西表，年份列为2025、2024、2023，没有2026。原脚注明普通批含征集，位次来自互联网仅供参考；不把发布时间或旧位次改作2026专业证据。

来源：[天津医科大学：招生官网](https://www.tmu.edu.cn/bkzs/main.htm) · [天津医科大学：最新分数公告（2023至2025）](https://www.tmu.edu.cn/bkzs/2026/0527/c8982a88058/page.htm) · [天津医科大学：2023至2025分数附件](https://www.tmu.edu.cn/_upload/article/files/a9/d3/5ef8666248b28b187342266ddd37/f99bf3b5-c3c0-4bb1-9fbd-526c3af87b84.pdf) · [天津医科大学：历年分数栏目](https://www.tmu.edu.cn/bkzs/8982/list.htm)

### 西南交通大学（10613）

官网导航的历史录取查询菜单只有2025、2024、2023、2022；按真实脚本省份映射构造的2026广西公开文件返回404，2025同格式广西文件可读取具体专业记录。没有把默认安徽表或旧年广西分数转成年份2026；404不等于录取0人，也不证明其他渠道没有公布。

来源：[西南交通大学：广西 2025](https://cjcx.swjtu.edu.cn/admission/admission_2025_ANXIZHUANGZUZIZHIOU.html) · [西南交通大学：广西 2026](https://cjcx.swjtu.edu.cn/admission/admission_2026_ANXIZHUANGZUZIZHIOU.html) · [西南交通大学：招生官网](https://zhaosheng.swjtu.edu.cn/) · [西南交通大学：当前公开分数查询页](https://cjcx.swjtu.edu.cn/admission/default.html) · [西南交通大学：当前公开分数查询页](https://cjcx.swjtu.edu.cn/admission/css/JavaScript.js)

### 西安电子科技大学（10701）

通过主站招生菜单和本科招生页找到当前公开分数前端。广西菜单最高2025；限定长安校区、全部招生类别，2026物理类、历史类、全部科类三次均code200/success=true且list空，2025物理同接口取得17条正向对照。本轮没有将旧年分数、计划年份或汇总投档线改成2026专业最低分。

来源：[西安电子科技大学：主站招生导航](https://www.xidian.edu.cn/zsjy.htm) · [西安电子科技大学：公开查询配置脚本](https://zsxc.xidian.edu.cn/auth/zsdata/lqxx/js/app.c9746a4c.js) · [西安电子科技大学：2026计划与近三年分数栏目](https://zsb.xidian.edu.cn/info/1073/6893.htm) · [西安电子科技大学：广西 2025-物理类](https://zsxc.xidian.edu.cn/lqxx/s/api/front/lqxx/getList) · [西安电子科技大学：广西 2026-全部](https://zsxc.xidian.edu.cn/lqxx/s/api/front/lqxx/getList) · [西安电子科技大学：广西 2026-历史类](https://zsxc.xidian.edu.cn/lqxx/s/api/front/lqxx/getList) · [西安电子科技大学：广西 2026-物理类](https://zsxc.xidian.edu.cn/lqxx/s/api/front/lqxx/getList) · [西安电子科技大学：招生官网](https://www.xidian.edu.cn/) · [西安电子科技大学：当前公开分数查询页](https://zsxc.xidian.edu.cn/auth/zsdata/lqxx/) · [西安电子科技大学：公开查询字段脚本](https://zsxc.xidian.edu.cn/auth/zsdata/lqxx/js/lqcxjg.13a6cba5.js) · [西安电子科技大学：年份与类别配置](https://zsxc.xidian.edu.cn/lqxx/s/api/front/lqxx/getType) · [西安电子科技大学：本科招生官网](https://zsb.xidian.edu.cn/)

## 复现

各batch目录按自身README获取公开资料并重建；独立复核程序同样需要相应的原始资料，仅发布PUBLIC-FILES.json列出的文件。复查时官网材料可能变化，需要重新核对结果，不能沿用本轮缺口结论。

在仓库根目录执行：

```sh
python3 docs/major-scores-2026-09-12/merge_batches.py
node scripts/import-major-score-batch.mjs docs/major-scores-2026-09-12
```

第二步只作增量预检；审阅完成后加`--apply`才写入。首次应用本批后，可核对发布基线和既有数据保护：

```sh
node scripts/report-score-review.mjs docs/major-scores-2026-09-12 db59aaf071965e814fe13dccb0f0c5eb73b2e7ac
npm test
npm run check
```

后续增量应另建报告并采用对应的新基线，本轮历史基线检查不会自动适用于将来的数据版本。
