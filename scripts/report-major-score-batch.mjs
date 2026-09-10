import assert from 'node:assert/strict';
import { readFile,writeFile } from 'node:fs/promises';
import { execFileSync } from 'node:child_process';
import { createHash } from 'node:crypto';
const root=new URL('../',import.meta.url),report=new URL('docs/major-scores-2026-09-10/',root);
const read=async path=>JSON.parse(await readFile(path,'utf8'));
const baseline='4f11e4b57c82384b74662dc918059e19d1ec9cdf';
const oldFile=name=>execFileSync('git',['show',`${baseline}:site/data/${name}.json`],{cwd:root,encoding:'utf8',maxBuffer:20*1024*1024});
const incoming=await read(new URL('major-cutoffs-upsert.json',report));
const reviews=await read(new URL('school-audit-notes.json',report));
const all=await read(new URL('site/data/major-cutoffs.json',root));
const old=JSON.parse(oldFile('major-cutoffs'));
const map=new Map(all.map(r=>[r.id,r]));
for(const r of old)assert.deepEqual(map.get(r.id),r,`Existing record changed: ${r.id}`);
for(const r of incoming)assert.deepEqual(map.get(r.id),r,`Batch record not installed: ${r.id}`);
assert.equal(all.length,old.length+incoming.length);
const preserved={};
for(const name of ['cutoffs','plans','ranks','special-programs','policies','supplementary-plans','plan-source-catalog','major-filing-cutoffs']){
  const text=await readFile(new URL(`site/data/${name}.json`,root),'utf8');assert.equal(text,oldFile(name),`Out-of-scope data changed: ${name}`);
  preserved[name]={unchanged:true,sha256:createHash('sha256').update(text).digest('hex')};
}
const schools=[...new Set(incoming.map(r=>r.schoolCode))].map(code=>{
  const rows=incoming.filter(r=>r.schoolCode===code);
  return {schoolCode:code,school:rows[0].school,records:rows.length,comparable:rows.filter(r=>r.scoreComparable!==false).length,pending:rows.filter(r=>r.scoreComparable===false).length,physics:rows.filter(r=>r.track==='物理').length,history:rows.filter(r=>r.track==='历史').length,rounds:[...new Set(rows.map(r=>r.round))],unknownGroup:rows.filter(r=>!r.group).length,unknownBatch:rows.filter(r=>/待核/.test(r.batch)).length};
});
const summary={year:2026,checkedAt:new Date().toISOString(),baselineCommit:baseline,reviewedSchoolCodes:new Set(reviews.map(r=>r.schoolCode)).size,sourceRecordsAdded:(await read(new URL('sources.json',report))).length,before:{records:old.length,schools:new Set(old.map(r=>r.schoolCode)).size,pending:old.filter(r=>r.scoreComparable===false).length},after:{records:all.length,schools:new Set(all.map(r=>r.schoolCode)).size,pending:all.filter(r=>r.scoreComparable===false).length},added:{records:incoming.length,comparable:incoming.filter(r=>r.scoreComparable!==false).length,pending:incoming.filter(r=>r.scoreComparable===false).length,schools},oldMajorRecordsUnchanged:old.length,preserved,limits:['部分覆盖，复查未取得不表示学校没有发布','不以2025数据或专业组投档分填补2026专业分','来源未区分轮次则保留汇总，不充作首轮','组码和精确批次未知保持待核','专业录取数不转换成计划数','加分处理按高校说明，不一律称为裸分']};
await writeFile(new URL('summary.json',report),JSON.stringify(summary,null,2)+'\n');
console.log(JSON.stringify({added:summary.added.records,comparable:summary.added.comparable,after:summary.after,preserved:old.length,reviewed:summary.reviewedSchoolCodes},null,2));
