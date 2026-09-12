"""Create local-only PDF table intermediates required by build.py."""
from pathlib import Path
import json
import pdfplumber

root=Path(__file__).resolve().parent
with pdfplumber.open(root/'raw/11313-plans.pdf') as pdf:
    tables=[page.extract_table() for page in pdf.pages]
assert len(tables)==3
(root/'fjbu-tables.json').write_text(json.dumps(tables,ensure_ascii=False,indent=2)+'\n')
