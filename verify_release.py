from pathlib import Path
import hashlib,csv,sys
root=Path(__file__).resolve().parent
items=list(csv.DictReader((root/'provenance/RELEASE_SHA256.csv').open()))
fail=[]
for row in items:
 p=root/row['relative_path']
 if not p.is_file():fail.append(('missing',str(p)));continue
 h=hashlib.sha256(p.read_bytes()).hexdigest()
 if h!=row['sha256'] or p.stat().st_size!=int(row['bytes']):fail.append(('changed',str(p)))
print(f'{len(items)} declared release files checked; {len(fail)} discrepancies')
for x in fail:print(x)
sys.exit(bool(fail))
