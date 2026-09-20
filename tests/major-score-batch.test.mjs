import test from 'node:test';
import assert from 'node:assert/strict';
import { prepareMajorScoreBatch } from '../scripts/import-major-score-batch.mjs';

const source={id:'official',title:'官方专业录取结果',url:'https://example.edu.cn/2026'};
const row={id:'score-1',year:2026,province:'广西',schoolCode:'10637',school:'示例大学',track:'物理',batch:'本科普通批',major:'地理科学类',round:'录取汇总（轮次未分）',group:null,score:532,sourceMaximumScore:550,sourceAverageScore:540,admissionType:'普通类',scoreType:'专业录取最低分',sourceId:'official',scoreComparable:true,evidenceStatus:'verified',scoreEvidenceGaps:[],conflictFields:[],reviewedAt:'2026-09-10'};

test('专业分导入拒绝错省年、投档线、综合分、合计、多专业拆分和无依据分组，失败不改当前数据',()=>{
  const current={scores:[],sources:[source],notes:[]},before=JSON.stringify(current);
  for(const patch of [{year:2025},{province:'广东'},{scoreType:'专业投档最低分'},{admissionType:'强基计划'},{track:'艺术'},{major:'材料类等专业'},{major:'工商管理类、旅游管理'},{major:'预科班'},{sourceId:'missing'},{group:'101'},{rank:1234,rankType:'最低位次'},{score:751},{sourceAverageScore:560},{sourceMaximumScore:520},{admittedCount:1},{score:0,sourceMaximumScore:0,sourceAverageScore:0,admittedCount:0},{referenceScore:100},{matchedGroupId:'group-1'},{scoreScaleMaximum:100},{scoreBasis:'100 分制综合成绩'},{round:'首轮',sourceNote:'征集'},{round:'首轮',evidenceRound:'第一次征集'}]){
    assert.throws(()=>prepareMajorScoreBatch(current,{scores:[{...row,...patch}],sources:[],notes:[]}));
    assert.equal(JSON.stringify(current),before);
  }
});

test('官方专业描述中的顿号可在成对中英文括号内出现，导入保留完整原名',()=>{
  const current={scores:[],sources:[source],notes:[]};
  for(const major of ['机械类（机器人、智能制造与新能源车辆）','应用化学（新材料、新能源与智能传感）','机械类(机器人、智能制造与新能源车辆)','工科试验班（智能制造(机器人、智能装备)、新能源）']){
    const officialRow={...row,major};
    const next=prepareMajorScoreBatch(current,{scores:[officialRow],sources:[],notes:[]});
    assert.deepEqual(next.scores,[officialRow]);
    assert.equal(next.changes[0].action,'add');
  }
  assert.deepEqual(current,{scores:[],sources:[source],notes:[]});
});

test('括号不能掩盖外部多专业、等专业、预科班或不完整的专业名称',()=>{
  const current={scores:[],sources:[source],notes:[]},before=JSON.stringify(current);
  for(const major of [
    '计算机科学与技术、软件工程',
    '机械类（机器人、智能制造）、软件工程',
    '计算机科学与技术、软件工程（智能方向）',
    '机械类（机器人、智能制造',
    '机械类（智能制造））',
    '机械类(机器人、智能制造）',
    '机械类（机器人(智能装备）、新能源)',
    '机械类（机器人等专业）',
    '机械类（预科班）',
    '（计算机科学与技术、软件工程）',
  ]){
    assert.throws(()=>prepareMajorScoreBatch(current,{scores:[{...row,major}],sources:[],notes:[]}),/Not a single major or formal major class/,major);
    assert.equal(JSON.stringify(current),before);
  }
});

test('保留汇总和征集；重复新ID与无证据改分拒绝，来源冲突保留原数但禁用比较',()=>{
  const current={scores:[row],sources:[source],notes:[]};
  assert.throws(()=>prepareMajorScoreBatch(current,{scores:[{...row,id:'duplicate'}],sources:[],notes:[]}));
  assert.throws(()=>prepareMajorScoreBatch(current,{scores:[{...row,score:533}],sources:[],notes:[]}));
  const next=prepareMajorScoreBatch(current,{scores:[{...row,id:'supplementary',round:'征集（次数未分）',score:530},{...row,id:'conflict',major:'城市地下空间工程',score:418,sourceMaximumScore:423,sourceAverageScore:428.2,scoreComparable:false,evidenceStatus:'source-conflict',conflictFields:['sourceAverageScore'],scoreEvidenceGaps:['平均分高于最高分'],note:'原表平均分428.2高于最高分423，待高校澄清。'}],sources:[],notes:[]});
  const unrelated=prepareMajorScoreBatch(current,{scores:[{...row,conflictFields:['filingScoreInSource','planIdentity']}],sources:[],notes:[]});
  assert.equal(unrelated.scores[0].scoreComparable,true);
  assert.equal(next.scores.length,3);assert.deepEqual(next.scores[0],row);
  assert.equal(next.scores[1].round,'征集（次数未分）');assert.equal(next.scores[2].score,418);assert.equal(next.scores[2].scoreComparable,false);
  const corrected=prepareMajorScoreBatch(current,{scores:[{...row,score:533,fieldSourceIds:{score:['official']}}],sources:[],notes:[]});
  assert.equal(corrected.changes[0].action,'update');assert.equal(current.scores[0].score,532);
});
