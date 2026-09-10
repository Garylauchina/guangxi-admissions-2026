import assert from 'node:assert/strict';
import { readFile, writeFile, readdir } from 'node:fs/promises';
import { execFileSync } from 'node:child_process';
import { exactGroupKey, firstRoundIndex } from '../site/logic.js';
const root = new URL('../',import.meta.url), dir = new URL('docs/plan-batches-2026-09-10/',root);
const read = async path=>JSON.parse(await readFile(new URL(path,root),'utf8'));
const baseline=await read('docs/plan-batches-2026-09-10/baseline.json');
const old=JSON.parse(execFileSync('git',['show',`${baseline.commit}:site/data/plans.json`],{cwd:root,encoding:'utf8',maxBuffer:16*1024*1024}));
const [plans,cutoffs,coverage,catalog,supplementary]=await Promise.all(['plans','cutoffs','school-coverage','plan-source-catalog','supplementary-plans'].map(n=>read(`site/data/${n}.json`)));
const oldIds=new Set(old.map(r=>r.id)), newPlans=plans.filter(r=>!oldIds.has(r.id));
assert.ok(old.every(r=>plans.some(p=>p.id===r.id)),'This collection must preserve all audited initial records');
for(const r of old){const next=plans.find(p=>p.id===r.id);assert.equal(next.plannedCount,r.plannedCount);assert.equal(next.group,r.group);}
const unchanged=[];
for(const file of ['cutoffs','major-cutoffs','major-filing-cutoffs','ranks','special-programs','policies']){
  assert.equal(await readFile(new URL(`site/data/${file}.json`,root),'utf8'),execFileSync('git',['show',`${baseline.commit}:site/data/${file}.json`],{cwd:root,encoding:'utf8',maxBuffer:16*1024*1024}));unchanged.push(file);
}
const index=firstRoundIndex(cutoffs);
const bySchool=[...new Set(newPlans.map(r=>r.schoolCode))].map(code=>{
  const rows=newPlans.filter(r=>r.schoolCode===code);
  return {school:rows[0].school,schoolCode:code,records:rows.length,plannedSeats:rows.reduce((n,r)=>n+r.plannedCount,0),matchedToFirstRound:rows.filter(r=>index.has(exactGroupKey(r))).length};
});
const batches=[];
for(const file of (await readdir(dir)).filter(n=>/^batch-.-import\.json$/.test(n)).sort())batches.push(await read(`docs/plan-batches-2026-09-10/${file}`));
const report={checkedAt:new Date().toISOString(),baseline,after:{plans:plans.length,planSchools:new Set(plans.map(r=>r.schoolCode)).size,matchedPlans:plans.filter(r=>index.has(exactGroupKey(r))).length,matchedGroups:coverage.reduce((n,r)=>n+r.groupsWithPlans,0),sourceCatalogSchools:catalog.length,supplementaryPlans:supplementary.length},newPlans:newPlans.length,bySchool,batches:batches.map(({batch,added,updated})=>({batch,added,updated})),checks:{oldPlansRetained:true,oldPlanCountsUnchanged:true,oldInitialGroupsUnchanged:true,unchangedDatasets:unchanged,searchOnlyHuzhouExcluded:!newPlans.some(r=>r.schoolCode==='10347')},remainingSources:catalog.filter(r=>r.status!=='collected').map(r=>({school:r.school,status:r.status,note:r.note,sourceIds:r.sourceIds})),limits:['新增计划不代表相应专业组资料全部完整。','未知组码、批次、再选要求或资格类别继续标缺，不用于强行匹配首轮分数。','征集剩余计划单独保存，只与同轮次投档组关联。','本次没有采集全省全部院校专业计划。']};
await writeFile(new URL('summary.json',dir),JSON.stringify(report,null,2)+'\n');
const rows=bySchool.map(r=>`| ${r.school} | ${r.records} | ${r.matchedToFirstRound} |`).join('\n');
await writeFile(new URL('README.md',dir),`# 专业计划分批采集 · 2026-09-10

本轮分 ${batches.length} 批处理，新增 **${newPlans.length} 条初始专业计划**，并修正广西民族大学 11 条学分互认项目的类别。初始计划总量从 ${baseline.plans} 条增加到 **${plans.length} 条 / ${report.after.planSchools} 校**。另收录 **${supplementary.length} 条征集剩余计划**，与初始计划分开。

| 新增院校 | 新增计划记录 | 可严格匹配首轮组线 |
|---|---:|---:|
${rows}

已匹配的首轮专业计划由 ${baseline.matchedPlans} 增至 **${report.after.matchedPlans} 条**，涉及的首轮组由 ${baseline.matchedGroups} 增至 **${report.after.matchedGroups} 个**。这些是不同科类、类别、专业的计划记录数，不能当作学校或专业总数；仍为部分覆盖。

“查看详情”新增该校计划来源、核查日期和采集状态，提供官方入口及跳转已收录计划的按钮。来源目录覆盖 ${catalog.length} 校，区分已采集、找到资料待采集、仅找到入口、未取得可读资料。其他学校保留官方完整查询入口，不把未采集误称为学校没有公布。

本科普通批第一、第二次征集的 ${supplementary.length} 条余额，仅在同年、同校代码与校名、同科类、同批次、同组码、**同轮次**的详情中显示，明确不是初始人数，也不表示目前仍可填报。桂理工材料化冶金应用技术初始181组与第一次征集182组的双源差异留在 [冲突证据](batch-a/cross-round-conflicts.json)，没有覆盖首轮。

## 核验与缺口

- 原有计划编号、人数与初始组码全部保留；原投档线、专业录取线、位次和特殊项目数据未变。
- 桂航逐行人数与公布组总对账；右江与桂医按直接广西列采集，未列批次和资格类别时保持待核，未拆科类的民族班与未核对地区子计划的定向人数另存缺口。
- 暨南大学109人加被排除的艺术4人与原表113人闭合；江西职业技术大学75人与本省表合计一致，再选要求未列则保持未知。
- 湖州师范大学原页直读失败，官方检索候选没有并入正式计划。全国总表减外省计划的推导人数没有并入。
- 来源表、原始文件摘要、采集与复查程序随仓库提供；原网页、图片、PDF和检索候选保留本地，不随网站上传。

各批明细：[A](batch-a/README.md)、[B](batch-b/README.md)、[C](batch-c/QA.md)${batches.some(b=>b.batch==='batch-d') ? '、[D](batch-d/QA.md)' : ''}。完整数字见 [合并统计与检查](summary.json)。网站交互与数据检查结果见 [验证报告](../validation.json)。本轮验证使用自动交互测试，未进行真实浏览器视觉验收。

## 后续批次

使用 \`node scripts/import-plan-batch.mjs <batch-directory>\` 先查看差异，加 \`--apply\` 才合并。输入必须为公开的2026广西初始计划、官方来源和逐校目录。它不删除未出现在新批次中的既有记录，不接收征集余额，也不把校内组序号转为广西组码。随后运行数据校验和受影响交互检查再发布。
`);
console.log(JSON.stringify({...report.after,newPlans:report.newPlans,bySchool},null,2));
