import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, mkdir, readFile, writeFile, copyFile, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { spawnSync } from 'node:child_process';

test('导入末尾资料年份错误或必需文件缺失时，不覆盖任何已发布数据',async()=>{
  const root=await mkdtemp(join(tmpdir(),'admissions-import-'));
  try {
    for(const dir of ['scripts','site/data','input/cutoffs','input/plans','input/ranks','input/special'])await mkdir(join(root,dir),{recursive:true});
    await copyFile(new URL('../scripts/import-data.py',import.meta.url),join(root,'scripts/import-data.py'));
    const fixture={year:2026,id:'record',sourceId:'official'};
    const files={
      'cutoffs/sources.json':[{id:'official',url:'https://example.edu.cn/2026'}],
      'ranks/sources.json':[], 'cutoffs/cutoffs-all.json':[fixture],
      'plans/plans.json':[], 'cutoffs/major-cutoffs.json':[],
      'special/special-programs.json':[], 'special/policies.json':[{...fixture,id:'wrong',year:2025}],
    };
    for(const [file,value] of Object.entries(files))await writeFile(join(root,'input',file),JSON.stringify(value));
    await writeFile(join(root,'site/data/cutoffs.json'),'preserve this published snapshot');
    let result=spawnSync('python3',[join(root,'scripts/import-data.py'),join(root,'input')],{encoding:'utf8'});
    assert.notEqual(result.status,0);assert.match(result.stderr,/Wrong year|wrong year/);
    assert.equal(await readFile(join(root,'site/data/cutoffs.json'),'utf8'),'preserve this published snapshot');
    await rm(join(root,'input/plans/plans.json'));
    result=spawnSync('python3',[join(root,'scripts/import-data.py'),join(root,'input')],{encoding:'utf8'});
    assert.notEqual(result.status,0);assert.equal(await readFile(join(root,'site/data/cutoffs.json'),'utf8'),'preserve this published snapshot');
  } finally { await rm(root,{recursive:true,force:true}); }
});
