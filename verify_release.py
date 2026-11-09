from pathlib import Path
import csv
import hashlib
import sys

root = Path(__file__).resolve().parent
manifest = root / "provenance" / "RELEASE_SHA256.csv"
if not manifest.exists():
    raise SystemExit("Release manifest missing. Upload the full prepared research bundle first.")

rows = list(csv.DictReader(manifest.open(encoding="utf-8")))
errors = []
for row in rows:
    path = root / row["relative_path"]
    if not path.is_file():
        errors.append(("missing", str(path)))
        continue
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != row["sha256"] or path.stat().st_size != int(row["bytes"]):
        errors.append(("changed", str(path)))

print(f"Checked {len(rows)} release files; {len(errors)} discrepancies.")
for reason, path in errors:
    print(reason, path)
sys.exit(bool(errors))
