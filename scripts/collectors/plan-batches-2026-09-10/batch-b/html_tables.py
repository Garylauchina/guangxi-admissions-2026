#!/usr/bin/env python3
"""Rebuild 2026 Guangxi major admission outcomes from saved official HTML.

This parser expands HTML rowspan/colspan rather than carrying the last school or
group name over arbitrary rows. It reads only specified aggregate public tables.

This file is a shared parser and Yulin-specific helper. To rebuild the complete
five-school delivery, run collect-additional-major.py, which imports this file.
"""
import collections
import datetime as dt
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent


def clean(value):
    return re.sub(r"\s+", " ", value).strip()


class Tables(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tables = []
        self.table = None
        self.row = None
        self.cell = None

    def handle_starttag(self, tag, attrs):
        if tag == "table":
            assert self.table is None, "Nested tables require review"
            self.table = []
        if tag == "tr" and self.table is not None:
            self.row = []
        if tag in ("td", "th") and self.row is not None:
            self.cell = {"text": "", "attrs": dict(attrs)}
        if tag == "br" and self.cell is not None:
            self.cell["text"] += " "

    def handle_data(self, value):
        if self.cell is not None:
            self.cell["text"] += value

    def handle_endtag(self, tag):
        if tag in ("td", "th") and self.cell is not None:
            self.cell["text"] = clean(self.cell["text"])
            self.row.append(self.cell)
            self.cell = None
        if tag == "tr" and self.row is not None:
            self.table.append(self.row)
            self.row = None
        if tag == "table" and self.table is not None:
            self.tables.append(self.table)
            self.table = None


def expand(rows):
    cells = {}
    for row_index, row in enumerate(rows):
        col_index = 0
        for cell in row:
            while (row_index, col_index) in cells:
                col_index += 1
            rowspan = int(cell["attrs"].get("rowspan", 1))
            colspan = int(cell["attrs"].get("colspan", 1))
            for offset_r in range(rowspan):
                for offset_c in range(colspan):
                    location = (row_index + offset_r, col_index + offset_c)
                    assert location not in cells, (location, "overlapping merged cell")
                    cells[location] = cell["text"]
            col_index += colspan
    width = max(col for row, col in cells) + 1
    return [[cells.get((row, col), "") for col in range(width)] for row in range(len(rows))]

class NestedTables(HTMLParser):
    """Keep each nested table independent; only explicitly matched data headers are used."""
    def __init__(self):
        super().__init__(convert_charrefs=True);self.tables=[];self.stack=[]
    def handle_starttag(self,tag,attrs):
        if tag=='table':self.stack.append({'table':[],'row':None,'cell':None});return
        if not self.stack:return
        state=self.stack[-1]
        if tag=='tr':state['row']=[]
        if tag in ('td','th') and state['row'] is not None:state['cell']={'text':'','attrs':dict(attrs)}
        if tag=='br' and state['cell'] is not None:state['cell']['text']+=' '
    def handle_data(self,value):
        if self.stack and self.stack[-1]['cell'] is not None:self.stack[-1]['cell']['text']+=value
    def handle_endtag(self,tag):
        if not self.stack:return
        state=self.stack[-1]
        if tag in ('td','th') and state['cell'] is not None:
            state['cell']['text']=clean(state['cell']['text']);state['row'].append(state['cell']);state['cell']=None
        if tag=='tr' and state['row'] is not None:state['table'].append(state['row']);state['row']=None
        if tag=='table':self.tables.append(state['table']);self.stack.pop()
