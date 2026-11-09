# Neural time arrows under unknown observation filters

A completed theoretical and computational neuroscience methods study with a
prespecified public-EEG demonstration and independent numerical audits.

Start with the [full report](output/neural_time_arrow_report.md), its
[PDF](output/neural_time_arrow_report.pdf), the
[Chinese interpretation](output/research_summary_zh.md), the
[compact results table](output/scientific_results_table.csv), and the
[scientific completion ledger](COMPLETION_LEDGER.md).

## What the study establishes

The population theory quantifies a component of Gaussian temporal asymmetry
that survives separate unknown channel filters. It provides a phase-relaxed
reversal density, an explicit triangle lower bound, and a sharp weak-signal
limit. A finite-record representation theorem then identifies the observation
boundary: unrestricted channel-filter memory prevents uniformly informative
finite-sample tests against the stated regular Gaussian alternatives.

The initial conjecture that a significant finite-window cycle score could
reject the entire reversible-latent/filter class was **falsified by a retained
counterexample**. This outcome led to the finite-record theorem and the
bandwidth-bias analysis.

In the fixed EEG analysis, mean Q is 6.9845e-5 in 78 retained eyes-open holdout
records and 1.9844e-4 in 84 retained eyes-closed holdout records. Both frozen
Holm-adjusted conditional sign-flip p values are 0.00004. An independent EDF
implementation reproduces every primary inclusion decision and all 177
retained pilot-plus-holdout scores within 9.9e-17. Q measures repeatable,
coherency-weighted finite-window sensor structure; the report keeps that
empirical statement separate from latent-mechanism identification.

The calculations and proofs are complete in the scope described by the
report. Novelty priority and journal assessment remain external scientific
reviews. Existing closure-phase, spectral-divergence, and optimization
ingredients are attributed in the report and prior-art audits.

## Directory guide

| Path | Contents |
|---|---|
| `output/` | Full Markdown/PDF report, compact scientific results table, PDF validation metadata |
| `src/` | Numerical study, EEG downloader/analysis, independent audits, figure/PDF builders, reproduction driver |
| `results/` | Participant-level and group-level outputs, simulation tables, cycle arrays, download/run metadata |
| `figures/` | PNG and SVG versions of the four scientific figures |
| `protocols/` | Frozen primary specification and SHA-256/timestamp record |
| `reviews/` | Independent mathematical, empirical, prior-art, and reporting reviews; exact audit outputs |
| `scouts/` | Independently frozen initial topic/data proposals, including unselected branches |
| `sources/` | Local reading cache, omitted from the distributed package; authoritative URLs and reading coverage are in the report/reviews |
| `data/eegmmidb/` | Raw EDF cache created by the downloader; omitted from the compact package |
| `tmp/pdfs/` | Generated equations and PDF-page previews; created during PDF export |

Project paths are resolved relative to the source files. Commands below run
from the project root; the driver also works when invoked from another working
directory.

## Environment

The completed run used Python 3.12. Exact installed package versions are
recorded in `requirements.txt`.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

For numerical work and figures without PDF export, the core requirements are:

```bash
python -m pip install numpy==2.3.5 scipy==1.17.0 pandas==2.2.3 matplotlib==3.10.8
```

ReportLab, Pillow, and PyMuPDF support PDF construction and page inspection.
The existing PDF renderer also uses Linux DejaVu Sans system fonts
(`fonts-dejavu-core` on Debian/Ubuntu). On an environment without that font
layout, use `--skip-pdf` and read the Markdown report. This font dependency is
specific to the PDF exporter; numerical project paths are portable.

The reproduction driver sets numerical thread counts to one by default.
Seeds and analysis settings are fixed in the study scripts. Floating-point
optimizers and BLAS implementations may produce small numerical differences;
timing and runtime timestamps will naturally differ.

## Reproduce without downloading raw EEG

Inspect the command sequence without executing any calculation:

```bash
python src/reproduce_all.py --without-eeg --dry-run
```

Recompute population tests, numerical certificates, calibration simulations,
independent mathematical audits, and Figures 1, 2, and 4:

```bash
python src/reproduce_all.py --without-eeg
```

This mode never runs the EEG downloader, EEG record analysis, or raw-data
empirical audit. It produces the theory/simulation/audit inputs needed by the
three non-EEG figures. The archived empirical tables and Figure 3 can still be
read without raw data.

The exact leakage-curve evaluator resumes completed window durations from
`reviews/math_review_v2_leakage_partial.json`. The `partial` name is historical:
the JSON is a resumable checkpoint, not a separate scientific analysis. To
recompute every leakage duration from scratch, run in a copy with that
checkpoint moved aside. The driver leaves the checkpoint semantics unchanged.

To rebuild all figures or the PDF from the supplied numerical outputs alone:

```bash
python src/make_figures.py
python src/build_report_pdf.py
```

