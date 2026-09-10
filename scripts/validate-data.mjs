import assert from 'node:assert/strict';
import { readFile, writeFile, readdir } from 'node:fs/promises';
import { exactGroupKey, firstRoundIndex, recordSourceIds } from '../site/logic.js';
import { buildCoverage } from '../site/coverage.js';
const root=new URL('../',import.meta.url);
const read=async name=>JSON.parse(await readFile(new URL(`site/data/${name}.json`,root),'utf8'));
const [cutoffs,plans,majorCutoffs,ranks,special,sources,policies]=await Promise.all(['cutoffs','plans','major-cutoffs','ranks','special-programs','sources','policies'].map(read));
const sourceMap=new Map(sources.map(s=>[s.id,s]));
function validateNestedSources(value){
  if(Array.isArray(value)){value.forEach(validateNestedSources);return;}
  if(!value || typeof value!=='object')return;
  for(const id of recordSourceIds(value))assert.ok(sourceMap.has(id),`Missing nested source ${id}`);
  Object.values(value).forEach(validateNestedSources);
}
assert.equal(sourceMap.size,sources.length,'Source identifiers must be unique');
for(const s of sources){assert.ok(s.id&&s.title&&/^https?:\/\//.test(s.url),`Invalid source ${s.id}`);if(s.sha256)assert.match(s.sha256,/^[a-f0-9]{64}$/);}
const ids=new Set();
for(const [kind,rows] of Object.entries({cutoffs,plans,majorCutoffs,ranks,special,policies})){
  assert.ok(Array.isArray(rows));
  for(const row of rows){
    assert.equal(row.year,2026,`${kind} must explicitly identify year 2026`);
    if(row.id){assert.ok(!ids.has(row.id),`Duplicate id ${row.id}`);ids.add(row.id);}
    const refs=recordSourceIds(row);
    assert.ok(refs.length>0,`Missing source on ${kind} ${row.id}`);
    for(const id of refs)assert.ok(sourceMap.has(id),`Missing source ${id}`);
    validateNestedSources(row);
    if(['cutoffs','plans','majorCutoffs','ranks'].includes(kind))assert.ok(['物理','历史'].includes(row.track),`Wrong track ${row.id}`);
    if(['cutoffs','plans','majorCutoffs'].includes(kind))assert.ok(row.school && /^\d{5}$/.test(String(row.schoolCode)),`Missing school identity ${row.id}`);
    if(row.score!==null && row.score!==undefined)assert.ok(Number.isFinite(row.score)&&row.score>=0&&row.score<=750,`Invalid comparable score ${row.id}`);
    if(kind==='plans'){assert.ok(row.major&&row.school);assert.ok(Number.isInteger(row.plannedCount)&&row.plannedCount>=0,`Invalid plan count ${row.id}`);assert.ok(['all','any','none','unknown'].includes(row.subjectRule));assert.ok(row.requiredSubjects.every(s=>['化学','生物','政治','地理'].includes(s)));if(['all','any'].includes(row.subjectRule))assert.ok(row.requiredSubjects.length>0,`An explicit subject rule needs subjects: ${row.id}`);assert.ok(!/预科直升批|艺术批|体育批/.test(row.batch),`Excluded admissions route in ordinary plan screening: ${row.id}`);}
    if(kind==='majorCutoffs'){assert.equal(row.scoreType,'专业录取最低分');assert.ok(row.major&&row.round,`Missing major or round ${row.id}`);if(row.scoreComparable===false)assert.ok(row.note,`Non-comparable scores require an explanation: ${row.id}`);}
    if(kind==='cutoffs'){assert.equal(row.rank,null,'No exact filing rank should be invented');assert.ok(row.group&&row.schoolCode&&row.round);}
    if(kind==='special'){assert.ok(['confirmed','unknown','excluded'].includes(row.guangxiStatus));assert.equal(row.score??null,null,'Special weighted/combined scores must not be ordinary comparable scores');}
  }
}
assert.equal(cutoffs.length,11448,'2026 official 16-table extraction baseline changed; review source changes first');
assert.equal(cutoffs.filter(r=>r.round==='首轮').length,8155);
assert.equal(cutoffs.filter(r=>r.round==='首轮'&&r.score===null).length,327);
assert.equal(ranks.length,1010);
assert.equal(special.filter(r=>r.type==='strong-foundation').length,39,'The verified 2026 national strong-foundation directory has 39 universities');
assert.ok(policies.length>=7,'Competition and special-admissions policies must be present');
for(const program of special){for(const score of program.scoreRecords || []){assert.equal(score.year,2026);assert.ok(score.scoreLabel,'Special score must explain its type');assert.ok(score.formula||(score.formulaStatus==='unverified'&&score.note.includes('尚未核实')),'Missing formula must carry an explicit evidence gap');assert.ok(Number.isFinite(score.score));assert.ok(score.sourceIds?.length);for(const sid of score.sourceIds)assert.ok(sourceMap.has(sid));}}
for(const program of special){
  assert.ok(program.planGapReason || program.planCount!==null,'Unknown special-plan counts need a concrete reason');
  for(const score of program.scoreRecords || []){
    if(score.maxScore)assert.ok(score.score<=score.maxScore,`Special score exceeds its stated scale: ${score.id}`);
    if(score.tieBreakCode){assert.ok(Number.isInteger(score.score));assert.equal(score.rawScoreText,`${score.score}.${score.tieBreakCode}`);}
    if(score.auditStatus==='prior-value-current-source-unreadable')assert.match(score.note,/无法|未能/);
  }
}
const gxufeTargeted=plans.filter(r=>r.school==='广西财经学院'&&/精准专项/.test(r.major));
assert.equal(gxufeTargeted.length,19);assert.ok(gxufeTargeted.every(r=>r.category==='精准专项'),'Targeted plans must not be misclassified as general');
for(const track of ['物理','历史']){
  const rows=ranks.filter(r=>r.track===track);
  for(let i=0;i<rows.length;i++){const r=rows[i];assert.equal(r.rankEnd-r.rankStart+1,r.count);if(i){assert.ok(r.score<rows[i-1].score);assert.equal(r.rankStart,rows[i-1].rankEnd+1);}}
}
const groupMap=firstRoundIndex(cutoffs);
const matchedPlans=plans.filter(r=>exactGroupKey(r)&&groupMap.has(exactGroupKey(r))).length;
const coverage=await read('school-coverage');
assert.deepEqual(coverage,buildCoverage({cutoffs,plans,majorCutoffs}),'School coverage is stale; run node scripts/build-coverage.mjs');
const auditNotes=await read('school-audit-notes');
for(const note of auditNotes){assert.equal(note.year,2026);assert.ok(note.school&&note.note&&note.checkedAt);assert.ok(note.sourceIds?.length||note.checkedUrls?.length,`Review notes require evidence: ${note.school}`);for(const id of note.sourceIds||[])assert.ok(sourceMap.has(id),`Missing review source ${id}`);for(const url of note.checkedUrls||[])assert.match(url,/^https?:\/\//);}
const filings=await read('major-filing-cutoffs');
for(const row of filings){assert.equal(row.year,2026);assert.equal(row.scoreType,'专业投档最低分');assert.ok(!ids.has(row.id),'Professional filing must remain outside actual-admission records');validateNestedSources(row);assert.ok(row.score>=0&&row.score<=750);}
const excluded=JSON.parse(await readFile(new URL('docs/audit-2026-09-10/plans/excluded-plans.json',root),'utf8'));
const planIds=new Set(plans.map(r=>r.id));
for(const item of excluded){assert.ok(item.plan?.id&&item.reason&&item.evidence?.length);assert.ok(!planIds.has(item.plan.id),'Excluded admissions routes must not reappear in plan screening');}
const html=await readFile(new URL('site/index.html',root),'utf8');
assert.ok(html.includes('lang="zh-CN"'));assert.ok(!html.includes('2025'));
for(const match of html.matchAll(/(?:src|href)="\.\/([^"#]+)"/g))await readFile(new URL('site/'+match[1],root));
for(const file of await readdir(new URL('site/data/',root))){const text=await readFile(new URL('site/data/'+file,root),'utf8');assert.ok(!/\/Users\/|南宁二中|火箭班|校内前25|gh[pousr]_[A-Za-z0-9]{20}/.test(text),`Private material in ${file}`);}
const summary={year:2026,checkedAt:new Date().toISOString(),status:'passed',cutoffs:cutoffs.length,firstRound:8155,firstRoundSchools:new Set(cutoffs.filter(r=>r.round==='首轮').map(r=>r.schoolCode)).size,plans:plans.length,planSchools:new Set(plans.map(r=>r.school)).size,plansMatchedToFirstRoundGroup:matchedPlans,majorCutoffs:majorCutoffs.length,majorCutoffSchools:new Set(majorCutoffs.map(r=>r.school)).size,specialPrograms:special.length,specialGuangxiStatus:Object.fromEntries(['confirmed','unknown','excluded'].map(k=>[k,special.filter(p=>p.guangxiStatus===k).length])),strongGuangxiStatus:Object.fromEntries(['confirmed','unknown','excluded'].map(k=>[k,special.filter(p=>p.type==='strong-foundation'&&p.guangxiStatus===k).length])),specialScores:special.reduce((n,p)=>n+(p.scoreRecords||[]).length,0),majorScoresPending:majorCutoffs.filter(r=>r.scoreComparable===false).length,majorFilingRecordsSeparate:filings.length,schoolReviewNotes:auditNotes.length,schoolsWithReviewNotes:new Set(auditNotes.map(r=>r.schoolCode)).size,sources:sources.length,ranks:ranks.length,limits:['专业计划与实际专业录取线为部分覆盖','首轮及征集分轮记录','无官方专业组码的计划不匹配分数','特殊通道不参与普通分数比较']};
if(process.argv.includes('--write-report'))await writeFile(new URL('docs/validation.json',root),JSON.stringify(summary,null,2)+'\n');
console.log(JSON.stringify(summary,null,2));
