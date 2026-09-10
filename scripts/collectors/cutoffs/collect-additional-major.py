#!/usr/bin/env python3
"""Reproduce the five-school 2026 Guangxi official major-outcome supplement.

Run without flags to rebuild from local evidence. --refresh downloads the same
official source pages first. This is the complete major-data rebuild entrypoint.
"""
import argparse
import collections
import datetime as dt
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import urllib.request

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("base_major", ROOT / "collect-major.py")
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)

RAW_SOURCES = {
    "ylu-2026-7162.html": "https://zjw.ylu.edu.cn/info/1013/7162.htm",
    "nepu-2026.html": "https://zsxxw.nepu.edu.cn/info/1164/10476.htm",
    "qqhru-2026.html": "https://zs.qqhru.edu.cn/info/1140/4903.htm",
    "cqie-plan-2026.html": "https://www.cqie.edu.cn/html/7/content/26/06/78111.shtml",
    "cqie-2026.html": "https://zs.cqie.edu.cn/html/7/content/26/07/78849.shtml",
    "sdjtu-2026-7012.html": "https://zsw.sdjtu.edu.cn/info/1012/7012.htm",
}


def read_table(filename, encoding="utf-8"):
    raw = (ROOT / "raw" / filename).read_bytes()
    text = raw.decode(encoding)
    assert "2026" in text
    parser = base.Tables()
    parser.feed(text)
    assert len(parser.tables) == 1, filename
    return base.expand(parser.tables[0])


def source(source_id, name, filename, title, url, date, count, notes):
    path = ROOT / "raw" / filename
    return {"id": source_id, "title": title, "url": url, "publisher": name,
            "publishedAt": date, "accessedAt": dt.datetime.fromtimestamp(path.stat().st_mtime, dt.timezone.utc).isoformat(),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "recordCount": count,
            "method": "Official HTML table; expand declared rowspan/colspan; preserve original score and headcount meanings; validate numeric columns and source totals.",
            "rawPath": "raw/" + filename, "notes": notes}


def norm_major(name):
    return re.sub(r"\s+", "", name).replace("（", "(").replace("）", ")")


