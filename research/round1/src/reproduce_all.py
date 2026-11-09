"""Portable subprocess runner for the completed research challenge.

This module imports only Python's standard library and never imports study
modules to discover their behavior. Use --dry-run to inspect all commands.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]

# make_figures.py is guarded by __name__ == '__main__'. Running its definitions
# under a distinct name in a fresh child allows the three non-EEG figure
# functions to execute without importing or running any EEG analysis module.
NON_EEG_FIGURES = """
from pathlib import Path
import runpy
import sys
root = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(root / 'src'))
namespace = runpy.run_path(str(root / 'src' / 'make_figures.py'), run_name='figure_subset')
for name in ('population', 'finite_resolution', 'serialization'):
    namespace[name]()
print('Figures 1, 2, and 4 saved to', root / 'figures')
""".strip()


def plan(full: bool, skip_pdf: bool):
    def script(label, name, *args):
        return label, [sys.executable, str(ROOT / 'src' / name), *args]
    steps = [
        script('population_theory', 'theory_study.py'),
        script('variational_certificates', 'variational_study.py'),
        script('finite_sample_calibration', 'finite_sample_study.py'),
        script('independent_math_audit', 'math_review_independent.py'),
        script('math_followup_and_serialization', 'math_review_v2_calculations.py'),
    ]
    if not full:
        steps.append(('non_eeg_figures', [sys.executable, '-c', NON_EEG_FIGURES, str(ROOT)]))
        return steps
    steps.extend([
        script('eeg_primary', 'eeg_study.py', '--subjects', '1-109', '--mode', 'primary', '--reference', 'original'),
        script('eeg_four_seconds', 'eeg_study.py', '--subjects', '1-109', '--mode', 'four_seconds', '--reference', 'original'),
        script('eeg_alternating', 'eeg_study.py', '--subjects', '1-109', '--mode', 'alternating', '--reference', 'original'),
        script('eeg_average_reference', 'eeg_study.py', '--subjects', '1-109', '--mode', 'primary', '--reference', 'average'),
        script('eeg_filter_recomputed_qc', 'eeg_study.py', '--subjects', '1-109', '--mode', 'primary', '--reference', 'original', '--causal-filters'),
        script('eeg_filter_fixed_original_mask', 'filter_robustness.py'),
        script('independent_empirical_audit', 'empirical_audit_independent.py'),
        script('scientific_results_table', 'build_scientific_results_table.py'),
        script('all_figures', 'make_figures.py'),
    ])
    if not skip_pdf:
        steps.append(script('report_pdf', 'build_report_pdf.py'))
    return steps


def display_command(command):
    if '-c' in command:
        return f'{shlex.quote(command[0])} -c <guarded Figure 1/2/4 dispatcher> {shlex.quote(str(ROOT))}'
    return shlex.join(command)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--without-eeg', action='store_true',
                      help='Run theory, simulations, mathematical audits, and Figures 1/2/4 without EDF access.')
    mode.add_argument('--full', action='store_true',
                      help='Also download/reuse EEG, run all sensitivities and empirical audit, build all figures and PDF.')
    parser.add_argument('--skip-pdf', action='store_true',
                        help='Skip the optional PDF exporter in --full mode.')
    parser.add_argument('--dry-run', action='store_true',
                        help='Print the ordered plan without executing scripts or creating run outputs.')
    parser.add_argument('--threads', type=int, default=1,
                        help='BLAS/OpenMP thread count passed to subprocesses (default: 1).')
    args = parser.parse_args()
    if args.threads < 1:
        parser.error('--threads must be at least 1')
    steps = plan(args.full, args.skip_pdf)
    for i, (label, command) in enumerate(steps, start=1):
        if '-c' not in command and not Path(command[1]).is_file():
            parser.error(f'Required script is missing: {command[1]}')
        print(f'{i:02d}. {label}: {display_command(command)}', flush=True)
    if args.dry_run:
        return 0

    env = os.environ.copy()
    for key in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS',
                'VECLIB_MAXIMUM_THREADS', 'NUMEXPR_NUM_THREADS'):
        env[key] = str(args.threads)
    env['PYTHONUNBUFFERED'] = '1'
    env['MPLBACKEND'] = 'Agg'
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S_%fZ')
    run_dir = ROOT / 'output' / 'reproduction_runs' / stamp
    run_dir.mkdir(parents=True, exist_ok=False)
    for name in ('results', 'reviews', 'figures'):
        (ROOT / name).mkdir(parents=True, exist_ok=True)
    manifest = dict(started_utc=datetime.now(timezone.utc).isoformat(),
                    mode='full' if args.full else 'without-eeg',
                    threads=args.threads, python=sys.version,
                    project_root=str(ROOT), steps=[])
    manifest_path = run_dir / 'manifest.json'
    for i, (label, command) in enumerate(steps, start=1):
        log = run_dir / f'{i:02d}_{label}.log'
        print(f'Running {label}; log: {log.relative_to(ROOT)}', flush=True)
        start = time.perf_counter()
        with log.open('w', encoding='utf-8') as handle:
            result = subprocess.run(command, cwd=ROOT, env=env,
                                    stdout=handle, stderr=subprocess.STDOUT, check=False)
        record = dict(name=label, command=command, exit_code=result.returncode,
                      wall_seconds=time.perf_counter()-start,
                      log=str(log.relative_to(ROOT)))
        manifest['steps'].append(record)
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding='utf-8')
        if result.returncode:
            print(f'Failed: {label} (exit {result.returncode}). See {log.relative_to(ROOT)}.', file=sys.stderr)
            print(log.read_text(encoding='utf-8', errors='replace')[-5000:], file=sys.stderr)
            return result.returncode
        print(f'Completed {label} in {record["wall_seconds"]:.2f} s', flush=True)
    manifest['completed_utc'] = datetime.now(timezone.utc).isoformat()
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    print('Reproduction complete. Manifest:', manifest_path.relative_to(ROOT), flush=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
