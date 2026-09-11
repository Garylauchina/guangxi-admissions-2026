#!/usr/bin/env python3
"""Extract the single official Guangxi brochure locally; requires pypdf."""
from pathlib import Path
from pypdf import PdfReader
R=Path(__file__).resolve().parent
p=R/'raw/bnu-gx-2026-brochure.pdf';doc=PdfReader(p)
assert len(doc.pages)==1
p.with_suffix('.txt').write_text('\n'.join(page.extract_text() for page in doc.pages))
print('Extracted one page. Output stays in non-public raw/.')
