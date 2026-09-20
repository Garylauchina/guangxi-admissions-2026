import assert from 'node:assert/strict';
import { readFile, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { pathToFileURL } from 'node:url';
import { recordSourceIds } from '../site/logic.js';
import { buildCoverage } from '../site/coverage.js';

const read = async path => JSON.parse(await readFile(path, 'utf8'));
const identity = r => [r.year,r.schoolCode,r.track,r.batch,r.group || '',r.major,r.round,r.admissionType || ''].join('|');
const isSingleMajorName = major => {
  if(typeof major!=='string' || /等专业|预科班/.test(major))return false;
  const closing=[];
  let mainName='';
  for(const char of major){
    if(char==='（' || char==='('){closing.push(char==='（'?'）':')');continue;}
    if(char==='）' || char===')'){
      if(closing.pop()!==char)return false;
      continue;
    }
    // Official major descriptions may enumerate directions inside matched parentheses.
    if(!closing.length){if(char==='、')return false;mainName+=char;}
  }
  return closing.length===0 && mainName.trim().length>0;
};
const index = (rows,label) => {
  assert.ok(Array.isArray(rows),`${label} must be an array`);
  const map = new Map();
  for(const row of rows){ assert.ok(row.id && !map.has(row.id),`Missing or repeated ${label} ID: ${row.id}`);map.set(row.id,row); }
  return map;
};

// Preflight the whole batch. A failed source or row must leave every live file intact.
export function prepareMajorScoreBatch(current,batch){
  const scores=index(current.scores,'existing score'),sources=index(current.sources,'existing source'),notes=index(current.notes,'existing note');
  index(batch.scores,'batch score');index(batch.sources,'batch source');index(batch.notes,'batch note');
  for(const s of batch.sources){
    assert.ok(s.title && /^https?:\/\//.test(s.url),`Invalid source ${s.id}`);
    if(s.sha256)assert.match(s.sha256,/^[a-f0-9]{64}$/);
    const old=sources.get(s.id);if(old)assert.equal(s.url,old.url,`Source URL changed: ${s.id}`);
    sources.set(s.id,{...old,...s});
  }
  const refs=r=>{const ids=recordSourceIds(r);assert.ok(ids.length,`Missing sources: ${r.id}`);for(const id of ids)assert.ok(sources.has(id),`Missing source ${id}`);};
  const changes=[];
  for(const r of batch.scores){
    assert.equal(r.year,2026);assert.equal(r.province,'广西');assert.match(String(r.schoolCode),/^\d{5}$/);
    assert.ok(r.school && r.major && r.batch && r.round && r.reviewedAt);
    assert.ok(['物理','历史'].includes(r.track));assert.equal(r.scoreType,'专业录取最低分');
    assert.ok(!Object.hasOwn(r,'referenceScore') && !r.matchedGroupId,`Major score cannot be replaced by a group reference: ${r.id}`);
    if(r.scoreScaleMaximum!=null)assert.equal(r.scoreScaleMaximum,750,`Different score scale: ${r.id}`);
    assert.ok(!/校测|艺体综合|综合成绩|百[分制]|100\s*分制/.test(r.scoreBasis || ''),`Different score basis: ${r.id}`);
    const roundEvidence=[r.sourceRound,r.evidenceRound].filter(Boolean);
    if(roundEvidence.some(v=>/征集/.test(v)) || /^征集(?:$|[（(：:\s])/.test(r.sourceNote || ''))assert.ok(/征集/.test(r.round),`Supplementary evidence cannot establish first-round scores: ${r.id}`);
    assert.ok(!/艺术批|体育批|艺术类|体育类|职教高考|高职单招|对口|强基|保送/.test(`${r.batch} ${r.admissionType || ''} ${r.sourceTrack || ''} ${r.sourceCategory || ''}`),`Wrong score route: ${r.id}`);
    assert.ok(isSingleMajorName(r.major),`Not a single major or formal major class: ${r.id}`);
    const validScore=n=>typeof n==='number' && Number.isFinite(n) && n>=0 && n<=750;
    assert.ok(validScore(r.score),`Invalid minimum: ${r.id}`);
    for(const key of ['sourceMaximumScore','sourceAverageScore'])if(r[key]!=null)assert.ok(validScore(r[key]),`Invalid ${key}: ${r.id}`);
    for(const key of ['plannedCount','admittedCount'])if(r[key]!=null)assert.ok(Number.isInteger(r[key]) && r[key]>=0,`Invalid ${key}: ${r.id}`);
    if(r.admittedCount!=null)assert.ok(r.admittedCount>0,`No admitted students cannot establish an actual cutoff: ${r.id}`);
    if(r.group){assert.match(String(r.group),/^\d{3}$/);assert.ok(r.fieldSourceIds?.group?.length,`Group needs direct evidence: ${r.id}`);}
    if(r.rank!=null)assert.ok(r.rankType && r.fieldSourceIds?.rank?.length,`Rank needs direct evidence: ${r.id}`);
    assert.ok(typeof r.scoreComparable==='boolean' && Array.isArray(r.scoreEvidenceGaps) && Array.isArray(r.conflictFields));
    const min=r.score,max=r.sourceMaximumScore,avg=r.sourceAverageScore;
    const conflict=(max!=null && min>max) || (avg!=null && (avg<min || (max!=null && avg>max))) || (r.admittedCount===1 && max!=null && min!==max);
    const scoreFields=new Set(['score','scoreRange','sourceMaximumScore','sourceAverageScore','maxScore','averageScore','minScore','admittedCount','scoreBasis','scoreScaleMaximum']);
    if(conflict || r.conflictFields.some(k=>scoreFields.has(k))){assert.equal(r.scoreComparable,false,`Conflicting score cannot be compared: ${r.id}`);assert.equal(r.evidenceStatus,'source-conflict');}
    if(r.scoreEvidenceGaps.length)assert.equal(r.scoreComparable,false,`Unresolved score evidence cannot be compared: ${r.id}`);
    if(!r.scoreComparable)assert.ok(r.note && r.scoreEvidenceGaps.length,`Unusable score needs a visible reason: ${r.id}`);
    refs(r);
    const old=scores.get(r.id);
    if(old){
      for(const key of ['year','schoolCode','school','track','major'])assert.equal(r[key],old[key],`Identity changed: ${r.id} ${key}`);
      for(const key of ['score','batch','group','round','admissionType','scoreComparable'])if(r[key]!==old[key])assert.ok(r.fieldSourceIds?.[key]?.length,`Correction needs field evidence: ${r.id} ${key}`);
    }else assert.ok(![...scores.values()].some(x=>identity(x)===identity(r)),`Duplicate with a new ID: ${r.id}`);
    if(!old || JSON.stringify(old)!==JSON.stringify(r))changes.push({id:r.id,school:r.school,action:old?'update':'add'});
    scores.set(r.id,r);
  }
  for(const r of batch.notes){
    assert.equal(r.year,2026);assert.match(String(r.schoolCode),/^\d{5}$/);assert.equal(r.auditKind,'major-scores');
    assert.ok(r.school && r.note && r.checkedAt && r.status);refs(r);
    for(const url of r.checkedUrls || [])assert.match(url,/^https?:\/\//);
    notes.set(r.id,r);
  }
  return {scores:[...scores.values()],sources:[...sources.values()],notes:[...notes.values()],changes};
}

async function main(){
  const directory=process.argv[2];assert.ok(directory,'Usage: node scripts/import-major-score-batch.mjs <batch-directory> [--apply]');
  const data=new URL('../site/data/',import.meta.url);
  const [scores,sources,notes,cutoffs,plans]=await Promise.all(['major-cutoffs','sources','school-audit-notes','cutoffs','plans'].map(n=>read(new URL(`${n}.json`,data))));
  const [newScores,newSources,newNotes]=await Promise.all(['major-cutoffs-upsert','sources','school-audit-notes'].map(n=>read(resolve(directory,`${n}.json`))));
  const next=prepareMajorScoreBatch({scores,sources,notes},{scores:newScores,sources:newSources,notes:newNotes});
  const report={before:scores.length,after:next.scores.length,added:next.changes.filter(r=>r.action==='add').length,updated:next.changes.filter(r=>r.action==='update').length,schoolCodes:new Set(next.scores.map(r=>r.schoolCode)).size,pending:next.scores.filter(r=>r.scoreComparable===false).length,changes:next.changes};
  if(process.argv.includes('--apply')){
    const files={'major-cutoffs':next.scores,sources:next.sources,'school-audit-notes':next.notes,'school-coverage':buildCoverage({cutoffs,plans,majorCutoffs:next.scores})};
    const backups=new Map(await Promise.all(Object.keys(files).map(async n=>[n,await readFile(new URL(`${n}.json`,data),'utf8')])));
    try{for(const [name,rows] of Object.entries(files))await writeFile(new URL(`${name}.json`,data),JSON.stringify(rows,null,name==='sources'?2:undefined)+'\n');}
    catch(error){for(const [name,text] of backups)await writeFile(new URL(`${name}.json`,data),text);throw error;}
  }
  console.log(JSON.stringify(report,null,2));
}
if(process.argv[1] && import.meta.url===pathToFileURL(resolve(process.argv[1])).href)await main();
