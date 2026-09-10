import test from 'node:test';
import assert from 'node:assert/strict';
import { getReference, scoreMatch, subjectStatus, filterRows, exactGroupKey, csvCell, safeUrl } from '../site/logic.js';

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
  assert.equal(filterRows([{...row,major:'金融学（精准专项）'}],{kind:'general',band:'all'}).length,0);
});
test('筛选隔离历史/物理、资格计划；专业搜索只查已采集专业', () => {
  const rows = [{id:'a',track:'物理',school:'广西大学',score:550,note:'国家专项计划'},{id:'b',track:'历史',school:'广西大学',score:550},{id:'c',track:'物理',school:'广西大学',score:551,joinedMajors:['计算机科学与技术']}];
  const opts = {track:'物理',kind:'general',reference:550,band:'20',query:'计算机'};
  assert.deepEqual(filterRows(rows,opts).map(r=>r.id),['c']);
  assert.equal(filterRows(rows,{...opts,query:'不存在'}).length,0);
});
test('专业组连接必须同时匹配年、校、科类、批次和组码', () => {
  const a={year:2026,school:'某大学',track:'物理',batch:'本科普通批',group:'101'};
  assert.notEqual(exactGroupKey(a),exactGroupKey({...a,track:'历史'}));
  assert.notEqual(exactGroupKey(a),exactGroupKey({...a,year:2024}));
  assert.equal(exactGroupKey({...a,group:null}),null);
});
test('导出和来源链接拒绝公式注入及脚本协议', () => {
  assert.equal(csvCell('=1+1'),'"\'=1+1"');
  assert.equal(safeUrl('javascript:alert(1)'),'#');
  assert.equal(safeUrl('https://www.gxeea.cn/'),'https://www.gxeea.cn/');
});
