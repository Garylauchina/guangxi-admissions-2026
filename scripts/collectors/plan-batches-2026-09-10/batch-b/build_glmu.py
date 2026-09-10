"""Parse the official 2026 plan PDF; pdfplumber required. Rendered source inspected in full."""
import json,re,datetime
import pdfplumber
from pathlib import Path
from build import row
ROOT=Path(__file__).resolve().parent
NOW=datetime.datetime.now(datetime.timezone.utc).isoformat()
def read(n):return json.loads((ROOT/n).read_text())
with pdfplumber.open(ROOT/'raw/glmu-plan-pdf.pdf') as pdf:
    pages=[p.extract_tables() for p in pdf.pages];assert len(pages)==2
    assert '2026年普通高等教育本专科招生计划' in pdf.pages[0].extract_text()
tab=pages[0][0];assert tab[1][7]=='广西' and tab[2][7]=='4008' and tab[3][7]=='3608'
plans=[];excluded=[];last=[None]*4;vocational=False
for i,c in enumerate(tab[4:],5):
    if c[0] and '合计' in c[0]:
        assert '高职' in c[0] and c[7]=='400';vocational=True;last=[None]*4;continue
    for j in range(4):
        if c[j] is not None:last[j]=c[j]
        else:c[j]=last[j]
    name=re.sub(r'\s+','',c[2]);req=c[4]
    if '定向' in name:
        excluded.append({'sourceId':'batch-b-glmu-plan-pdf','sourcePage':1,'sourceRow':i,'major':name,'plannedCount':int(c[7]),'reason':'定向58人需进一步地区/组码/批次证据，本批不入'});continue
    assert req.startswith(('物理','历史')) and c[7].isdigit()
    track='历史' if req.startswith('历史') else '物理';r=row('glmu-plan-pdf','桂林医科大学','10601',track,name,c[7],i)
    r.update(majorCode=c[1],duration={'三年':'3','四年':'4','五年':'5'}[c[3]],tuition=c[5],requirementText=req,
             requiredSubjects=[x for x in ('化学','生物') if x in req],subjectRule='all' if '+' in req else 'none',
             batch='高职（批次待核）' if vocational else '本科（批次待核）',category='未注明招生类别',sourcePage=1)
    r['note']='直接采用2026官方计划PDF广西列；原表未列专业组及录取批次，资格范围尚待核实。'
    if '民族班' in name:r['category']='民族班';r['note']='本条原名明确民族班；人数来自官方广西列；专业组和批次未列。'
    if '中澳' in name:
        r['category']='中澳联合培养项目';r['note']='本条为中澳学分互认联合培养项目；原学费为6480+澳方，未给澳方金额；专业组和批次未列。'
    plans.append(r)
assert len(plans)==40 and sum(r['plannedCount'] for r in plans)==3950
assert sum(int(c[7]) for c in pages[1][0][1:])==202
excluded.append({'sourceId':'batch-b-glmu-plan-pdf','sourcePage':2,'plannedCount':202,'reason':'第二页全部预科，本批排除'})
sources=[]
for sid,title,count in [('glmu-plan','桂林医科大学2026年普通高等教育本专科招生计划一览表',0),('glmu-plan-pdf','桂林医科大学2026年普通高等教育本专科招生计划原PDF',40)]:
    m=read('raw/'+sid+'.meta.json');s={'id':'batch-b-'+sid,'title':title,'url':m['url'],'publisher':'桂林医科大学','year':2026,
         'publishedAt':'2026-06-13','accessedAt':m['accessedAt'],'sha256':m['sha256'],'recordCount':count,'rawPath':m['rawFile'],
         'method':'直接读取广西列；只延续原图跨行合并的专业名称/代码/学制，不分配合计人数。原表全部适用行已目视核对。未列批次/资格类别不推断。','status':200}
    if sid.endswith('pdf'):s['parentSourceId']='batch-b-glmu-plan'
    sources.append(s)
extension={'plans':plans,'sources':sources,'excluded':excluded,
           'catalog':{'schoolCode':'10601','school':'桂林医科大学','year':2026,'status':'collected','sourceIds':['batch-b-glmu-plan','batch-b-glmu-plan-pdf'],
                      'checkedAt':NOW,'recordCount':40,'coverage':'partial','entryUrl':sources[0]['url'],
                      'note':'直接广西列40条3950人；本专科4008人中另排定向58人，第二页预科202另排。全部组码/具体批次未列，未注明资格类别行保持待核；明确民族班和中澳项目单列。'},
           'checks':[{'school':'桂林医科大学','records':40,'plannedCount':3950,'sourceGuangxiTotal':4008,'excludedDirectedSeats':58,
                      'preparatorySeparatelyExcluded':202,'totalReconciliation':'PASS','fullSourceVisualReview':'PASS',
                      'samples':[plans[0],plans[len(plans)//2],plans[-1]]}]}
(ROOT/'glmu-extension.json').write_text(json.dumps(extension,ensure_ascii=False,indent=2)+'\n')
print('GLMU: 40 rows / 3950 seats')
