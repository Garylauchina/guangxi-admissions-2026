#!/usr/bin/env python3
"""Fetch/parse Guangxi 2026 ordinary-batch filing cutoffs using stdlib only.

Run `python3 collect.py` to reproduce from saved public-source files, or add
`--refresh` to retrieve the 16 explicitly listed official public pages again.
No account, student record, or private workspace dataset is accessed.
"""
import argparse
import collections
import concurrent.futures
import datetime as dt
import hashlib
import html
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import urllib.request

ROOT = Path(__file__).resolve().parent
SPECS = [
    (33106, "历史", "本科普通批", "首轮"),
    (33107, "物理", "本科普通批", "首轮"),
    (33145, "历史", "本科普通批", "第一次征集"),
    (33146, "物理", "本科普通批", "第一次征集"),
    (33167, "历史", "本科普通批", "第二次征集"),
    (33168, "物理", "本科普通批", "第二次征集"),
    (33187, "历史", "本科普通批", "第三次征集"),
    (33188, "物理", "本科普通批", "第三次征集"),
    (33225, "历史", "本科普通批", "第四次征集"),
    (33226, "物理", "本科普通批", "第四次征集"),
    (33315, "历史", "高职高专普通批", "首轮"),
    (33316, "物理", "高职高专普通批", "首轮"),
    (33332, "历史", "高职高专普通批", "第一次征集"),
    (33333, "物理", "高职高专普通批", "第一次征集"),
    (33354, "历史", "高职高专普通批", "第二次征集"),
    (33355, "物理", "高职高专普通批", "第二次征集"),
]
HEADER = ["院校代码", "院校名称", "专业组", "投档最低分", "备注"]


def normalize(value):
    return re.sub(r"\s+", " ", value).strip()


