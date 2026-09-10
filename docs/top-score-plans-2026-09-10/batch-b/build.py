#!/usr/bin/env python3
"""Build a conservative 2026 Guangxi plan supplement from reviewed public facts."""
from pathlib import Path
from collections import Counter
import json,hashlib,datetime
R=Path(__file__).resolve().parent

def read(p): return json.loads((R/p).read_text())
def write(p,x): (R/p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
T=read('transcribed-sjtu-2026.json')
assert hashlib.sha256((R/'raw/sjtu-2026-plan-image.png').read_bytes()).hexdigest()==T['imageSha256']
M={p.name[:-10]:json.loads(p.read_text()) for p in sorted((R/'raw').glob('*.meta.json'))}
check=max(x['accessedAt'] for x in M.values())
prefix='top-b-'
titles={
'sjtu-2026-plan-api':'上海交通大学2026年招生计划（含医学院）—官方公开文章 API',
'sjtu-2026-plan-image':'上海交大报2026年6月15日招生专刊第3版招生计划原图',
'sjtu-2026-plan-page':'上海交通大学2026年招生计划（含医学院）',
'sjtu-plan-news-list':'上海交通大学招生计划官方公开栏目 API',
'sjtu-pujiang-overview':'上海交通大学浦江国际学院—走进学院',
'sjtu-med-home':'上海交通大学医学院阳光招生网',
'sjtu-med-plan-list':'上海交通大学医学院招生计划栏目',
'sjtu-med-plan-home':'上海交通大学医学院旧计划路径（本轮404）',
'gxeea-2026-physics-filing':'广西2026年普通高校招生本科普通批物理类投档最低分数线（仅校码与组身份佐证）',
'fudan-plan-list':'复旦大学招生计划栏目（本轮最新可读2024）',
'fudan-home':'复旦大学本科招生网',
'fudan-2026-charter':'复旦大学2026年招生章程发布',
'nju-home':'南京大学本科招生网',
'nju-init-js':'南京大学官网公开导航配置',
'nju-common-js':'南京大学官网公开页面脚本',
'nju-plan-page':'南京大学招生计划查询公开前端',
'nju-plan-api':'南京大学2026广西计划查询 API（本轮403）',
'nju-plan-params':'南京大学计划筛选参数 API（本轮403）',
'nju-plan-gx-physics':'南京大学2026广西物理类普通批次计划查询 API（本轮403）',
'nju-tplt-js':'南京大学官网公开会话与CSRF请求流程脚本',
'nju-params-session':'南京大学招生计划公开筛选参数（正常前端流程200）',
'nju-gx-2026-normal':'南京大学2026广西物理类普通批次计划（正常前端流程200）',
'zju-zsc-home':'浙江大学本科招生网',
'zju-entry':'浙江大学2026广西本科招生咨询联系方式入口（不是计划查询）',
'zju-detail-js':'浙江大学公开咨询详情页脚本',
'zju-config':'浙江大学公开咨询站点配置（标题：本科招生咨询联系方式）',
'zju-undergraduate-info':'浙江大学本科教育信息公开栏目',
'zju-information-list':'浙江大学本科招生信息公开栏目',
'zju-news-list':'浙江大学本科招生最新公告栏目',
}
sources=[]
for key,m in M.items():
 method='本轮直接下载官方公开页面；用于入口或缺口证据，不提供可入库的2026广西专业人数。'
 if key=='sjtu-2026-plan-image': method='按五张独立表逐项目视识别广西列；本次只导出校本部普通理工15条35人及医学院普通理工3条15人。校本部总列36=理工35+文史1；图内高校专项、国家专项另表未导入。原图未列省编组码、再选科目、学制学费与省内批次，全部保留未知。以上计划均以当地省级教育考试机构公布为准。'
 if key=='sjtu-2026-plan-api': method='公开只读POST返回文章标题、发布日期2026-07-03 09:05、2026计划原图链接。'
 if key=='gxeea-2026-physics-filing': method='GB18030解码，仅核对10248本部和19248医学院身份及目标组存在；不得由组投档线反推组内专业或人数。'
 if key=='sjtu-pujiang-overview': method='官方正文说明浦江国际学院负责本科阶段英文中外合作办学项目招生及人才培养；仅用于电子信息类（浦江国际学院）类别旁证，不补学费、科目或组码。'
 if key=='nju-params-session': method='遵循官网tplt.js的正常Cookie会话及公开CSRF流程读取；广西2026物理类明确有普通批次选项。早期裸请求403不代表该校数据不可公开读取。会话值不保存。'
 if key=='nju-gx-2026-normal': method='按公开前端流程选择广西、2026、物理类、普通批次，逐行直接列省年科类；12条计划47人与汇总一致。原表直接列四年、物理化学均须选考；学费及广西具体批次未列，withZyz=false、组码字段空。planStage initial为非征集分类，官网未给发布版次，不能证明首发版或省最终版。会话字段jessionid删除；sha256为脱敏归档哈希，responseSha256为原响应哈希。'
 if m['status']!=200: method='按官方公开前端路径或公开脚本所列接口尝试，记录失败；未绕过访问限制，未视为无招生。'
 sources.append(dict(id=prefix+key,title=titles.get(key,key),url=m['url'],year=2026,publishedAt='2026-06-15' if key=='sjtu-2026-plan-image' else ('2026-07-03' if key in ['sjtu-2026-plan-api','sjtu-2026-plan-page'] else None),accessedAt=m['accessedAt'],sha256=m.get('sha256'),recordCount=18 if key=='sjtu-2026-plan-image' else 0,method=method,httpStatus=m['status'],request=m.get('request'),requestEncoding=m.get('requestEncoding'),accessError=m.get('error'),rawFile=m.get('rawFile')))
 if key=='nju-gx-2026-normal': sources[-1]['recordCount']=12
 if m.get('responseSha256'): sources[-1].update(responseSha256=m['responseSha256'],archiveSha256=m['archiveSha256'],redactedFields=m['redactedFields'])
plans=[]
for i,x in enumerate(T['rows'],1):
 code=x['schoolCode'];note='官方2026计划原图广西列直接人数；源科类“理工”，规范为广西物理类，再选科目尚待核实。原图未列广西专业组、专业代码及省内批次，不能归到锁定目标组。'
 if x['category']=='中外合作办学':note+='浦江国际学院项目类别另以该学院官网说明核实；学费未在计划图列明。'
 plans.append(dict(id=f'plan26-top-b-sjtu-{code}-{i:02}',year=2026,province='广西',planStage='initial',school='上海交通大学' if code=='10248' else '上海交通大学医学院',schoolCode=code,track='物理',sourceTrack='理工',batch='本科（批次待核）',group=None,major=x['major'],majorCode=None,plannedCount=x['plannedCount'],duration=None,tuition=None,requiredSubjects=[],subjectRule='unknown',requirementText='原表科类：理工；广西再选科目未列',category=x['category'],sourceId=prefix+'sjtu-2026-plan-image',sourceIds=[prefix+'sjtu-2026-plan-image',prefix+'sjtu-2026-plan-api',prefix+'gxeea-2026-physics-filing']+([prefix+'sjtu-pujiang-overview'] if x['category']=='中外合作办学' else []),sourceTable=x['table'],sourceRow=x['tableDataRow'],note=note,reviewedAt=check,groupMappingStatus='unmatched',coverageStatus='学校物理类计划已采集，专业组归属待核'))
assert len(plans)==18 and sum(x['plannedCount'] for x in plans)==50
assert sum(x['plannedCount'] for x in plans if x['schoolCode']=='10248')==35
assert sum(x['plannedCount'] for x in plans if x['schoolCode']=='19248')==15
nju=read('raw/nju-gx-2026-normal.json');njrows=nju['data']['zsjhList'];njtotal=nju['data']['zsjhTotal']
assert nju['state']==1 and len(njrows)==12 and sum(x['zsjhs'] for x in njrows)==47
assert len(njtotal)==1 and njtotal[0]['nf']=='2026' and njtotal[0]['ssmc']=='广西' and njtotal[0]['klmc']=='物理类' and njtotal[0]['zsjhs']==47
assert not nju['data']['withZyz']
for i,x in enumerate(njrows,1):
 assert x['nf']=='2026' and x['ssmc']=='广西' and x['klmc']=='物理类' and x['zslx']=='普通批次'
 assert not any(x.get(k) for k in ['zyz','zyzdm','zyzname','zycc','zyxf','zydh'])
 assert x['zyxz']=='四年' and x['xkkm']=='物理,化学(2门科目考生均须选考方可报考)'
 plans.append(dict(id=f'plan26-top-b-nju-{i:02}',year=2026,province='广西',planStage='initial',planVersion='2026高校公开普通招生计划（当前查询版；广西组码待核）',school='南京大学',schoolCode='10284',track='物理',sourceTrack='物理类',batch='本科（批次待核）',group=None,major=x['zymc'],majorCode=None,sourceDisciplineCode=x['zydm'],plannedCount=x['zsjhs'],duration=x['zyxz'],tuition=None,requiredSubjects=['化学'],subjectRule='all',requirementText=x['xkkm'],category='普通类',sourceCategory=x['zslx'],sourceId=prefix+'nju-gx-2026-normal',sourceIds=[prefix+'nju-gx-2026-normal',prefix+'nju-params-session',prefix+'gxeea-2026-physics-filing'],fieldSourceIds={'schoolCode':[prefix+'gxeea-2026-physics-filing']},sourceRow=i,note='官网2026广西物理类普通批次计划直接人数；原表列四年、物理和化学均须选考。未列广西具体批次、组码、学费和省编专业代号，均保留待核；专业学科代码另存，不作为广西填报代码。',reviewedAt=check,groupMappingStatus='unmatched',coverageStatus='学校物理类计划已采集，专业组归属待核'))
school_keys={
'10248':['sjtu-2026-plan-page','sjtu-2026-plan-api','sjtu-2026-plan-image','sjtu-plan-news-list','sjtu-pujiang-overview','gxeea-2026-physics-filing'],
'19248':['sjtu-2026-plan-page','sjtu-2026-plan-api','sjtu-2026-plan-image','sjtu-med-home','sjtu-med-plan-list','sjtu-med-plan-home','gxeea-2026-physics-filing'],
'10335':['zju-zsc-home','zju-entry','zju-config','zju-detail-js','zju-undergraduate-info','zju-information-list','zju-news-list'],
'10246':['fudan-plan-list','fudan-home','fudan-2026-charter'],
'10284':['nju-home','nju-init-js','nju-plan-page','nju-tplt-js','nju-params-session','nju-gx-2026-normal','nju-plan-params','nju-plan-api','nju-plan-gx-physics','gxeea-2026-physics-filing']}
notes={
'10248':'官网2026初始计划已逐项录入15条普通理工35人（含1条浦江国际学院项目）；广西组码、再选科目和批次未列。109与110组均无法把具体专业严格归组，本次目标未匹配。',
'19248':'官网2026医学院单独普通计划已录入3条15人，独立校码19248；原图未列广西101/102等组归属，不能认定101组已有计划匹配。医学院计划栏目另查仅见2025及2024，未由旧年补2026字段。',
'10335':'核查招生主页、信息公开与最新公告未取得2026广西分专业人数及150组清单。此前xjjh-detail/2026?id=450000经官网链接、配置和详情脚本确认是本科招生咨询联系方式，并非计划查询，不能据其页面年份认定有广西2026计划。',
'10246':'官方招生计划栏目当前最新可读2024；2026章程只说明分省专业计划以各省级招办公布为准。未取得2026广西102组专业和人数；搜索发现的“2026参考”旧年或预测表未采用。',
'10284':'按官网公开正常会话和CSRF流程已成功取得2026广西物理类普通批次12条47人，四年、物理化学均须均有直接依据；具体广西批次、学费、省编专业代号、组码未列，105组仍不能匹配。早期裸请求403为已解决的访问方式问题，不能再表述为当前接口不可读取。'}
catalog=[]
for code,keys in school_keys.items():
 ids=[prefix+k for k in keys];rows=[p for p in plans if p['schoolCode']==code]
 catalog.append(dict(schoolCode=code,school={'10248':'上海交通大学','19248':'上海交通大学医学院','10335':'浙江大学','10246':'复旦大学','10284':'南京大学'}[code],year=2026,province='广西',status='collected' if rows else 'entry-only',sourceIds=ids,checkedUrls=[M[k]['url'] for k in keys],checkedAt=check,note=notes[code],entryUrl=M['nju-plan-page' if code=='10284' else keys[0]]['url'],recordCount=len(rows),plannedCount=sum(p['plannedCount'] for p in rows) if rows else None,groupCoverage='unmatched',accessRestriction='missing-current-plan' if not rows else 'missing-group-code'))
targets=json.loads((R.parent/'targets.json').read_text())
if isinstance(targets,dict): targets=targets['targets']
keys={('10248','109'),('10248','110'),('19248','101'),('10246','102'),('10335','150'),('10284','105')}
results=[]
for t in targets:
 if (str(t['schoolCode']),str(t['group'])) not in keys:continue
 c=next(c for c in catalog if c['schoolCode']==str(t['schoolCode']))
 results.append(dict(cutoffId=t.get('cutoffId',t.get('id')),priority=t.get('priority'),school=t['school'],schoolCode=t['schoolCode'],track=t['track'],group=t['group'],score=t['score'],status='source-found' if c['recordCount'] else 'entry-only',note=c['note'],sourceIds=c['sourceIds'],checkedUrls=c['checkedUrls'],checkedAt=check,matchedPlanCount=0,unmappedSchoolPlanCount=c['recordCount'],accessRestriction=c['accessRestriction']))
assert len(results)==6
write('plans-upsert.json',plans);write('sources.json',sources);write('source-catalog.json',catalog);write('target-results.json',results)
# Every attempted download remains separately auditable, including non-200 responses.
write('fetch-results.json',list(M.values()))
print('built',len(plans),'rows',len(sources),'sources',len(results),'targets')
