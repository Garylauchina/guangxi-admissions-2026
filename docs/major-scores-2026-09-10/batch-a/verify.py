#!/usr/bin/env python3
"""Verify this bounded 8-school audit and the explicit publication allowlist."""
import hashlib,json,re
from pathlib import Path

R=Path(__file__).resolve().parent
def read(n):return json.loads((R/n).read_text())

def main():
    rows=read('major-cutoffs-upsert.json');notes=read('school-audit-notes.json');sources=read('sources.json')
    assert len(rows)==16 and len({x['id'] for x in rows})==16
    assert sum(x['scoreComparable'] for x in rows)==15
    assert all(x['schoolCode']=='11765' and x['province']=='广西' and x['year']==2026 for x in rows)
    assert all(x['group'] is None and x['rank'] is None and x['scoreType']=='专业录取最低分' for x in rows)
    assert all('admittedCount' not in x and 'plannedCount' not in x for x in rows)
    assert all(x['score']-x['controlScore']==x['scoreDifference'] for x in rows)
    assert all(x['score']<=x['sourceAverageScore']<=x['sourceMaximumScore'] for x in rows if x['scoreComparable'])
    bad=[x for x in rows if not x['scoreComparable']];assert len(bad)==1
    assert bad[0]['major']=='城市地下空间工程（数智岩土方向）' and (bad[0]['score'],bad[0]['sourceMaximumScore'],bad[0]['sourceAverageScore'])==(418,423,428.2)
    assert bad[0]['evidenceStatus']=='source-conflict' and bad[0]['conflictFields']
    assert {x['schoolCode'] for x in notes}=={'10001','19001','10003','10002','10358','10007','10006','11765'}
    assert len(notes)==8 and all(x['province']=='广西' and x['year']==2026 for x in notes)
    assert all(x['importedRecordCount']==0 for x in notes if x['schoolCode']!='11765')
    ids={s['id'] for s in sources};assert len(ids)==len(sources)==34
    assert all(sid in ids for n in notes for sid in n['sourceIds'])
    queries=read('query-results.json');assert len(queries)==7
    assert all(q['state']==1 and q['majorRowCount']==0 and q['schoolSummaryRowCount']==0 and q['request']['zsnf']=='2026' and q['request']['ssmc']=='广西' for q in queries)
    for source in sources:
        assert source['recordCount']==(16 if source['id']=='major-a-huuc-score-2026' else 0)
        local=R/source['rawFile']
        if local.exists():assert hashlib.sha256(local.read_bytes()).hexdigest()==source['sha256'],source['id']
    public=read('PUBLIC-FILES.json');assert isinstance(public,list)
    for name in public:
        assert name and '/' not in name and '\\' not in name and name!='raw'
        data=(R/name).read_text()
        assert not re.search(r'/(?:Users|home)/|Bearer\s+[A-Za-z0-9]|Authorization\s*[=:]',data),name
        # Protocol field names in code are allowed; fixed session/account values are not.
        assert not re.search(r'(?:["\x27](?:jessionid|jsessionid|sessionid|password|access_token)["\x27]\s*:\s*["\x27][^"\x27]{4,})',data,re.I),name
    assert all(x['sourceId'] in ids and all(s in ids for s in x['sourceIds']) for x in rows)
    print(f'PASS: 8 schools, 7 successful empty 2026 queries, 16 imported rows, 15 comparable, 34 sources, {len(public)} public files')

if __name__=='__main__':main()
