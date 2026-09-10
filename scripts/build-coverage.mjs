import { readFile, writeFile } from 'node:fs/promises';
import { buildCoverage } from '../site/coverage.js';
const root = new URL('../', import.meta.url);
const [cutoffs, plans, majorCutoffs] = await Promise.all(['cutoffs', 'plans', 'major-cutoffs'].map(async name => JSON.parse(await readFile(new URL(`site/data/${name}.json`, root), 'utf8'))));
const rows = buildCoverage({cutoffs, plans, majorCutoffs});
await writeFile(new URL('site/data/school-coverage.json', root), JSON.stringify(rows));
console.log(JSON.stringify({schoolEntries: rows.length, withPlans: rows.filter(r => r.plans).length, withMajorCutoffs: rows.filter(r => r.majorCutoffs).length, groupsWithPlans: rows.reduce((n,r) => n+r.groupsWithPlans, 0)}));
