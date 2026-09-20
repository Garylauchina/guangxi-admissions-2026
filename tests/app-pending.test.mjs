import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { JSDOM } from 'jsdom';
function openSchoolSubview(destination, code='10601', track='物理') {
  const $=id=>document.getElementById(id);
  const input=(id,value)=>{$(id).value=value;$(id).dispatchEvent(new window.Event('input',{bubbles:true}));};
  if($('detail').open)$('close-detail').click();
  document.querySelector('.tabs [data-view="cutoffs"]').click();$('reset').click();
  input('query',code);input('track',track);input('batch','all');input('kind','all');
  document.querySelector('#results-list [data-detail]').click();
  document.querySelector('#detail-content [data-destination="'+destination+'"]').click();
}

import { buildCoverage } from '../site/coverage.js';

async function mount(suffix, fetchRows) {
  const html=await readFile(new URL('../site/index.html',import.meta.url),'utf8');
  const dom=new JSDOM(html,{url:'https://example.test/'});
  const {window}=dom;
  globalThis.document=window.document;globalThis.window=window;globalThis.localStorage=window.localStorage;
  const requestedUrls=[];
  globalThis.fetch=async url=>{requestedUrls.push(new URL(url));return {ok:true,status:200,json:()=>fetchRows(url)};};
  window.HTMLElement.prototype.scrollIntoView=function(){};
  window.HTMLDialogElement.prototype.showModal=function(){this.open=true;};
  window.HTMLDialogElement.prototype.close=function(){this.open=false;};
  await import(`../site/app.js?${suffix}`);
  for(let i=0;i<200&&document.documentElement.dataset.ready===undefined;i++)await new Promise(resolve=>setTimeout(resolve,10));
  assert.equal(document.documentElement.dataset.ready,'true');
  const $=id=>document.getElementById(id);
  const input=(id,value,event='input')=>{$(id).value=value;$(id).dispatchEvent(new window.Event(event,{bubbles:true}));};
  return {dom,$,input,requestedUrls};
}

