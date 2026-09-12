"""Extract statistical fields only from locally archived public sources.

Raw pages and API envelopes are intentionally excluded from publication.
"""
import datetime, hashlib, html, json, re
from pathlib import Path
ROOT = Path(__file__).resolve().parent
RAW = ROOT / 'raw'
def load(name):
    return json.loads((RAW / name).read_text())
def save(name, value):
    (ROOT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
def clean(text):
    return re.sub(r'\s+', ' ', html.unescape(re.sub('<[^>]+>', ' ', text))).strip()

facts = []
for code in ['10589', '11414']:
    for path in sorted(RAW.glob(code + '-scores-*.json')):
        if '.meta.' in path.name:
            continue
        body = json.loads(path.read_text())
        assert body['state'] == 1
        rows = body['data']['sszygradeList']
        for number, row in enumerate(rows, 1):
            fields = {key: row.get(key) for key in [
                'nf', 'ssmc', 'klmc', 'zylx', 'zymc', 'pcmc', 'minScore',
                'maxScore', 'avgScore', 'minOrder', 'rs', 'zyzname', 'zydm', 'remarks'
            ]}
            assert str(fields['nf']) == '2026' and fields['ssmc'] == '广西'
            facts.append({'file': path.name, 'schoolCode': code,
                          'sourceRow': number, 'sourceTable': 'sszygradeList',
                          'fields': fields})
for i in [1, 2]:
    name = f'10542-scores{i}-1.json'
    rows = load(name)['list']
    majors = load(f'10542-majormenu{i}-1.json')['majorList']
    assert sorted(majors) == sorted(row['majorName'] for row in rows)
    for number, row in enumerate(rows, 1):
        fields = {key: row.get(key) for key in [
            'year', 'cityName', 'scienceClass', 'type', 'batch', 'majorName',
            'hightScore', 'lowScore', 'avgScore', 'lowScoreRank', 'enrollNum',
            'majorGroup', 'remark', 'xkkm'
        ]}
        assert fields['year'] == 2026 and fields['cityName'] == '广西'
        facts.append({'file': name, 'schoolCode': '10542', 'sourceRow': number,
                      'sourceTable': 'list', 'fields': fields})
s = (RAW / '10511-gx2026.html').read_text()
number = 0
for tr in re.findall(r'<tr\b[^>]*>(.*?)</tr>', s, re.S | re.I):
    cells = [clean(td) for td in re.findall(r'<t[dh]\b[^>]*>(.*?)</t[dh]>', tr, re.S | re.I)]
    if len(cells) >= 7 and cells[0] == '2026' and cells[1] == '广西':
        number += 1
        fields = dict(zip(['year', 'province', 'batch', 'track', 'major', 'minimum', 'rankText', 'remark'], cells))
        fields['year'] = int(fields['year'])
        fields['minimum'] = int(fields['minimum'])
        facts.append({'file': '10511-gx2026.html', 'schoolCode': '10511',
                      'sourceRow': number, 'sourceTable': '专业录取分数表', 'fields': fields})
assert number == 17
# Manually transcribed and visually checked in the four-page official PDF, page 2.
# The actual minimum is the 平行志愿 -> 最低分 column. 首轮投档线 is a separate column.
facts.append({'file': '10366-pdf.pdf', 'schoolCode': '10366', 'sourceRow': '广西唯一行',
              'sourcePage': 2, 'sourceTable': '平行志愿录取统计', 'fields': {
                  'year': 2026, 'province': '广西', 'track': '物理类', 'batch': '普通本科批',
                  'major': '临床医学', 'minimum': 602, 'maximum': 602, 'average': 602.0,
                  'planned': 1, 'admitted': 1, 'round': '平行志愿', 'firstFilingScore': 602,
                  'supplementaryColumns': '空白'
              }})
assert len(facts) == 141
save('evidence-rows.json', facts)
print('Extracted', len(facts), 'current-year major facts')
