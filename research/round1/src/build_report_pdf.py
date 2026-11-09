"""Render the full research report to a checked, typeset PDF."""
from pathlib import Path
import re
import html
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph,
    Spacer, Image, Table, TableStyle, PageBreak, NextPageTemplate, CondPageBreak,
    KeepTogether)
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output'
TMP=ROOT/'tmp'/'pdfs'
TMP.mkdir(parents=True,exist_ok=True)
NAVY=colors.HexColor('#20354c')
TEAL=colors.HexColor('#00897b')
LIGHT=colors.HexColor('#edf4f5')
FONTDIR=Path('/usr/share/fonts/truetype/dejavu')
pdfmetrics.registerFont(TTFont('Research',str(FONTDIR/'DejaVuSans.ttf')))
pdfmetrics.registerFont(TTFont('ResearchBold',str(FONTDIR/'DejaVuSans-Bold.ttf')))
pdfmetrics.registerFont(TTFont('ResearchItalic',str(FONTDIR/'DejaVuSans-Oblique.ttf')))
pdfmetrics.registerFontFamily('Research',normal='Research',bold='ResearchBold',italic='ResearchItalic',boldItalic='ResearchBold')

styles={
 'title':ParagraphStyle('title',fontName='ResearchBold',fontSize=24,leading=29,textColor=NAVY,spaceAfter=18),
 'subtitle':ParagraphStyle('subtitle',fontName='Research',fontSize=14,leading=20,textColor=TEAL,spaceAfter=15),
 'h2':ParagraphStyle('h2',fontName='ResearchBold',fontSize=14,leading=19,textColor=NAVY,spaceBefore=16,spaceAfter=9,keepWithNext=True),
 'h3':ParagraphStyle('h3',fontName='ResearchBold',fontSize=11.1,leading=16,textColor=TEAL,spaceBefore=12,spaceAfter=7,keepWithNext=True),
 'body':ParagraphStyle('body',fontName='Research',fontSize=9.6,leading=14.1,textColor=NAVY,spaceAfter=7.5,allowWidows=0,allowOrphans=0),
 'bullet':ParagraphStyle('bullet',fontName='Research',fontSize=9.6,leading=14.1,textColor=NAVY,leftIndent=12,firstLineIndent=-8,spaceAfter=6),
 'caption':ParagraphStyle('caption',fontName='Research',fontSize=9.0,leading=12.6,textColor=NAVY,spaceBefore=8,spaceAfter=6),
 'cell':ParagraphStyle('cell',fontName='Research',fontSize=8.1,leading=11.2,textColor=NAVY),
 'cellhead':ParagraphStyle('cellhead',fontName='ResearchBold',fontSize=8.1,leading=11.2,textColor=colors.white),
 'refs':ParagraphStyle('refs',fontName='Research',fontSize=8.3,leading=12,textColor=NAVY,spaceAfter=8,splitLongWords=True),
}

def inline(s):
    s=html.escape(s,quote=False)
    s=re.sub(r'\*\*(.+?)\*\*',r'<b>\1</b>',s)
    s=re.sub(r'\[([^\]]+)\]\((https?://[^)]+)\)',r'<link href="\2" color="#00897b">\1</link>',s)
    # Raw URLs are preserved as readable links, with long-word wrapping.
    s=re.sub(r'(?<![">])(https?://[^\s<]+)',lambda m: m.group(0) if '"' in m.group(0) else '<link href="'+m.group(0)+'" color="#00897b">'+m.group(0)+'</link>',s)
    return s

def decorate(canvas,doc):
    width,height=canvas._pagesize
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor('#d8e1e5'))
    canvas.setLineWidth(.5)
    canvas.line(40,height-32,width-40,height-32)
    canvas.setFillColor(NAVY)
    canvas.setFont('Research',7.4)
    canvas.drawString(40,height-23,'NEURAL TIME ARROWS  /  THEORY, OBSERVATION, AND EEG')
    canvas.setFillColor(colors.HexColor('#73808c'))
    canvas.drawString(40,23,'Research challenge report  |  6 November 2026 UTC')
    canvas.drawRightString(width-40,23,str(doc.page))
    canvas.restoreState()

class Report(BaseDocTemplate):
    def afterFlowable(self,flowable):
        if isinstance(flowable,Paragraph) and flowable.style.name in ('h2','title'):
            title=flowable.getPlainText()
            key='section_'+str(self.page)+'_'+str(len(title))
            self.canv.bookmarkPage(key)
            self.canv.addOutlineEntry(title,key,level=0,closed=False)

def formula_image(tex,index,width):
    tex=tex.replace('\n',' ').strip()
    tex=tex.replace(r'\frac12',r'\frac{1}{2}')
    tex=re.sub(r'\\(mathcal|mathsf|widehat|overline)\s+([A-Za-z])',r'\\\1{\2}',tex)
    tex=tex.replace(r'\mathsf T',r'\mathsf{T}')
    tex=tex.replace(r'\overline P',r'\overline{P}').replace(r'\widehat P',r'\widehat{P}')
    tex=tex.replace(r'\ne ',r'\neq ')
    fig=plt.figure(figsize=(11,.7))
    fig.text(.01,.5,'$'+tex+'$',fontsize=16,color='#20354c',va='center')
    path=TMP/f'equation_{index:02d}.png'
    fig.savefig(path,dpi=240,bbox_inches='tight',pad_inches=.09,transparent=False,facecolor='white')
    plt.close(fig)
    from PIL import Image as PILImage
    im=PILImage.open(path); iw,ih=im.size
    w=min(width,iw/240*72)
    h=w*ih/iw
    return Image(str(path),width=w,height=h,hAlign='CENTER')

