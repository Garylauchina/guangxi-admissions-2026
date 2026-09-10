#!/usr/bin/env python3
"""Expand merged HTML cells used by audit.py. Requires pandas and lxml."""
import io,json,pathlib
import pandas as pd
BASE=pathlib.Path(__file__).resolve().parent
def put(name,value):(BASE/'raw'/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
def tables(key):
    return [df.where(df.notna(),None).values.tolist() for df in pd.read_html(io.StringIO((BASE/'raw'/(key+'.html')).read_text()),flavor='lxml',header=None)]
for i,rows in enumerate(tables('ylu_cutoff_recheck')):put(f'ylu_cutoff_expanded-{i}.json',rows)
put('ylu_teacher_plan_expanded.json',tables('ylu_plan_recheck')[2])
put('gxtcm_charter.expanded-0.json',tables('gxtcm_charter')[0])
