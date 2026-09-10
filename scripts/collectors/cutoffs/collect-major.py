#!/usr/bin/env python3
"""Rebuild 2026 Guangxi major admission outcomes from saved official HTML.

This parser expands HTML rowspan/colspan rather than carrying the last school or
group name over arbitrary rows. It reads only specified aggregate public tables.

This file is a shared parser and Yulin-specific helper. To rebuild the complete
five-school delivery, run collect-additional-major.py, which imports this file.
"""
import collections
import datetime as dt
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent


def clean(value):
    return re.sub(r"\s+", " ", value).strip()


class Tables(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tables = []
        self.table = None
        self.row = None
        self.cell = None

    def handle_starttag(self, tag, attrs):
        if tag == "table":
            assert self.table is None, "Nested tables require review"
            self.table = []
        if tag == "tr" and self.table is not None:
            self.row = []
        if tag in ("td", "th") and self.row is not None:
            self.cell = {"text": "", "attrs": dict(attrs)}
        if tag == "br" and self.cell is not None:
            self.cell["text"] += " "

    def handle_data(self, value):
        if self.cell is not None:
            self.cell["text"] += value

    def handle_endtag(self, tag):
        if tag in ("td", "th") and self.cell is not None:
            self.cell["text"] = clean(self.cell["text"])
            self.row.append(self.cell)
            self.cell = None
        if tag == "tr" and self.row is not None:
            self.table.append(self.row)
            self.row = None
        if tag == "table" and self.table is not None:
            self.tables.append(self.table)
            self.table = None


def expand(rows):
    cells = {}
    for row_index, row in enumerate(rows):
        col_index = 0
        for cell in row:
            while (row_index, col_index) in cells:
                col_index += 1
            rowspan = int(cell["attrs"].get("rowspan", 1))
            colspan = int(cell["attrs"].get("colspan", 1))
            for offset_r in range(rowspan):
                for offset_c in range(colspan):
                    location = (row_index + offset_r, col_index + offset_c)
                    assert location not in cells, (location, "overlapping merged cell")
                    cells[location] = cell["text"]
            col_index += colspan
    width = max(col for row, col in cells) + 1
    return [[cells.get((row, col), "") for col in range(width)] for row in range(len(rows))]


def dump(filename, data):
    (ROOT / filename).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def ylu():
    path = ROOT / "raw/ylu-2026-7162.html"
    raw = path.read_bytes()
    text = raw.decode("utf-8")
    assert "玉林师范学院2026年广西各批次最低分录取公告" in text
    parser = Tables()
    parser.feed(text)
    assert len(parser.tables) == 10
    expanded = [expand(rows) for rows in parser.tables]
    dump("ylu-expanded-tables.json", expanded)
    group_rows = json.loads((ROOT / "cutoffs-first-round.json").read_text())
    group_map = {(r["track"], r["group"]): r for r in group_rows if r["schoolCode"] == "10606"}
    records = []
    warnings = []
    excluded = []
    for table_index, track, batch, admission_type, header_count in [
        (5, "物理", "本科提前批其他一类", "公费师范生", 2),
        (6, "历史", "本科提前批其他一类", "公费师范生", 2),
        (7, "历史", "本科普通批", "普通类", 1),
        (8, "物理", "本科普通批", "普通类", 1),
    ]:
        rows = expanded[table_index]
        assert rows[header_count - 1][-1] == "最低分"
        for row_number, row in enumerate(rows[header_count:], start=header_count + 1):
            group, major = row[:2]
            assert re.fullmatch(r"\d{3}", group), row
            if "预科" in major:
                excluded.append({"table": table_index + 1, "row": row_number, "cells": row, "reason": "预科项目不是本科专业；已有独立专业组投档数据，未混入专业录取线。"})
                continue
            assert all(re.fullmatch(r"\d+", value) for value in row[-4:]), row
            filing_score, planned_count, admitted_count, score = map(int, row[-4:])
            round_name = "征集（次数未公布）" if "征集" in major else "首轮"
            major_name = re.sub(r"[（(]?征集[）)]?", "", major).strip()
            nature = admission_type
            note = "计划数和录取数分别来自原表，不跨首轮与征集相加；原页发布日期为最初发布日期，后续录取更新日期未单列。"
            if admission_type == "公费师范生":
                note += "公费师范生定向培养，具体服务地区见专业名；须满足广西户籍、体检及相应报考条件，英语须口语测试合格。"
                if "生物科学" in major or "应用心理学" in major:
                    note += "原文要求不招色盲、色弱考生。"
            else:
                group_data = group_map[(track, group)]
                if group_data["note"]:
                    nature = group_data["note"]
                    note += "专业组类别据广西招生考试院同年同校同科类同组原表：" + group_data["note"] + "。"
                if round_name == "首轮" and filing_score != group_data["score"]:
                    warning = f"高校公告出档分 {filing_score} 与考试院同组首轮线 {group_data['score']} 不一致；本条 score 保留高校公告的专业最低分 {score}。"
                    warnings.append({"table": table_index + 1, "row": row_number, "warning": warning, "groupSourceId": group_data["sourceId"]})
                    note += "【原文出档分冲突】" + warning
                if round_name == "首轮":
                    assert score >= group_data["score"], (track, group, score, group_data["score"])
            if round_name != "首轮":
                note += "征集记录单列，原表未标第几次征集，不能用于首轮最低分筛选。"
            record = {
                "id": f"major-2026-ylu-t{table_index+1}-r{row_number}",
                "year": 2026, "school": "玉林师范学院", "schoolCode": "10606",
                "track": track, "batch": batch, "group": group,
                "major": major_name, "score": score,
                "scoreType": "专业录取最低分", "plannedCount": planned_count,
                "admittedCount": admitted_count, "sourceId": "ylu-2026-7162",
                "note": note, "round": round_name, "admissionType": nature,
                "filingScoreInSource": filing_score,
                "sourceTable": table_index + 1, "sourceRow": row_number,
            }
            if admission_type != "公费师范生":
                record["qualificationSourceId"] = group_map[(track, group)]["sourceId"]
            records.append(record)
    duplicates = collections.defaultdict(list)
    for r in records:
        duplicates[(r["track"], r["batch"], r["group"], r["major"], r["round"])].append(r)
    for key, group in duplicates.items():
        if len(group) > 1:
            warnings.append({"key": key, "ids": [r["id"] for r in group], "warning": "原公告同组同名分列多条，不同子计划区别未注明；保留每行，不自动合并。"})
            for r in group:
                r["note"] += "【原文分列待核实】同组同名有多条原始记录，不同子计划区别未注明，须向学校核实。"
    assert len({r["id"] for r in records}) == len(records)
    source = {
        "id": "ylu-2026-7162", "title": "玉林师范学院2026年广西各批次最低分录取公告",
        "url": "https://zjw.ylu.edu.cn/info/1013/7162.htm", "publisher": "玉林师范学院招生就业处",
        "publishedAt": "2026-07-11T12:36:04+08:00",
        "accessedAt": dt.datetime.fromtimestamp(path.stat().st_mtime, dt.timezone.utc).isoformat(),
        "sha256": hashlib.sha256(raw).hexdigest(), "recordCount": len(records),
        "rawPath": "raw/ylu-2026-7162.html",
        "method": "Official UTF-8 HTML; expand merged cells; select regular bachelor and non-sports publicly funded teacher tables; preserve major minimum, planned count, admitted count as distinct source columns.",
        "notes": [
            "网页初始发布日期早于部分录取批次，页面后续更新时间未单列；accessedAt 是本次数据快照时间。",
            "艺体专业分及综合投档分未混入。预科为单独项目，不列作本科专业录取线。",
            "正投表含征集附行，已按专业名的征集标识拆分。计划数不可跨首轮和征集直接相加。",
            "高校公告历史912组出档分与考试院不一致；保留实际专业最低分并显示冲突标记。",
        ],
    }
    qa = {"sourceId": source["id"], "recordCount": len(records), "year": 2026,
          "byBatchTrackRound": dict(collections.Counter(r["batch"] + "|" + r["track"] + "|" + r["round"] for r in records)),
          "warnings": warnings, "excludedRows": excluded,
          "samples": [records[0], records[len(records)//2], records[-1]],
          "checks": {"mergedCellsNoOverlap": "PASS", "numericFieldsSeparate": "PASS",
                     "ordinaryFirstRoundMajorMinimumAboveOfficialGroupCutoff": "PASS", "uniqueRecordIds": "PASS"}}
    return records, source, qa


if __name__ == "__main__":
    rows, source, qa = ylu()
    dump("major-cutoffs.json", rows)
    dump("sources-major.json", [source])
    dump("quality-major.json", qa)
    print(json.dumps({"recordCount": len(rows), "warnings": len(qa["warnings"]), "byBatchTrackRound": qa["byBatchTrackRound"]}, ensure_ascii=False, indent=2))
