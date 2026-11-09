from pathlib import Path
import hashlib,csv,json,zipfile,shutil,subprocess
import fitz
R=Path(__file__).resolve().parents[1];OUT=Path('/mnt/data')
# Preserve the user's complete original figure/data/source bundle as an immutable input.
A=R/'archives';A.mkdir(exist_ok=True)
name='PRE_Figures_Tables_Reproducibility.zip'
if not (A/name).exists():shutil.copy2(OUT/name,A/name)
# Remove Python bytecode and stale temporary build detritus, keep logs for verifiable QA.
for p in list(R.rglob('__pycache__')):shutil.rmtree(p)
for p in R.rglob('*'):
 if p.is_file() and p.suffix.lower() in ['.ttf','.otf','.woff','.woff2']:raise RuntimeError('Font file must not be shared: '+str(p))
# Retain final only contact/detail renderings; historical drafts remain in baseline_R3.
Q=R/'qa'
for p in list(Q.glob('*.png'))+list(Q.glob('*.jpg')):
 if ('final_' not in p.name and 'FINAL_' not in p.name and p.name!='response_first.png'):p.unlink()
# Version metadata does not imply journal acceptance.
meta={'version':'R4','date':'2026-11-09','author':'Yanzhe Zhao','affiliation':'School of Future Technology, Tianjin University','email':'justinzhaoyz@outlook.com','status':'Author-final-review submission materials; no external journal acceptance claimed','main_pages':len(fitz.open(R/'manuscript/main.pdf')),'supplement_pages':len(fitz.open(R/'manuscript/supplement.pdf')),'main_figures':8,'supplement_figures':17,'new_independent_record_pairs':600,'new_test_analyses':8520}
(R/'RELEASE.json').write_text(json.dumps(meta,indent=2))
manifest=R/'MANIFEST_SHA256.csv'
files=sorted(p for p in R.rglob('*') if p.is_file() and p!=manifest)
with manifest.open('w',newline='',encoding='utf8') as f:
 w=csv.writer(f);w.writerow(['path','bytes','sha256'])
 for p in files:w.writerow([p.relative_to(R).as_posix(),p.stat().st_size,hashlib.sha256(p.read_bytes()).hexdigest()])
# Verify before packaging. The verifier prints but does not mutate the signed tree.
r=subprocess.run(['python',str(R/'src/verify_package.py')],capture_output=True,text=True)
if r.returncode:raise RuntimeError(r.stdout+r.stderr)
print(r.stdout)
full=OUT/'PRE_R4_Full_Research_and_Submission_Package_2026-11-09.zip'
with zipfile.ZipFile(full,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in sorted(R.rglob('*')):
  if p.is_file():z.write(p,'PRE_R4/'+p.relative_to(R).as_posix())
light=OUT/'PRE_R4_Editorial_Submission_Kit_2026-11-09.zip'
with zipfile.ZipFile(light,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in sorted(R.rglob('*')):
  if not p.is_file():continue
  rel=p.relative_to(R)
  if rel.parts[0] in ['manuscript','docs'] or rel.name in ['README_FIRST_CN.md','README.TXT','RELEASE.json'] or rel.as_posix()=='src/build_documents.py':
   z.write(p,'PRE_R4_EDITORIAL/'+rel.as_posix())
checks=[]
for p in [full,light]:
 with zipfile.ZipFile(p) as z:
  bad=z.testzip();checks.append({'name':p.name,'bytes':p.stat().st_size,'MiB':p.stat().st_size/2**20,'entries':len(z.namelist()),'bad_entry':bad,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
  if bad:raise RuntimeError('ZIP failed '+bad)
(OUT/'PRE_R4_Release_Checks.json').write_text(json.dumps(checks,indent=2));print(json.dumps(checks,indent=2))