class TableParser(HTMLParser):
    """Read cells in source order. These 16 source tables have no rowspans."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.rows = []
        self.row = None
        self.cell = None

    def handle_starttag(self, tag, attrs):
        if tag == "tr":
            self.row = []
        if tag in ("td", "th") and self.row is not None:
            self.cell = ""
        if tag == "br" and self.cell is not None:
            self.cell += " "

    def handle_data(self, data):
        if self.cell is not None:
            self.cell += data

    def handle_endtag(self, tag):
        if tag in ("td", "th") and self.cell is not None:
            self.row.append(normalize(self.cell))
            self.cell = None
        if tag == "tr" and self.row is not None:
            self.rows.append(self.row)
            self.row = None


def write_json(name, data):
    (ROOT / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def fetch(spec, refresh=False):
    number = spec[0]
    path = ROOT / "raw" / f"content_624_{number}.html"
    url = f"https://www.gxeea.cn/view/content_624_{number}.htm"
    if refresh or not path.exists():
        request = urllib.request.Request(url, headers={"User-Agent": "Guangxi2026PublicCutoffResearch/1.0"})
        with urllib.request.urlopen(request, timeout=45) as response:
            assert response.status == 200, (url, response.status)
            path.write_bytes(response.read())
    return path, url


def independent_regex_rows(text):
    rows = []
    for row in re.findall(r"<tr\b[^>]*>(.*?)</tr>", text, re.S | re.I):
        cells = [normalize(html.unescape(re.sub(r"<[^>]*>", " ", cell)))
                 for cell in re.findall(r"<t[dh]\b[^>]*>(.*?)</t[dh]>", row, re.S | re.I)]
        if cells and re.fullmatch(r"\d{5}", cells[0]):
            rows.append(cells)
    return rows


def parse(spec, fetched):
    number, track, batch, round_name = spec
    path, url = fetched
    raw = path.read_bytes()
    text = raw.decode("gbk")
    title = html.unescape(re.search(r"<title>(.*?)</title>", text, re.S).group(1)).strip()
    assert "2026" in title and batch in title and track in title, title
    assert ("征集" not in title) if round_name == "首轮" else round_name in title
    assert not re.search(r"rowspan\s*=", text, re.I), "Review merged-row parser before reuse"
    parser = TableParser()
    parser.feed(text)
    assert HEADER in parser.rows, (url, "unexpected columns")
    data_rows = [row for row in parser.rows if row and re.fullmatch(r"\d{5}", row[0])]
    independent_rows = independent_regex_rows(text)
    assert data_rows == independent_rows, (url, "independent extraction differs")
    assert len(data_rows) > 0
    source_id = f"gxeea-2026-{number}"
    records = []
    for index, row in enumerate(data_rows, start=1):
        assert len(row) == 5, (url, index, row)
        school_code, school, group, score_text, note = row
        assert school and re.fullmatch(r"\d{3}", group), (url, index, row)
        assert not score_text or re.fullmatch(r"\d{3}", score_text), (url, index, row)
        score = int(score_text) if score_text else None
        assert score is None or 0 <= score <= 750, (url, index, row)
        record = {
            "id": f"gx-2026-{number}-{school_code}-{group}",
            "year": 2026,
            "schoolCode": school_code,
            "school": school,
            "track": track,
            "batch": batch,
            "round": round_name,
            "group": group,
            "score": score,
            "rank": None,
            "note": note,
            "sourceId": source_id,
            "sourceRow": index,
        }
        records.append(record)
    assert len({record["id"] for record in records}) == len(records), (url, "duplicate group keys")
    publication = re.search(r'<meta name="PubDate" content="([^"]+)"', text).group(1)
    published_at = dt.datetime.strptime(publication, "%Y-%m-%d %H:%M").replace(
        tzinfo=dt.timezone(dt.timedelta(hours=8))).isoformat()
    accessed_at = dt.datetime.fromtimestamp(path.stat().st_mtime, tz=dt.timezone.utc).isoformat()
    notes = [row[0] for row in parser.rows if len(row) == 1 and "说明" in row[0]]
    assert any("空白处表示无出档考生" in note for note in notes), (url, "missing source blank-score definition")
    source = {
        "id": source_id,
        "title": title,
        "url": url,
        "publisher": "广西招生考试院",
        "publishedAt": published_at,
        "accessedAt": accessed_at,
        "sha256": hashlib.sha256(raw).hexdigest(),
        "recordCount": len(records),
        "method": "Official GBK HTML table; standard-library HTMLParser; independently cross-checked against regex extraction of every source cell; no OCR or third-party table used.",
        "rawPath": "raw/" + path.name,
        "track": track,
        "batch": batch,
        "round": round_name,
        "notes": notes,
        "scoreSemantics": "院校专业组投档最低分；空白表示无出档考生，保存为 null。不是具体专业录取最低分。",
        "rankSemantics": "原表未公布投档位次，rank 均为 null；不能把一分一档的分数名次直接宣称为精确投档位次。",
    }
    sample_indices = {0, len(records) // 2, len(records) - 1}
    for predicate in [lambda r: r["score"] is None, lambda r: "国家专项" in r["note"], lambda r: "高校专项" in r["note"],
                      lambda r: "地方专项" in r["note"],
                      lambda r: "民族" in r["note"], lambda r: "精准" in r["note"],
                      lambda r: "降" in r["note"], lambda r: "不招" in r["note"],
                      lambda r: "身高" in r["note"]]:
        index = next((i for i, r in enumerate(records) if predicate(r)), None)
        if index is not None:
            sample_indices.add(index)
    scores = [r["score"] for r in records if r["score"] is not None]
    check = {
        "sourceId": source_id,
        "title": title,
        "recordCount": len(records),
        "schoolCount": len({r["schoolCode"] for r in records}),
        "nullScores": sum(r["score"] is None for r in records),
        "notedRows": sum(bool(r["note"]) for r in records),
        "minScore": min(scores),
        "maxScore": max(scores),
        "independentCellComparison": "PASS",
        "uniqueKeys": "PASS",
        "schemaAndBounds": "PASS",
        "samples": [{"sourceRow": i + 1, "sourceCells": independent_rows[i],
                     "parsed": records[i], "result": "PASS"} for i in sorted(sample_indices)],
    }
    return records, source, check


def main():
    args = argparse.ArgumentParser(description=__doc__)
    args.add_argument("--refresh", action="store_true")
    options = args.parse_args()
    (ROOT / "raw").mkdir(parents=True, exist_ok=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        fetched = list(pool.map(lambda spec: fetch(spec, options.refresh), SPECS))
    records, sources, checks = [], [], []
    for spec, source_file in zip(SPECS, fetched):
        rows, source, check = parse(spec, source_file)
        records.extend(rows)
        sources.append(source)
        checks.append(check)
    first = [r for r in records if r["round"] == "首轮"]
    supplementary = [r for r in records if r["round"] != "首轮"]
    assert len({r["id"] for r in records}) == len(records)
    assert all(r["rank"] is None for r in records)
    summary = {
        "generatedAt": dt.datetime.now(dt.timezone.utc).isoformat(),
        "sourceCount": len(sources),
        "recordCount": len(records),
        "firstRoundCount": len(first),
        "supplementaryCount": len(supplementary),
        "firstRoundSchoolCount": len({r["schoolCode"] for r in first}),
        "nullScoreCount": sum(r["score"] is None for r in records),
        "firstRoundNullScoreCount": sum(r["score"] is None for r in first),
        "nullRankCount": len(records),
        "rounds": dict(collections.Counter(r["batch"] + "|" + r["track"] + "|" + r["round"] for r in records)),
        "checks": checks,
        "limitations": [
            "Complete relative to the 16 listed official ordinary-batch tables; does not cover every admissions route or prove complete national school/program coverage.",
            "These are group filing cutoffs, not final admission cutoffs or major-specific cutoffs; group composition requires separately sourced 2026 plans.",
            "Score is null when the original source cell is blank; this means no filed candidates and does not mean zero points.",
            "All exact filing ranks are unavailable in these sources; rank remains null.",
            "National/targeted/minority and other eligibility restrictions remain in original notes and must be shown to users.",
            "Historical 2026 results are not a forecast or admission guarantee for another year.",
        ],
    }
    write_json("cutoffs-all.json", records)
    write_json("cutoffs-first-round.json", first)
    write_json("cutoffs-supplementary.json", supplementary)
    write_json("sources.json", sources)
    write_json("quality-report.json", summary)
    print(json.dumps({k: v for k, v in summary.items() if k not in ("checks", "limitations", "rounds")}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
