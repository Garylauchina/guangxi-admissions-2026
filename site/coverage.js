import { exactGroupKey, firstRoundIndex, recordSourceIds } from './logic.js';

export const PLAN_GAPS = {
  group: '专业组代码', batch: '录取批次', subjects: '再选科目要求',
  tuition: '学费', duration: '学制', groupScore: '可关联的首轮组线', seats: '当前高考可填计划人数',
};
export function planGaps(row, index) {
  const gaps = [];
  if (!row.group) gaps.push('group');
  if (!row.batch || /待核|未明|未注/.test(row.batch)) gaps.push('batch');
  if (!row.subjectRule || row.subjectRule === 'unknown') gaps.push('subjects');
  if (row.tuition === null || row.tuition === undefined || row.tuition === '') gaps.push('tuition');
  if (!row.duration) gaps.push('duration');
  if (row.currentGaokaoSeatsKnown === false) gaps.push('seats');
  const group = index.get(exactGroupKey(row));
  if (!group || group.score === null) gaps.push('groupScore');
  return gaps;
}
const refs = recordSourceIds;

// This is a census of the collected records, not proof of full school coverage.
export function buildCoverage({ cutoffs, plans, majorCutoffs }) {
  const index = firstRoundIndex(cutoffs), schools = new Map();
  function school(row) {
    const key = String(row.schoolCode || `name:${row.school}`);
    if (!schools.has(key)) schools.set(key, {
      year: 2026, schoolCode: row.schoolCode || null, school: row.school,
      names: new Set(), tracks: new Set(), sourceIds: new Set(), firstRoundGroups: 0,
      groupsWithNoFiling: 0, groupsWithPlans: new Set(), plans: 0,
      plansWithComparableGroupScore: 0, majorCutoffs: 0, majorScoresPending: 0, majorRounds: new Set(),
      planGaps: Object.fromEntries(Object.keys(PLAN_GAPS).map(k => [k, 0])),
    });
    const entry = schools.get(key);
    entry.names.add(row.school); entry.tracks.add(row.track);
    refs(row).forEach(id => entry.sourceIds.add(id));
    return entry;
  }
  for (const row of cutoffs.filter(r => r.round === '首轮')) {
    const entry = school(row); entry.firstRoundGroups++;
    if (row.score === null) entry.groupsWithNoFiling++;
  }
  for (const row of plans) {
    const entry = school(row), gaps = planGaps(row, index); entry.plans++;
    for (const key of gaps) entry.planGaps[key]++;
    if (!gaps.includes('groupScore')) entry.plansWithComparableGroupScore++;
    const key = exactGroupKey(row);
    if (index.has(key)) entry.groupsWithPlans.add(key);
  }
  for (const row of majorCutoffs) {
    const entry = school(row); entry.majorCutoffs++;
    if (row.scoreComparable === false) entry.majorScoresPending++;
    entry.majorRounds.add(row.round || '未注明轮次');
  }
  return [...schools.values()].map(r => ({
    ...r, names: [...r.names].sort(), tracks: [...r.tracks].sort(),
    sourceIds: [...r.sourceIds].sort(), groupsWithPlans: r.groupsWithPlans.size,
    groupsWithoutCollectedPlans: r.firstRoundGroups - r.groupsWithPlans.size,
    majorRounds: [...r.majorRounds].sort(), coverageStatus: 'partial',
  })).sort((a, b) => String(a.schoolCode).localeCompare(String(b.schoolCode)));
}
