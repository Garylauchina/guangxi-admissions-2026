import { getReference, filterRows, exactGroupKey, escapeHTML as h, csvCell, safeUrl, subjectStatus, specialLabel } from './logic.js';

const $ = id => document.getElementById(id);
const fmt = n => Number(n).toLocaleString('zh-CN');
const YEAR = 2026;
const programType = value => ({'strong-foundation':'强基计划','competition':'学科竞赛','recommendation':'保送生','olympiad-recommendation':'奥赛保送','olympiad':'学科竞赛','young-talent':'少年 / 英才项目','youth-program':'少年 / 英才项目','math-talent':'数学英才计划','physics-talent':'物理英才计划','youth-class':'少年班'}[value] || (/[a-z]/i.test(value || '')?'特殊招生通道':value || '强基计划'));
const PAGE_SIZE = 25;
const STORE = 'guangxi-admissions-2026-shortlist-v1';
let data, sourceMap, allRows, groupIndex, planIndex, filtered = [], page = 1, view = 'cutoffs', reference = {score:null};
let saved = new Set();
try { const ids = JSON.parse(localStorage.getItem(STORE) || '[]'); if (Array.isArray(ids)) saved = new Set(ids.filter(x => typeof x === 'string')); } catch { /* Browser storage may be disabled. */ }
let toastTimer;
function toast(message) { const element=$('toast');element.textContent = message;element.hidden = false;clearTimeout(toastTimer);toastTimer = setTimeout(() => { element.hidden = true; }, 3200); }
function sourceLink(id, label = '官方来源 ↗') {
  const s = sourceMap.get(id);
  return s ? `<a href="${h(safeUrl(s.url))}" target="_blank" rel="noopener noreferrer">${h(label)}</a>` : '<span class="muted">来源待核实</span>';
}
function sourceIds(row) { return row.sourceIds || (row.sourceId ? [row.sourceId] : []); }
function sourceLinks(row) { return sourceIds(row).map(id => sourceLink(id)).join(' · '); }
function initialize() {
  sourceMap = new Map(data.sources.map(s => [s.id, s]));
  groupIndex = new Map(data.cutoffs.filter(r => r.round === '首轮').map(r => [exactGroupKey(r), r]));
  planIndex = new Map();
  for (const r of data.plans) { const key = exactGroupKey(r); if (key) { if (!planIndex.has(key)) planIndex.set(key, []); planIndex.get(key).push(r); } }
  data.cutoffs = data.cutoffs.map(r => ({...r, joinedMajors:(r.round === '首轮' ? planIndex.get(exactGroupKey(r)) || [] : []).map(p => p.major)}));
  data.plans = data.plans.map(r => {
    const group = groupIndex.get(exactGroupKey(r));
    return {...r, referenceScore: group?.score ?? null, matchedGroupId: group?.id ?? null};
  });
  allRows = new Map([...data.cutoffs, ...data.plans, ...data.majorCutoffs].map(r => [r.id, r]));
  saved = new Set([...saved].filter(id => allRows.has(id)));
  const batches=[...new Set([...data.plans,...data.majorCutoffs].map(r=>r.batch))].filter(b=>b&&!['本科普通批','高职高专普通批'].includes(b));
  for(const batch of batches){const option=document.createElement('option');option.value=batch;option.textContent=batch;$('batch').appendChild(option);}
  const rounds=[...new Set(data.majorCutoffs.map(r=>r.round || '未注明轮次'))].filter(r=>!['首轮','第一次征集','第二次征集','第三次征集','第四次征集'].includes(r));
  for(const round of rounds){const option=document.createElement('option');option.value=round;option.textContent=round;$('round').appendChild(option);}
  updateSavedCount();
  renderCoverage(); renderSources(); renderSpecial(); render();
  document.documentElement.dataset.ready = 'true';
}
function options() {
  return { track:$('track').value, query:$('query').value, batch:$('batch').value,
    kind:$('kind').value, reference:reference.score, band:$('band').value,
    subjects:view === 'plans' ? [...document.querySelectorAll('input[name=subject]:checked')].map(e => e.value) : [],
    onlyVerifiedSubjects:view === 'plans' && $('verified-subjects').checked,
    includeUnknown:$('unknown').checked, savedOnly:$('saved-only').checked, saved };
}
function updateReference() {
  const mode = $('mode').value;
  reference = getReference($('value').value, mode, $('track').value, data.ranks);
  $('value-label').textContent = mode === 'rank' ? '参考位次' : '高考总分';
  $('value').min = mode === 'rank' ? '1' : '0';
  if (mode === 'rank') $('value').removeAttribute('max'); else $('value').max = '750';
  $('value').placeholder = mode === 'rank' ? '例如 20000' : '例如 550';
  $('reference-note').classList.toggle('invalid', !!reference.error);
  $('value').setAttribute('aria-invalid', reference.error ? 'true' : 'false');
  if (reference.error) $('reference-note').textContent = reference.error;
  else if (reference.empty) $('reference-note').textContent = '不填分数也可以浏览。分数须按 2026 年口径；跨年优先结合位次比较。';
  else {
    const rank = reference.rank;
    $('reference-note').innerHTML = `<strong>${reference.fromRank ? '对应 2026 参考分' : '2026 参考分'} ${h(reference.score)}</strong><br>${rank ? `同分名次 ${fmt(rank.rankStart)}–${fmt(rank.rankEnd)}` : '该分数没有公开名次区间，不作推算。'}<br><span>一分一档口径：总成绩＋全国性加分。地方性加分需另核。</span>`;
  }
}
function render() {
  if (!data || !['cutoffs','plans','majorCutoffs'].includes(view)) return;
  updateReference();
  const isPlan = view === 'plans', isMajor = view === 'majorCutoffs';
  $('round-field').hidden = isPlan;
  $('subjects-field').hidden = !isPlan;
  $('result-title').textContent = isPlan ? '专业招生计划' : isMajor ? '专业实际录取分数' : '院校专业组';
  const rows = view === 'cutoffs' ? data.cutoffs.filter(r => r.round === $('round').value) : isMajor ? data.majorCutoffs.filter(r=>(r.round || '未注明轮次')===$('round').value) : data[view];
  filtered = reference.error ? [] : filterRows(rows, options());
  const sort = $('sort').value;
  const scoreOf = r => r.referenceScore ?? r.score ?? null;
  filtered.sort((a,b) => {
    if (sort === 'school') return a.school.localeCompare(b.school,'zh-CN') || (a.major || a.group || '').localeCompare(b.major || b.group || '','zh-CN');
    const x = scoreOf(a), y = scoreOf(b);
    if (x === null && y === null) return a.school.localeCompare(b.school,'zh-CN');
    if (x === null) return 1; if (y === null) return -1;
    if (sort === 'distance' && reference.score !== null) return Math.abs(x-reference.score)-Math.abs(y-reference.score) || y-x;
    return sort === 'score-asc' ? x-y : y-x;
  });
  const total = Math.max(1,Math.ceil(filtered.length/PAGE_SIZE)); page = Math.max(1,Math.min(page,total));
  const schoolCount = new Set(filtered.map(r => r.schoolCode || r.school)).size;
  $('result-count').textContent = `找到 ${fmt(filtered.length)} 条记录 · ${fmt(schoolCount)} 个院校条目`;
  $('current-summary').textContent = `${YEAR} · ${$('track').value}类 · ${$('batch').selectedOptions[0].textContent}${!isPlan ? ` · ${$('round').selectedOptions[0].textContent}` : ''}`;
  $('result-notice').innerHTML = isPlan
    ? '<strong>专业计划为部分覆盖。</strong> 已关联的分数仅是同专业组首次投档线；未匹配组码的计划不分配分数。招生人数是本条计划人数，不能理解为全校总计划。'
    : isMajor
    ? '<strong>这里展示高校公开的具体专业录取最低分，现为部分覆盖。</strong> 左侧“投档轮次”可切换首轮、征集或高校录取汇总；汇总不能当作首轮。未公布组码不猜测。'
    : `<strong>专业组线 ≠ 专业录取线。</strong> 专业关键词只搜索已核实组码的已收录计划。${$('round').value === '首轮' ? '分数为空表示原表无出档考生。' : '正在查看征集投档，与首次投档分开比较。'}`;
  if (!filtered.length) $('results-list').innerHTML = `<div class="empty-state"><strong>${reference.error ? '请先修正输入' : '当前条件下没有结果'}</strong><p>${reference.error ? h(reference.error) : '试试清空关键词、放宽分差或切换“全部已收录批次”。'}</p><p class="tiny">未收录或未匹配专业计划，不代表该校没有招生。</p>${view==='cutoffs'&&$('query').value?'<button type="button" class="outline-button" data-search-plans>到专业计划中搜索</button>':''}</div>`;
  else $('results-list').innerHTML = filtered.slice((page-1)*PAGE_SIZE,page*PAGE_SIZE).map(r => card(r)).join('');
  $('prev').disabled = page <= 1; $('next').disabled = page >= total;
  $('page-status').textContent = `${page} / ${total} 页`;
}
function card(r) {
  const isPlan = view === 'plans', isMajor = view === 'majorCutoffs';
  const score = r.referenceScore ?? r.score ?? null;
  const diff = score !== null && reference.score !== null ? reference.score-score : null;
  let major = '';
  if (isPlan) {
    const status = subjectStatus(r, options().subjects);
    const subjects = r.subjectRule === 'unknown' || !r.subjectRule ? '选科要求待核实' : r.requiredSubjects?.length ? `${r.requiredSubjects.join(r.subjectRule === 'any' ? ' / ' : ' + ')}${r.subjectRule === 'any' ? '（任选一）' : '（须同时选）'}` : '再选科目不限';
    major = `<p class="record-major"><strong>${h(r.major)}</strong></p><p class="record-meta">计划 ${r.plannedCount !== null && r.plannedCount !== undefined ? h(r.plannedCount)+' 人' : '人数待核'} · ${h(subjects)}${status === 'unknown' ? ' · 条件未确认' : ''}<br>学费 ${r.tuition !== null && r.tuition !== undefined ? h(r.tuition) : '待核实'}${typeof r.tuition === 'number' ? ' 元/年' : ''} · 学制 ${r.duration ? h(r.duration) : '待核实'}</p>`;
  } else if (isMajor) major = `<p class="record-major"><strong>${h(r.major)}</strong></p>`;
  else major = r.joinedMajors?.length ? `<p class="record-major">已收录专业：${h([...new Set(r.joinedMajors)].slice(0,5).join('、'))}${r.joinedMajors.length > 5 ? '…' : ''}</p><p class="muted tiny">仅列已采集计划，不代表全组专业完整。</p>` : '<p class="record-major muted">组内专业计划尚未匹配，请查官方招生计划。</p>';
  return `<article class="result-card" data-record="${h(r.id)}"><div><div class="school-line"><h3 class="school-name">${h(r.school)}</h3>${r.group ? `<span class="group-tag">${h(r.group)} 组</span>` : '<span class="group-tag">组码待核</span>'}</div><p class="record-meta">${h(r.schoolCode || '代码待核')} · ${h(r.track)}类 · ${h(r.batch)}${r.round ? ' · '+h(r.round) : ''} · ${h(specialLabel(r))}</p>${major}${r.note ? `<p class="record-note">${h(r.note)}</p>` : ''}<div class="record-actions"><button type="button" data-detail="${h(r.id)}">查看详情</button><button type="button" data-save="${h(r.id)}" class="${saved.has(r.id)?'saved':''}" aria-pressed="${saved.has(r.id)}">${saved.has(r.id)?'已加备选':'＋ 加入备选'}</button>${sourceLinks(r)}</div></div><div class="score-box"><strong class="score ${score === null ? 'empty' : ''}">${score === null ? (isPlan ? '待匹配' : '未公布') : h(score)}</strong><div class="score-label">${isMajor ? '专业录取最低分' : isPlan ? '2026 首轮组线' : '2026 组投档线'}${isPlan ? '<br>不是专业录取分' : ''}</div>${diff !== null ? `<span class="diff ${diff<0?'negative':''}">${diff >= 0 ? '高于线 ' : '低于线 '}${Math.abs(diff)} 分</span>` : ''}</div></article>`;
}
function updateSavedCount() { $('saved-count').textContent = saved.size; $('export').textContent = saved.size ? `导出备选 (${saved.size})` : '导出备选'; }
function saveRow(id) {
  if (saved.has(id)) saved.delete(id); else saved.add(id);
  try { localStorage.setItem(STORE,JSON.stringify([...saved])); } catch { toast('本机存储不可用，备选仅保留到本次页面关闭。'); }
  updateSavedCount(); render();
}
function openDetail(id) {
  const r = allRows.get(id); if (!r) return;
  const group = r.matchedGroupId ? allRows.get(r.matchedGroupId) : null;
  const plans = r.round === '首轮' ? planIndex.get(exactGroupKey(r)) || [] : [];
  const rows = [['数据年份',r.year],['科类 / 批次',`${r.track}类 / ${r.batch}`],['专业组代码',r.group || '待核实'],['投档或录取轮次',r.round || '见高校来源说明'],['最低分',r.score ?? group?.score ?? '未公布 / 未匹配'],['分数口径',data.plans.some(p=>p.id===r.id) ? '同组首次投档线，不是专业录取线' : r.scoreType || '院校专业组投档最低分']];
  if (r.major) rows.push(['专业名称',r.major]);
  if (r.plannedCount !== undefined) rows.push(['计划人数',r.plannedCount ?? '待核实']);
  if (r.admittedCount !== undefined && r.admittedCount !== null) rows.push(['实际录取人数（不是计划数）',r.admittedCount]);
  $('detail-content').innerHTML = `<h2>${h(r.school)}${r.group?' · '+h(r.group)+' 组':''}</h2><div class="detail-grid">${rows.map(([k,v])=>`<div><span>${h(k)}</span><strong>${h(v)}</strong></div>`).join('')}</div>${r.note ? `<div class="notice">${h(r.note)}</div>` : ''}${r.major && r.requiredSubjects ? `<p>再选科目：${r.subjectRule === 'unknown' ? '待核实' : r.requiredSubjects.length ? h(r.requiredSubjects.join(r.subjectRule==='any'?' / ':' + ')) : '不限'}。学费：${h(r.tuition ?? '待核实')}；学制：${h(r.duration ?? '待核实')}。</p>` : ''}${r.round === '首轮' ? `<h3>已采集并匹配到本组的专业计划（${plans.length} 条）</h3><p class="tiny muted">目前是部分计划覆盖；填报前需确认全组专业及调剂范围。</p>${plans.length ? plans.map(p=>`<div class="detail-plan"><strong>${h(p.major)}</strong><p>计划 ${h(p.plannedCount ?? '待核实')} 人 · 学费 ${h(p.tuition ?? '待核实')} · 学制 ${h(p.duration ?? '待核实')}</p><p>${h(p.note || '')}</p>${sourceLinks(p)}</div>`).join('') : '<p>本组还没有可严格匹配的专业计划。请到官方计划系统或高校招生网站核对，不能用相似专业推断。</p>'}` : ''}<h3 style="margin-top:24px">来源与核验</h3>${sourceIds(r).map(id=>{const s=sourceMap.get(id);return s ? `<p>${sourceLink(id,s.title)}<br><span class="tiny muted">发布：${h(s.publishedAt || '原页未标日期')} · 采集：${h(s.accessedAt?.slice(0,10) || '未标')} ${r.sourceRow ? '· 原表数据行 '+h(r.sourceRow) : ''}</span></p>${s.notes?.length ? `<p class="tiny">${h(s.notes.join(' '))}</p>` : ''}` : '';}).join('')}${group ? `<p>组投档线来源：${sourceLinks(group)}</p>` : ''}<p class="help">院校章程中的体检、单科、外语语种、校区、调剂与资格限制仍须逐项核对。2026 年数据不能保证未来录取。</p>`;
  $('detail').showModal();
}
function exportSaved() {
  if (!saved.size) return toast('先把感兴趣的院校或专业加入备选。');
  const header=['年份','院校','院校代码','科类','批次','轮次','专业组','专业','计划人数','录取人数','分数','分数口径','备注','官方来源'];
  const rows=[...saved].map(id=>allRows.get(id)).filter(Boolean).map(r=>[r.year,r.school,r.schoolCode,r.track,r.batch,r.round,r.group,r.major,r.plannedCount,r.admittedCount,r.referenceScore??r.score,r.major && !r.matchedGroupId ? r.scoreType || '无已匹配分数' : '专业组投档线，不是专业录取分',r.note,sourceIds(r).map(id=>sourceMap.get(id)?.url || '').join(' | ')]);
  const blob=new Blob(['\uFEFF'+[header,...rows].map(row=>row.map(csvCell).join(',')).join('\r\n')],{type:'text/csv;charset=utf-8;'});
  const url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download='广西2026志愿备选.csv';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);toast(`已导出 ${rows.length} 条备选记录。`);
}
function renderCoverage() {
  const first=data.cutoffs.filter(r=>r.round==='首轮'), schools=new Set(first.map(r=>r.schoolCode)).size, planSchools=new Set(data.plans.map(r=>r.school)).size, majorSchools=new Set(data.majorCutoffs.map(r=>r.school)).size;
  $('coverage-strip').innerHTML=`<span><strong>${fmt(schools)}</strong>个首轮院校代码</span><span><strong>${fmt(first.length)}</strong>条首次投档记录</span><span><strong>${fmt(data.plans.length)}</strong>条专业计划</span><span class="gap">计划与专业录取线：部分覆盖</span>`;
  $('coverage-detail').innerHTML=`<div class="notice"><strong>覆盖边界：</strong>普通批投档表按已列官方原表完整采集；分专业计划、专业实际录取线及特殊通道广西证据仍有缺口，本站不是全专业完整数据库。</div><table class="coverage-table"><thead><tr><th>资料</th><th>已收录</th><th>范围</th></tr></thead><tbody><tr><td>普通批首次投档</td><td>${fmt(first.length)} 条 / ${fmt(schools)} 个院校代码</td><td>本科、高职高专；物理、历史</td></tr><tr><td>普通批征集投档</td><td>${fmt(data.cutoffs.length-first.length)} 条</td><td>按轮次分开，空分保持空值</td></tr><tr><td>分专业招生计划</td><td>${fmt(data.plans.length)} 条 / ${planSchools} 校</td><td><strong>部分覆盖</strong>，不是全区完整招生计划</td></tr><tr><td>专业实际录取分</td><td>${fmt(data.majorCutoffs.length)} 条 / ${majorSchools} 校</td><td><strong>部分覆盖</strong>，以高校公布的口径为准</td></tr><tr><td>一分一档</td><td>${fmt(data.ranks.length)} 个分数档</td><td>物理、历史；全国性加分口径</td></tr><tr><td>强基与竞赛通道</td><td>${data.special.filter(p=>p.type==='strong-foundation').length} 校强基 + ${data.special.filter(p=>p.type!=='strong-foundation').length} 个其他项目</td><td>全国目录与广西可报状态分开标注</td></tr></tbody></table><p class="help">当前数据采集日期：2026-09-10。计划已收录学校：${h([...new Set(data.plans.map(r=>r.school))].sort((a,b)=>a.localeCompare(b,'zh-CN')).join('、') || '正在整理')}。</p>`;
}
function renderSources() {
  $('sources-list').innerHTML=data.sources.map(s=>`<article class="source-row">${sourceLink(s.id,s.title)}<small>${h(s.publisher || '官方公开来源')} · 发布 ${h(s.publishedAt || '未标日期')} · 采集 ${h(s.accessedAt?.slice(0,10)||'未标')} ${s.recordCount!==undefined?'· '+h(s.recordCount)+' 条记录':''}</small><details><summary>采集与校验信息</summary><p>${h(s.method || s.verification || '官方公开来源，详见原页')} ${h(s.note || '')}</p>${s.sha256 ? `<p>原始文件 SHA-256：<code>${h(s.sha256)}</code></p>` : '<p>未归档原文件哈希，仅保留官方页面引用。</p>'}</details></article>`).join('');
}
function specialScoreDetails(program) {
  return (program.scoreRecords || []).map(score => `<div class="detail-plan"><strong>${h(score.major || '')}：${h(score.score)} 分</strong><p>${h(score.scoreLabel || '分数口径待核实')}${score.maxScore ? ' · '+h(score.maxScore)+' 分制' : ' · 满分口径待核实'}</p><p>计算口径：${h(score.formula || '公式尚未核实，请查看官方原文；不跨分制比较')}</p><p>${h(score.note || '')}</p><p>${(score.sourceIds || []).map(id=>sourceLink(id,'该项分数来源 ↗')).join(' · ')}</p></div>`).join('');
}
function renderSpecial() {
  if (!data) return;
  const policies=Array.isArray(data.policies)?data.policies:[];
  $('special-policy').innerHTML=`<div class="policy-box"><h3>先分清这几条路</h3><p>强基一般类、竞赛破格、奥赛保送和少年／英才项目各有独立条件。奖项并不自动获得降分、保送或录取资格。2026 年是否保留竞赛破格，以每校当年简章为准。</p><p>强基的高考入围分、加权入围成绩与综合录取成绩不能互相比较，也不参与左侧普通批分数筛选。</p><details><summary>查看 ${policies.length} 条招生规则与竞赛政策</summary>${policies.map(p=>`<p><strong>${h(p.title || p.name || '')}</strong> ${h(p.summary || p.description || '')} ${(p.sourceIds || (p.sourceId?[p.sourceId]:[])).map(id=>sourceLink(id,'政策原文 ↗')).join(' · ')}</p>`).join('')}</details></div>`;
  const q=$('special-query').value.trim().toLowerCase(), status=$('special-status').value;
  const programs=data.special.filter(p=>(status==='all'||p.guangxiStatus===status)&&(!q||JSON.stringify([p.school,p.type,p.title,p.majors,p.summary]).toLowerCase().includes(q)));
  $('special-count').textContent=`${programs.length} 个项目 · 广西可报状态按逐校证据标注`;
  const labels={confirmed:'已确认面向广西',unknown:'广西范围待核实',excluded:'已确认不面向广西'};
  $('special-list').innerHTML=programs.length?programs.map(p=>`<article class="special-card"><h3>${h(p.school || p.title)}</h3><span class="status-label ${h(p.guangxiStatus || 'unknown')}">${h(labels[p.guangxiStatus] || labels.unknown)}</span><p><strong>${h(programType(p.type))}</strong>${p.title && p.school && p.title!==p.school ? ' · '+h(p.title) : ''}</p>${p.majors?.length?`<p>${p.majorsScope==='guangxi'?'广西专业':'全国简章专业'}：${h(Array.isArray(p.majors)?p.majors.join('、'):p.majors)}</p><p class="tiny muted">广西具体投放专业与选科须查分省计划。</p>`:''}<p>${h(p.summary || '')}</p><details><summary>资格、广西证据与分数口径</summary><p>报名条件：${h(p.eligibility || '请核对当年高校简章。')}</p><p>选科：${h(p.subjectRequirements || '请核对分专业要求。')}</p><p>竞赛通道：${h(p.competitionRoute || '未核实，不推定可破格或保送。')}</p><p>广西证据：${h(p.guangxiEvidence || '当前未获取足够证据。')}</p><p>广西计划：${p.planCount!==null && p.planCount!==undefined?h(p.planCount)+' 人':'未公开或未核实'}</p><p>2026 报名时间：${h(p.deadline || '见当年简章（已结束）')}</p>${p.scoreRecords?.length ? specialScoreDetails(p) : '<p>广西入围／综合录取分：未收录；不以普通批线代替。</p>'}${p.evidenceGaps?.length?`<p>证据缺口：${h(p.evidenceGaps.join('；'))}</p>`:''}<p>${sourceLinks(p)}</p></details><a href="${h(safeUrl(p.officialUrl || sourceMap.get(sourceIds(p)[0])?.url))}" target="_blank" rel="noopener noreferrer">查看官方简章 ↗</a></article>`).join(''):'<div class="empty-state">当前没有匹配项目，试试清空关键词或切换状态。</div>';
}
function changeView(next) {
  if (!data) return;
  view=next;page=1;
  if(view==='cutoffs'&&!data.cutoffs.some(r=>r.round===$('round').value))$('round').value='首轮';
  document.querySelectorAll('[data-view]').forEach(b=>{const active=b.dataset.view===view;b.classList.toggle('active',active);if(active)b.setAttribute('aria-current','page');else b.removeAttribute('aria-current');});
  $('query-layout').hidden=['special','sources'].includes(view);$('special-view').hidden=view!=='special';$('sources-view').hidden=view!=='sources';
  if (view==='special') renderSpecial(); else render();
}
document.querySelectorAll('[data-view]').forEach(b=>b.addEventListener('click',()=>changeView(b.dataset.view)));
$('filters').addEventListener('submit',e=>e.preventDefault());
$('filters').addEventListener('input',e=>{
  if(e.target.name==='subject' && document.querySelectorAll('input[name=subject]:checked').length>2){e.target.checked=false;toast('再选科目最多选择两门。');return;}
  page=1;render();
});
$('mode').addEventListener('change',()=>{$('value').value='';page=1;render();});
$('query').addEventListener('input',()=>{page=1;render();});
$('sort').addEventListener('change',()=>{page=1;render();});
$('reset').addEventListener('click',()=>{$('filters').reset();$('query').value='';$('sort').value='distance';page=1;render();});
$('prev').addEventListener('click',()=>{page--;render();$('results').scrollIntoView({block:'start'});});
$('next').addEventListener('click',()=>{page++;render();$('results').scrollIntoView({block:'start'});});
$('results-list').addEventListener('click',e=>{const detail=e.target.closest('[data-detail]'),save=e.target.closest('[data-save]');if(detail)openDetail(detail.dataset.detail);if(save)saveRow(save.dataset.save);if(e.target.closest('[data-search-plans]'))changeView('plans');});
$('close-detail').addEventListener('click',()=>$('detail').close());
$('detail').addEventListener('click',e=>{if(e.target===$('detail')){const r=$('detail').getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)$('detail').close();}});
$('export').addEventListener('click',exportSaved);
$('special-query').addEventListener('input',renderSpecial);$('special-status').addEventListener('change',renderSpecial);
$('reload').addEventListener('click',()=>location.reload());

const names={cutoffs:'cutoffs',plans:'plans',majorCutoffs:'major-cutoffs',ranks:'ranks',special:'special-programs',sources:'sources',policies:'policies'};
Promise.all(Object.entries(names).map(async([key,file])=>{const response=await fetch(new URL(`./data/${file}.json`,import.meta.url));if(!response.ok)throw new Error(`${file}: HTTP ${response.status}`);const records=await response.json();if(!Array.isArray(records))throw new Error(`${file}: 数据格式错误`);return [key,records];}))
  .then(entries=>{data=Object.fromEntries(entries);initialize();})
  .catch(error=>{$('data-error').hidden=false;$('query-layout').hidden=true;$('coverage-strip').textContent='数据载入未完成，请刷新重试。';$('error-detail').textContent=error.message;document.documentElement.dataset.ready='error';});
