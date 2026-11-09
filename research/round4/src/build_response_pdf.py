from pathlib import Path
import re,html
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,PageBreak
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
R=Path(__file__).resolve().parents[1];D=R/'docs'
for name,file in [('DejaVu','DejaVuSans.ttf'),('DejaVuBold','DejaVuSans-Bold.ttf'),('DejaVuOblique','DejaVuSans-Oblique.ttf')]:
 pdfmetrics.registerFont(TTFont(name,'/usr/share/fonts/truetype/dejavu/'+file))
pdfmetrics.registerFontFamily('DejaVu',normal='DejaVu',bold='DejaVuBold',italic='DejaVuOblique')
s=getSampleStyleSheet();s.add(ParagraphStyle(name='BodyR',fontName='DejaVu',fontSize=9.3,leading=14,spaceAfter=8));s.add(ParagraphStyle(name='H1R',fontName='DejaVuBold',fontSize=17,leading=22,spaceAfter=15));s.add(ParagraphStyle(name='H2R',fontName='DejaVuBold',fontSize=11.4,leading=16,spaceBefore=12,spaceAfter=8,keepWithNext=True))
def fmt(x):
 x=html.escape(x);x=re.sub(r'\*\*(.*?)\*\*',r'<b>\1</b>',x);x=re.sub(r'\*(.*?)\*',r'<i>\1</i>',x);return x
story=[]
for p in (D/'RESPONSE_TO_REVIEWERS.md').read_text().split('\n\n'):
 if not p.strip():continue
 if p.startswith('# '):style='H1R';p=p[2:]
 elif p.startswith('## '):style='H2R';p=p[3:]
 else:style='BodyR'
 story.append(Paragraph(fmt(p).replace('\n','<br/>'),s[style]))
def footer(c,d):
 c.setFont('DejaVu',8);c.setFillColor(colors.HexColor('#555555'));c.drawString(43,26,'PRE preparation | Internal-review response | R4');c.drawRightString(552,26,str(d.page))
SimpleDocTemplate(str(D/'RESPONSE_TO_REVIEWERS.pdf'),pagesize=(595.28,841.89),rightMargin=43,leftMargin=43,topMargin=42,bottomMargin=42,title='Response to the PRE-style internal review — R4',author='Yanzhe Zhao').build(story,onFirstPage=footer,onLaterPages=footer)
print('Response PDF written')
