import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { readFile, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

const sha = content => createHash('sha256').update(content).digest('hex');

// The same release key is used for every fetched JSON file. Include sorted file
// names and exact bytes, separated by NUL, so any dataset change refreshes all.
export function dataVersion(entries) {
  const hash = createHash('sha256');
  for (const [name, content] of [...entries].sort(([a], [b]) => a.localeCompare(b, 'en'))) {
    hash.update(name).update('\0').update(content).update('\0');
  }
  return hash.digest('hex');
}

export function fetchedDataFiles(app) {
  const match = app.match(/const names=(\{[^\n]+\});/);
  assert.ok(match, 'Missing JSON-compatible names map in app.js.');
  const names = Object.values(JSON.parse(match[1]));
  assert.ok(names.length && names.every(name => /^[a-z][a-z-]*$/.test(name)), 'Unexpected data filename.');
  assert.equal(new Set(names).size, names.length, 'Duplicate data filenames.');
  return names.map(name => `${name}.json`);
}

export async function assetVersions(root = new URL('../site/', import.meta.url)) {
  const [app, html, coverage] = await Promise.all(['app.js', 'index.html', 'coverage.js'].map(name => readFile(new URL(name, root), 'utf8')));
  const files = fetchedDataFiles(app);
  const entries = await Promise.all(files.map(async name => [name, await readFile(new URL(`data/${name}`, root))]));
  const version = dataVersion(entries);
  const coverageVersion = sha(coverage).slice(0, 12);
  assert.match(app, /const DATA_VERSION = '[a-f0-9]{64}';/, 'Missing DATA_VERSION assignment.');
  assert.match(app, /from '\.\/coverage\.js\?v=[a-f0-9]+'/, 'Missing versioned coverage import.');
  assert.match(html, /src="\.\/app\.js\?v=[a-f0-9]+"/, 'Missing versioned app script.');
  const updatedApp = app
    .replace(/const DATA_VERSION = '[a-f0-9]{64}';/, `const DATA_VERSION = '${version}';`)
    .replace(/from '\.\/coverage\.js\?v=[a-f0-9]+'/, `from './coverage.js?v=${coverageVersion}'`);
  const appVersion = sha(updatedApp).slice(0, 12);
  const updatedHtml = html.replace(/src="\.\/app\.js\?v=[a-f0-9]+"/, `src="./app.js?v=${appVersion}"`);
  return { files, version, coverageVersion, appVersion, app, html, updatedApp, updatedHtml };
}

async function main() {
  assert.ok(process.argv.slice(2).every(arg => arg === '--check'), 'Usage: node scripts/update-asset-versions.mjs [--check]');
  const check = process.argv.includes('--check');
  const versions = await assetVersions();
  if (check) {
    assert.equal(versions.app, versions.updatedApp, 'Data or coverage version is stale; run node scripts/update-asset-versions.mjs after all data builds.');
    assert.equal(versions.html, versions.updatedHtml, 'App version is stale; run node scripts/update-asset-versions.mjs after all data builds.');
  } else {
    // Update dependencies before the parent module's content version.
    if (versions.app !== versions.updatedApp) await writeFile(new URL('../site/app.js', import.meta.url), versions.updatedApp);
    if (versions.html !== versions.updatedHtml) await writeFile(new URL('../site/index.html', import.meta.url), versions.updatedHtml);
  }
  console.log(JSON.stringify({ mode: check ? 'checked' : 'updated', files: versions.files.length, dataVersion: versions.version, coverageVersion: versions.coverageVersion, appVersion: versions.appVersion }, null, 2));
}
if (process.argv[1] && pathToFileURL(resolve(process.argv[1])).href === import.meta.url) await main();
