import test from 'node:test';
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { readFile } from 'node:fs/promises';

test('页面及新增模块依赖使用内容版本号，避免旧缓存缺失导出导致白屏',async()=>{
  const [html,app,coverage]=await Promise.all(['index.html','app.js','coverage.js'].map(name=>readFile(new URL(`../site/${name}`,import.meta.url),'utf8')));
  const hash=text=>createHash('sha256').update(text).digest('hex').slice(0,12);
  const moduleVersion=app.match(/from '\.\/coverage\.js\?v=([a-f0-9]+)'/);
  assert.ok(moduleVersion,'app 必须显式刷新有新导出的 coverage 模块');
  assert.equal(moduleVersion[1],hash(coverage));
  const appVersion=html.match(/src="\.\/app\.js\?v=([a-f0-9]+)"/);
  assert.ok(appVersion);
  assert.equal(appVersion[1],hash(app));
});

test('所有实际加载数据的内容共同决定DATA_VERSION，提交版本须与当前12个文件一致',async()=>{
  const app=await readFile(new URL('../site/app.js',import.meta.url),'utf8');
  const names=Object.values(JSON.parse(app.match(/const names=(\{[^\n]+\});/)[1]));
  assert.equal(names.length,12);
  const hash=createHash('sha256');
  for(const name of names.map(name=>`${name}.json`).sort()){
    hash.update(name);hash.update('\0');
    hash.update(await readFile(new URL(`../site/data/${name}`,import.meta.url)));
    hash.update('\0');
  }
  assert.equal(app.match(/const DATA_VERSION = '([a-f0-9]{64})';/)[1],hash.digest('hex'),'修改数据后必须生成新的共同数据版本');
});

test('任一数据文件内容或身份变化都会改变共同版本，清单顺序不影响版本',async()=>{
  const {dataVersion}=await import('../scripts/update-asset-versions.mjs');
  const entries=[['plans.json',Buffer.from('[{"id":"old-plan"}]')],['major-cutoffs.json',Buffer.from('[{"score":600}]')]];
  const before=dataVersion(entries);
  assert.equal(dataVersion([...entries].reverse()),before);
  assert.notEqual(dataVersion([['plans.json',Buffer.from('[{"id":"new-plan"}]')],entries[1]]),before);
  assert.notEqual(dataVersion([entries[0],['major-cutoffs.json',Buffer.from('[{"score":601}]')]]),before);
  assert.notEqual(dataVersion([['supplementary-plans.json',entries[0][1]],entries[1]]),before);
});
