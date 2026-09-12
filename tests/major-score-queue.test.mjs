import test from 'node:test';
import assert from 'node:assert/strict';
import { buildMajorScoreQueue, INPUT_DATASETS, isMajorScoreAudit } from '../scripts/build-major-score-queue.mjs';

const asOf = '2026-09-12';
const emptyData = () => ({ ...Object.fromEntries(INPUT_DATASETS.map(n => [n, []])), sources: [{ id: 'official' }] });
const row = (code, extra = {}) => ({ year: 2026, schoolCode: code, school: `学校${code}`, sourceId: 'official', ...extra });
const audit = (code, id, extra = {}) => row(code, { id, checkedAt: '2026-09-11', note: '仅检查此入口', ...extra });

test('score queue uses every code-based dataset and keeps identical names under different codes', () => {
  const data = emptyData();
  data.cutoffs = [
    row('10001', { school: '同名大学', track: '物理', batch: '本科普通批', round: '首轮', score: 650 }),
    row('19001', { school: '同名大学', track: '历史', batch: '本科普通批', round: '第一次征集', score: 600 }),
  ];
  data.plans = [row('20001', { major: '临床医学', track: '物理', batch: '本科（批次待核）' })];
  data['major-cutoffs'] = [row('30001', { major: '计算机科学与技术', track: '物理', batch: '本科普通批', score: 500, scoreComparable: false })];
  data['school-coverage'] = [row('40001')];
  data['supplementary-plans'] = [row('50001')];
  data['major-filing-cutoffs'] = [row('60001', { score: 200 })];
  data['school-audit-notes'] = [audit('70001', 'review-major-gap-70001')];
  data['plan-source-catalog'] = [row('80001')];
  const { inventory, summary } = buildMajorScoreQueue(data, { asOf });
  assert.equal(inventory.length, 9);
  assert.deepEqual(inventory.filter(r => r.school === '同名大学').map(r => r.schoolCode), ['10001', '19001']);
  assert.deepEqual(summary.scope.supplementaryOnlyCodes, ['19001']);
  assert.equal(summary.scope.otherDataOnlyCodes.length, 7);
  assert.equal(inventory.find(r => r.schoolCode === '20001').ordinaryLevel, 'unknown');
  assert.equal(inventory.find(r => r.schoolCode === '20001').observedLevel, 'undergraduate');
  assert.equal(inventory.find(r => r.schoolCode === '30001').scoreStatus, 'reviewed-no-actual-records');
  assert.equal(summary.actualMajorScores.schoolCodesWithSomeRecords, 1);
  assert.equal(summary.actualMajorScores.schoolCodesWithComparableRecords, 0);
  assert.deepEqual(summary.actualMajorScores.pendingOnlySchoolCodes, ['30001']);
  assert.equal(summary.scoreAudit.reviewedSchoolCodes, 2);
  assert.equal(summary.scoreAudit.schoolCodesWithAuditNotes, 1);
  assert.equal(inventory.find(r => r.schoolCode === '30001').actualMajorScore.comparableRecords, 0);
  assert.equal(inventory.find(r => r.schoolCode === '60001').actualMajorScore.records, 0);
  assert.equal(inventory.find(r => r.schoolCode === '60001').nextAction.code, 'verify-final-major-admission-outcomes');
  assert.ok(inventory.every(r => r.schoolCompleteness === 'not-established' && r.sourceCompleteness === 'not-established'));
  assert.equal(new Set(inventory.map(r => r.taskId)).size, 9);
});

