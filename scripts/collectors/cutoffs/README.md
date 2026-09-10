# 普通批与专业录取数据重建

三个程序均只依赖 Python 3.9+ 标准库。建议复制本目录到独立工作目录后顺序运行：

```sh
python3 collect.py --refresh
python3 collect-additional-major.py --refresh
```

第一步获取2026年16张考试院普通批表；第二步获取5所高校的专业录取公告和已明确列出的计划数。第二步会导入 `collect-major.py`，并读取第一步输出以核对专业组和原文冲突。原始下载存入 `raw/`，无需上传仓库。

输出包括 `cutoffs-all.json`、`cutoffs-first-round.json`、`cutoffs-supplementary.json`、`major-cutoffs.json`、`plans-supplement.json`、来源与质量报告。生成结果需核对再导入网站，不会自动发布。

专业录取公告中的计划数不等于已验证的最初版招生计划；该区别保留在 `planBasis` / `note`。同校、同科类、同批次已有独立招生计划时，网站不再把录取公告计划作为重复计划加入，但专业录取详情仍保留原公告的计划与录取人数。