test('仅有年份冲突待核分的学校留在已核查缺口，记录与详情仍可查看',async()=>{
  const base={year:2026,track:'物理',batch:'本科普通批',sourceId:'official',group:'101',round:'首轮'};
  const row=(code,extra)=>({...base,schoolCode:code,school:`测试院校${code}`,...extra});
  const cutoffs=['10001','10002','10003','10004'].map(code=>row(code,{id:`group-${code}`,score:500}));
  const plans=[row('10001',{id:'plan-pending-school',major:'数学',plannedCount:1,subjectRule:'unknown'})];
  const majors=[
    row('10001',{id:'pending-only',conflictFields:['year'],major:'数学',score:510,scoreComparable:false,group:null,round:'轮次待核',scoreType:'专业录取最低分',note:'2026查询与2025页面配置不一致，年份冲突待核。'}),
    row('10002',{id:'mixed-pending',major:'化学',score:520,scoreComparable:false}),
    row('10002',{id:'mixed-valid',major:'物理学',score:530,scoreComparable:true}),
  ];
  const auditStatuses=['access-limited','prior-year-only','reviewed-gap','other-route-only','outcome-without-scores','schedule-only'];
  const notes=auditStatuses.map((status,i)=>row('10003',{id:`audit-${i}`,auditKind:'major-scores',checkedAt:'2026-09-12',status,note:'本次检查范围有限。'}));
  notes.push(row('10004',{id:'plan-audit',checkedAt:'2026-09-12',status:'source-found',note:'仅核查招生计划。'}));
  const payload={
    cutoffs,plans,'major-cutoffs':majors,'school-coverage':buildCoverage({cutoffs,plans,majorCutoffs:majors}),
    'school-audit-notes':notes,sources:[{id:'official',title:'学校官方来源',url:'https://example.edu.cn/admissions',accessedAt:'2026-09-12'}],
    'group-admission-scores':[row('10004',{id:'whole-group',province:'广西',score:515,scoreType:'专业组录取最低分',evidenceScope:'official-group-summary',roundScope:'annual',round:'录取汇总（轮次未分）'})],
  };
  const {dom,$,input,requestedUrls}=await mount('pending-only-fixture',async url=>payload[new URL(url).pathname.split('/').at(-1).replace('.json','')]||[]);
  assert.equal(requestedUrls.length,13,'全部实际JSON请求都需要共同版本');
  assert.equal(document.querySelectorAll('.tabs [data-view="plans"],.tabs [data-view="majorCutoffs"]').length,0);
  const complete=document.querySelector('[data-record="group-10004"]');
  assert.equal(complete.querySelector('.filing-score .score').textContent,'500');
  assert.equal(complete.querySelector('.admission-score .score').textContent,'515');
  assert.match(complete.textContent,/2026年投档线.*2026年最低录取分.*全年录取汇总/);
  assert.equal(document.querySelector('[data-record="group-10002"] .admission-score .score').textContent,'待补齐','部分专业分不能冒充完整组录取分');
  assert.equal(new Set(requestedUrls.map(url=>url.searchParams.get('v'))).size,1);
  assert.ok(requestedUrls.every(url=>/^[a-f0-9]{64}$/.test(url.searchParams.get('v')||'')),'不允许无版本JSON请求混入旧缓存');
  assert.match($('coverage-strip').textContent,/4个目标院校代码.*1个已有可比较专业分.*2个已核查仍缺可比较分.*1个待核查专业分/);
  assert.match($('major-review-note').textContent,/已核查 3 个院校代码/);
  assert.match($('major-review-note').textContent,/1 条可比较专业录取分.*2 条原文待核.*1 校仅有待核记录/);
  input('query','10001');document.querySelector('[data-detail]').click();
  assert.match($('detail-content').textContent,/0 条可比较专业录取分、1 条原文待核/);
  assert.match($('detail-content').textContent,/已核查但尚无可比较专业分/);
  const embedded=document.querySelector('[data-embedded-record="pending-only"]');
  assert.ok(embedded);assert.match(embedded.textContent,/原文待核（不参与比较）/);
  assert.equal(document.querySelector('#detail-content [data-destination="majorCutoffs"]').textContent,'查看待核专业分');
  document.querySelector('#detail-content [data-destination="majorCutoffs"]').click();
  assert.equal(document.querySelectorAll('.result-card').length,1);
  assert.equal(document.querySelector('.score').textContent,'原文待核');
  assert.match($('results-list').textContent,/2026查询与2025页面配置不一致/);
  document.querySelector('[data-detail]').click();assert.match($('detail-content').textContent,/检索年份（原文年份冲突待核）/);$('close-detail').click();
  $('unknown').checked=false;$('unknown').dispatchEvent(new window.Event('input',{bubbles:true}));
  assert.equal(document.querySelectorAll('.result-card').length,0);
  document.querySelector('[data-view="gaps"]').click();
  input('gap-query','10001');
  input('gap-status','major-collected','change');assert.equal(document.querySelectorAll('.gap-card').length,0);
  input('gap-status','major-not-reviewed','change');assert.equal(document.querySelectorAll('.gap-card').length,0);
  for(const status of ['no-majors','major-reviewed-gap','major-pending-only']){
    input('gap-status',status,'change');assert.equal(document.querySelectorAll('.gap-card').length,1,status);
  }
  const metrics=Object.fromEntries([...document.querySelectorAll('.gap-metrics > div')].map(el=>[el.querySelector('dt').textContent,el.querySelector('dd').textContent]));
  assert.equal(metrics['可比较专业录取分'],'0 条');assert.equal(metrics['原文待核专业分'],'1 条');
  assert.match($('gap-list').textContent,/该校已核查，但尚无可比较专业录取分/);
  document.querySelector('#gap-list [data-destination="majorCutoffs"]').click();
  assert.equal(document.querySelector('.score').textContent,'原文待核');
  openSchoolSubview('plans','10001');input('query','10001');document.querySelector('[data-detail]').click();
  assert.match($('detail-content').textContent,/0 条可比较专业录取分、1 条原文待核/);$('close-detail').click();
  document.querySelector('[data-view="gaps"]').click();input('gap-status','major-reviewed-gap','change');input('gap-query','10003');
  for(const label of ['官方入口访问受限','仅取得往年专业分','已核查，仍缺可比较专业分','仅取得其他招生通道资料','已公布录取进展，未提供专业分','仅取得录取日程信息'])assert.ok($('gap-list').textContent.includes(label),label);
  for(const status of auditStatuses)assert.ok(!$('gap-list').textContent.includes(status));
  dom.window.close();
});

