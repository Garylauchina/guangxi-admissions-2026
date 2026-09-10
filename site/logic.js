export const SPECIAL = /专项|预科|民族班|定向|免费|公费|精准|地方优师|边防|乡村|基层|只投|资格名单|仅招|只招|限招|须为|政治面貌/;
export const restrictionText = row => `${row.note || ''} ${row.batch || ''} ${row.category || ''} ${row.admissionType || ''} ${row.major || ''}`.replaceAll('非定向','').replaceAll('不含预科直升','');
export function specialLabel(row) {
  if (row.category === '未注明招生类别') return '招生类别待核';
  const text = restrictionText(row);
  const labels = ['国家专项', '地方专项', '高校专项', '预科', '民族班', '公费', '免费', '定向'];
  return labels.filter(x => text.includes(x)).join(' · ') || (SPECIAL.test(text) ? '有资格或地域限制' : '一般计划');
}
export const schoolKey = name => (name || '').replace(/[（）()\s]/g, '');
export const recordSourceIds = row => [...new Set([...(row.sourceIds || []), ...(row.sourceId ? [row.sourceId] : []), ...Object.values(row.fieldSourceIds || {}).flat()])];
export function exactGroupKey(row) {
  return row.year && row.schoolCode && row.school && row.group && row.track && row.batch ? [row.year, String(row.schoolCode), schoolKey(row.school), row.track, row.batch, String(row.group)].join('|') : null;
}
export function firstRoundIndex(rows) {
  const index = new Map();
  for (const row of rows.filter(r => r.round === '首轮')) {
    const key = exactGroupKey(row);
    if (!key || index.has(key)) throw new Error('首轮专业组身份缺失或重复，请核查数据。');
    index.set(key, row);
  }
  return index;
}
export function getReference(value, mode, track, ranks) {
  if (value === '' || value === null || value === undefined) return { score: null, empty: true };
  const n = Number(value);
  if (!Number.isInteger(n) || n < (mode === 'rank' ? 1 : 0) || (mode !== 'rank' && n > 750)) return { score: null, error: mode === 'rank' ? '请填写大于 0 的整数位次。' : '请填写 0–750 之间的整数分数。' };
  const rows = ranks.filter(r => r.track === track);
  if (mode === 'rank') {
    const r = rows.find(r => n >= r.rankStart && n <= r.rankEnd);
    return r ? { score: r.score, rank: r, fromRank: true } : { score: null, error: '该位次不在公开一分一档表的可查范围内，不能换算分数。' };
  }
  return { score: n, rank: rows.find(r => r.score === n) || null, fromRank: false };
}
export function subjectStatus(row, selected) {
  if (!selected.length) return 'unchecked';
  if (!row.subjectRule || row.subjectRule === 'unknown') return 'unknown';
  if (row.subjectRule === 'none' || !row.requiredSubjects?.length) return 'match';
  const ok = row.subjectRule === 'any' ? row.requiredSubjects.some(s => selected.includes(s)) : row.requiredSubjects.every(s => selected.includes(s));
  return ok ? 'match' : 'mismatch';
}
export function scoreMatch(score, reference, band, includeUnknown = true) {
  if (score === null || score === undefined) return includeUnknown;
  if (reference === null || reference === undefined || band === 'all') return true;
  if (band === 'below') return score <= reference;
  const radius = Number(band);
  return Math.abs(score - reference) <= radius;
}
export const comparableScore = row => row.scoreComparable === false ? null : row.referenceScore ?? row.score ?? null;
export function filterRows(rows, opts) {
  const query = (opts.query || '').trim().toLowerCase();
  return rows.filter(r => {
    if (opts.track && r.track !== opts.track) return false;
    if (opts.batch && opts.batch !== 'all' && r.batch !== opts.batch) return false;
    if (opts.kind === 'general' && SPECIAL.test(restrictionText(r))) return false;
    if (opts.kind === 'special' && !SPECIAL.test(restrictionText(r))) return false;
    if (query && ![r.school, r.schoolCode, r.group, r.major, r.note, ...(r.joinedMajors || [])].filter(Boolean).join(' ').toLowerCase().includes(query)) return false;
    if (!scoreMatch(comparableScore(r), opts.reference, opts.band, opts.includeUnknown)) return false;
    if (opts.subjects?.length && subjectStatus(r, opts.subjects) === 'mismatch') return false;
    if (opts.onlyVerifiedSubjects && (!r.subjectRule || r.subjectRule === 'unknown')) return false;
    if (opts.savedOnly && !opts.saved.has(r.id)) return false;
    return true;
  });
}
export function escapeHTML(value) {
  return String(value ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
}
export function csvCell(value) {
  let s = String(value ?? '');
  if (/^[=+\-@\t\r]/.test(s)) s = "'" + s;
  return '"' + s.replace(/"/g, '""') + '"';
}
export function safeUrl(value) {
  try { const u = new URL(value); return ['https:', 'http:'].includes(u.protocol) ? u.href : '#'; } catch { return '#'; }
}