These two commands require the supplied derived result files, including the
cycle arrays and covariance example, but do not require EDF files or network
access. The PDF builder formats the retained report text; it does not rewrite
the scientific narrative from new results.

## Reproduce with raw EEG

The raw data source, version, license, and required attribution are in
[DATA_NOTICE.md](DATA_NOTICE.md). Missing files are retrieved from the
versioned PhysioNet endpoint; existing EDF files are reused.

Download the complete two-baseline collection first, if desired:

```bash
python src/eeg_study.py --subjects 1-109 --download-only
```

The 218 expected paths have this form:

```text
data/eegmmidb/S011/S011R01.edf
data/eegmmidb/S011/S011R02.edf
...
data/eegmmidb/S109/S109R02.edf
```

On a fresh package copy, the command downloads every raw baseline file. To
force a fresh download in an existing working tree, first move the raw cache
and any `data/pilot/` copies outside that copy; the downloader deliberately
reuses files already present. A failed download is logged rather than replaced
by another participant.

Run the complete computational sequence:

```bash
python src/reproduce_all.py --full --dry-run
python src/reproduce_all.py --full
```

For a numerical/figure-only full rerun:

```bash
python src/reproduce_all.py --full --skip-pdf
```

The full mode runs the same theory and simulation work as `--without-eeg`, then
the primary EEG analysis, four-second and alternating-window sensitivities,
common-average-reference sensitivity, initial recomputed-QC filtering branch,
fixed-original-mask filtering, independent raw-EDF audit, compact results
table, all figures, and PDF export. It uses cached EDFs when present.

### Explicit full command order

The driver executes these scripts in separate subprocesses; several scientific
scripts perform work at top level and should not be imported as a discovery
mechanism.

```bash
python src/theory_study.py
python src/variational_study.py
python src/finite_sample_study.py
python src/math_review_independent.py
python src/math_review_v2_calculations.py
python src/eeg_study.py --subjects 1-109 --mode primary --reference original
python src/eeg_study.py --subjects 1-109 --mode four_seconds --reference original
python src/eeg_study.py --subjects 1-109 --mode alternating --reference original
python src/eeg_study.py --subjects 1-109 --mode primary --reference average
python src/eeg_study.py --subjects 1-109 --mode primary --reference original --causal-filters
python src/filter_robustness.py
python src/empirical_audit_independent.py
python src/build_scientific_results_table.py
python src/make_figures.py
python src/build_report_pdf.py
```

Only `--full` uses the last ten commands. The download-free mode dispatches
just the `population`, `finite_resolution`, and `serialization` figure
functions in a separate process after their outputs exist. It does not invoke
the EEG figure function.

Each executed driver step has a timestamped log under
`output/reproduction_runs/`, together with a JSON run manifest. The driver
stops on the first failed step and records its exit status. A rerun overwrites
the scripts' derived CSV/JSON/figure outputs; use a separate package copy when
preserving the originally supplied numerical snapshot is important.

## Historical and current artifact identities

- `protocols/protocol_v1.md` and `freeze_v1.json` retain the empirical decision
  record. The main score, channels, frequency band, and exclusions were not
  retuned after opening the holdout.
- `theory_v1.md` is the initial theoretical draft. The final report adds the
  finite-record theorem, bias/error analysis, sharpness, and revised
  interpretation; use the report for the completed scientific scope.
- `results/variational_certificates_v1_archived.csv` is the earlier
  computed-matrix certificate table. It predates propagation of inverse
  residuals into both interval endpoints. It is retained for the correction
  trail and is not the final certificate table.
- `results/variational_certificates.csv` is the final interval study generated
  by `variational_study.py` with the current certificate implementation.
- `results/variational_runner_reproduction.json` records the historical input
  sequence/replay check; the driver does not regenerate this retrospective
  comparison against the earlier implementation.
- `eeg_primary_original_filtered_*` files are the initial filtering sensitivity
  with QC recomputed after filtering. `matched_filter_robustness.csv` and
  `matched_filter_summary.json` hold original participants and epoch masks
  fixed; these are the clean perturbation comparison.
- `reviews/*v1.md` and `reviews/math_review_v2_addendum.md` are dated review
  narratives. They preserve what was reviewed and what changed. Recomputing
  audit JSON/CSV files does not rewrite those historical review documents.
- `_pilot` cohorts and S001-S010 remain separate from the prespecified
  S011-S109 holdout. Frequencies, triangles, and epochs are never independent
  biological sample counts.

See the full report and completion ledger for the scientific meaning of each
retained negative result and correction.

## Snapshot integrity

`MANIFEST_SHA256.csv` gives the SHA-256 digest and size of every distributed
file other than the manifest itself. `results/raw_data_manifest.csv` separately
records all 218 original EDF hashes and sizes, with their versioned source
base URL. The original raw records can therefore be checked after downloading.
The ZIP includes all five sensitivity/primary cycle-array files as well as all
participant tables. Raw EDFs and downloaded article copies are omitted.