test('legacy score audits count, plan audits do not, and some score rows never establish completeness', () => {
  const data = emptyData();
  data['school-audit-notes'] = [
    audit('10001', 'review-major-gap-10001'),
    audit('10002', 'review-major-collected-10002'),
    audit('10003', 'review-plan-batch-a-10003'),
    audit('10004', 'review-2026-10004', { auditKind: 'major-scores' }),
    audit('10004', 'review-plans-10004', { checkedAt: '2026-09-12' }),
  ];
  data['major-cutoffs'] = [row('10002', { major: '数学', track: '物理', score: 600, evidenceStatus: 'source-conflict', scoreComparable: true })];
  const { inventory, summary } = buildMajorScoreQueue(data, { asOf });
  assert.equal(summary.scoreAudit.reviewedSchoolCodes, 3);
  assert.equal(summary.scoreAudit.noteRecords, 3);
  assert.equal(summary.scoreAudit.legacyNoteRecords, 2);
  assert.deepEqual(summary.scoreStatusCounts, { 'not-score-reviewed': 1, 'partial-collected': 1, 'reviewed-no-actual-records': 2 });
  assert.equal(inventory.find(r => r.schoolCode === '10003').scoreAudit.noteIds.length, 0);
  assert.equal(inventory.find(r => r.schoolCode === '10004').scoreAudit.latestNoteId, 'review-2026-10004');
  assert.equal(summary.actualMajorScores.comparableRecords, 1);
  assert.equal(summary.actualMajorScores.sourceConflictRecords, 1);
  assert.equal(summary.actualMajorScores.professionalDenominator, null);
  assert.equal(summary.actualMajorScores.professionalCompletenessPercent, null);
  assert.equal(isMajorScoreAudit({ id: 'review-major-plan-10001' }), false);
});
test('pending-only major scores do not fill plan-score gaps; mixed schools use only comparable rows for overlap', () => {
  const data=emptyData();
  data.plans=[row('10001',{major:'数学',track:'物理'}),row('10002',{major:'数学',track:'物理'})];
  data['major-cutoffs']=[
    row('10001',{major:'数学',track:'物理',score:500,scoreComparable:false}),
    row('10002',{major:'数学',track:'物理',score:500,scoreComparable:false}),
    row('10002',{major:'法学',track:'历史',score:600,scoreComparable:true}),
  ];
  const {inventory,summary}=buildMajorScoreQueue(data,{asOf});
  assert.equal(inventory[0].scoreStatus,'reviewed-no-actual-records');
  assert.equal(inventory[0].planScoreOverlap.hasBothAtSchoolLevel,false);
  assert.equal(inventory[1].scoreStatus,'partial-collected');
  assert.equal(inventory[1].actualMajorScore.records,2);
  assert.equal(inventory[1].actualMajorScore.comparableRecords,1);
  assert.equal(inventory[1].planScoreOverlap.hasBothAtSchoolLevel,true);
  assert.equal(summary.planScoreOverlap.bothSchoolCodes,1);
  assert.equal(summary.planScoreOverlap.plansWithoutActualScoresSchoolCodes,1);
  assert.equal(summary.planScoreOverlap.planRowsWithCandidateLiteralMatch,0);
  assert.equal(summary.actualMajorScores.schoolCodesWithSomeRecords,2);
  assert.equal(summary.actualMajorScores.schoolCodesWithComparableRecords,1);
  assert.deepEqual(summary.actualMajorScores.pendingOnlySchoolCodes,['10001']);
});

test('ranking remains per track and uses known first-round group scores while candidate major matches stay unverified', () => {
  const data = emptyData();
  data.cutoffs = [
    row('10001', { track: '物理', batch: '本科普通批', round: '首轮', score: 610 }),
    row('10001', { track: '物理', batch: '本科普通批', round: '首轮', score: 640, note: '国家专项' }),
    row('10001', { track: '物理', batch: '本科普通批', round: '第二次征集', score: 680 }),
    row('10001', { track: '历史', batch: '本科普通批', round: '首轮', score: 630 }),
    row('10001', { track: '历史', batch: '高职高专普通批', round: '首轮', score: null }),
  ];
  data.plans = [row('10001', { track: '物理', major: '临床医学', batch: '本科普通批', group: '101' })];
  data['major-cutoffs'] = [row('10001', { track: '物理', major: '临床医学', batch: '本科提前批', group: '201', score: 620 })];
  const { inventory, summary } = buildMajorScoreQueue(data, { asOf });
  const school = inventory[0];
  assert.equal(school.ordinaryLevel, 'mixed');
  assert.equal(school.priorityByTrack['物理'].maximumFirstRoundGroupScore, 640);
  assert.equal(school.priorityByTrack['物理'].maximumFirstRoundGeneralGroupScore, 610);
  assert.equal(school.priorityByTrack['历史'].maximumFirstRoundGroupScore, 630);
  assert.equal(school.priorityByTrack['历史'].knownScoreGroups, 1);
  assert.equal(school.planScoreOverlap.literalTrackMajorKeys, 1);
  assert.equal(school.planScoreOverlap.exactAssociationEstablished, false);
  assert.equal(summary.planScoreOverlap.exactAssociationEstablished, false);
});

