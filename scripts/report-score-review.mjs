import assert from 'node:assert/strict';
import { readFile, writeFile } from 'node:fs/promises';
import { execFileSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

const [directory, baseline] = process.argv.slice(2);
assert.ok(directory && baseline, 'Usage: node scripts/report-score-review.mjs <review-directory> <baseline-commit>');
const root = new URL('../', import.meta.url);
const report = pathToFileURL(resolve(directory) + '/');
const read = async path => JSON.parse(await readFile(path, 'utf8'));
const oldFile = name => execFileSync('git', ['show', `${baseline}:site/data/${name}.json`], { cwd: root, encoding: 'utf8', maxBuffer: 20 * 1024 * 1024 });
const incoming = await read(new URL('major-cutoffs-upsert.json', report));
const reviews = await read(new URL('school-audit-notes.json', report));
const sources = await read(new URL('sources.json', report));
const targets = await read(new URL('targets.json', report));
const all = await read(new URL('site/data/major-cutoffs.json', root));
const old = JSON.parse(oldFile('major-cutoffs'));
const oldSources = JSON.parse(oldFile('sources'));
const oldSourceIds = new Set(oldSources.map(r => r.id));
const installedSources = new Map((await read(new URL('site/data/sources.json', root))).map(r => [r.id, r]));
for (const r of oldSources) assert.deepEqual(installedSources.get(r.id), r, `Existing source changed: ${r.id}`);
const map = new Map(all.map(r => [r.id, r]));
for (const r of old) assert.deepEqual(map.get(r.id), r, `Existing record changed: ${r.id}`);
for (const r of incoming) assert.deepEqual(map.get(r.id), r, `Batch record not installed: ${r.id}`);
assert.equal(all.length, old.length + incoming.length);
for (const target of targets) assert.ok(reviews.some(r => r.schoolCode === target.schoolCode && r.auditKind === 'major-scores'), `Target not reviewed: ${target.schoolCode}`);
for (const [file, additions] of [['school-audit-notes', reviews], ['sources', sources]]) {
  const installed = new Map((await read(new URL(`site/data/${file}.json`, root))).map(r => [r.id, r]));
  for (const item of additions) assert.deepEqual(installed.get(item.id), item, `Review evidence not installed: ${item.id}`);
}
const preserved = {};
for (const name of ['cutoffs', 'plans', 'ranks', 'special-programs', 'policies', 'supplementary-plans', 'plan-source-catalog', 'major-filing-cutoffs']) {
  const text = await readFile(new URL(`site/data/${name}.json`, root), 'utf8');
  assert.equal(text, oldFile(name), `Out-of-scope data changed: ${name}`);
  preserved[name] = { unchanged: true, sha256: createHash('sha256').update(text).digest('hex') };
}
const schools = [...new Set(incoming.map(r => r.schoolCode))].map(code => {
  const rows = incoming.filter(r => r.schoolCode === code);
  return { schoolCode: code, school: rows[0].school, records: rows.length, comparable: rows.filter(r => r.scoreComparable !== false).length, pending: rows.filter(r => r.scoreComparable === false).length, physics: rows.filter(r => r.track === '物理').length, history: rows.filter(r => r.track === '历史').length, rounds: [...new Set(rows.map(r => r.round))], unknownGroup: rows.filter(r => !r.group).length, unknownBatch: rows.filter(r => /待核/.test(r.batch)).length, publishedRank: rows.filter(r => Number.isFinite(r.rank)).length };
});
const counts = rows => ({ records: rows.length, schools: new Set(rows.map(r => r.schoolCode)).size, pending: rows.filter(r => r.scoreComparable === false).length });
const summary = {
  year: 2026, checkedAt: new Date().toISOString(), baselineCommit: baseline,
  priorityTargetSchools: targets.length, reviewedSchoolCodes: new Set(reviews.map(r => r.schoolCode)).size,
  reviewedSchoolsWithoutNewScores: new Set(reviews.filter(r => !incoming.some(s => s.schoolCode === r.schoolCode)).map(r => r.schoolCode)).size,
  sourceRecordsInBatch: sources.length, sourceRecordsAdded: sources.filter(r => !oldSourceIds.has(r.id)).length,
  oldSourceRecordsUnchanged: oldSources.length, before: counts(old), after: counts(all),
  added: { records: incoming.length, comparable: incoming.filter(r => r.scoreComparable !== false).length, pending: incoming.filter(r => r.scoreComparable === false).length, schools },
  oldMajorRecordsUnchanged: old.length, preserved,
  limits: ['部分覆盖，复查未取得不表示学校没有发布', '不以2025数据或专业组投档分填补2026专业分', '来源未区分轮次则保留汇总，不充作首轮', '组码和精确批次未知保持待核', '专业录取数不转换成计划数', '加分处理按高校说明，不一律称为裸分', '优先级分数是该校符合筛选条件的首轮组最高分，不是该校最低分']
};
await writeFile(new URL('summary.json', report), JSON.stringify(summary, null, 2) + '\n');
console.log(JSON.stringify({ added: summary.added.records, after: summary.after, preserved: old.length, reviewed: summary.reviewedSchoolCodes, targets: targets.length }, null, 2));
