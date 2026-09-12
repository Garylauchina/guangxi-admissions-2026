import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { pathToFileURL } from 'node:url';
import { SPECIAL, restrictionText, recordSourceIds, reviewDate } from '../site/logic.js';
import { isComparableMajorScore } from '../site/coverage.js';

export const CODE_DATASETS = [
  'cutoffs', 'plans', 'major-cutoffs', 'school-coverage',
  'supplementary-plans', 'major-filing-cutoffs',
  'school-audit-notes', 'plan-source-catalog',
];
export const INPUT_DATASETS = [...CODE_DATASETS, 'special-programs', 'sources'];

// Early score reviews predate auditKind. Plan reviews must remain separate.
export function isMajorScoreAudit(row) {
  return row.auditKind === 'major-scores'
    || /^review-major-(?:gap|collected)-/.test(row.id || '');
}

const sorted = values => [...new Set(values)].filter(v => v !== undefined && v !== null).sort();
const counts = (rows, key) => Object.fromEntries(sorted(rows.map(r => r[key] || 'not-specified'))
  .map(value => [value, rows.filter(r => (r[key] || 'not-specified') === value).length]));
const literalMajorKey = row => JSON.stringify([String(row.schoolCode), row.track, row.major]);
const maximum = values => values.length ? Math.max(...values) : null;

function batchLevel(batches) {
  const under = batches.some(b => /本科/.test(b));
  const vocational = batches.some(b => /高职|专科/.test(b));
  return under && vocational ? 'mixed' : under ? 'undergraduate' : vocational ? 'vocational' : 'unknown';
}

function nextAction(status, latestReviews, pending, filingOnly) {
  if (pending) return {
    code: 'resolve-source-conflict-and-complete-roster',
    label: '先复核原文冲突，再核对完整广西专业名录及其余分数；原待核行继续不参与比较。',
  };
  if (status === 'partial-collected') return {
    code: 'complete-professional-roster-and-score-fields',
    label: '核对该校全部广西专业、科类、批次和招生类别，继续补齐未收专业及缺失字段。',
  };
  if (filingOnly) return {
    code: 'verify-final-major-admission-outcomes',
    label: '已存专业投档线；另查实际专业录取结果，保持两种分数口径分开。',
  };
  if (status === 'not-score-reviewed') return {
    code: 'discover-and-audit-official-score-sources',
    label: '定位学校官方招生及信息公开入口，检查2026广西逐科类专业录取结果。',
  };
  if (latestReviews.length > 1) return {
    code: 'review-same-day-evidence-before-continuing',
    label: '并读最近同日全部核查记录，再继续检查公开来源；台账不按记录ID推断当天先后或结果覆盖关系。',
  };
  const latest = latestReviews[0];
  if (/restricted|limited|captcha|412|gateway|transport/.test(`${latest?.status || ''} ${latest?.accessLimitType || ''}`)) return {
    code: 'check-public-alternative-and-record-access-limit',
    label: '检查官网其他公开发布渠道；记录原入口访问限制，不绕过登录或验证。',
  };
  return {
    code: 'recheck-2026-official-score-channel',
    label: '从上次官方入口和限定查询条件继续核查；旧年、空结果或组汇总不能填入实际专业分。',
  };
}

