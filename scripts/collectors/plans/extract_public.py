"""Expand official merged HTML tables and extract public PDF tables.

Image transcriptions are separate reviewed JSON artifacts, not inferred by this script.
"""
from collect import BASE
import json
import pandas as pd
import pdfplumber

for key in ['gxnun_plan', 'gxgc_plan']:
    tables = pd.read_html(BASE / 'raw' / f'{key}.html', flavor='lxml')
    assert len(tables) == 1
    tables[0].to_json(BASE / 'raw' / f'{key}.expanded-0.json', force_ascii=False, orient='values')

with pdfplumber.open(BASE / 'raw' / 'bbgu_plan_pdf.pdf') as pdf:
    tables = [p.extract_tables() for p in pdf.pages]
(BASE / 'raw' / 'bbgu_plan_pdf.tables.json').write_text(json.dumps(tables, ensure_ascii=False, indent=2))
