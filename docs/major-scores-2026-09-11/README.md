# 2026 广西专业录取分缺口续查

核查日期：2026-09-11（北京时间）。本轮核查30个院校条目，按分数优先复查其中20所尚未收录专业分的学校，再补充其他已经取得官方结果的学校。[前后统计与既有数据保护检查](summary.json) · [20校优先目标](targets.json)

## 本轮结果

新增6校132条专业或正式招生大类的实际录取最低分，均通过普通高考750分尺度及原表数值检查。全站由17校816条增至23校948条；原有3条分数冲突继续保留原值并停用比较。记录数包含同专业的不同科类和招生类别，不等于独立专业数。

| 院校 | 新增记录 | 物理 | 历史 | 公布位次 | 主要缺口 |
|---|---:|---:|---:|---:|---|
| 中央民族大学 | 35 | 17 | 18 | 35 | 35条组码、精确批次和轮次未明；民族班、国家专项、合作项目分开保留 |
| 西交利物浦大学 | 3 | 2 | 1 | 0 | 3个正式招生大类，不能拆给大类内每个专业；组码、精确批次和轮次未明 |
| 江西水利电力大学 | 18 | 15 | 3 | 0 | 18条原表位次存在跨行次序疑点，保留原值但待核；含2条定向军士 |
| 四川旅游学院 | 5 | 3 | 2 | 0 | 5条组码由原表直接给出；轮次未分，合作项目条件保留 |
| 山西大同大学 | 8 | 5 | 3 | 0 | 组码、轮次及原表未列的选科要求待核 |
| 福建商学院 | 63 | 37 | 26 | 0 | 2页广西表63行；选科组合文字不是组码，轮次未分 |

132条全部保留“录取汇总（轮次未分）”，不能理解为首轮。127条组码为空，38条精确批次待核，不按相似分数或选科猜测。中央民族大学35条最低分排名直接取自校方专业表；江西水利电力大学18条原位次保存在详情的待核字段，未按分数倒改位次或分数。

6校里有民族班、国家专项、合作办学和定向军士。具体招生资格、语言或单科条件、体检、培养与转专业限制按已核实的章程保留。西交利物浦原表的计划人数和实际录取人数分别读取；本次没有向招生计划库新增或改写人数。

## 尚未取得的资料

优先目标20校均已实查，本轮均未取得可入库的2026广西单专业分数。优先级使用各校符合筛选条件的首轮专业组最高分（664至643分），只是安排查找次序，不能理解为该校最低分。

另查的长春工业大学、曲靖师范学院、四川师范大学、湖州学院也未取得合格专业分。合计24个本轮核查条目仍没有新增分数。查询空、访问受限、年份缺口和只有学校/组汇总分别记录；不能据此宣称学校在任何渠道都没有公布。

典型年份陷阱包括：东南、复旦医学院在2026发布的分数表实际为2025；华北电力北京的专业JSON虽在2026生成，全部1308条仍属于2025；长春工业默认查询有2026吉林数据，广西年度选项却仅到2025。这些均没有进入本年广西分数库。重庆2026配置返回应用错误，没有写成成功的空录取列表。

## 页面与校验

详情补充招生与培养要求、位次原值及字段来源；没有明确组码的选科文字仍按选科展示。普通类筛选会排除民族班、国家专项和定向军士等已识别资格条件。核查日期按北京时间显示，最新核查日期不表示全库同日重查。

17项自动测试、数据检查及真实数据页面交互验证通过，包括新收录高校的位次来源、日期、招生大类条件、未知组码和定向军士筛选。交互验证使用jsdom，不声称完成浏览器截图视觉检查。原有816条专业分逐条未改；投档线、计划、一分一档、强基与竞赛、征集计划等8个其他数据文件与发布基线逐字节一致。

[新增分数的独立原源复核](independent-review/REVIEW.md) · [无新增结果的独立核查](gap-review/gap-review.md)。每个采集包另有核验记录和公开白名单；原始网页、PDF、图像及会话内容仅留本地。

## 逐校核查记录

### 四川大学（10610）

四川大学招生网及当前分数索引均返回HTTP 412；公开分数查询系统返回HTTP 483，正文提示访问策略禁止访问。学院可读目录链接的是截止2025年的分数统计。未取得2026广西分专业录取数据。

