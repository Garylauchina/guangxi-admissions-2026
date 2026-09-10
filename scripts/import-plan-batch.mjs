import assert from 'node:assert/strict';
import { readFile, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { pathToFileURL } from 'node:url';
import { recordSourceIds } from '../site/logic.js';
import { buildCoverage } from '../site/coverage.js';

const statuses = new Set(['collected', 'source-found', 'entry-only', 'unavailable']);
const identity = r => [r.year, r.schoolCode, r.track, r.batch, r.major, r.category || '', r.majorCode || ''].join('|');
const read = async path => JSON.parse(await readFile(path, 'utf8'));
const unique = (rows, key, label) => {
  assert.ok(Array.isArray(rows), `${label} must be an array`);
  const map = new Map();
  for (const row of rows) { assert.ok(row[key] && !map.has(row[key]), `Missing or repeated ${label} key: ${row[key]}`); map.set(row[key], row); }
  return map;
};

// Build and validate the entire proposed update before touching any published file.
export function prepareBatch(current, batch) {
  const plans = unique(current.plans, 'id', 'existing plan');
  const sources = unique(current.sources, 'id', 'existing source');
  const catalog = unique(current.catalog, 'schoolCode', 'existing catalog');
  unique(batch.plans, 'id', 'batch plan'); unique(batch.sources, 'id', 'batch source'); unique(batch.catalog, 'schoolCode', 'batch catalog');
  for (const source of batch.sources) {
    assert.ok(source.title && /^https?:\/\//.test(source.url), `Invalid source ${source.id}`);
    if (source.sha256) assert.match(source.sha256, /^[a-f0-9]{64}$/);
    const old = sources.get(source.id);
    if (old) assert.equal(source.url, old.url, `Existing source URL changed: ${source.id}`);
    sources.set(source.id, {...old, ...source});
  }
  const checkRefs = row => {
    const ids = recordSourceIds(row); assert.ok(ids.length, `Missing sources: ${row.id || row.schoolCode}`);
    for (const id of ids) assert.ok(sources.has(id), `Missing source ${id}`);
  };
  const changes = [];
  for (const row of batch.plans) {
    assert.equal(row.year, 2026); assert.equal(row.province, '广西'); assert.equal(row.planStage, 'initial', '征集余额不能导入初始计划');
    assert.ok(!/征集/.test(row.evidenceRound || ''), '征集证据不能建立初始分组');
    for (const key of ['firstRoundMatchAllowed','initialPlanEligible']) assert.notEqual(row[key],false, `Not an initial plan: ${row.id} ${key}`);
    assert.notEqual(row.plannedCountScope,'remaining-supplementary-plan');
    assert.match(String(row.schoolCode), /^\d{5}$/); assert.ok(row.school && row.major && row.batch);
    assert.ok(['物理', '历史'].includes(row.track));
    assert.ok(Number.isInteger(row.plannedCount) && row.plannedCount >= 0);
    assert.ok(!/征集|预科直升|艺术批|体育批/.test(`${row.batch} ${row.round || ''}`), `Wrong plan stage: ${row.id}`);
    assert.ok(['none', 'all', 'any', 'unknown'].includes(row.subjectRule));
    assert.ok(Array.isArray(row.requiredSubjects) && row.requiredSubjects.every(s => ['化学', '生物', '政治', '地理'].includes(s)));
    if (['all', 'any'].includes(row.subjectRule)) assert.ok(row.requiredSubjects.length);
    if (row.group) assert.match(String(row.group), /^\d{3}$/);
    assert.ok(!row.groupEvidenceRound || ['首轮', '初始计划'].includes(row.groupEvidenceRound), 'Other-round group evidence cannot establish initial grouping');
    checkRefs(row);
    const old = plans.get(row.id);
    if (old) {
      for (const key of ['year','schoolCode','school','track','major','majorCode']) assert.equal(row[key],old[key],`Existing plan identity changed: ${row.id} ${key}`);
      for (const key of ['batch','category','group','plannedCount']) if (row[key] !== old[key]) assert.ok(row.fieldSourceIds?.[key]?.length,`Field correction needs direct evidence: ${row.id} ${key}`);
    }
    else assert.ok(![...plans.values()].some(r => identity(r) === identity(row)), `Possible duplicate plan with a new ID: ${row.id}`);
    if (!old || JSON.stringify(old) !== JSON.stringify(row)) changes.push({id:row.id, school:row.school, action:old ? 'update' : 'add', fields:old ? Object.keys({...old,...row}).filter(k => JSON.stringify(old[k]) !== JSON.stringify(row[k])) : []});
    plans.set(row.id, row);
  }
  for (const row of batch.catalog) {
    assert.equal(row.year, 2026); assert.match(String(row.schoolCode), /^\d{5}$/);
    assert.ok(row.school && row.checkedAt && row.note && statuses.has(row.status)); checkRefs(row);
    if (row.entryUrl) assert.match(row.entryUrl, /^https?:\/\//);
    const old = catalog.get(row.schoolCode);
    catalog.set(row.schoolCode, {...old, ...row, sourceIds:[...new Set([...(old?.sourceIds || []), ...row.sourceIds])]});
  }
  return {plans:[...plans.values()], sources:[...sources.values()], catalog:[...catalog.values()], changes};
}

async function main() {
  const directory = process.argv[2]; assert.ok(directory, 'Usage: node scripts/import-plan-batch.mjs <batch-directory> [--apply]');
  const root = new URL('../', import.meta.url), data = new URL('site/data/', root);
  const [plans, sources, catalog, cutoffs, majorCutoffs, auditNotes] = await Promise.all(['plans','sources','plan-source-catalog','cutoffs','major-cutoffs','school-audit-notes'].map(name => read(new URL(`${name}.json`, data))));
  const incoming = await Promise.all(['plans-upsert','sources','source-catalog'].map(name => read(resolve(directory, `${name}.json`))));
  const next = prepareBatch({plans,sources,catalog}, {plans:incoming[0],sources:incoming[1],catalog:incoming[2]});
  const report = {batch:directory.split('/').filter(Boolean).at(-1), before:plans.length, after:next.plans.length, added:next.changes.filter(c=>c.action==='add').length, updated:next.changes.filter(c=>c.action==='update').length, catalogSchools:next.catalog.length, changes:next.changes};
  if (process.argv.includes('--apply')) {
    const coverage = buildCoverage({cutoffs, plans:next.plans, majorCutoffs});
    const notes = new Map(auditNotes.map(row=>[row.id,row]));
    for (const row of incoming[2]) { const id=`review-plan-batch-${report.batch}-${row.schoolCode}`; notes.set(id,{...row,id,title:'分批采集：专业计划来源复查',checkedUrls:row.entryUrl ? [row.entryUrl] : []}); }
    const files = {plans:next.plans, sources:next.sources, 'plan-source-catalog':next.catalog, 'school-coverage':coverage, 'school-audit-notes':[...notes.values()]};
    const backups = new Map(await Promise.all(Object.keys(files).map(async name => [name, await readFile(new URL(`${name}.json`,data),'utf8')])));
    try { for (const [name, rows] of Object.entries(files)) await writeFile(new URL(`${name}.json`,data), JSON.stringify(rows,null,name==='sources' ? 2 : undefined)+'\n'); }
    catch (error) { for (const [name, text] of backups) await writeFile(new URL(`${name}.json`,data),text); throw error; }
  }
  console.log(JSON.stringify(report,null,2));
}
if (process.argv[1] && import.meta.url === pathToFileURL(resolve(process.argv[1])).href) await main();
