"""Create school review summaries and a minimal public reproduction request manifest."""
import collections,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
def read(n):return json.loads((ROOT/n).read_text())
def write(n,v):(ROOT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
rows=read('corrected-major-cutoffs.json');sources=read('sources.json');source_index={s['id']:s for s in sources}
jobs={j['id']:j for j in read('fetch-manifest.json')};public=[]
for s in sources:
    if s['id'] in jobs:j=dict(jobs[s['id']])
    elif s['id'].startswith('gxeea-'):
        j={'id':Path(s['rawPath']).stem,'url':s['url'],'ext':'html'}
    else:raise ValueError(s['id'])
    j['expectedSha256']=s['sha256'];public.append(j)
write('public-fetch-manifest.json',public)
summaries=[]
for code in sorted({r['schoolCode'] for r in rows}):
    school_rows=[r for r in rows if r['schoolCode']==code];ids=sorted({r['sourceId'] for r in school_rows})
    summaries.append({'school':school_rows[0]['school'],'schoolCode':code,
                      'checkedAt':max(source_index[s]['accessedAt'] for s in ids),
                      'sourceIds':ids,'checkedUrls':[source_index[s]['url'] for s in ids],
                      'result':'已核对并收入'+str(len(school_rows))+'条2026广西具体专业录取最低分；限列明专业与来源。',
                      'recordCount':len(school_rows),'scoreComparableCount':sum(r['scoreComparable'] for r in school_rows),
                      'byCategory':dict(collections.Counter(r['admissionType'] for r in school_rows)),
                      'byRound':dict(collections.Counter(r['round'] for r in school_rows)),
                      'conflictRecordIds':[r['id'] for r in school_rows if r['conflictFields']],
                      'accessLimitType':'none-for-listed-sources','scope':'已取得源表内全部适用专业行；非对全校所有渠道的穷尽证明'})
summaries.extend(read('negative-findings.json'))
write('school-reviews.json',summaries)
write('fetch-results.json',[read(str(p.relative_to(ROOT))) for p in sorted((ROOT/'raw').glob('*.meta.json'))])
