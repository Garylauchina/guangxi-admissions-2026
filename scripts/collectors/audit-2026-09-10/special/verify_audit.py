"""Validate delivered research JSON without contacting sites or using private data."""
from pathlib import Path
from collections import Counter
import json
R=Path(__file__).resolve().parent
def read(n):return json.loads((R/n).read_text())
p,s,pol,f=map(read,['corrected-special-programs.json','sources.json','policies.json','findings.json'])
checks=[]
def check(name,condition):
    checks.append(dict(name=name,passed=bool(condition)))
    assert condition,name
ids={x['id'] for x in s}
records=[r for x in p for r in x['scoreRecords']]
strong=[x for x in p if x['type']=='strong-foundation']
check('43项含39强基及4独立项目',len(p)==43 and len(strong)==39)
check('项目来源分数ID全部唯一',len({x['id'] for x in p})==43 and len(ids)==len(s) and len({x['id'] for x in records})==len(records))
check('省份范围21确认14待核4排除',Counter(x['guangxiStatus'] for x in strong)=={'confirmed':21,'unknown':14,'excluded':4})
check('全部项目和分数属于2026',all(x['year']==2026 for x in p+records))
check('34条均广西分数',len(records)==34 and all(x['province']=='广西' for x in records))
check('排除院校无广西成绩或人数',all(not x['scoreRecords'] and x['planCount'] is None and x['planStatus']=='not-applicable-province' for x in strong if x['guangxiStatus']=='excluded'))
check('未知人数保持空值且逐项注明具体原因',all(x['planCount'] is None and x.get('planGapReason') and x.get('planEvidence',{}).get('sourceIds') for x in p))
def allrefs(obj):
    if isinstance(obj,dict):
        for k,v in obj.items():
            if k=='sourceIds':yield from v
            else:yield from allrefs(v)
    elif isinstance(obj,list):
        for v in obj:yield from allrefs(v)
check('所有嵌套来源引用均可解析',all(x in ids for x in allrefs(p+pol+[f])))
check('全部成绩有公式和分数口径',all(x.get('formula') and x.get('scoreType') and x.get('scoreLabel') for x in records))
check('所有录取综合成绩已注明满分',all(x['maxScore'] in [100,750,1000] and 0<=x['score']<=x['maxScore'] for x in records if x['scoreType']=='admission-composite'))
check('六处原缺失公式均已修复',f['formulaRepairs']==6 and not any(x.get('formulaStatus')=='unverified' for x in records))
check('华科3条排序码从分数中剥离',len([x for x in records if 'tieBreakCode' in x])==3 and all(x['score']==int(x['rawScoreText'].split('.')[0]) and len(x['tieBreakCode'])==9 for x in records if 'tieBreakCode' in x))
check('原24数值不变',len(f['originalScoreAudit'])==24 and all(x['unchanged'] for x in f['originalScoreAudit']))
check('22原分数重读通过2重庆保留缺口',f['originalScoresReverified']==22 and f['originalScoresCurrentSourceUnreadable']==2 and sum(x.get('auditStatus')=='prior-value-current-source-unreadable' for x in records)==2)
check('所有来源包含标题URL访问日与官方身份',all(x.get('title') and x.get('url','').startswith('http') and x.get('accessedAt') and x['sourceType']=='official' for x in s))
out=dict(status='passed',checkCount=len(checks),checks=checks,factualLimit='结构检查不替代事实核验；14校广西投放、全部广西名额及2条重庆原表仍有明确缺口。')
(R/'validation.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(out,ensure_ascii=False,indent=2))
