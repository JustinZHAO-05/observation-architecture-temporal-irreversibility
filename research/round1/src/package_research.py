"""Build and verify the complete distributable research snapshot."""
from pathlib import Path
import csv
import hashlib
import json
import zipfile

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / 'output' / 'neural_time_arrow_reproducibility.zip'
MANIFEST = ROOT / 'MANIFEST_SHA256.csv'
VALIDATION = ROOT / 'output' / 'package_validation.json'
EXCLUDED_TOP = {'data', 'sources', 'tmp'}


def included(path):
    rel = path.relative_to(ROOT)
    if rel.parts[0] in EXCLUDED_TOP or '__pycache__' in rel.parts:
        return False
    if path in {ARCHIVE, MANIFEST, VALIDATION}:
        return False
    if path.suffix in {'.pyc', '.part', '.zip'}:
        return False
    if rel.parts[:2] == ('output', 'reproduction_runs'):
        return False
    if rel.parts[0] == 'data_scout' and path.name != 'provenance.json':
        return False
    return path.is_file()


def main():
    files = sorted(p for p in ROOT.rglob('*') if included(p))
    rows = [(str(p.relative_to(ROOT)), p.stat().st_size,
             hashlib.sha256(p.read_bytes()).hexdigest()) for p in files]
    with MANIFEST.open('w', newline='', encoding='utf-8') as handle:
        writer = csv.writer(handle)
        writer.writerow(['relative_path', 'size_bytes', 'sha256'])
        writer.writerows(rows)
    with zipfile.ZipFile(ARCHIVE, 'w', compression=zipfile.ZIP_DEFLATED,
                         compresslevel=6, allowZip64=True) as archive:
        for path in files + [MANIFEST]:
            archive.write(path, str(Path('neural_time_arrow_study') / path.relative_to(ROOT)))
    with zipfile.ZipFile(ARCHIVE) as archive:
        corrupt = archive.testzip()
        if corrupt:
            raise RuntimeError(f'ZIP CRC check failed: {corrupt}')
        for rel, size, digest in rows:
            data = archive.read('neural_time_arrow_study/' + rel)
            if len(data) != size or hashlib.sha256(data).hexdigest() != digest:
                raise RuntimeError(f'Archived file differs from manifest: {rel}')
    result = dict(archive=str(ARCHIVE), archive_bytes=ARCHIVE.stat().st_size,
                  archive_sha256=hashlib.sha256(ARCHIVE.read_bytes()).hexdigest(),
                  archived_file_count=len(files)+1,
                  manifested_file_count=len(files), crc_check='passed',
                  every_archived_file_sha256='passed',
                  excluded=['raw EDF data', 'downloaded article copies',
                            'temporary PDF renders', 'unselected raw scout datasets'])
    VALIDATION.write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