export function buildMajorScoreQueue(data, { asOf, inputEvidence = [] } = {}) {
  assert.match(asOf || '', /^\d{4}-\d{2}-\d{2}$/, 'An explicit YYYY-MM-DD asOf date is required.');
  assert.equal(new Date(`${asOf}T00:00:00.000Z`).toISOString().slice(0, 10), asOf, 'Invalid asOf date.');
  for (const name of INPUT_DATASETS) assert.ok(Array.isArray(data[name]), `Missing array: ${name}`);
  const schools = new Map();
  for (const name of CODE_DATASETS) {
    for (const row of data[name]) {
      assert.equal(row.year, 2026, `Unexpected year in ${name}.`);
      assert.ok(row.schoolCode && row.school, `Missing school identity in ${name}.`);
      const code = String(row.schoolCode);
      assert.match(code, /^\d{5}$/, `Expected a five-digit school code in ${name}.`);
      if (!schools.has(code)) schools.set(code, Object.fromEntries(CODE_DATASETS.map(n => [n, []])));
      schools.get(code)[name].push(row);
    }
  }
  const sourceIds = new Set(data.sources.map(s => s.id));
  assert.equal(sourceIds.size, data.sources.length, 'Duplicate source IDs.');
  const inventory = [...schools].sort(([a], [b]) => a.localeCompare(b)).map(([code, datasets]) => {
    const all = CODE_DATASETS.flatMap(name => datasets[name]);
    const groups = datasets.cutoffs;
    const first = groups.filter(r => r.round === '首轮');
    const plans = datasets.plans;
    const scores = datasets['major-cutoffs'];
    const reviews = datasets['school-audit-notes'].filter(isMajorScoreAudit)
      .sort((a, b) => (a.checkedAt || '').localeCompare(b.checkedAt || '') || a.id.localeCompare(b.id));
    const latestReviewDate = sorted(reviews.map(r => reviewDate(r.checkedAt)).filter(Boolean)).at(-1) || null;
    const latestReviews = latestReviewDate
      ? reviews.filter(r => reviewDate(r.checkedAt) === latestReviewDate)
      : reviews;
    // A date-only review cannot be ordered against another review that day.
    // Retain every review on the latest day; ID sorting is display order only.
    const latest = latestReviews.length === 1 ? latestReviews[0] : null;
    const coverage = datasets['school-coverage'];
    assert.ok(coverage.length <= 1, `Duplicate coverage code: ${code}`);
    const names = sorted(all.map(r => r.school));
    const comparableScores = scores.filter(isComparableMajorScore);
    const pending = scores.length - comparableScores.length;
    // Pending-only evidence is reviewed, but does not establish a usable actual score.
    const status = comparableScores.length ? 'partial-collected' : (scores.length || reviews.length) ? 'reviewed-no-actual-records' : 'not-score-reviewed';
    const pkeys = new Set(plans.map(literalMajorKey));
    const mkeys = new Set(comparableScores.map(literalMajorKey));
    const sourceRefs = sorted(all.flatMap(recordSourceIds));
    for (const id of sourceRefs) assert.ok(sourceIds.has(id), `Unknown source reference ${id} for ${code}.`);
    const priorityByTrack = Object.fromEntries(['物理', '历史'].map(track => {
      const trackRows = first.filter(r => r.track === track && Number.isFinite(r.score));
      return [track, {
        maximumFirstRoundGroupScore: maximum(trackRows.map(r => r.score)),
        maximumFirstRoundGeneralGroupScore: maximum(trackRows.filter(r => !SPECIAL.test(restrictionText(r))).map(r => r.score)),
        knownScoreGroups: trackRows.length,
      }];
    }));
    return {
      taskId: `2026-gx-major-${code}`,
      year: 2026,
      schoolCode: code,
      school: coverage[0]?.school || all[0].school,
      names,
      datasets: CODE_DATASETS.filter(name => datasets[name].length).map(name => `${name}.json`),
      ordinaryLevel: batchLevel(sorted(groups.map(r => r.batch))),
      ordinaryLevelBasis: 'observed ordinary-filing batches, not the official institutional classification',
      observedLevel: batchLevel(sorted([...groups, ...plans, ...scores].map(r => r.batch)).filter(Boolean)),
      tracks: sorted([...groups, ...plans, ...scores].map(r => r.track)),
      batches: sorted([...groups, ...plans, ...scores].map(r => r.batch)),
      ordinaryBatches: sorted(groups.map(r => r.batch)),
      scopeException: groups.length ? null : 'code-present-only-in-other-collected-data',
      cutoff: {
        records: groups.length,
        rounds: counts(groups, 'round'),
        firstRoundGroups: first.length,
        firstRoundNullScores: first.filter(r => r.score === null).length,
        allRoundsNullScores: groups.filter(r => r.score === null).length,
      },
      plan: {
        records: plans.length,
        supplementaryRecords: datasets['supplementary-plans'].length,
        sourceCatalogRecords: datasets['plan-source-catalog'].length,
        literalTrackMajorKeys: pkeys.size,
        firstRoundGroupsWithSomeMatchedPlans: coverage[0]?.groupsWithPlans || 0,
        planRecordsWithComparableGroupScore: coverage[0]?.plansWithComparableGroupScore || 0,
      },
      actualMajorScore: {
        records: scores.length,
        comparableRecords: comparableScores.length,
        pendingComparisonRecords: pending,
        sourceConflictRecords: scores.filter(r => r.evidenceStatus === 'source-conflict').length,
        tracks: sorted(scores.map(r => r.track)),
        batches: counts(scores, 'batch'),
        rounds: counts(scores, 'round'),
        literalTrackMajorKeys: mkeys.size,
        recordsWithGroup: scores.filter(r => r.group).length,
        recordsWithPublishedRank: scores.filter(r => Number.isFinite(r.rank)).length,
        recordsWithAdmittedCount: scores.filter(r => Number.isFinite(r.admittedCount)).length,
      },
      majorFilingOnlyRecords: datasets['major-filing-cutoffs'].length,
      planScoreOverlap: {
        hasBothAtSchoolLevel: Boolean(plans.length && comparableScores.length),
        literalTrackMajorKeys: [...pkeys].filter(k => mkeys.has(k)).length,
        planRowsWithLiteralMatch: plans.filter(r => mkeys.has(literalMajorKey(r))).length,
        scoreRowsWithLiteralMatch: comparableScores.filter(r => pkeys.has(literalMajorKey(r))).length,
        exactAssociationEstablished: false,
      },
      scoreStatus: status,
      scoreAudit: {
        noteIds: reviews.map(r => r.id),
        statuses: counts(reviews, 'status'),
        latestReviewDate,
        latestNoteIds: latestReviews.map(r => r.id),
        latestStatuses: sorted(latestReviews.map(r => r.status)),
        latestNotes: latestReviews.map(r => ({ id: r.id, checkedAt: r.checkedAt || null, status: r.status || null, note: r.note || null })),
        latestSelectionBasis: latestReviews.length > 1
          ? 'all reviews on the latest Beijing calendar date retained; ID order is not temporal order; same-day supersession unverified'
          : latestReviewDate ? 'one review on latest Beijing calendar date' : 'no usable review date; order unknown',
        latestNoteId: latest?.id || null,
        latestCheckedAt: latest?.checkedAt || null,
        latestStatus: latest?.status || null,
        latestNote: latest?.note || null,
        checkedUrls: sorted(reviews.flatMap(r => r.checkedUrls || [])),
        sourceRefs: sorted(reviews.flatMap(recordSourceIds)),
      },
      anyAuditNoteRecords: datasets['school-audit-notes'].length,
      priorityByTrack,
      prioritySemantics: '同科类任务排序依据：各首轮专业组最低投档分中的最高值；不是专业分，也不是学校最低录取分。物理与历史不混排。',
      nextAction: nextAction(status, latestReviews, pending, datasets['major-filing-cutoffs'].length),
      schoolCompleteness: 'not-established',
      sourceCompleteness: 'not-established',
      sourceRefs,
    };
  });
  const levelCounts = rows => counts(rows, 'ordinaryLevel');
  const partial = inventory.filter(r => r.scoreStatus === 'partial-collected');
  const reviewedEmpty = inventory.filter(r => r.scoreStatus === 'reviewed-no-actual-records');
  const unreviewed = inventory.filter(r => r.scoreStatus === 'not-score-reviewed');
  const sum = (key, field) => inventory.reduce((n, r) => n + r[key][field], 0);
  const ordinaryNames = new Map();
  for (const row of inventory) for (const name of row.names) ordinaryNames.set(name, [...(ordinaryNames.get(name) || []), row.schoolCode]);
  const specialItems = data['special-programs'].map(r => ({
    taskId: `2026-gx-special-${r.id}`,
    id: r.id, school: r.school, type: r.type,
    name: r.title || r.school,
    year: 2026,
    schoolCode: null,
    schoolCodeStatus: 'unknown; requires explicit identity evidence',
    schoolCodeInDataset: r.schoolCode || null,
    exactNameOrdinaryCodeCandidates: ordinaryNames.get(r.school) || [],
    identityCandidates: (ordinaryNames.get(r.school) || []).map(code => ({
      schoolCode: code, matchBasis: 'exact school name only', status: 'pending-verification',
    })),
    identityMappingEstablished: false,
    guangxiStatus: r.guangxiStatus || 'unknown',
    scoreRecordsCount: r.scoreRecords?.length || 0,
    schoolCompleteness: 'not-established',
    sourceCompleteness: 'not-established',
    nextAction: {
      code: r.guangxiStatus === 'excluded' ? 'retain-exclusion-and-verify-2026-program-scope' : 'verify-identity-and-guangxi-program-score-scope',
      label: r.guangxiStatus === 'excluded'
        ? '保留当前不适用广西的证据，复核2026项目范围；不把其他省份分数纳入广西筛选。'
        : '核实学校身份和2026广西项目范围，分别核对入围、校测及录取分口径；已有数字不证明全项目完整。',
    },
    sourceRefs: recordSourceIds(r).sort(),
  }));
  assert.equal(new Set(specialItems.map(r => r.taskId)).size, specialItems.length, 'Duplicate special task IDs.');
  for (const item of specialItems) for (const id of item.sourceRefs) assert.ok(sourceIds.has(id), `Unknown special source: ${id}.`);
  const ordinaryCodes = new Set(data.cutoffs.map(r => String(r.schoolCode)));
  const firstCodes = new Set(data.cutoffs.filter(r => r.round === '首轮').map(r => String(r.schoolCode)));
  const summary = {
    schemaVersion: 1,
    year: 2026,
    asOf,
    scope: {
      schoolCodes: inventory.length,
      ordinaryFilingCodes: ordinaryCodes.size,
      firstRoundFilingCodes: firstCodes.size,
      supplementaryOnlyCodes: sorted([...ordinaryCodes].filter(code => !firstCodes.has(code))),
      otherDataOnlyCodes: inventory.filter(r => !ordinaryCodes.has(r.schoolCode)).map(r => r.schoolCode),
      codeBasedDatasets: CODE_DATASETS.map(name => `${name}.json`),
      ordinaryLevelCounts: levelCounts(inventory),
    },
    records: Object.fromEntries(INPUT_DATASETS.map(name => [name, data[name].length])),
    scoreStatusCounts: counts(inventory, 'scoreStatus'),
    scoreAudit: {
      noteRecords: data['school-audit-notes'].filter(isMajorScoreAudit).length,
      reviewedSchoolCodes: inventory.filter(r => r.scoreAudit.noteIds.length || r.actualMajorScore.records).length,
      schoolCodesWithAuditNotes: inventory.filter(r => r.scoreAudit.noteIds.length).length,
      legacyNoteRecords: data['school-audit-notes'].filter(r => r.auditKind !== 'major-scores' && isMajorScoreAudit(r)).length,
      reviewedNoActualScoreLevelCounts: levelCounts(reviewedEmpty),
      notReviewedLevelCounts: levelCounts(unreviewed),
      anyAuditKindSchoolCodes: inventory.filter(r => r.anyAuditNoteRecords).length,
      onlyNonScoreAuditCodes: inventory.filter(r => r.anyAuditNoteRecords && !r.scoreAudit.noteIds.length).map(r => r.schoolCode),
      classificationRule: 'audit notes: auditKind === major-scores OR id matches ^review-major-(gap|collected)-; plan-only audits excluded; schools with stored actual-score evidence (including pending-only) are also reviewed',
    },
    actualMajorScores: {
      schoolCodesWithSomeRecords: inventory.filter(r => r.actualMajorScore.records).length,
      schoolCodesWithComparableRecords: partial.length,
      pendingOnlySchoolCodes: inventory.filter(r => r.actualMajorScore.records && !r.actualMajorScore.comparableRecords).map(r => r.schoolCode),
      schoolStatusRule: 'partial-collected requires at least one comparable numeric actual score; pending-only schools are reviewed-no-actual-records (no comparable actual score)',
      ordinaryLevelCounts: levelCounts(partial),
      comparableRecords: sum('actualMajorScore', 'comparableRecords'),
      pendingComparisonRecords: sum('actualMajorScore', 'pendingComparisonRecords'),
      sourceConflictRecords: sum('actualMajorScore', 'sourceConflictRecords'),
      literalTrackMajorKeys: sum('actualMajorScore', 'literalTrackMajorKeys'),
      recordsWithGroup: sum('actualMajorScore', 'recordsWithGroup'),
      recordsWithPublishedRank: sum('actualMajorScore', 'recordsWithPublishedRank'),
      recordsWithAdmittedCount: sum('actualMajorScore', 'recordsWithAdmittedCount'),
      schoolCompletenessEstablished: false,
      professionalDenominator: null,
      professionalCompletenessPercent: null,
    },
    planScoreOverlap: {
      planSchoolCodes: inventory.filter(r => r.plan.records).length,
      scoreSchoolCodes: partial.length,
      bothSchoolCodes: inventory.filter(r => r.plan.records && r.actualMajorScore.comparableRecords).length,
      plansWithoutActualScoresSchoolCodes: inventory.filter(r => r.plan.records && !r.actualMajorScore.comparableRecords).length,
      actualScoresWithoutPlansSchoolCodes: inventory.filter(r => !r.plan.records && r.actualMajorScore.comparableRecords).length,
      neitherSchoolCodes: inventory.filter(r => !r.plan.records && !r.actualMajorScore.comparableRecords).length,
      candidateLiteralTrackMajorKeys: sum('planScoreOverlap', 'literalTrackMajorKeys'),
      planRowsWithCandidateLiteralMatch: sum('planScoreOverlap', 'planRowsWithLiteralMatch'),
      scoreRowsWithCandidateLiteralMatch: sum('planScoreOverlap', 'scoreRowsWithLiteralMatch'),
      exactAssociationEstablished: false,
    },
    majorFilingOnly: {
      records: data['major-filing-cutoffs'].length,
      schoolCodes: sorted(data['major-filing-cutoffs'].map(r => String(r.schoolCode))),
      includedInActualMajorScores: false,
    },
    specialProgramDirectory: {
      records: specialItems.length,
      schoolNames: new Set(specialItems.map(r => r.school)).size,
      types: counts(specialItems, 'type'),
      guangxiStatuses: counts(specialItems, 'guangxiStatus'),
      scoreRecords: specialItems.reduce((n, r) => n + r.scoreRecordsCount, 0),
      recordsWithoutSchoolCode: specialItems.filter(r => !r.schoolCodeInDataset).length,
      schoolNamesOutsideOrdinaryExactNameSet: sorted(specialItems.filter(r => !r.exactNameOrdinaryCodeCandidates.length).map(r => r.school)),
      includedInOrdinaryCodeInventory: false,
      items: specialItems,
    },
    limits: [
      '院校身份以原 schoolCode 为准，保留名称和校区原文，不按相似名称合并。',
      '已有可比较专业分和已审记录均不证明全专业或全部发布渠道完整；缺口不代表未发布。',
      '仅有待核记录的学校计为已核查仍缺可比较专业分；待核原文保留，不纳入计划与可比较专业分交集。',
      '计划与分数的逐字专业名交集仅是候选，不证明科类之外的批次、组码、招生类别、校区与轮次一致。',
      '逐字专业名称计数不是独立专业总数，正式专业分母仍缺。',
      '专业组投档分、专业投档分、实际专业录取分和特殊招生分数不能混用。',
      'asOf 是台账复现日期，不代表在这一天重新核查了所有学校网站。',
    ],
    inputEvidence,
    checks: {
      schoolCodeUnique: new Set(inventory.map(r => r.schoolCode)).size === inventory.length,
      taskIdUnique: new Set(inventory.map(r => r.taskId)).size === inventory.length,
      statusPartitionComplete: partial.length + reviewedEmpty.length + unreviewed.length === inventory.length,
      noAssumedSchoolCompleteness: inventory.every(r => r.schoolCompleteness === 'not-established'),
      noAssumedSourceCompleteness: inventory.every(r => r.sourceCompleteness === 'not-established'),
    },
  };
  for (const [key, value] of Object.entries(summary.checks)) assert.ok(value, key);
  return { inventory, summary, 'special-inventory': specialItems };
}

