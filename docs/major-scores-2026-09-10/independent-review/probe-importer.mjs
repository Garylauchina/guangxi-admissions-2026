// Read-only adversarial checks; writes only the requested review output path.
import {readFile,writeFile} from 'node:fs/promises';
import {resolve} from 'node:path';
import {pathToFileURL} from 'node:url';
import {createHash} from 'node:crypto';
const repo=resolve(process.argv[2] || 'guangxi-admissions-2026');
const {prepareMajorScoreBatch}=await import(pathToFileURL(resolve(repo,'scripts/import-major-score-batch.mjs')));
const {filterRows,comparableScore}=await import(pathToFileURL(resolve(repo,'site/logic.js')));
const base={id:'independent-fixture',year:2026,province:'广西',schoolCode:'10637',school:'重庆师范大学',track:'物理',batch:'本科普通批',round:'录取汇总（轮次未分）',reviewedAt:'2026-09-10',major:'小学教育',score:515,scoreType:'专业录取最低分',admissionType:'普通类',scoreComparable:true,scoreEvidenceGaps:[],conflictFields:[],sourceId:'official'};
const source={id:'official',title:'官方专业录取分（测试中来源占位）',url:'https://zsb.cqnu.edu.cn/info/10438/88323.htm'};
const cases={
 wrongYear:{year:2025},wrongProvince:{province:'广东'},referenceScoreOverride:{referenceScore:100},
 unknownCategory:{admissionType:'未注明招生类别',category:'未注明招生类别'},
 sourceOnlyTargeted:{sourceCategory:'国家专项计划'},sourceOnlyRound:{round:'首轮',sourceNote:'征集'},
 sourceScoreConflict:{scoreEvidenceGaps:['最低分原文尚不能核实'],scoreComparable:true},
 wrongScale:{scoreScaleMaximum:100,score:90,scoreBasis:'综合评价成绩'},
 nonScoreConflict:{conflictFields:['filingScoreInSource'],evidenceStatus:'source-conflict'},
 zeroAdmitted:{score:0,admittedCount:0}};
const results=[];
for(const [name,patch] of Object.entries(cases)){
 try{const [r]=prepareMajorScoreBatch({scores:[],sources:[],notes:[]},{scores:[{...base,...patch}],sources:[source],notes:[]}).scores;
 results.push({name,patch,imported:true,compared:comparableScore(r),generalFilter:filterRows([r],{kind:'general',band:'all',includeUnknown:false}).length});
 }catch(e){results.push({name,patch,imported:false,error:e.message.split('\n')[0]});}
}
const hashes={};for(const name of ['scripts/import-major-score-batch.mjs','site/logic.js','site/app.js'])hashes[name]=createHash('sha256').update(await readFile(resolve(repo,name))).digest('hex');
const out={checkedAt:new Date().toISOString(),note:'Synthetic regression probes, not real admissions records; does not modify repository. imported=true describes observed validator acceptance, not confirmed correctness.',hashes,results};
if(process.argv[3])await writeFile(process.argv[3],JSON.stringify(out,null,2)+'\n');
console.log(JSON.stringify(out,null,2));
