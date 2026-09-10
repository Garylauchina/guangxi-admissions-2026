#!/usr/bin/env python3
"""Fetch only the official 2026 national-bonus score distribution; do not fill gaps."""
from urllib.request import urlopen
from pathlib import Path
import re
import html
import json
import hashlib
import datetime
import argparse

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--raw-dir', type=Path, default=ROOT / 'raw' / 'ranks')
args = parser.parse_args()
args.raw_dir.mkdir(parents=True, exist_ok=True)
data, sources = [], []
for slug, track in [('wuli', '物理'), ('lishi', '历史')]:
    url = f'https://www.gxeea.cn/2026yfyd/yifenyidang/2026_yifenyidang_{slug}_qg.html'
    raw = urlopen(url, timeout=40).read()
    encoding = 'gb18030' if re.search(br'charset=["\']?(?:gbk|gb2312)', raw[:3000], re.I) else 'utf-8'
    text = raw.decode(encoding)
    assert f'2026年{track}类一分一档表' in text, 'Source year / track mismatch'
    (args.raw_dir / f'{slug}.html').write_bytes(raw)
    source_id = f'rank-2026-{slug}'
    rows = []
    for tr in re.findall(r'<tr\b[^>]*>(.*?)</tr>', text, re.S | re.I):
        cells = [html.unescape(re.sub('<[^>]+>', '', value)).strip()
                 for value in re.findall(r'<td\b[^>]*>(.*?)</td>', tr, re.S | re.I)]
        if len(cells) == 4 and all(x.isdigit() for x in cells):
            score, count, end, start = map(int, cells)
            assert end - start + 1 == count
            rows.append(dict(year=2026, track=track, score=score, count=count,
                             rankStart=start, rankEnd=end, sourceId=source_id))
    assert len(rows) > 300, 'Unexpected incomplete source'
    for i in range(1, len(rows)):
        assert rows[i]['score'] < rows[i-1]['score']
        assert rows[i]['rankStart'] == rows[i-1]['rankEnd'] + 1
    data.extend(rows)
    sources.append(dict(id=source_id, title=f'2026年{track}类一分一档表（总分=总成绩+全国性加分）',
        url=url, publisher='广西招生考试院', publishedAt='2026-06-25',
        accessedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        sha256=hashlib.sha256(raw).hexdigest(), recordCount=len(rows),
        method='官方HTML四列严格解析；校验名次区间长度等于人数及累计连续性',
        note='只保留原表公布的分数档；同分名次区间不是专业组最低投档位次。'))
    print(track, len(rows), 'rows;', 'range', rows[0]['score'], rows[-1]['score'])
(ROOT / 'site/data/ranks.json').write_text(json.dumps(data, ensure_ascii=False, separators=(',', ':')))
(args.raw_dir / 'sources.json').write_text(json.dumps(sources, ensure_ascii=False, indent=2))
