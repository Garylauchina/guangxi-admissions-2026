import test from 'node:test';
import assert from 'node:assert/strict';
import {groupAdmissionIndex,groupAdmissionFor} from '../site/coverage.js';

const identity={year:2026,province:'广西',school:'测试大学',schoolCode:'10001',track:'物理',batch:'本科普通批',group:'101'};
const outcome={...identity,score:580,scoreType:'专业组录取最低分',scoreComparable:true,evidenceScope:'official-group-summary',roundScope:'annual',round:'录取汇总（轮次未分）'};
test('组录取分只能按完整组身份匹配，不能跨科类批次年份或院校代码',()=>{
  const index=groupAdmissionIndex([outcome]);
  const cutoff={...identity,round:'首轮',score:570};
  assert.equal(groupAdmissionFor(cutoff,index).score,580);
  for(const patch of [{track:'历史'},{year:2025},{schoolCode:'20001'},{group:'102'},{batch:'本科提前批'}])assert.equal(groupAdmissionFor({...cutoff,...patch},index),null);
  assert.equal(groupAdmissionFor({...cutoff,group:null},index),null);
});
test('首轮和征集录取口径分别匹配；年度汇总保留年度标签，不能由专业分推算',()=>{
  const first={...outcome,score:582,roundScope:'round',round:'首轮'};
  const index=groupAdmissionIndex([outcome,first]);
  assert.equal(groupAdmissionFor({...identity,round:'首轮'},index),first);
  assert.equal(groupAdmissionFor({...identity,round:'第一次征集'},index),outcome);
  const roundOnly=groupAdmissionIndex([first]);
  assert.equal(groupAdmissionFor({...identity,round:'第一次征集'},roundOnly),null);
  assert.throws(()=>groupAdmissionIndex([{...outcome,major:'计算机科学与技术',scoreType:'专业录取最低分',evidenceScope:'partial-majors'}]));
  assert.throws(()=>groupAdmissionIndex([outcome,{...outcome,score:579}]));
});