test('special program identities and score counts stay separate and output is reproducible for a fixed date', () => {
  const data = emptyData();
  data.cutoffs = [row('10001', { school: '大学甲', track: '物理', batch: '本科普通批', round: '首轮', score: 600 })];
  data['special-programs'] = [
    { id: 'strong-a', school: '大学甲', title: '甲强基', type: 'strong-foundation', guangxiStatus: 'confirmed', scoreRecords: [{ score: 80 }], sourceIds: ['official'] },
    { id: 'strong-b', school: '大学乙', type: 'strong-foundation', guangxiStatus: 'unknown', sourceIds: ['official'] },
  ];
  const before = structuredClone(data);
  const options = { asOf, inputEvidence: [{ path: 'site/data/cutoffs.json', bytes: 123, sha256: 'example', records: 1 }] };
  const result = buildMajorScoreQueue(data, options);
  assert.deepEqual(result, buildMajorScoreQueue(data, options));
  assert.deepEqual(data, before, 'The queue builder must not modify the source records.');
  assert.equal(result.inventory.length, 1);
  assert.equal(result.summary.specialProgramDirectory.schoolNames, 2);
  assert.equal(result.summary.specialProgramDirectory.scoreRecords, 1);
  assert.deepEqual(result.summary.specialProgramDirectory.schoolNamesOutsideOrdinaryExactNameSet, ['大学乙']);
  const special = result['special-inventory'][0];
  assert.equal(special.taskId, '2026-gx-special-strong-a');
  assert.equal(special.schoolCode, null);
  assert.equal(special.identityMappingEstablished, false);
  assert.deepEqual(special.identityCandidates, [{ schoolCode: '10001', matchBasis: 'exact school name only', status: 'pending-verification' }]);
  assert.equal(special.scoreRecordsCount, 1);
  assert.equal(result.summary.asOf, asOf);
  assert.throws(() => buildMajorScoreQueue(data), /explicit/);
  data.plans.push(row('10002', { sourceId: 'missing-source' }));
  assert.throws(() => buildMajorScoreQueue(data, options), /Unknown source/);
});

test('same-day reviews retain all results without using IDs as chronology and codes require five digits', () => {
  const data = emptyData();
  data['school-audit-notes'] = [
    audit('10001', 'review-major-gap-z', { checkedAt: '2026-09-12', status: 'access-restricted' }),
    audit('10001', 'review-major-gap-a', { checkedAt: '2026-09-12T10:30:00+08:00', status: 'group-only' }),
    audit('10001', 'review-major-gap-prior', { checkedAt: '2026-09-11T15:00:00+08:00', status: 'entry-only' }),
  ];
  const school = buildMajorScoreQueue(data, { asOf }).inventory[0];
  assert.equal(school.scoreAudit.latestReviewDate, '2026-09-12');
  assert.deepEqual(new Set(school.scoreAudit.latestNoteIds), new Set(['review-major-gap-z', 'review-major-gap-a']));
  assert.deepEqual(school.scoreAudit.latestStatuses, ['access-restricted', 'group-only']);
  assert.equal(school.scoreAudit.latestNoteId, null);
  assert.equal(school.scoreAudit.latestStatus, null);
  assert.equal(school.nextAction.code, 'review-same-day-evidence-before-continuing');
  assert.match(school.scoreAudit.latestSelectionBasis, /not temporal order/);
  data.plans.push(row('1000'));
  assert.throws(() => buildMajorScoreQueue(data, { asOf }), /five-digit/);
});
