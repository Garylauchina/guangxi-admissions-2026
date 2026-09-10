#!/usr/bin/env python3
"""Extract only the explicitly headed 2026 Guangxi block from the official table."""
import hashlib,html,json,re
from html.parser import HTMLParser
from pathlib import Path

R=Path(__file__).resolve().parent

class Rows(HTMLParser):
    def __init__(self):super().__init__();self.rows=[];self.row=None;self.cell=None
    def handle_starttag(self,tag,attrs):
        if tag=='tr':self.row=[]
        elif tag in ('td','th') and self.row is not None:
            a=dict(attrs);self.cell={'text':'','rowspan':int(a.get('rowspan','1')),'colspan':int(a.get('colspan','1'))}
    def handle_data(self,data):
        if self.cell is not None:self.cell['text']+=data
    def handle_endtag(self,tag):
        if tag in ('td','th') and self.cell is not None:
            self.cell['text']=re.sub(r'\s+','',self.cell['text']);self.row.append(self.cell);self.cell=None
        elif tag=='tr' and self.row is not None:self.rows.append(self.row);self.row=None

def extract():
    raw=(R/'raw/huuc-score-2026.html').read_text()
    assert '2026年外省本科录取情况' in raw and '2026年08月14日' in raw
    parsed=Rows();parsed.feed(raw)
    starts=[i for i,row in enumerate(parsed.rows) if ''.join(c['text'] for c in row)=='2026广西本科录取情况']
    assert len(starts)==1;start=starts[0]
    header=[c['text'] for c in parsed.rows[start+1]]
    assert header==['科类','控制线','专业','最高分','最低分','线差','平均分'],header
    end=next(i for i in range(start+2,len(parsed.rows)) if ''.join(c['text'] for c in parsed.rows[i])=='2026海南本科录取情况')
    content=[(i,row) for i,row in enumerate(parsed.rows[start+2:end],start+2) if any(c['text'] for c in row)]
    assert len(content)==16
    expanded=[];carry={}
    for index,cells in content:
        output={};next_carry={}
        for col,(text,left) in carry.items():
            output[col]=text
            if left>1:next_carry[col]=(text,left-1)
        col=0
        for cell in cells:
            while col in output:col+=1
            for offset in range(cell['colspan']):
                output[col+offset]=cell['text']
                if cell['rowspan']>1:next_carry[col+offset]=(cell['text'],cell['rowspan']-1)
            col+=cell['colspan']
        carry=next_carry
        assert sorted(output)==list(range(7)),(index,output)
        expanded.append({'htmlRow':index+1,'cells':[output[i] for i in range(7)]})
    assert sum(x['cells'][0]=='物理类' for x in expanded)==15
    assert sum(x['cells'][0]=='历史类' for x in expanded)==1
    meta=json.loads((R/'raw/huuc-score-2026.meta.json').read_text())
    code_evidence=(R/'raw/huuc-school-code-evidence.html').read_bytes().decode('gb18030',errors='replace')
    assert re.search(r'11765[\s\S]{0,2000}河南城建学院',code_evidence)
    records=[];conflicts=[]
    for rownum,row in enumerate(expanded,1):
        track,control,major,max_score,min_score,difference,average=row['cells']
        control=int(control);minimum=float(min_score);maximum=float(max_score);average=float(average);difference=float(difference)
        assert minimum-control==difference,(major,'control difference inconsistent')
        def numeric(v):return int(v) if v.is_integer() else v
        record_id='major-2026-huuc-gx-'+hashlib.sha256((track+'|'+major).encode()).hexdigest()[:12]
        errors=[]
        if not minimum<=average<=maximum:
            errors=['sourceAverageScore','sourceMaximumScore','score']
            conflicts.append({'id':record_id,'major':major,'sourceRow':rownum,'sourceHtmlRow':row['htmlRow'],
                'sourceId':'major-a-huuc-score-2026','originalValues':{'score':numeric(minimum),'sourceMaximumScore':numeric(maximum),'sourceAverageScore':average},
                'issue':'原表平均分高于最高分，无法判断哪个字段误录；三个原值均保留，不参加分数比较。'})
        note='原页广西本科录取情况表直接给出专业最低分；未区分首轮和征集，未列广西正式批次、专业组、专业最低位次或录取人数。学校2026招生章程第14条以高考投档成绩为依据、第19条认可政策加分；原表未单列加分处理方式，可按学校普通高考总分口径参考，不称为裸分。'
        if errors:note+='原表最高423、最低418、平均428.2，平均分超过最高分；保留原文数值并标记冲突，不擅自更正。'
        records.append({'id':record_id,'province':'广西','year':2026,'schoolCode':'11765','school':'河南城建学院',
            'track':'物理' if track=='物理类' else '历史','batch':'本科（批次待核）','group':None,'major':major,
            'score':numeric(minimum),'scoreType':'专业录取最低分','round':'录取汇总（轮次未分）',
            'admissionType':'普通类','sourceAdmissionType':'广西本科录取情况（物理类/历史类）',
            'scoreComparable':not bool(errors),'scoreBasis':'普通高考总分口径；学校认可政策加分，原表未单列加分处理方式',
            'rank':None,'rankType':None,'sourceMaximumScore':numeric(maximum),'sourceAverageScore':average,
            'controlScore':control,'scoreDifference':numeric(difference),
            'sourceId':'major-a-huuc-score-2026','sourceIds':['major-a-huuc-score-2026','major-a-huuc-charter-2026','major-a-huuc-school-code-evidence'],
            'fieldSourceIds':{'schoolCode':['major-a-huuc-school-code-evidence'],'scoreComparable':['major-a-huuc-charter-2026']},
            'sourceSection':'2026广西本科录取情况','sourceTable':'2026广西本科录取情况','sourceRow':rownum,'sourceHtmlRow':row['htmlRow'],
            'reviewedAt':meta['accessedAt'],'note':note,'evidenceStatus':'source-conflict' if errors else 'verified',
            'scoreEvidenceGaps':['原表平均分超过最高分，冲突字段待学校澄清'] if errors else [],
            'conflictFields':errors,'requiredSubjects':[],'subjectRule':'unknown','requirementText':None})
    assert len(conflicts)==1 and conflicts[0]['major']=='城市地下空间工程（数智岩土方向）'
    return records,conflicts,expanded

if __name__=='__main__':
    records,conflicts,expanded=extract()
    print(json.dumps({'records':records,'conflicts':conflicts,'expandedTable':expanded},ensure_ascii=False,indent=2))
