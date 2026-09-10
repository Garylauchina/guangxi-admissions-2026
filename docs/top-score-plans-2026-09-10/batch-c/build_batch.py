"""Build auditable school plans; formal Guangxi group codes are never inferred."""
from pathlib import Path
from collections import Counter
import json,hashlib,re,html
from parse_tables import parse
R=Path(__file__).resolve().parent;E=R/'evidence';DATE='2026-09-10';P='top20-c-2026-'
def read(name):return json.loads((E/name).read_text())
def write(name,data):(R/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
def text(name):return re.sub(r'\s+',' ',html.unescape(re.sub('<[^>]+>',' ',(E/name).read_text())))
config={
'bit':('10007','北京理工大学','101','https://admission.bit.edu.cn/static/front/bit/basic/html_web/zsjh.html',4,7),
'buaa':('10006','北京航空航天大学','101','https://lqcx.buaa.edu.cn/static/front/buaa/basic/html_web/zsjh.html',10,23),
'hit':('10213','哈尔滨工业大学','101','https://zsb.hit.edu.cn/information/plan?province=%E5%B9%BF%E8%A5%BF&year=2026',7,12),
'sysu':('10558','中山大学','103','https://admission.sysu.edu.cn/zsw/zsjh.html',24,167),
'hust':('10487','华中科技大学','102','https://zsb.hust.edu.cn/bkzn/zsjh.htm',27,160)}
plans=[];sources=[];checks=[]
def check(label,ok,detail=''):
 checks.append({'check':label,'passed':bool(ok),'detail':detail});assert ok,(label,detail)
def base(key,major,count,sourceRow):
 code,school,*_=config[key]
 return dict(id='plan26-top20-c-'+hashlib.sha256(f'{code}|物理|普通类|{major}'.encode()).hexdigest()[:16],year=2026,province='广西',planStage='initial',schoolCode=code,school=school,track='物理',batch='本科普通批',group=None,schoolGroupLabel=None,major=major,majorCode=None,plannedCount=int(count),requiredSubjects=[],subjectRule='unknown',requirementText=None,tuition=None,duration=None,note='',sourceId=P+key,category='普通类',currentGaokaoSeatsKnown=True,planVersion='2026高校当前公开普通类计划查询（非征集类别；广西组码待核）',checkedAt=DATE,sourceRow=sourceRow,fieldSourceIds={'schoolCode':[P+'gx-identity'],'batch':[P+'gx-identity']},groupMissingReason='官方公开初始计划未给出广西正式三位专业组代码，不能据校内名称、招生人数或首轮唯一组推定对应关系。')
def addnote(p,n,field=None,src=None):
 if n:p['note']+='；'*(bool(p['note']))+n
 if field and src:p['fieldSourceIds'].setdefault(field,[]).append(P+src)
def api(key):
 obj=read(key+'.json');d=obj['data'];rows=d['zsjhList']
 check(key+' 当前2026广西物理数据',all(x['nf']=='2026' and x['ssmc']=='广西' and x['klmc']=='物理类' for x in rows))
 check(key+' 列表与汇总闭合',sum(int(x['zsjhs']) for x in rows)==sum(int(x['zsjhs']) for x in d['zsjhTotal']))
 check(key+' 原始省组码未给出',d['withZyz'] is False and all(not x.get('zyzdm') for x in rows))
 for i,x in enumerate(rows,1):
  p=base(key,x['zymc'],x['zsjhs'],i);p.update(tuition=int(x['xf']) if x['xf'] else None,duration=x['xz'] or None,requirementText=x['xkkm'],schoolMajorCode=x.get('zydh') or None,disciplineCode=x.get('zydm') or None,campus=x.get('jdxq') or None,sourceCategory=x['zylx'],rawRemark=x.get('remarks') or '',majorDirections=x.get('bhzy') or None,college=x.get('xy') or None)
  if '化学' in x['xkkm']:p.update(requiredSubjects=['化学'],subjectRule='all')
  elif '不提科目要求' in x['xkkm'] or '物理(1门' in x['xkkm']:p.update(requiredSubjects=[],subjectRule='none')
  p['majorCodeNote']='校方查询的专业代号和学科代码单独保留，未核对为广西填报专业代码。'
  addnote(p,x.get('remarks'))
  if p['majorDirections']:addnote(p,'包含专业/培养方向：'+p['majorDirections'])
  if p['campus']:addnote(p,'计划所列校区：'+p['campus'])
  if key=='bit':
   addnote(p,'已查2026章程官方链接，但全文访问受限，未补录章程中的体检及其他报考限制；专业任选仍须符合正式培养和体检规定')
   p['conditionsStatus']='plan-remarks-verified-charter-unavailable'
  if key=='buaa':
   if '软件工程' in (p['majorDirections'] or ''):
    p['tuitionNote']='计划列5500元/年；如分流至软件工程，三、四年级为15000元/年。'
    addnote(p,p['tuitionNote'],'tuitionNote','buaa-charter')
   if '医工交叉' in p['major']:addnote(p,'本专业不招色盲、色弱考生','healthRequirement','buaa-charter')
   if '070202-应用物理学' in (p['majorDirections'] or ''):addnote(p,'包含专业中的应用物理学不招色盲，按正式大类分流和体检要求执行','healthRequirement','buaa-charter')
   if '080901-计算机科学与技术' in (p['majorDirections'] or ''):addnote(p,'包含专业中的计算机科学与技术要求能准确识别显示器上红、黄、绿、蓝、紫各颜色的数码和字母','healthRequirement','buaa-charter')
  if key=='sysu':
   p['trainingCampusNote']='2026级新生大一在广州校区南校园集中培养，大一学年结束后进入高考录取专业所在校区（园）。'
   addnote(p,p['trainingCampusNote'],'trainingCampusNote','sysu-charter')
   if p['duration']=='八年医':p['rawDuration']='八年医';p['duration']='八年制医学'
   if any(p['major'].startswith(k) for k in ['心理学','临床医学','基础医学','口腔医学','生物医学工程']):addnote(p,'本专业不招色盲、色弱考生','healthRequirement','sysu-charter')
   if p['major'].startswith('化学（'):addnote(p,'章程规定化学类不招色盲、色弱；本行化学（拔尖计划）的适用体检条件须以校方专业确认答复为准','healthRequirement','sysu-charter')
  addnote(p,p['groupMissingReason']);addnote(p,'初始计划以省招办公布及正式调整为准');plans.append(p)
for key in ['bit','buaa','sysu']:api(key)
# HIT: keep actual 校本部 identity; no migration to 威海/深圳 admission codes.
hitrows=parse(E/'hit.html')[0]['rows'];directory=parse(E/'hit-major-directory.html')[0]['rows']
check('HIT 2026广西页面年份', '2026' in text('hit.html') and '广西' in text('hit.html'))
selected=[]
for i,r in enumerate(hitrows):
 if len(r)!=4 or r[0]!='校本部' or r[2]!='物理+化学' or any(k in r[1] for k in ['中外合作','国家专项','高校专项','民族班','其他']):continue
 selected.append(r);p=base('hit',r[1],r[3],i+1);p.update(requiredSubjects=['化学'],subjectRule='all',requirementText=r[2],admissionCampus='校本部',sourceCategory=r[2])
 rows=[d for d in directory[1:] if d[0]==r[1] or d[0].startswith(r[1]+'（培养地点：')]
 check('HIT 专业目录精确对应 '+r[1],bool(rows))
 fee=set(d[4] for d in rows)
 check('HIT 专业学费可核 '+r[1],all('5500元/年' in f for f in fee))
 p['tuition']=6230 if r[1]=='具身智能（大湾区班）' else 5500;p['fieldSourceIds']['tuition']=[P+'hit-major-directory'];p['durationMissingReason']='已读初始计划及2026专业目录，未单列本行学制；不按本科名称推定。'
 dirs=list(dict.fromkeys(d[1] for d in rows if d[1]));p['majorDirections']='；'.join(dirs) or None
 p['college']='；'.join(dict.fromkeys(d[2] for d in rows if d[2]));p['fieldSourceIds']['majorDirections']=[P+'hit-major-directory']
 if p['majorDirections']:addnote(p,'包含专业/培养方向：'+p['majorDirections'])
 if '培养地点：' in rows[0][0]:
  p['trainingCampusNote']=rows[0][0].split('（培养地点：',1)[1].rstrip('）');addnote(p,'培养地点：'+p['trainingCampusNote'],'trainingCampusNote','hit-major-directory')
 addnote(p,'按校本部代码招生；培养地点与招生院校代码分别记录','admissionCampus','hit-charter')
 if '脑机智能' in p['major'] or '自主智能' in p['major']:addnote(p,'集群内'+('、'.join(k for k in ['智能医学工程','生物信息学','生物技术'] if k in (p['majorDirections'] or '')))+'不招色盲、色弱；此为包含专业限制，不能据此一概排除整个集群','healthRequirement','hit-charter')
 else:addnote(p,'专业任选仍须满足对应专业体检要求，详见2026章程第二十条','healthRequirement','hit-charter')
 addnote(p,p['durationMissingReason']);addnote(p,p['groupMissingReason']);addnote(p,'初始计划以省招办公布及正式调整为准');plans.append(p)
# HUST: only actual 2026 inline records. Missing fields remain unknown.
raw=(E/'hust.html').read_text();hustobj=json.JSONDecoder().raw_decode(raw.split('var year_listObject = ',1)[1])[0]
hust=[x for x in hustobj['2026'] if x['NF']=='2026' and x['SYSSMC']=='广西' and x['KLMC']=='物理类' and x['JHLBMC']=='普通类']
(E/'hust-2026-guangxi-physics.json').write_text(json.dumps(hust,ensure_ascii=False,indent=2)+'\n')
for i,x in enumerate(hust,1):
 p=base('hust',x['ZYMC'],x['ZSJHS'],i);p.update(sourceCategory=x['JHLBMC'],sourceRecordId=str(x['_id']),disciplineCode=x['ZSZYDM'],college=x['YXBMMC'] or None,majorDirections=x['BZ'] or None,rawRemark=x['BZ'] or '')
 p['requirementText']='原2026广西初始计划未列选科要求';p['subjectMissingReason']='官网当前2026广西计划内嵌记录没有选考科目字段；章程只要求考生符合专业选科要求，未逐专业列出。'
 p['durationMissingReason']='官网当前2026广西计划的XZMC字段为空；未从其他生源类别或旧年份推定。'
 p['tuitionMissingReason']='官网当前2026广西计划SFBZ字段为空；章程仅对本行所在普通专业给出4500—5850元/学年范围，未核到具体专业标准。'
 p['tuitionRange']=[4500,5850];p['fieldSourceIds']['tuitionRange']=[P+'hust-charter']
 if p['majorDirections']:addnote(p,'包含专业：'+p['majorDirections'])
 if x['ZYMC']=='软件工程':
  p['tuition']=5850;p['tuitionNote']='第1—2学年5850元/学年，第3—4学年16000元/学年。';p['fieldSourceIds']['tuition']=[P+'hust-charter'];p.pop('tuitionMissingReason');p.pop('tuitionRange');p['fieldSourceIds'].pop('tuitionRange');addnote(p,p['tuitionNote'],'tuitionNote','hust-charter')
 else:addnote(p,p['tuitionMissingReason'])
 if '八年制' in p['major']:p['duration']='八年制';p.pop('durationMissingReason');p['fieldSourceIds']['duration']=[P+'hust']
 if p['major'].startswith('临床医学'):addnote(p,'本专业不招色盲、色弱考生','healthRequirement','hust-charter')
 addnote(p,p['subjectMissingReason']);addnote(p,p.get('durationMissingReason'));addnote(p,p['groupMissingReason']);addnote(p,'初始计划以省招办公布及正式调整为准');plans.append(p)
for p in plans:
 if p.get('majorDirections'):
  p['includedMajors']=re.sub(r'(?:(?<=^)|(?<=[;；]))[0-9]+-','',p['majorDirections'])
  p['fieldSourceIds'].setdefault('includedMajors',p['fieldSourceIds'].get('majorDirections',[p['sourceId']]))
# Official ledger, with raw hash separate from redacted archive hash.
for key,(code,school,group,entry,n,seats) in config.items():
 m=read(('sysu_session' if key=='sysu' else key)+'.meta.json')
 s=dict(id=P+key,title=f'{school}2026年广西普通类物理科初始招生计划（官方公开查询）',url=entry,apiUrl=m['url'] if m.get('request') else None,publisher=school,sourceType='official',year=2026,publishedAt=None,accessedAt=DATE,recordCount=n,method='按2026/广西/物理类/普通类别精确筛选学校公开初始计划；未使用录取人数或征集余额。',notes=['原始省专业组代码未给出，不能用于目标首轮组完整匹配。'],request=m.get('request'),sha256=m.get('sanitizedSha256',m.get('sha256')),rawResponseSha256=m.get('rawResponseSha256',m.get('sha256')))
 if key=='hit':s['method']='校方2026广西初始计划HTML表，仅取校本部非中外合作物理+化学7条；合并单元格按原表展开。另从2026本科招生专业目录核对学费、包含专业和培养地点。'
 if key=='hust':s['method']='官网招生计划页面内嵌year_listObject[2026]；逐条校验NF=2026、SYSSMC=广西、KLMC=物理类、JHLBMC=普通类。'
 if key=='sysu':s['method']='依照官网公开tplt.js规定的Cookie和CSRF流程，无账号查询；会话和token不归档，响应顶层jessionid已移除。'
 sources.append(s)
for key,date,title in [('buaa-charter','2026-05-31','北京航空航天大学2026年招生章程'),('hit-charter','2026-05-28','哈尔滨工业大学2026年本科招生章程'),('hit-major-directory','2026-06-02','哈尔滨工业大学2026年本科招生专业'),('sysu-charter','2026-05-29','中山大学2026年本科招生章程'),('hust-charter','2026-05-29','华中科技大学2026年本科招生章程')]:
 m=read(key+'.meta.json');sources.append(dict(id=P+key,title=title,url=m['url'],publisher=config[key.split('-')[0]][1],sourceType='official',year=2026,publishedAt=date,accessedAt=DATE,sha256=m.get('sanitizedSha256',m.get('sha256')),method='逐条读取当年官方全文，用于相关字段和限制；不产生计划人数。'))
sources.append(dict(id=P+'gx-identity',title='广西2026本科普通批首轮物理类院校身份及批次核对',url='https://www.gxeea.cn/view/content_624_33107.htm',publisher='广西招生考试院',sourceType='official',year=2026,publishedAt='2026-07-18',accessedAt=DATE,method='复用现站已核对院校代码及本科普通批身份；不读取投档人数生成初始计划，不据此推定组码。'))
targets=json.loads((R.parent/'targets.json').read_text());results=[];catalog=[]
for key,(code,school,group,entry,n,seats) in config.items():
 rows=[p for p in plans if p['schoolCode']==code];check(key+' 收录范围行数人数',len(rows)==n and sum(p['plannedCount'] for p in rows)==seats,{'rows':len(rows),'seats':sum(p['plannedCount'] for p in rows)})
 t=next(x for x in targets if x['schoolCode']==code and x['group']==group)
 note=f'已采2026年广西普通物理计划{n}条、{seats}人；公开查询未给出广西正式{group}组对应证据。专业组内全部专业范围仍未核定，所有新行group=null，不能认定目标组已补齐。'
 sourceids=[s['id'] for s in sources if s['id']==P+key or s['id'].startswith(P+key+'-')]
 results.append(dict(cutoffId=t['id'],schoolCode=code,school=school,track='物理',group=group,status='partial',note=note,sourceIds=sourceids,checkedAt=DATE,matchedPlanRows=0,schoolPlanRows=n,schoolPlannedCount=seats,groupCoverage='unverified',checkedUrls=[entry]+[s['url'] for s in sources if s['id'] in sourceids and s['url']!=entry]))
 catalog.append(dict(schoolCode=code,school=school,year=2026,status='collected',entryUrl=entry,sourceIds=sourceids,checkedAt=DATE,note=note,scope='广西普通类物理科；同校计划已采，目标省组尚未匹配',rowCount=n,plannedCount=seats,targetStatus='partial'))
# Record actual ancillary attempts, not fictional negatives.
results[0]['checkedUrls']+=['https://admission.bit.edu.cn/','https://www.bit.edu.cn/wx/index2.htm','https://gaokao.chsi.com.cn/zsgs/zhangcheng/listVerifedZszc--infoId-7657206740,method-view,schId-7.dhtml','https://mp.weixin.qq.com/s/cNDch543wiY6MVzU0lDqBA']
results[0]['attemptNotes']=['官网招生计划成功。官网导航链接的2026章程阳光高考页面HTTP412；校方微信文章无法读取完整正文，章程限制缺口保留。']
results[1]['checkedUrls']+=['https://zs.buaa.edu.cn/','https://drafoon.epub360.com.cn/v2/manage/book/ub4sza/?from=singlemessage','https://js.epub360.com/ub4sza/776/index.js']
results[1]['attemptNotes']=['2026官方电子报考指南入口及公开图册数据已读，未完成70页逐图核验，未据图册推定101组；实际计划API成功、组码空。']
results[3]['attemptNotes']=['直接无会话POST返回403；依照官方公开CSRF握手后200。没有登录或私有接口绕过。']
check('总计72条369人',len(plans)==72 and sum(p['plannedCount'] for p in plans)==369)
check('所有目标严格来自锁定清单',len(results)==5 and all(r['cutoffId'] in {x['id'] for x in targets} for r in results))
check('所有正式组保持未知',all(p['group'] is None for p in plans) and all(t['status']=='partial' and t['matchedPlanRows']==0 for t in results))
check('华科未知选科不得判为不限',all(p['subjectRule']=='unknown' for p in plans if p['schoolCode']=='10487'))
check('所有行广西2026初始计划',all(p['year']==2026 and p['province']=='广西' and p['planStage']=='initial' for p in plans))
check('来源ID完整',all(x in {s['id'] for s in sources} for p in plans for x in [p['sourceId']]+[s for a in p['fieldSourceIds'].values() for s in a]))
check('记录ID唯一',len({p['id'] for p in plans})==len(plans))
check('中山首年培养地点逐行可见',all('大一在广州校区南校园' in p['note'] for p in plans if p['schoolCode']=='10558'))
check('API脱敏归档',all(not any(k in read(key+'.json') for k in ['jessionid','jsessionid','token','csrfToken']) for key in ['bit','buaa','sysu']))
for name,data in [('plans-upsert.json',plans),('sources.json',sources),('source-catalog.json',catalog),('target-results.json',results),('QA.json',dict(checkedAt=DATE,passed=all(c['passed'] for c in checks),checks=checks,summary={'schools':5,'rows':72,'seats':369,'targetMatched':0,'targetPartial':5}))]:write(name,data)
print(json.dumps({'rows':len(plans),'seats':sum(p['plannedCount'] for p in plans),'checks':len(checks),'targetPartial':5},ensure_ascii=False))