async function main() {
  const args = process.argv.slice(2);
  const asOfIndex = args.indexOf('--as-of');
  let asOf = asOfIndex >= 0 ? args[asOfIndex + 1] : null;
  const check = args.includes('--check');
  const accepted = new Set(['--as-of', asOf, '--check']);
  assert.ok(args.every(a => accepted.has(a)) && (asOf || (check && asOfIndex < 0)), 'Usage: node scripts/build-major-score-queue.mjs --as-of YYYY-MM-DD [--check], or --check to verify the saved snapshot date');
  const root = new URL('../', import.meta.url);
  if (!asOf) asOf = JSON.parse(await readFile(new URL('docs/full-major-score-collection/summary.json', root), 'utf8')).asOf;
  const entries = await Promise.all(INPUT_DATASETS.map(async name => {
    const path = `site/data/${name}.json`;
    const buffer = await readFile(new URL(path, root));
    return [name, JSON.parse(buffer), {
      path, bytes: buffer.byteLength,
      sha256: createHash('sha256').update(buffer).digest('hex'),
      records: JSON.parse(buffer).length,
    }];
  }));
  const result = buildMajorScoreQueue(Object.fromEntries(entries.map(([name, rows]) => [name, rows])), {
    asOf, inputEvidence: entries.map(([, , evidence]) => evidence),
  });
  const directory = new URL('docs/full-major-score-collection/', root);
  if (!check) await mkdir(directory, { recursive: true });
  for (const name of ['inventory', 'summary', 'special-inventory']) {
    const expected = JSON.stringify(result[name], null, 2) + '\n';
    const path = new URL(`${name}.json`, directory);
    if (check) assert.ok(await readFile(path, 'utf8') === expected, `Queue drift detected: ${name}.json; regenerate using the same explicit --as-of date.`);
    else await writeFile(path, expected);
  }
  console.log(JSON.stringify({ mode: check ? 'checked' : 'generated', asOf, schoolCodes: result.inventory.length, statuses: result.summary.scoreStatusCounts }, null, 2));
}

if (process.argv[1] && pathToFileURL(resolve(process.argv[1])).href === import.meta.url) {
  await main();
}