test('真实库全部专业投档记录可由同校同科类详情展开且不混入实际分筛选',async()=>{
  const read=async url=>JSON.parse(await readFile(url,'utf8'));
  const [filing,cutoffs,plans]=await Promise.all(['major-filing-cutoffs','cutoffs','plans'].map(name=>read(new URL(`../site/data/${name}.json`,import.meta.url))));
  assert.ok(filing.some(r=>r.id.startsWith('p100a-')),'包含本轮新增记录');
  assert.ok(filing.some(r=>!r.id.startsWith('p100a-')),'包含先前归档记录');
  const {dom,$,input}=await mount('real-filing-detail',read);
  const groups=[...new Set(filing.map(r=>`${r.schoolCode}|${r.track}`))];
  const displayed=new Set();
  for(const key of groups){
    const [code,track]=key.split('|');
    document.querySelector('[data-view="cutoffs"]').click();$('reset').click();
    input('query',code);input('track',track);input('kind','all');input('batch','all');
    const cutoff=cutoffs.find(r=>r.schoolCode===code&&r.track===track);
    assert.ok(cutoff,`投档记录所属院校科类应有详情入口 ${key}`);
    input('round',cutoff.round);
    document.querySelector('[data-detail]').click();
    const panel=document.querySelector('.major-filing-panel');
    const expected=filing.filter(r=>r.schoolCode===code&&r.track===track);
    assert.match(panel.querySelector('summary').textContent,/专业投档分（不是实际专业录取分）/);
    assert.equal(panel.querySelector('details').open,false,'列表默认折叠');
    panel.querySelector('details').open=true;
    assert.equal(panel.querySelectorAll('[data-major-filing]').length,expected.length);
    for(const r of expected){
      const entry=[...panel.querySelectorAll('[data-major-filing]')].find(el=>el.dataset.majorFiling===r.id);
      assert.ok(entry);displayed.add(r.id);
      assert.ok(entry.textContent.includes(r.major));assert.ok(entry.textContent.includes(r.round));
      assert.ok(entry.querySelector('a[href^="https:"]')||entry.querySelector('a[href^="http:"]'));
      if(r.scoreComparable===false)assert.match(entry.textContent,/原文待核.*不参与比较/);
      else assert.ok(entry.textContent.includes(`${r.score} 分`));
    }
    $('close-detail').click();
  }
  assert.equal(displayed.size,filing.length,'所有原归档和新投档条目均有详情展示');
  const plan=plans.find(r=>groups.includes(`${r.schoolCode}|${r.track}`));
  assert.ok(plan);
  openSchoolSubview('plans',plan.schoolCode,plan.track);$('reset').click();input('query',plan.schoolCode);input('track',plan.track);input('kind','all');input('batch','all');
  document.querySelector('[data-detail]').click();assert.ok(document.querySelector('.major-filing-panel'));$('close-detail').click();
  openSchoolSubview('majorCutoffs');$('reset').click();input('query','14127');input('kind','all');input('batch','all');
  assert.equal(document.querySelectorAll('.result-card').length,0,'投档记录不能充当实际专业分');
  dom.window.close();
});
