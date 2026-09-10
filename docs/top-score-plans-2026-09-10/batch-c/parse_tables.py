"""Read public HTML tables, preserving explicit rowspan/colspan semantics."""
from html.parser import HTMLParser
from pathlib import Path
import json,re

def clean(s):return re.sub(r'\s+',' ',s).strip()
class Tables(HTMLParser):
    def __init__(self):
        super().__init__();self.tables=[];self.depth=0;self.rows=[];self.row=None;self.cell=None;self.text=[];self.context=''
    def handle_starttag(self,t,attrs):
        a=dict(attrs)
        if t=='table':
            self.depth+=1
            if self.depth==1:self.rows=[];self.context=' '.join(self.text[-20:])[-500:]
        if self.depth!=1:return
        if t=='tr':self.row=[]
        if t in ['td','th']:self.cell={'text':[],'rowspan':int(a.get('rowspan',1)),'colspan':int(a.get('colspan',1))}
        if t in ['br','p'] and self.cell is not None:self.cell['text'].append(' ')
    def handle_data(self,s):
        if s.strip():self.text.append(s.strip())
        if self.depth==1 and self.cell is not None:self.cell['text'].append(s)
    def handle_endtag(self,t):
        if self.depth==1 and t in ['td','th'] and self.cell is not None:
            self.cell['text']=clean(''.join(self.cell['text']))
            if self.row is not None:self.row.append(self.cell)
            self.cell=None
        if self.depth==1 and t=='tr' and self.row is not None:
            self.rows.append(self.row);self.row=None
        if t=='table':
            if self.depth==1:self.tables.append({'context':self.context,'rawRows':self.rows,'rows':expand(self.rows)})
            self.depth-=1

def expand(rows):
    cells={};out=[]
    for ri,row in enumerate(rows):
        ci=0
        for cell in row:
            while (ri,ci) in cells:ci+=1
            for rr in range(ri,ri+cell['rowspan']):
                for cc in range(ci,ci+cell['colspan']):cells[rr,cc]=cell['text']
            ci+=cell['colspan']
        width=max([cc for rr,cc in cells if rr==ri],default=-1)+1
        out.append([cells.get((ri,cc),'') for cc in range(width)])
    return out

def parse(path):
    p=Tables();p.feed(Path(path).read_text());return p.tables

