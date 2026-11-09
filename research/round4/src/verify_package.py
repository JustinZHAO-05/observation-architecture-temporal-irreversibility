"""Check packaged file digests, numerical accounting and final PDF text.
Run from any working directory. This verifies a delivered archive, not scientific
priority, external review, or all possible model classes.
"""
from pathlib import Path
import csv,hashlib,json
import pandas as pd
import fitz
R=Path(__file__).resolve().parents[1];errors=[];verified=0
manifest=R/'MANIFEST_SHA256.csv'
if manifest.exists():
 for row in csv.DictReader(manifest.open(encoding='utf8')):
  p=R/row['path']
  if not p.is_file():errors.append('Missing: '+row['path']);continue
  if hashlib.sha256(p.read_bytes()).hexdigest()!=row['sha256']:errors.append('Digest: '+row['path'])
  verified+=1
f=pd.read_csv(R/'results/finite_support_lifts.csv');cal=pd.read_csv(R/'results/unknown_shape_calibration_replicates.csv');test=pd.read_csv(R/'results/unknown_shape_test_replicates.csv')
if len(f)!=72 or not (f.all_frequency_lower>0).all():errors.append('Finite-support accounting')
if len(cal)!=1680 or len(test)!=8520:errors.append('Calibration accounting')
if not test.loc[test.calibrated,'valid'].all():errors.append('Invalid calibrated certificate')
if not json.loads((R/'results/independent_audit.json').read_text())['all_pass']:errors.append('Independent audit failed')
pages={}
for name in ['main','supplement']:
 d=fitz.open(R/'manuscript'/f'{name}.pdf');pages[name]=len(d);text='\n'.join(p.get_text() for p in d)
 if '??' in text:errors.append(name+': unresolved PDF reference')
 if 'Yanzhe Zhao' not in text:errors.append(name+': author metadata')
 for line in (R/'manuscript'/f'{name}.log').read_text(errors='ignore').splitlines():
  if 'undefined' in line or 'multiply defined' in line or 'Overfull' in line:errors.append(name+': '+line)
print(json.dumps({'files_verified':verified,'pdf_pages':pages,'errors':errors},indent=2))
if errors:raise SystemExit(1)
