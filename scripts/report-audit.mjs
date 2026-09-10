import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { execFileSync } from 'node:child_process';
import { buildCoverage } from '../site/coverage.js';
const root=new URL('../',import.meta.url), baseline='f95fb8c056a07b3fc94995cdb071bb63cff80a26';
const read=async name=>JSON.parse(await readFile(new URL(`site/data/${name}.json`,root),'utf8'));
const previous=name=>JSON.parse(execFileSync('git',['show',`${baseline}:site/data/${name}.json`],{cwd:root,encoding:'utf8',maxBuffer:20*1024*1024}));
const names=['cutoffs','plans','major-cutoffs','special-programs','policies','sources'];
const before=Object.fromEntries(names.map(n=>[n,previous(n)]));
const after=Object.fromEntries(await Promise.all(names.map(async n=>[n,await read(n)])));
function stats(data){
  const coverage=buildCoverage({cutoffs:data.cutoffs,plans:data.plans,majorCutoffs:data['major-cutoffs']});
  const special=data['special-programs'].filter(r=>r.type==='strong-foundation');
  return {plans:data.plans.length,planSchools:new Set(data.plans.map(r=>r.schoolCode)).size,
    planGroupCodes:data.plans.filter(r=>r.group).length,
    matchedFirstRoundGroups:coverage.reduce((n,r)=>n+r.groupsWithPlans,0),
    comparablePlans:coverage.reduce((n,r)=>n+r.plansWithComparableGroupScore,0),
    planFieldGaps:Object.fromEntries(Object.keys(coverage[0].planGaps).map(k=>[k,coverage.reduce((n,r)=>n+r.planGaps[k],0)])),
    majorCutoffs:data['major-cutoffs'].length,majorSchools:new Set(data['major-cutoffs'].map(r=>r.schoolCode)).size,
    nonComparableMajorScores:data['major-cutoffs'].filter(r=>r.scoreComparable===false).length,
    strongGuangxi:Object.fromEntries(['confirmed','unknown','excluded'].map(k=>[k,special.filter(r=>r.guangxiStatus===k).length])),
    specialScoreRecords:data['special-programs'].reduce((n,r)=>n+(r.scoreRecords||[]).length,0),
    specialScoresMissingFormula:data['special-programs'].flatMap(r=>r.scoreRecords||[]).filter(r=>!r.formula).length,
    sources:data.sources.length,policies:data.policies.length,schoolEntries:coverage.length,
    schoolsWithoutPlans:coverage.filter(r=>!r.plans).length,schoolsWithoutMajorCutoffs:coverage.filter(r=>!r.majorCutoffs).length};
}
const changes=Object.fromEntries(names.map(name=>{
  const old=new Map(before[name].map(r=>[r.id,r])), now=new Map(after[name].map(r=>[r.id,r]));
  const added=after[name].filter(r=>!old.has(r.id)).map(r=>r.id);
  const removed=before[name].filter(r=>!now.has(r.id)).map(r=>r.id);
  const changed=after[name].filter(r=>old.has(r.id)&&JSON.stringify(old.get(r.id))!==JSON.stringify(r)).map(r=>({id:r.id,fields:[...new Set([...Object.keys(old.get(r.id)),...Object.keys(r)])].filter(k=>JSON.stringify(old.get(r.id)[k])!==JSON.stringify(r[k]))}));
  return [name,{added,removed,changed}];
}));
const report={year:2026,checkedAt:new Date().toISOString(),baselineCommit:baseline,before:stats(before),after:stats(after),changes};
await mkdir(new URL('docs/audit-2026-09-10/',root),{recursive:true});
await writeFile(new URL('docs/audit-2026-09-10/summary.json',root),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({before:report.before,after:report.after},null,2));
