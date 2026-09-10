import test from 'node:test';
import assert from 'node:assert/strict';
import { getReference, reviewDate, scoreMatch, subjectStatus, filterRows, exactGroupKey, firstRoundIndex, csvCell, safeUrl } from '../site/logic.js';
import { buildCoverage } from '../site/coverage.js';

test('位次只按同科类公开区间换算；缺档不猜测', () => {
  const rows = [{track:'物理',score:600,rankStart:100,rankEnd:120},{track:'历史',score:600,rankStart:20,rankEnd:30}];
  assert.equal(getReference('110','rank','物理',rows).score,600);
  assert.ok(getReference('110','rank','历史',rows).error);
  assert.ok(getReference('1','rank','物理',rows).error);
  assert.equal(getReference('','score','物理',rows).score,null);
  assert.ok(getReference('751','score','物理',rows).error);
  assert.equal(getReference('0','score','物理',rows).score,0);
});
test('分差边界、未知分数和全部模式', () => {
  assert.equal(scoreMatch(580,600,'20'),true);
  assert.equal(scoreMatch(621,600,'20'),false);
  assert.equal(scoreMatch(600,600,'below'),true);
  assert.equal(scoreMatch(null,600,'20',false),false);
  assert.equal(scoreMatch(null,600,'20',true),true);
  assert.equal(scoreMatch(null,600,'all',false),false);
  assert.equal(scoreMatch(null,null,'20',false),false);
});
test('选科同时满足/任选其一/未知分别处理', () => {
  const row = {requiredSubjects:['化学','生物'],subjectRule:'all'};
  assert.equal(subjectStatus(row,['化学']), 'mismatch');
  assert.equal(subjectStatus(row,['化学','生物']), 'match');
  assert.equal(subjectStatus({...row,subjectRule:'any'},['生物']), 'match');
  assert.equal(subjectStatus({...row,subjectRule:'unknown'},['生物']), 'unknown');
});
test('非定向计划不会因含有定向两字误判为资格限制计划',()=>{
  const row={school:'某大学',note:'普通本科批；非定向',track:'物理'};
  assert.equal(filterRows([row],{kind:'general',band:'all'}).length,1);
  assert.equal(filterRows([{...row,note:'非定向；国家专项计划'}],{kind:'general',band:'all'}).length,0);
  assert.equal(filterRows([{...row,category:'精准专项'}],{kind:'general',band:'all'}).length,0);
  assert.equal(filterRows([{...row,sourceCategory:'国家专项'}],{kind:'general',band:'all'}).length,0);
  assert.equal(filterRows([{...row,category:'未注明招生类别'}],{kind:'general',band:'all'}).length,0);
  assert.equal(filterRows([{...row,category:'未注明招生类别'}],{kind:'all',band:'all'}).length,1);
  assert.equal(filterRows([{...row,major:'金融学（精准专项）'}],{kind:'general',band:'all'}).length,0);
  assert.equal(filterRows([{...row,note:'普通类；不含预科直升；批次待核'}],{kind:'general',band:'all'}).length,1);
});
test('筛选隔离历史/物理、资格计划；专业搜索只查已采集专业', () => {
  const rows = [{id:'a',track:'物理',school:'广西大学',score:550,note:'国家专项计划'},{id:'b',track:'历史',school:'广西大学',score:550},{id:'c',track:'物理',school:'广西大学',score:551,joinedMajors:['计算机科学与技术']}];
  const opts = {track:'物理',kind:'general',reference:550,band:'20',query:'计算机'};
  assert.deepEqual(filterRows(rows,opts).map(r=>r.id),['c']);
  assert.equal(filterRows(rows,{...opts,query:'不存在'}).length,0);
});
test('原文分数存在未解决冲突时不参与分数比较',()=>{
  const row={id:'conflict',school:'某校',track:'物理',score:500,scoreComparable:false};
  const opts={track:'物理',reference:500,band:'20',includeUnknown:false};
  assert.equal(filterRows([row],opts).length,0);
  assert.equal(filterRows([row],{...opts,includeUnknown:true}).length,1);
  const actual={...row,scoreComparable:true,scoreType:'专业录取最低分',score:500,referenceScore:100};
  assert.equal(filterRows([actual],opts).length,1,'组参考分不得覆盖实际专业最低分');
});
test('专业组连接必须同时匹配年、校、科类、批次和组码', () => {
  const a={year:2026,schoolCode:'10001',school:'某大学',track:'物理',batch:'本科普通批',group:'101'};
  assert.notEqual(exactGroupKey(a),exactGroupKey({...a,track:'历史'}));
  assert.notEqual(exactGroupKey(a),exactGroupKey({...a,year:2024}));
  assert.equal(exactGroupKey({...a,group:null}),null);
  assert.equal(exactGroupKey({...a,schoolCode:null}),null);
  assert.notEqual(exactGroupKey(a),exactGroupKey({...a,schoolCode:'10002'}));
  assert.throws(()=>firstRoundIndex([{...a,round:'首轮'},{...a,round:'首轮'}]),/重复/);
});
test('逐校盘点区分组数、计划条数、空投档分、未收录和字段缺口',()=>{
  const a={year:2026,schoolCode:'10001',school:'某大学',track:'物理',batch:'本科普通批',group:'101',sourceId:'source'};
  const cutoffs=[{...a,round:'首轮',score:500},{...a,group:'102',round:'首轮',score:null}];
  const plans=[{...a,major:'甲',subjectRule:'all',requiredSubjects:['化学'],tuition:0,duration:'四年'}, {...a,major:'乙',subjectRule:'unknown',tuition:null,duration:null}];
  const [row]=buildCoverage({cutoffs,plans,majorCutoffs:[]});
  assert.equal(row.firstRoundGroups,2);assert.equal(row.groupsWithPlans,1);assert.equal(row.plans,2);
  assert.equal(row.groupsWithoutCollectedPlans,1);assert.equal(row.groupsWithNoFiling,1);assert.equal(row.majorCutoffs,0);
  assert.equal(row.planGaps.tuition,1);assert.equal(row.planGaps.subjects,1);assert.equal(row.plansWithComparableGroupScore,2);
  assert.equal(row.coverageStatus,'partial');
});
test('导出和来源链接拒绝公式注入及脚本协议', () => {
  assert.equal(csvCell('=1+1'),'"\'=1+1"');
  assert.equal(safeUrl('javascript:alert(1)'),'#');
  assert.equal(safeUrl('https://www.gxeea.cn/'),'https://www.gxeea.cn/');
});

test('核查时间按北京时间显示，跨日不误标为昨日；纯日期保持原值',()=>{
  assert.equal(reviewDate('2026-09-10T18:03:30.012851+00:00'),'2026-09-11');
  assert.equal(reviewDate('2026-09-11T02:03:30+08:00'),'2026-09-11');
  assert.equal(reviewDate('2026-09-10'),'2026-09-10');
  assert.equal(reviewDate(null),'');assert.equal(reviewDate('not-a-date'),'');
});