来源：[四川大学本科招生网](https://zs.scu.edu.cn/) · [四川大学化学工程学院：历年招生数据](https://cpse.scu.edu.cn/zsjy/zsxx/bkszs/lnsj.htm) · [四川大学本科录取历年分数统计（截止2025年）](https://zs.scu.edu.cn/info/1105/3314.htm) · [四川大学公开录取分数查询入口](https://zjczs.scu.edu.cn/aoadmin/#/scu-enrollscorew)

### 西安交通大学（10698）

历年录取查询URL正常GET返回HTTP 200，但正文是访问验证/网站正在加载中页面，未取得专业查询表；本次未执行或绕过验证挑战。未取得2026广西分专业录取数据。

来源：[西安交通大学历年录取查询入口](https://zs.xjtu.edu.cn/bkscx/lnlqcx.htm)

### 哈尔滨工业大学(深圳)（18213）

公开历年分数前端已读取并实际查询年份接口，仅返回2025和2024，没有2026所需的年份ID。未猜测年份ID，未提交伪造2026参数；本轮没有2026广西专业分可采。

来源：[哈尔滨工业大学（深圳）报考指南](https://zsb.hitsz.edu.cn/zs_common/bkzn/zswz?flbs=2) · [哈尔滨工业大学（深圳）历年分数查询前端](https://zsb.hitsz.edu.cn/zs_common/bkzn/zswz/lnfs) · [哈尔滨工业大学（深圳）历年分数年份选项](https://zsb.hitsz.edu.cn/zs_common/bkzn/ndDmx1)

### 东南大学（10286）

广西官方目录的本年资料为2026招生计划；最新可读分专业录取表虽在2026-01-13发布，正文年份是2025。2026录取进度公告不列专业分。未将计划或旧年分数拼成2026记录。

来源：[东南大学广西壮族自治区招生资料目录](https://zsb.seu.edu.cn/gxzzzzq/listm.htm) · [东南大学2025年广西壮族自治区各专业分数线](https://zsb.seu.edu.cn/2026/0113/c23741a552222/pagem.htm) · [东南大学2026本科招生录取进度表（截至2026年7月28日）](https://zsb.seu.edu.cn/2026/0714/c23610a576713/pagem.htm)

### 中南大学（10533）

已读取本科普通类公开前端和接口配置。当前年份选项为2020至2025；使用前端公开字段分别请求2026/广西/物理类、历史类，均成功返回code=200、list=[]、total=0。没有分页遗漏或专业分入库；不能据空结果断言校方所有渠道均未发布。

来源：[中南大学本科普通类历年分数查询](https://zhaosheng.csu.edu.cn/lnfs/bkptl.htm) · [中南大学本科普通类录取结果公示：公开查询配置](https://job-web-api.jobpi.cn/enroll/config/v2/2614?sch_school_id=21393) · [中南大学2026广西历史类普通本科专业分查询](https://job-web-api.jobpi.cn/enroll/2614?sch_school_id=21393&page=1&page_size=9999&filter_column=%7B%22A%22%3A2026%2C%22B%22%3A%22%E5%B9%BF%E8%A5%BF%22%2C%22C%22%3A%22%E5%8E%86%E5%8F%B2%E7%B1%BB%22%7D) · [中南大学2026广西物理类普通本科专业分查询](https://job-web-api.jobpi.cn/enroll/2614?sch_school_id=21393&page=1&page_size=9999&filter_column=%7B%22A%22%3A2026%2C%22B%22%3A%22%E5%B9%BF%E8%A5%BF%22%2C%22C%22%3A%22%E7%89%A9%E7%90%86%E7%B1%BB%22%7D)

### 北京邮电大学（10013）

本科招生网及检索发现的旧年分数公告入口均返回HTTP 412，未取得可读专业表。旧年检索条目不当作2026录取分；本轮未取得2026广西专业实际录取数据。

来源：[北京邮电大学本科招生网](https://zsb.bupt.edu.cn/) · [北京邮电大学2024年各省录取时间及分数线入口](https://zsb.bupt.edu.cn/info/1003/2386.htm)

### 复旦大学医学院（19246）

官方分数目录最新可读表为2025年分省录取分数，2026-01-21发布；表中医学院列主要为院校科类汇总，不能当作2026单专业分数。2026章程明确本部与医学院招生分别实施；本包保留医学院独立代码19246。

来源：[复旦大学分省录取分数目录](https://ao.fudan.edu.cn/36333/list.htm) · [复旦大学2025年分省录取分数（含医学院列）](https://ao.fudan.edu.cn/b7/a6/c36333a767910/page.htm) · [复旦大学2026年本科招生章程](https://news.fudan.edu.cn/2026/0528/c4a149374/page.htm)

### 中央民族大学（10052）

2026广西物理/历史公开分专业接口采得35条：普通本科28、民族班5、国家专项1、合作办学1。六个科类类别响应均核对total等于rows长度，完整采集本次公开选项下的35条；体育科类未进入采集。保留专业最低分排名与资格限制；仍缺省编组码、精确批次、分轮次及录取人数，不宣称全部招生项目已覆盖。

来源：[中央民族大学录取分数查询](https://zb.muc.edu.cn/content/zs/b7079c38-91e5-11f0-98a5-6c92bf4353bb.htm) · [中央民族大学2026广西录取科类选项](https://zb.muc.edu.cn/query/findKlList.json) · [中央民族大学2026广西历史类招生类型选项](https://zb.muc.edu.cn/query/findLxList.json) · [中央民族大学2026年本、预科招生章程](https://zb.muc.edu.cn/content/zs/93108d8f-5802-11f1-98a5-6c92bf4353bb.htm) · [中央民族大学2026广西历史类普通本科分专业录取情况](https://zb.muc.edu.cn/query/findAdmissionScore.json)

### 西交利物浦大学（16302）

2026年分省录取数据正文的广西表采得3个正式招生大类、实际录取110人（历史21、物理89）。计划数与录取数分别转录。URL含2023但当前h1为2026。学校按大类招生，大类名不等于入学后具体专业；组列是选科组合，省编组码及分轮次仍缺，具体批次名称待核。

来源：[西交利物浦大学2026年分省录取数据](https://www.xjtlu.edu.cn/zh/admissions/domestic/ug/2023luqushuju) · [西交利物浦大学招生政策](https://www.xjtlu.edu.cn/zh/admissions/ug/domestic/admission-policy) · [西交利物浦大学2026年中国内地本科招生章程](https://www.xjtlu.edu.cn/wp-content/uploads/2026/05/8988b8e1529327ca85e0f611494aa080.pdf)

### 南方医科大学（12121）

官方往年分数入口提供2025/2024/2023。公开表单配置明确无需登录、无需短信验证码；按页面真实字段、广西、2026及不限定科类/类别查询，HTTP 200、业务码9999并明确“未查询到相关数据”。同样广西2025查询得到22条，仅作接口正向对照，不计入2026专业分。

来源：[南方医科大学官方专业分资料复查：smu-entry](https://portal.smu.edu.cn/bkzs/bkzn/wnfs.htm) · [南方医科大学官方专业分资料复查：smu-query-config](https://portal.smu.edu.cn/aop_component//webber/formquery/query/front/items/get) · [南方医科大学官方专业分资料复查：smu-gx-2025-all](https://portal.smu.edu.cn/aop_component//webber/formquery/data/get/info)

### 武汉大学（10486）

从本校主页进入公开分数查询并读取当前前端。广西配置最新2025，物理/历史及普通、单设投档、国家专项等均无2026配置。按真实JSON参数查2026广西、校本部、全部类别，物理/历史/全部三个请求均成功返回空list。初次误用form的500已用前端JSON请求纠正，未把500当作未发布证据。

来源：[武汉大学官方专业分资料复查：whu-home](https://aoff.whu.edu.cn/) · [武汉大学官方专业分资料复查：whu-entry](https://zsdata.whu.edu.cn/public/wzgl/) · [武汉大学官方专业分资料复查：whu-app](https://zsdata.whu.edu.cn/public/wzgl/js/app.a1258ec5.js) · [武汉大学官方专业分资料复查：whu-types-json](https://zsdata.whu.edu.cn/wzgl/wxmini/api/front/lqxx/getType) · [武汉大学官方专业分资料复查：whu-gx-2026-物理类](https://zsdata.whu.edu.cn/wzgl/wxmini/api/front/lqxx/getList)

### 西北工业大学（10699）

本科招生入口直接访问和网页读取均返回HTTP 412，未取得分专业查询配置。已读学校官网2026本科招生工作总结，虽有广西650分/1150位次，但表格按省汇总全校物理类，不是具体专业或正式招生大类最低分，未导入专业线。本次尚不能判断该校其他官方入口是否已公开2026专业分。

来源：[西北工业大学官方专业分资料复查：nwpu-home](https://zsb.nwpu.edu.cn/) · [西北工业大学官方专业分资料复查：nwpu-2026-summary](https://www.nwpu.edu.cn/info/1208/125738.htm)

### 天津大学（10056）

从官方主页链接进入历年分数，前端明确实际API仍为/lqxx/s/。广西配置只有2025北洋园校区、物理/全部，类别含普通、国家专项、高校专项；没有2026。按2026广西、北洋园校区、全部类别查询物理/历史/全部，均HTTP 200且success=true，list和sumList为空。未把历史空结果推定为该校不招历史。

来源：[天津大学官方专业分资料复查：tju-home](https://zs.tju.edu.cn/) · [天津大学官方专业分资料复查：tju-entry](https://zsdata.tju.edu.cn/zsdata/lqxx/) · [天津大学官方专业分资料复查：tju-app](https://zsdata.tju.edu.cn/zsdata/lqxx/js/app.5e99a1d9.js) · [天津大学官方专业分资料复查：tju-component](https://zsdata.tju.edu.cn/zsdata/lqxx/js/lqcxjg.6cb03fa5.js) · [天津大学官方专业分资料复查：tju-types](https://zsdata.tju.edu.cn/lqxx/s/api/front/lqxx/getType) · [天津大学官方专业分资料复查：tju-gx-2026-物理类](https://zsdata.tju.edu.cn/lqxx/s/api/front/lqxx/getList)

### 南京航空航天大学（10287）

当前录取分数页的公开年份API最新2025；2026可选省份为空。按前端真实year/sf/kl字段查询2026广西物理类及历史类、不限定类别，均成功返回空data。查询的是getAdmissionScore逐专业接口，没有把getAdmissionScoreOverview概况当成专业分。

来源：[南京航空航天大学官方专业分资料复查：nuaa-entry](https://zs.nuaa.edu.cn/lnlqfs/list.psp) · [南京航空航天大学官方专业分资料复查：nuaa-years](https://zsservice.nuaa.edu.cn/zsw-admin/api/admissionScore/years) · [南京航空航天大学官方专业分资料复查：nuaa-2026-provinces](https://zsservice.nuaa.edu.cn/zsw-admin/api/admissionScore/provinces?year=2026) · [南京航空航天大学官方专业分资料复查：nuaa-gx-2026-物理类](https://zsservice.nuaa.edu.cn/zsw-admin/api/getAdmissionScore?year=2026&sf=%E5%B9%BF%E8%A5%BF&kl=%E7%89%A9%E7%90%86%E7%B1%BB) · [南京航空航天大学官方专业分资料复查：nuaa-gx-2026-历史类](https://zsservice.nuaa.edu.cn/zsw-admin/api/getAdmissionScore?year=2026&sf=%E5%B9%BF%E8%A5%BF&kl=%E5%8E%86%E5%8F%B2%E7%B1%BB)

### 哈尔滨工业大学(威海)（19213）

威海校区官方分数页及广西配置均只列2025/2024/2023；2026广西年份查询成功返回空类别、空招生类型及空list。原系统广西科类名为“综改”，未擅自拆成物理/历史。另核校本部官网广西三校区汇总表，2026列是计划，最高/平均/最低对应2025及2024，不能把2026计划表头误套到旧分。威海代码19213独立保留，不与10213本部混并。

来源：[哈尔滨工业大学(威海)官方专业分资料复查：hitwh-home](https://zsb.hitwh.edu.cn/) · [哈尔滨工业大学(威海)官方专业分资料复查：hitwh-entry](https://zsb.hitwh.edu.cn/home/query/score) · [哈尔滨工业大学(威海)官方专业分资料复查：hitwh-gx-2025-config](https://zsb.hitwh.edu.cn/api/score_qb_province) · [哈尔滨工业大学(威海)官方专业分资料复查：hitwh-gx-2026-config](https://zsb.hitwh.edu.cn/api/score_qb_year) · [哈尔滨工业大学(威海)官方专业分资料复查：hit-summary-gx](https://zsb.hit.edu.cn/information/summary?province=%E5%B9%BF%E8%A5%BF)

### 同济大学（10247）

已读取同济官方前端的公开查询流程、字段和签名算法，按正常未登录请求查询。年份API最新2025；实际专业录取接口以year=2026、provinceCode=45、pageIndex=1/pageSize=50查询，isSuccess=true但totalCount=0、items=[]。请求不限定科类及类别，故空结果不是只查某一科类；未使用个人登录令牌，也未保存会话值。

来源：[同济大学官方专业分资料复查：tongji-entry](https://bkzs.tongji.edu.cn/luqu/admission) · [同济大学官方专业分资料复查：tongji-js-2574580](https://bkzs.tongji.edu.cn/pc/2574580.js) · [同济大学官方专业分资料复查：tongji-js-373d896](https://bkzs.tongji.edu.cn/pc/373d896.js) · [同济大学官方专业分资料复查：tongji-js-5e0cf47](https://bkzs.tongji.edu.cn/pc/5e0cf47.js)

### 江西水利电力大学（11319）

本轮采集18条2026广西单专业实际录取最低分，所有数值逐行对应官方原表，未用学校或专业组投档线代替专业录取分。完整覆盖列明原表的广西普通高考专业行；未证明覆盖学校全年全部录取轮次。其中2条为定向培养军士，单独保留资格类别；原表位次跨行次序有不一致，rank全部留空、原值放sourceMinimumRank供核查，不参与位次比较。

来源：[江西水利电力大学2026年广西本科批录取公告](https://envo.juwp.edu.cn/info/1185/6212.htm) · [江西水利电力大学2026年广西高职高专提前批定向类录取公告](https://envo.juwp.edu.cn/info/1185/6502.htm) · [江西水利电力大学2026年普通高考招生章程](https://envo.juwp.edu.cn/info/1186/5432.htm)

### 四川旅游学院（11552）

本轮采集5条2026广西单专业实际录取最低分，所有数值逐行对应官方原表，未用学校或专业组投档线代替专业录取分。完整覆盖列明原表的广西普通高考专业行；未证明覆盖学校全年全部录取轮次。

来源：[四川旅游学院2026年在广西普通本科批次录取结束](https://www.sctu.edu.cn/zsjyc/info/1018/2267.htm) · [四川旅游学院2026年普通高等教育本专科招生章程](https://www.sctu.edu.cn/zsjyc/info/1017/2114.htm)

### 山西大同大学（10120）

本轮采集8条2026广西单专业实际录取最低分，所有数值逐行对应官方原表，未用学校或专业组投档线代替专业录取分。完整覆盖列明原表的广西普通高考专业行；未证明覆盖学校全年全部录取轮次。

来源：[山西大同大学2026年本科招生录取进展（四）](https://zhs.sxdtdx.edu.cn/news-show-431.html) · [山西大同大学2026年本科招生章程](https://zhs.sxdtdx.edu.cn/news-show-421.html)

### 福建商学院（11313）

本轮采集63条2026广西单专业实际录取最低分，所有数值逐行对应官方原表，未用学校或专业组投档线代替专业录取分。完整覆盖列明原表的广西普通高考专业行；未证明覆盖学校全年全部录取轮次。

来源：[福建商学院2026年广西壮族自治区本科专业招生录取情况表（公告页）](https://zsb.fjbu.edu.cn/info/1121/7711.htm) · [福建商学院2026年本科专业招生录取情况表（广西-143，2页PDF）](https://zsb.fjbu.edu.cn/__local/6/73/99/6446D4758253177993062B3978B_A3A99843_2175D.pdf) · [福建商学院2026年普通高考招生章程](https://zsb.fjbu.edu.cn/info/1161/7611.htm)

### 长春工业大学（10190）

已按公开JS的省份/层次/年份级联接口核查：广西本科年份选项只含2025—2020；2026广西科类返回空，直接2026广西本科表单也无结果。默认页的2026吉林专业数据未入库。

来源：[长春工业大学历年分数公开查询入口](https://bzkzs.ccut.edu.cn/lnsfx.jsp?urltype=tree.TreeTempUrl&wbtreeid=1077) · [长春工业大学历年分数省份选项](https://bzkzs.ccut.edu.cn/system/resource/importdata/getData.jsp?sf=) · [长春工业大学广西本科历年分数年份选项](https://bzkzs.ccut.edu.cn/system/resource/importdata/getData.jsp) · [长春工业大学2026广西本科分数查询结果](https://bzkzs.ccut.edu.cn/lnsfx.jsp?wbtreeid=1077)

### 曲靖师范学院（10684）

2026进度页显示广西普通类7月21日录取结束，公告标题为无链接文本；历年分数栏目最新全日制本科分省分专业表为2025。未将录取进度或2025统计作2026专业分。

来源：[曲靖师范学院2026年录取进度](https://zs.qjnu.edu.cn/contents/12912/182913.html) · [曲靖师范学院历年录取分数栏目](https://zs.qjnu.edu.cn/channels/12914.html)

### 四川师范大学（10636）

公开招生首页及公告栏目本轮返回WAF安全助手环境检查页；HTTPS、HTTP均未取得正文，当前无可用浏览器。搜索结果显示2026广西普通本科录取结束公告线索，但未以摘要拼接数据。

来源：[四川师范大学招生信息最新公告入口（访问受限）](https://zs.sicnu.edu.cn/SubPage.aspx?Id=2)

### 湖州学院（13287）

官方2026广西普通录取快讯仅给出物理/历史科类整体最高最低分，并注明正投不含征集；无单专业实际最低分，未导入该汇总数。

来源：[湖州学院2026年广西普通类录取快讯](https://zsw.zjhzu.edu.cn/2026/0725/c16a43436/page.htm)

### 华南理工大学（10561）

官方年份菜单为2025/2024/2023；按页面实际字段分别查询2026广西普通类物理、历史，均返回“没有您想要的查询结果”，2025两科正向对照有记录。另一个最新分数公告栏目发布于2026的广西文章，实际数据年为2025。不将计划、旧年分或空结果用作2026专业最低分。

来源：[华南理工大学：录取分数查询入口](https://admission.scut.edu.cn/30821/list.htm) · [华南理工大学：公开查询字段与菜单](https://admission.scut.edu.cn/_web/_apps/commonquery/commonquery/api/queryMatch/16.rst?_p=YXM9MzQ4JnQ9MTcyMyZwPTEmbT1OJg__&mongo=false) · [华南理工大学：最新录取分数公告目录](https://admission.scut.edu.cn/lqzdfstj/list.htm) · [华南理工大学：广西 2026-物理类](https://admission.scut.edu.cn/_web/_apps/commonquery/commonquery/api/commonqueryCacheResult/16.rst?_p=YXM9MzQ4JnQ9MTcyMyZwPTEmbT1OJg__&mobileTemplate=false)

### 电子科技大学（10614）

当前官方公开分数菜单广西年份最高2025。按前端实际JSON字段查询2026广西普通类、本部、物理及历史，两次code200且专业列表空；2025物理正向对照有结果。校区字段已限定本部，不将沙河校区或旧年分数混入。其他资格类别的2026记录本轮未取得。

来源：[电子科技大学：招生官网](https://zs.uestc.edu.cn/) · [电子科技大学：公开查询字段与菜单](https://chaxun.uestc.edu.cn/public/zsdata/lqxx/) · [电子科技大学：查询页面脚本](https://chaxun.uestc.edu.cn/public/zsdata/lqxx/js/app.b9fb24b1.js) · [电子科技大学：分数查询页面脚本](https://chaxun.uestc.edu.cn/public/zsdata/lqxx/js/lqcxjg.7ac4330b.js) · [电子科技大学：分数查询年份及类别](https://chaxun.uestc.edu.cn/lqxx/s/api/front/lqxx/getType) · [电子科技大学：广西 2026-物理类](https://chaxun.uestc.edu.cn/lqxx/s/api/front/lqxx/getList)

### 重庆大学（10611）

官方年份菜单只有2025/2024/2023。按页面实际接口请求2026查询配置，返回应用code500且msg为空，不能建立本年专业查询；2025同接口code0且字段/广西选项完整。属于本年配置不可用的证据，不冒称2026查询成功但零录取，也不以强基综合分或全校最低分替代。

来源：[重庆大学：录取分数查询入口](https://zhaosheng.cqu.edu.cn/pub/desktopend/queryadmitline) · [重庆大学：公开查询字段与菜单](https://zhaosheng.cqu.edu.cn/pagejs/pub/desktopend/querydata/listqueryitem1.js?v=20260726) · [重庆大学：查询配置 2026](https://zhaosheng.cqu.edu.cn/pub/share/getQueryConditionByAdmitLine)

### 华北电力大学(北京)（10054）

官网分数页直接读取公开JSON，全量1308条专业记录和114条院校汇总记录的数据年均为2025，其中广西分别43条和5条。JSON生成时间为2026不改变其表内年份；本轮未取得2026广西专业线。北京与保定使用独立入口及院校代码，不混用。

来源：[华北电力大学(北京)：招生官网](https://goto.ncepu.edu.cn/) · [华北电力大学(北京)：录取分数查询入口](https://goto.ncepu.edu.cn/wnfs/index.htm) · [华北电力大学(北京)：公开查询字段与菜单](https://goto.ncepu.edu.cn/js/json_filter_2.js?v=1788977662928) · [华北电力大学(北京)：分专业录取数据（2025）](https://goto.ncepu.edu.cn/common/major_json.json) · [华北电力大学(北京)：录取汇总数据（2025）](https://goto.ncepu.edu.cn/common/aii_json.json)

### 南开大学（10055）

招生主站直接读取403；通过官网导航的独立录取查询站正常公开会话流程已成功读取年份菜单及分数接口。广西菜单只有2025/2024，本科普通批2026物理、历史均state1且学校/专业列表为空，2025物理有正向对照。访问限制与查询结果分别记录，不用2024招生宣传附件补充2026分数。

来源：[南开大学：招生官网](https://zsb.nankai.edu.cn/) · [南开大学：录取分数查询入口](https://zsb.nankai.edu.cn/Baokao/fenshu.html) · [南开大学：官方分数查询](https://lqcx.nankai.edu.cn/zsw/lnfs.html) · [南开大学：分数查询年份菜单](https://lqcx.nankai.edu.cn/f/ajax_lnfs_param) · [南开大学：广西 2026-物理类](https://lqcx.nankai.edu.cn/f/ajax_lnfs)

### 中国药科大学（10316）

官方年份选项最新2025；按页面查询脚本的省份f8=广西、年份f7=2026请求，成功响应但total0/data空，2025广西正向对照有结果。默认分数表未展示年份和省份，不能因页面导航写2026招生计划而将默认表中的专业分误标为2026广西。

来源：[中国药科大学：录取分数查询入口](https://zb.cpu.edu.cn/fs/listm.htm) · [中国药科大学：官方分数查询](https://zb.cpu.edu.cn/_upload/tpl/03/37/823/template823/search_lqfs.js) · [中国药科大学：广西 2026](https://zb.cpu.edu.cn/_wp3services/generalQuery?queryObj=articles)

## 复现

在各batch目录按照README重建并复核。公开包只保留PUBLIC-FILES.json或PUBLIC_FILES.json列出的文件。之后在仓库根目录执行：

```sh
python3 docs/major-scores-2026-09-11/merge_batches.py
node scripts/import-major-score-batch.mjs docs/major-scores-2026-09-11
```

第二步为增量预检；审核后加`--apply`才写网站。不要用旧研究结果覆盖新审查结论。首次应用本批后，使用以下命令核对原有记录和其他资料未变：

```sh
node scripts/report-score-review.mjs docs/major-scores-2026-09-11 9a5821c939a8a846e63cafd230a609a8de0f10aa
npm test
npm run check
```

历史基线检查在后续新增数据后可能不再适用，应给下一批另建报告并指定对应基线。
