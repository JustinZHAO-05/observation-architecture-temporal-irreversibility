from pathlib import Path
import csv,hashlib,json,zipfile,shutil,re
import fitz
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[1];Q=R/'qa'
# Render every final page for inspection, plus readable details on added results.
page_meta={};details=[]
for name in ['main','supplement']:
 d=fitz.open(R/'manuscript'/f'{name}.pdf');page_meta[name]=len(d);tiles=[]
 for i,page in enumerate(d):
  pix=page.get_pixmap(matrix=fitz.Matrix(.36,.36));im=Image.frombytes('RGB',[pix.width,pix.height],pix.samples);im.thumbnail((228,310))
  tile=Image.new('RGB',(238,335),'white');tile.paste(im,((238-im.width)//2,18));ImageDraw.Draw(tile).text((7,3),f'{name} {i+1}',fill='black');tiles.append(tile)
  text=page.get_text()
  if any(t in text for t in ['FIG. 7.','Proposition 5','Proposition 6','Proposition 7','Figure S13','Figure S14','Figure S15','Figure S16','Figure S17']):
   dest=Q/f'{name}_final_p{i+1}.png';page.get_pixmap(matrix=fitz.Matrix(1.3,1.3)).save(dest);details.append(str(dest.relative_to(R)))
 canvas=Image.new('RGB',(1190,335*((len(tiles)+4)//5)),'#dedede')
 for i,im in enumerate(tiles):canvas.paste(im,((i%5)*238,(i//5)*335))
 canvas.save(Q/f'{name}_FINAL_contact.jpg',quality=92)
# Figure/label accounting from final TeX outputs.
main=(R/'manuscript/source/main.tex').read_text();supp=(R/'manuscript/source/supplement.tex').read_text()+(R/'manuscript/source/r4_supplement.tex').read_text()
page_meta['main_figures']=len(re.findall(r'\\begin\{figure\*?\}',main));page_meta['supplement_figures']=len(re.findall(r'\\begin\{figure\*?\}',supp));page_meta['detail_renders']=details
(Q/'final_pdf_inventory.json').write_text(json.dumps(page_meta,indent=2))
# Top-level deliverables are copies of the final verified build, not stale old PDFs.
for src,dest in [('manuscript/main.pdf','PRE_R4_Main_Manuscript_2026-11-09.pdf'),('manuscript/supplement.pdf','PRE_R4_Supplemental_Material_2026-11-09.pdf'),('docs/RESPONSE_TO_REVIEWERS.pdf','PRE_R4_Response_to_Reviewers_2026-11-09.pdf')]:shutil.copy2(R/src,Path('/mnt/data')/dest)
print(json.dumps(page_meta,indent=2))