def main():
    rows, ylu_source, ylu_qa = base.ylu()
    sources = [ylu_source]
    reports = [ylu_qa]
    plans = []
    for r in rows:
        if r["round"] == "首轮" and r["plannedCount"] is not None:
            plans.append({"id": "plan-" + r["id"], "year": 2026, "schoolCode": r["schoolCode"],
                          "school": r["school"], "track": r["track"], "batch": r["batch"], "group": r["group"],
                          "major": r["major"], "majorCode": None, "requiredSubjects": [], "subjectRule": "unknown",
                          "plannedCount": r["plannedCount"], "tuition": None, "duration": None,
                          "note": r["note"] + "计划来自正投行，不包含征集附行；不是录取前最初版计划存档。",
                          "sourceId": r["sourceId"], "category": r["admissionType"], "requirementText": None,
                          "round": "首轮", "planBasis": "正投录取公告中的计划数（非征集剩余；未核实最初发布版）"})

    nepu = read_table("nepu-2026.html")
    assert nepu[0] == ["省份", "科类", "批次", "计划类型", "专业名称", "计划数", "录取数", "最高分", "最低分", "平均分"]
    nepu_records = []
    for row_number, r in enumerate(nepu[1:], 2):
        assert r[0] == "广西" and r[2] == "本科批" and r[3] == "普通类"
        if r[4] == "整体":
            continue
        assert all(re.fullmatch(r"\d+", r[i]) for i in [5, 6, 7, 8])
        assert int(r[8]) <= float(r[9]) <= int(r[7])
        record = {"id": f"major-2026-nepu-r{row_number}", "year": 2026,
                  "school": "东北石油大学", "schoolCode": "10220", "track": r[1].replace("类", ""),
                  "batch": "本科普通批", "group": None, "major": r[4], "score": int(r[8]),
                  "scoreType": "专业录取最低分", "plannedCount": int(r[5]), "admittedCount": int(r[6]),
                  "sourceId": "nepu-2026-10476", "round": "录取汇总（轮次未分）", "admissionType": "普通类",
                  "note": "普通类本科批录取公示；原表列计划数与录取数，已分别保存。专业组及选科要求未公布，未据分数推定；原文未逐行拆分录取轮次。",
                  "sourceRow": row_number}
        nepu_records.append(record)
        plans.append({"id": "plan-" + record["id"], "year": 2026, "schoolCode": "10220", "school": record["school"],
                      "track": record["track"], "batch": "本科普通批", "group": None, "major": r[4], "majorCode": None,
                      "requiredSubjects": [], "subjectRule": "unknown", "plannedCount": int(r[5]), "tuition": None,
                      "duration": None, "note": "来自普通批录取公示的计划数列，非录取人数换名，非征集剩余计划；未核实录取前最初版。",
                      "sourceId": record["sourceId"], "category": "普通类", "requirementText": None,
                      "round": "普通批计划", "planBasis": "普通批录取公示中的计划数（非征集剩余；未核实最初发布版）"})
    assert len(nepu_records) == 56
    for track, expected in [("物理", 166), ("历史", 24)]:
        assert sum(r["plannedCount"] for r in nepu_records if r["track"] == track) == expected
        assert sum(r["admittedCount"] for r in nepu_records if r["track"] == track) == expected
    rows.extend(nepu_records)
    sources.append(source("nepu-2026-10476", "东北石油大学招生办", "nepu-2026.html", "2026年广西本科普通批录取公示",
                          "https://zsxxw.nepu.edu.cn/info/1164/10476.htm", "2026-07-24", 56,
                          ["物理类计划及录取均166人，历史类均24人；逐专业相加与原表整体行一致。", "未公布专业组及再选科目。计划列属于录取阶段公示，未核实最初发布计划版本。", "原文未拆分首轮与征集，不能标成纯首轮专业线。", "详细录取信息请登录各省市招考院网站查询。 "]))
    reports.append({"sourceId": "nepu-2026-10476", "recordCount": 56, "totalsMatchSource": "PASS", "numericColumns": "PASS",
                    "samples": [nepu_records[0], nepu_records[28], nepu_records[-1]]})

    qqhru = read_table("qqhru-2026.html")
    assert qqhru[1] == ["科类", "专业名称", "最高分", "最低分", "平均分", "备注"]
    qqhru_records = []
    for row_number, r in enumerate(qqhru[2:], 3):
        if r[0] not in ("历史类", "物理类"):
            continue
        assert int(r[3]) <= float(r[4]) <= int(r[2])
        qqhru_records.append({"id": f"major-2026-qqhru-r{row_number}", "year": 2026,
                              "school": "齐齐哈尔大学", "schoolCode": "10232", "track": r[0].replace("类", ""),
                              "batch": "本科普通批", "group": None, "major": r[1], "score": int(r[3]),
                              "scoreType": "专业录取最低分", "plannedCount": None, "admittedCount": None,
                              "sourceId": "qqhru-2026-4903", "round": "录取汇总（含征集）", "admissionType": "普通类",
                              "note": "原表为分专业录取分数线，数值列称投档成绩；未公布计划数、录取人数、专业组。原文附注征集志愿投档成绩：市场营销455、林学453；不能把整张表声称为首轮。" + ("原备注：" + r[5] if r[5] else ""),
                              "sourceRow": row_number})
    assert len(qqhru_records) == 29
    rows.extend(qqhru_records)
    sources.append(source("qqhru-2026-4903", "齐齐哈尔大学招生就业处", "qqhru-2026.html", "2026年广西录取分数线——本科批",
                          "https://zs.qqhru.edu.cn/info/1140/4903.htm", "2026-07-24", 29,
                          ["表头为投档成绩，按专业给出录取最低、最高、平均分。", "省控线历史类398，物理类368；征集志愿投档成绩：市场营销455，林学453。", "同分排位1、同分排位7不是全区位次，保留在原备注。", "原页无计划或录取人数列，不推算人数。 "]))
    reports.append({"sourceId": "qqhru-2026-4903", "recordCount": 29, "numericColumns": "PASS",
                    "nullCountsPreserved": "PASS", "samples": [qqhru_records[0], qqhru_records[14], qqhru_records[-1]]})

    cqie_plan = read_table("cqie-plan-2026.html", "gbk")
    cqie_plan_records = []
    for row_number, r in enumerate(cqie_plan[3:], 4):
        if r[0] != "本科批":
            continue
        assert r[7] in ("历史", "物理") and r[8] in ("不限", "化学")
        assert re.fullmatch(r"\d{3}", r[4]) and r[6].isdigit()
        cqie_plan_records.append({"id": f"plan-2026-cqie-r{row_number}", "year": 2026, "schoolCode": "12608",
                                  "school": "重庆工程学院", "track": r[7], "batch": "本科普通批", "group": r[4],
                                  "major": r[2], "majorCode": r[5], "requiredSubjects": [] if r[8] == "不限" else ["化学"],
                                  "subjectRule": "any" if r[8] == "不限" else "all", "plannedCount": int(r[6]),
                                  "tuition": int(r[9]) if r[9].isdigit() else None, "duration": None,
                                  "note": ("大类包含：" + r[3] + "。" if r[3] else "") + ("学费原文待定。" if not r[9].isdigit() else "") + "招生代码和最终招生计划以广西考试院公布为准。",
                                  "sourceId": "cqie-plan-2026-78111", "category": "普通类", "requirementText": r[8],
                                  "round": "首轮", "planBasis": "2026-06-17录取前发布的普通批招生计划，非征集剩余",
                                  "sourceRow": row_number})
    assert len(cqie_plan_records) == 15 and sum(r["plannedCount"] for r in cqie_plan_records) == 118
    for track, expected in [("历史", 10), ("物理", 108)]:
        assert sum(r["plannedCount"] for r in cqie_plan_records if r["track"] == track) == expected
    plans.extend(cqie_plan_records)
    sources.append(source("cqie-plan-2026-78111", "重庆工程学院", "cqie-plan-2026.html", "2026年广西本科招生专业及计划",
                          "https://www.cqie.edu.cn/html/7/content/26/06/78111.shtml", "2026-06-17", 15,
                          ["历史类10人，物理类108人，合计118人。各专业行数与总数一致。", "招生代码和最终招生计划以广西考试院公布为准。", "大数据管理与应用学费待定，保存为null。", "有明确专业组、选科要求、志愿专业代号；大类下含专业仅列在note，不重复计计划人数。 "]))
    plan_map = {(r["track"], norm_major(r["major"])): r for r in cqie_plan_records}
    assert len(plan_map) == 15
    cqie = read_table("cqie-2026.html", "gbk")
    cqie_records = []
    for row_number, r in enumerate(cqie[3:], 4):
        if r[0] != "广西":
            continue
        assert int(r[5]) <= float(r[7]) <= int(r[6])
        track = r[2].replace("类", "")
        plan = plan_map[(track, norm_major(r[4]))]
        cqie_records.append({"id": f"major-2026-cqie-r{row_number}", "year": 2026,
                             "school": "重庆工程学院", "schoolCode": "12608", "track": track,
                             "batch": "本科普通批", "group": plan["group"], "major": r[4], "score": int(r[5]),
                             "scoreType": "专业录取最低分", "plannedCount": plan["plannedCount"], "admittedCount": None,
                             "sourceId": "cqie-2026-78849", "planSourceId": plan["sourceId"],
                             "round": "录取汇总（轮次未分）", "admissionType": "普通类",
                             "note": "原录取公示按考生总成绩从高分到低分进行专业录取，未拆分轮次；原公告无录取人数列。专业组及计划数取同年6月17日广西计划，按同科类同专业名关联，仅归一化括号与空白。",
                             "sourceRow": row_number})
    assert len(cqie_records) == 15
    rows.extend(cqie_records)
    sources.append(source("cqie-2026-78849", "重庆工程学院", "cqie-2026.html", "2026年录取公告（广西本科批）",
                          "https://zs.cqie.edu.cn/html/7/content/26/07/78849.shtml", "2026-07-27", 15,
                          ["学校公告称广西普通类本科批录取工作已完成，招生计划录满。没有分专业录取人数，不能据此生成admittedCount。", "学校按考生总成绩从高分到低分进行专业录取。", "录取分数源与专业组/计划数源分开标记；后者来自2026-06-17官方计划。", "公示未区分首轮和征集，按录取汇总展示。 "]))
    reports.append({"sourceId": "cqie-2026-78849", "recordCount": 15, "strictOfficialPlanJoin": "PASS: all 15",
                    "planTotal": 118, "numericColumns": "PASS", "samples": [cqie_records[0], cqie_records[7], cqie_records[-1]]})

    sdjtu_parser = base.Tables()
    sdjtu_text = (ROOT / "raw/sdjtu-2026-7012.html").read_text()
    assert "2026年广西本科批招生录取信息公告" in sdjtu_text
    sdjtu_parser.feed(sdjtu_text)
    sdjtu_tables = [base.expand(t) for t in sdjtu_parser.tables]
    sdjtu = [t for t in sdjtu_tables if t[0][:3] == ["省份", "批次", "计划性质"]]
    assert len(sdjtu) == 1
    sdjtu = sdjtu[0]
    assert sdjtu[0] == ["省份", "批次", "计划性质", "学制", "科类", "分数线", "专业", "录取数", "录取 最高分", "录取 最低分", "录取 平均分"]
    sdjtu_records = []
    for row_number, r in enumerate(sdjtu[1:], 2):
        assert r[:4] == ["广西", "本科批", "非定向", "4"]
        assert r[4] in ("历史", "物理") and int(r[9]) <= float(r[10]) <= int(r[8])
        assert r[5] == ("398" if r[4] == "历史" else "368")
        sdjtu_records.append({"id": f"major-2026-sdjtu-r{row_number}", "year": 2026,
                              "school": "山东交通学院", "schoolCode": "11510", "track": r[4],
                              "batch": "本科普通批", "group": None, "major": r[6], "score": int(r[9]),
                              "scoreType": "专业录取最低分", "plannedCount": None, "admittedCount": int(r[7]),
                              "sourceId": "sdjtu-2026-7012", "round": "录取汇总（轮次未分）",
                              "admissionType": "中外合作办学" if "中外合作" in r[6] else "普通类",
                              "note": "原表的录取数已保存为admittedCount，未当作计划数；原表分数线列是本科控制线，score来自专业录取最低分列。未公布专业组，也未区分首轮与征集。学制四年，非定向。",
                              "sourceRow": row_number})
    assert len(sdjtu_records) == 24
    assert sum(r["admittedCount"] for r in sdjtu_records) == 60
    rows.extend(sdjtu_records)
    sources.append(source("sdjtu-2026-7012", "山东交通学院招生就业处", "sdjtu-2026-7012.html",
                          "2026年广西本科批招生录取信息公告", "https://zsw.sdjtu.edu.cn/info/1012/7012.htm", "2026-07-25", 24,
                          ["24条专业录取结果，录取数合计60人；未公布计划数，不转换为计划数据。",
                           "原表分数线列历史398/物理368为本科控制线，专业录取最低分是另一列。",
                           "所有专业为本科批、非定向、学制4年；中外合作办学双证项目从专业原名称识别，单独标记。",
                           "未公布专业组和录取轮次，分别保存null和录取汇总（轮次未分）。"]))
    reports.append({"sourceId": "sdjtu-2026-7012", "recordCount": 24, "numericColumns": "PASS",
                    "admittedTotal": 60, "plansNotInSource": "PASS: all null",
                    "samples": [sdjtu_records[0], sdjtu_records[12], sdjtu_records[-1]]})

    assert all(r["year"] == 2026 for r in rows + plans)
    assert len({r["id"] for r in rows}) == len(rows)
    assert len({r["id"] for r in plans}) == len(plans)
    source_ids = {s["id"] for s in sources}
    group_source_ids = {s["id"] for s in json.loads((ROOT / "sources.json").read_text())}
    assert len(source_ids) == len(sources)
    for r in rows:
        assert r["sourceId"] in source_ids and r["track"] in ("物理", "历史")
        assert isinstance(r["score"], int) and 0 <= r["score"] <= 750
        assert r["group"] is None or re.fullmatch(r"\d{3}", r["group"])
        for key in ("plannedCount", "admittedCount"):
            assert r[key] is None or isinstance(r[key], int) and r[key] >= 0
        if "qualificationSourceId" in r:
            assert r["qualificationSourceId"] in group_source_ids
        if "planSourceId" in r:
            assert r["planSourceId"] in source_ids
    for r in plans:
        assert r["sourceId"] in source_ids and isinstance(r["plannedCount"], int) and r["plannedCount"] >= 0
    base.dump("major-cutoffs.json", rows)
    base.dump("sources-major.json", sources)
    base.dump("plans-supplement.json", plans)
    base.dump("quality-major.json", {"recordCount": len(rows), "planRecordCount": len(plans), "sources": reports,
                                     "bySchool": dict(collections.Counter(r["school"] for r in rows)),
                                     "planCountsBySchool": dict(collections.Counter(r["school"] for r in plans)),
                                     "crossDatasetChecks": {"uniqueIds": "PASS", "all2026": "PASS",
                                         "sourceReferences": "PASS", "schemaAndNumericBounds": "PASS",
                                         "admittedCountsNotConvertedToPlans": "PASS"}})
    print(json.dumps({"majorCount": len(rows), "planCount": len(plans), "bySchool": dict(collections.Counter(r["school"] for r in rows))}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    args = argparse.ArgumentParser(description=__doc__)
    args.add_argument("--refresh", action="store_true", help="Download known official source HTML before rebuilding")
    if args.parse_args().refresh:
        (ROOT / "raw").mkdir(parents=True, exist_ok=True)
        for filename, url in RAW_SOURCES.items():
            request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            raw = urllib.request.urlopen(request, timeout=60).read()
            assert len(raw) > 1000, (filename, "Unexpected short response")
            (ROOT / "raw" / filename).write_bytes(raw)
    main()