def table(lines,width):
    rows=[[c.strip() for c in x.strip().strip('|').split('|')] for x in lines]
    rows=[r for r in rows if not all(re.fullmatch(r'[:\-\s]+',c or '-') for c in r)]
    n=len(rows[0])
    sizes=[]
    for j in range(n):
        sizes.append(min(42,max(10,max(len(row[j]) for row in rows)**.7*3)))
    if n==6:sizes=[19,15,12,18,29,19]
    if n==3:sizes=[24,40,28]
    total=sum(sizes); widths=[width*s/total for s in sizes]
    cells=[[Paragraph(inline(c),styles['cellhead' if i==0 else 'cell']) for c in row] for i,row in enumerate(rows)]
    t=Table(cells,colWidths=widths,repeatRows=1,hAlign='LEFT')
    t.setStyle(TableStyle([
      ('BACKGROUND',(0,0),(-1,0),NAVY),('VALIGN',(0,0),(-1,-1),'TOP'),
      ('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6),
      ('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7),
      ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,LIGHT]),
      ('LINEBELOW',(0,0),(-1,0),.6,TEAL),
      ('LINEBELOW',(0,-1),(-1,-1),.4,colors.HexColor('#c7d4db'))
    ]))
    return t

def main():
    pw,ph=A4;lw,lh=landscape(A4)
    margin=43
    doc=Report(str(OUT/'neural_time_arrow_report.pdf'),pagesize=A4,
        leftMargin=margin,rightMargin=margin,topMargin=46,bottomMargin=40,
        title='Neural time arrows under unknown observation filters',
        author='AI-assisted research challenge for Justin',
        subject='Population bounds, finite-record nonidentifiability, and held-out EEG',
        pageCompression=1)
    doc.addPageTemplates([
        PageTemplate(id='Portrait',frames=[Frame(margin,40,pw-2*margin,ph-86,
                     leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0)],
                     onPage=decorate,pagesize=A4),
        PageTemplate(id='Landscape',frames=[Frame(42,38,lw-84,lh-80,
                     leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0)],
                     onPage=decorate,pagesize=landscape(A4))
    ])
    lines=(OUT/'neural_time_arrow_report.md').read_text().splitlines()
    story=[];i=0;eq=0;refs=False;figure_paths=[]
    width=pw-2*margin
    while i<len(lines):
        s=lines[i].strip()
        if not s:i+=1;continue
        if s.startswith('!['):
            match=re.search(r'!\[.*?\]\((.*?)\)',s)
            path=(OUT/match.group(1)).resolve();figure_paths.append(str(path))
            i+=1
            while i<len(lines) and not lines[i].strip():i+=1
            caption=lines[i].strip() if i<len(lines) and lines[i].startswith('**Figure') else ''
            if caption:i+=1
            story.extend([NextPageTemplate('Landscape'),PageBreak()])
            from PIL import Image as PILImage
            im=PILImage.open(path);iw,ih=im.size
            maxw=lw-90;maxh=lh-145
            w=min(maxw,maxh*iw/ih);h=w*ih/iw
            story.append(Image(str(path),width=w,height=h,hAlign='CENTER'))
            if caption:story.append(Paragraph(inline(caption),styles['caption']))
            story.extend([NextPageTemplate('Portrait'),PageBreak()])
            continue
        if s.startswith('$$'):
            parts=[s[2:]];i+=1
            while not parts[-1].rstrip().endswith('$$'):
                parts.append(lines[i]);i+=1
            parts[-1]=parts[-1].rstrip()[:-2]
            eq+=1
            story.extend([Spacer(1,3),formula_image('\n'.join(parts),eq,width),Spacer(1,8)])
            continue
        if s.startswith('|'):
            batch=[]
            while i<len(lines) and lines[i].strip().startswith('|'):
                batch.append(lines[i]);i+=1
            story.extend([Spacer(1,4),table(batch,width),Spacer(1,10)])
            continue
        if s.startswith('# '):
            story.append(Paragraph(inline(s[2:]),styles['title']));i+=1;continue
        if s.startswith('### '):
            story.extend([CondPageBreak(70),Paragraph(inline(s[4:]),styles['h3'])]);i+=1;continue
        if s.startswith('## '):
            title=s[3:]
            if title=='References':refs=True
            style='subtitle' if title.startswith('A completed') else 'h2'
            story.extend([CondPageBreak(90),Paragraph(inline(title),styles[style])]);i+=1;continue
        if s.startswith('- '):
            story.append(Paragraph('• '+inline(s[2:]),styles['bullet']));i+=1;continue
        para=[s];i+=1
        while i<len(lines) and lines[i].strip() and not lines[i].lstrip().startswith(('#','$$','![','|','- ')):
            para.append(lines[i].strip());i+=1
        story.append(Paragraph(inline(' '.join(para)),styles['refs' if refs else 'body']))
    doc.build(story)
    import fitz
    pdf=fitz.open(OUT/'neural_time_arrow_report.pdf')
    pages=[]
    for p in pdf:
        text=p.get_text()
        pages.append(dict(page=p.number+1,width=p.rect.width,height=p.rect.height,
                          text_chars=len(text),images=len(p.get_images())))
        pix=p.get_pixmap(matrix=fitz.Matrix(.65,.65),alpha=False)
        pix.save(str(TMP/f'page_{p.number+1:02d}.png'))
    (OUT/'pdf_validation.json').write_text(json.dumps(dict(pages=pages,equations=eq,
            figure_paths=figure_paths),indent=2))
    print(json.dumps(dict(pdf=str(OUT/'neural_time_arrow_report.pdf'),pages=len(pdf),equations=eq),indent=2))

if __name__=='__main__':
    main()

