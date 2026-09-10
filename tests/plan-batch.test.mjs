import test from 'node:test';
import assert from 'node:assert/strict';
import { prepareBatch } from '../scripts/import-plan-batch.mjs';

test('分批导入拒绝错误省年、征集余额、其他轮组码、缺失来源和重复专业，保留已有数据', () => {
  const source={id:'official',title:'官方2026广西计划',url:'https://example.edu.cn/2026'};
  const row={id:'plan-1',year:2026,province:'广西',planStage:'initial',schoolCode:'10001',school:'示例大学',track:'物理',batch:'本科普通批',major:'数学',majorCode:'01',plannedCount:5,group:'101',subjectRule:'all',requiredSubjects:['化学'],sourceId:'official'};
  const current={plans:[row],sources:[source],catalog:[]};
  const before=JSON.stringify(current);
  for (const patch of [{year:2025},{province:'广东'},{planStage:'supplementary'},{groupEvidenceRound:'第一次征集'},{evidenceRound:'第一次征集'},{firstRoundMatchAllowed:false},{initialPlanEligible:false},{plannedCountScope:'remaining-supplementary-plan'},{sourceId:'missing'},{id:'duplicate-id'}]) {
    assert.throws(()=>prepareBatch(current,{plans:[{...row,...patch}],sources:[],catalog:[]}));
    assert.equal(JSON.stringify(current),before);
  }
  const next=prepareBatch(current,{plans:[{...row,tuition:5000,fieldSourceIds:{tuition:['official']}}],sources:[],catalog:[]});
  assert.equal(next.plans.length,1);assert.equal(next.plans[0].plannedCount,5);assert.equal(next.plans[0].tuition,5000);
  assert.equal(next.changes[0].action,'update');assert.equal(JSON.stringify(current),before);
});

test('同名试验班按有来源的包含专业分别保留，重复分列仍拒绝', () => {
  const source={id:'official',title:'官方初始计划',url:'https://example.edu.cn/2026'};
  const row={id:'plan-a',year:2026,province:'广西',planStage:'initial',schoolCode:'10358',school:'中国科学技术大学',track:'物理',batch:'本科（批次待核）',major:'理科试验班类（拔尖计划科技英才班）',majorCode:null,plannedCount:2,group:null,subjectRule:'all',requiredSubjects:['化学'],sourceId:'official',includedMajors:'数学类;物理学类',fieldSourceIds:{includedMajors:['official']}};
  const current={plans:[row],sources:[source],catalog:[]};
  const second={...row,id:'plan-b',plannedCount:3,includedMajors:'化学类;生物科学类;空间科学与技术'};
  const next=prepareBatch(current,{plans:[second],sources:[],catalog:[]});
  assert.equal(next.plans.length,2);assert.equal(next.plans.reduce((n,r)=>n+r.plannedCount,0),5);
  assert.ok(next.plans.every(r=>r.group===null && r.major===row.major));
  assert.throws(()=>prepareBatch(current,{plans:[{...row,id:'duplicate'}],sources:[],catalog:[]}));
  assert.throws(()=>prepareBatch(current,{plans:[{...second,fieldSourceIds:{}}],sources:[],catalog:[]}));
});
