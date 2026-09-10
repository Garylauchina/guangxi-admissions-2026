"""2026 Guangxi physics initial plan batch; preserve internal group labels without mapping."""
from pathlib import Path
from collections import defaultdict
import json,re,hashlib,html
from parse_tables import parse
R=Path(__file__).resolve().parent
DATE='2026-09-10';plans=[]
manifest=json.loads((R/'request-manifest.json').read_text())
def clean(s):return re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]+>','；',str(s)))).replace('；；','；').strip('； ')
def add(school,code,major,count,localgroup,req,sid,**kw):
 required=['化学','生物'] if '物+化+生' in req else (['化学'] if ('物+化' in req or '物理+化学' in req) else [])
 note='仅公布校内组名称，广西正式专业组代码未核实；原计划查询未列学费；初始计划以省招办公布及正式调整为准'
 ident=hashlib.sha256('|'.join([code,localgroup,major]).encode()).hexdigest()[:16]
 d=dict(id='plan26-batch-d-'+ident,year=2026,province='广西',schoolCode=code,school=school,track='物理',batch='本科普通批',group=None,schoolGroupLabel=localgroup,major=major,majorCode=None,plannedCount=count,requiredSubjects=required,subjectRule='all' if required else 'none',requirementText=req,tuition=None,duration=None,note=note,sourceId=sid,category='普通类',planStage='initial',planVersion='2026高校公开初始计划（广西组码待核）',currentGaokaoSeatsKnown=True,checkedAt=DATE,fieldSourceIds={'schoolCode':['batch-d-2026-gx-identity'],'batch':['batch-d-2026-gx-identity']},groupMissingReason='原表只有校内专业组名称，未取得广西正式三位代码对应证据。')
 extra=kw.pop('note','');d.update(kw);d['note']=extra+'；'+note if extra else note;plans.append(d)
csu=json.loads((R/'evidence/csu.json').read_text())['data']
for i,x in enumerate(csu['list'],1):
 assert x['A']==2026 and x['B']=='广西' and x['C']=='物理类'
 req=clean(x['D']);localgroup=req.split('；')[0];rawmajor=clean(x['E']);major=rawmajor.lstrip('▲');remark=clean(x.get('H',''));direction=clean(x.get('F',''))
 category='中外合作办学' if '中外合作' in remark else '普通类'
 add('中南大学','10533',major,int(x['G']),localgroup,req,'batch-d-2026-csu',rawMajor=rawmajor,category=category,sourceRow=i,sourceRecordId=x['_id'],majorDirections=direction,note='原表备注：'+remark+'；分流去向：'+direction,duration='五年' if '五年制' in major else ('八年' if '八年制' in major else None))
assert len(csu['list'])==csu['total']==26
assert sum(int(x['G']) for x in csu['list'])==sum(int(x['E']) for x in csu['line_data'])==321
scut=parse(R/'evidence/scut.html')[0]['rows'];assert scut[0]==['省份','科类','类别','招生专业','计划','选考科目','专业组']
for i,x in enumerate(scut[1:],2):
 assert x[0]=='广西' and x[1]=='理工/物理类' and x[2]=='普通类'
 add('华南理工大学','10561',x[3],int(x[4]),x[6],x[5],'batch-d-2026-scut',sourceRow=i,note='原表类别：普通类；查询条件：2026年、广西、理工/物理类、普通类')
sources=[]
for k,school in [('csu','中南大学'),('scut','华南理工大学')]:
 m=manifest[k];f=R/'evidence'/('csu.json' if k=='csu' else 'scut.html')
 sources.append(dict(id='batch-d-2026-'+k,title=school+'2026年广西普通类物理科初始招生计划（官方公开查询）',url=m['entryUrl'],apiUrl=m['url'],publisher=school,sourceType='official',year=2026,publishedAt=None,accessedAt=DATE,sha256=hashlib.sha256(f.read_bytes()).hexdigest(),recordCount=sum(p['sourceId']=='batch-d-2026-'+k for p in plans),method=m['method'],notes=['本批仅采物理类；未宣称覆盖历史类或学校全部招生类型。','只有校内组名称，group保持null，不自动匹配首轮投档线。']))
sources.append(dict(id='batch-d-2026-gx-identity',title='广西2026本科普通批首轮物理类院校身份及批次核对',url='https://www.gxeea.cn/view/content_624_33107.htm',publisher='广西招生考试院',sourceType='official',year=2026,publishedAt='2026-07-18',accessedAt=DATE,recordCount=0,method='只核对10533中南大学、10561华南理工大学及本科普通批身份，不以投档人数产生初始计划，不据此映射组码。'))
catalog=[]
for school,code,k in [('中南大学','10533','csu'),('华南理工大学','10561','scut')]:
 rr=[r for r in plans if r['school']==school]
 catalog.append(dict(schoolCode=code,school=school,year=2026,province='广西',status='collected',sourceIds=['batch-d-2026-'+k,'batch-d-2026-gx-identity'],checkedAt=DATE,entryUrl=manifest[k]['entryUrl'],note=f"本批仅采2026广西普通类物理计划{len(rr)}条{sum(r['plannedCount'] for r in rr)}人；广西正式组码未核实，group=null，保留校内组名称。未覆盖历史类及其他招生类型，原查询未列学费。"))
for name,obj in [('plans-upsert.json',plans),('sources.json',sources),('source-catalog.json',catalog)]:
 (R/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'rows':len(plans),'seats':sum(x['plannedCount'] for x in plans),'schools':catalog},ensure_ascii=False,indent=2))
