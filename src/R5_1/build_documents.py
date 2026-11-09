"""Clean portable build of final REVTeX and Supplemental PDFs."""
from pathlib import Path
import shutil,subprocess,os
ROOT=Path(__file__).resolve().parents[1];WD=ROOT/'manuscript'
latex=shutil.which('pdflatex');bib=shutil.which('bibtex.original') or shutil.which('bibtex')
if not latex or not bib:raise SystemExit('Install TeX Live / MiKTeX with REVTeX 4.2 and BibTeX.')
for name in ['main','supplement']:
 for cmd in [[latex,'-interaction=nonstopmode','-halt-on-error',f'source/{name}.tex'],[bib,name],[latex,'-interaction=nonstopmode','-halt-on-error',f'source/{name}.tex'],[latex,'-interaction=nonstopmode','-halt-on-error',f'source/{name}.tex']]:
  r=subprocess.run(cmd,cwd=WD,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
  if r.returncode:raise RuntimeError(r.stdout[-6000:])
 print(name,'built')
