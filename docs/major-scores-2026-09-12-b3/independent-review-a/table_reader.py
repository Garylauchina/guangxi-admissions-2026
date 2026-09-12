"""Independent standard-library HTML table reader, including row/column spans."""
from html.parser import HTMLParser
import re
class Tables(HTMLParser):
 def __init__(self):super().__init__();self.tables=[];self.stack=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=='table':
   tab={'rows':[]};self.tables.append(tab);self.stack.append(tab)
  elif self.stack:
   tab=self.stack[-1]
   if tag=='tr':tab['row']=[];tab['rows'].append(tab['row'])
   elif tag in ('td','th'):
    cell={'text':[],'rowspan':int(a.get('rowspan',1)),'colspan':int(a.get('colspan',1))};tab['cell']=cell
    if 'row' not in tab:tab['row']=[];tab['rows'].append(tab['row'])
    tab['row'].append(cell)
 def handle_endtag(self,tag):
  if tag=='table' and self.stack:self.stack.pop()
  elif tag in ('td','th') and self.stack:self.stack[-1].pop('cell',None)
 def handle_data(self,data):
  if self.stack and 'cell' in self.stack[-1]:self.stack[-1]['cell']['text'].append(data)
 def expanded(self):
  out=[]
  for tab in self.tables:
   grid={};rows=[]
   for y,row in enumerate(tab['rows']):
    x=0
    for cell in row:
     while (y,x) in grid:x+=1
     value=re.sub(r'\s+','', ''.join(cell['text']))
     for dy in range(cell['rowspan']):
      for dx in range(cell['colspan']):grid[y+dy,x+dx]=value
     x+=cell['colspan']
    if grid:
     width=max((xx for yy,xx in grid if yy==y),default=-1)+1
     rows.append([grid.get((y,xx),'') for xx in range(width)])
   out.append(rows)
  return out

def tables(text):
 t=Tables();t.feed(text);return t.expanded()
