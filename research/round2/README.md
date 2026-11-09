# PRE round 2 — observation architecture and temporal irreversibility

## Start here

- `output/PRE_Round2_Technical_Dossier.pdf`: self-contained proofs, assumptions, numerical results and reading comparison.
- `output/PRE_Round2_Technical_Dossier.md`: editable source; this is a research dossier, not the final submitted manuscript.
- `output/research_summary_zh.md`: Chinese interpretation and publication framing.
- `output/key_results.csv`: machine-readable principal findings with source filenames.
- `reviews/literature_review.md`: actual reading coverage, distinctions from nearby work, and priority limits.
- `protocols/round2_protocol.md`: execution specification and post-result amendments.

## Scientific scope

All statistical theorems concern real stationary Gaussian processes with variables even under time reversal. The one-delay construction permits correlated latent sources and spatial mixing after source-specific filtering. The positive inference certificate instead assumes the defined sensor-diagonal observation class and externally supplied bounds on spectral power and covariance tails. These are different model classes.

The latency resource is spectral power with fixed mixing gains, not metabolic energy. The EEG analysis is an exploratory reanalysis of archived derived arrays, with matched accepted windows; it is not a new raw-EDF decoding audit or a calibrated estimate of a latent brain reversal rate.

## Reproduction

Python 3.10+ with NumPy, SciPy, pandas and matplotlib. The delivered environment versions are in `environment.json` and `requirements.txt`. No GPU, external API, credentials, live data download, or network access is needed for the new calculations.

```bash
python -m pip install -r requirements.txt
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python reproduce.py
```

On Windows, set those environment variables in the shell, or simply run `python reproduce.py`, which supplies them to subprocesses. The pipeline overwrites computed results and figures but preserves its bundled inputs and `results/archive/`. Wall-clock fields and small floating-point optimization differences can vary across environments. Scientific counts, equality checks and conclusions are the reproducibility targets.

Individual entry points:

```bash
python src/theory_round2.py
python src/finite_certificate.py
python src/power_cost_and_coordinates.py
python src/latency_cost_lp_audit.py
python src/audit_round2.py
python src/multichannel_audit.py
python src/continuous_rate_certificate.py
python src/eeg_matched_reference.py
python src/make_figures_round2.py
python src/validate_package.py
```

`power_cost_and_coordinates.py` retains an intentionally unsuccessful SLSQP attempt. Its success flag is not a correctness gate. The analytic proof and the separate full-matrix cutting-plane audit are the evidence for the cost formula. Floating-point LP brackets are numerical checks, not directed-rounding certificates.

## Contents and provenance

`inputs/round1_results/` contains two first-round imaginary-cycle arrays and their subject tables. Each source array is hashed in `results/eeg_followup_provenance.json`. These files support the full matched-window reanalysis. The first-round raw EEG source remains PhysioNet EEGMMIDB v1.0.0; see `DATA_NOTICE.md`.

The finite-grid simulations contain 1,920 independent longest trajectories, each examined at four nested prefixes (7,680 analyses). The rate study contains 128 independent longest trajectories, each examined at three prefixes (384 analyses). Prefixes are not independent replicates. The 113 EEG records come from 71 participants; condition-paired analyses use 42 participants.

`results/archive/` retains the earlier rate grid before the explicitly documented extension to longer records. All zero-power cells remain in the results. No exclusion based on a desirable scientific outcome is applied.

## Limits of completion

The scoped mathematical and computational package is complete and suitable for author-level review and manuscript preparation. It has not received external peer review. A final specialist priority assessment and independent human verification of the new proofs remain submission responsibilities. No guarantee of PRE acceptance is implied.

No independent subagent endpoint was available in this session. Separate implementations are computational cross-checks, not independent human reviewers. AI assisted derivation, coding, analysis, literature comparison and documentation; human authors retain scientific responsibility. No journal submission or public repository upload was performed.
