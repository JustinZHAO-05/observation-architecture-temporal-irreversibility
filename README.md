# Observation architecture and the identifiability of temporal irreversibility

Research code, source data, and reproducibility material for the manuscript by **Yanzhe Zhao** (School of Future Technology, Tianjin University).

**Article:** *Observation architecture and the identifiability of temporal irreversibility*  
**Contact:** justinzhaoyz@outlook.com  
**Repository:** https://github.com/JustinZHAO-05/observation-architecture-temporal-irreversibility

## Contents

- `manuscript_source/`: editable REVTeX main manuscript, appendices, and references.
- `paper/figures/`: all 8 main and 17 supplementary publication figures in vector PDF.
- `research/round1/`: exact closure invariants, time-domain simulations, EEG protocols and independent audit.
- `research/round2/`: reversible latent spectral lifts, power minimization, finite-record certificates, and EEG rereferencing.
- `research/round3/`: white-latent example, finite-bandwidth mechanism controls, and independent scale calibration.
- `research/round4/`: constrained-latent results, broadband optimality, unknown-shape independent calibration, and real EEG transformations.
- `src/R5_1/`: final figure editorial production and associated scripts.
- `results/R5_1/`: latest manuscript numerical tables, individual calibration runs, model checks.
- `figure_sources/`: source tables, validated CSV/NPZ arrays, original vector panel assets, and plots' production metadata.
- `provenance/`: stage source indexes and SHA-256 checksums.

The **original PhysioNet EDF recordings are not mirrored here**. Download EEGMMIDB version 1.0.0 from https://physionet.org/content/eegmmidb/1.0.0/ (DOI: [10.13026/C28G6P](https://doi.org/10.13026/C28G6P)). The original study used the R01/R02 baseline runs. The relevant processed spectral-cycle arrays and subject-level statistics are included.

## Reproduction

1. Use Python >= 3.10 and install the stage-specific dependencies in `research/round1/requirements.txt` and `research/round2/requirements.txt`. Common scientific packages are NumPy, SciPy, pandas, and matplotlib.
2. Start with `research/round1/README.md` and its frozen protocols, then `research/round2/README.md` and `research/round2/reproduce.py`.
3. Round-3/4 experiment drivers are in `research/round3/src/` and `research/round4/src/`. The released result CSV/NPZ files allow independent numerical checks without recomputing expensive stages.
4. Use `provenance/FIGURE_PANEL_INDEX.csv` and `figure_sources/FIGURE_PANEL_INDEX.csv` to trace published figure panels to data.
5. Run `python verify_release.py` to check that the uploaded files agree with `provenance/RELEASE_SHA256.csv`.

The complete research-file release is available in this repository. The numerical model assumptions, observation regimes, and limitations are specified in the manuscript and its supplemental material. Source release metadata is in `provenance/RELEASE_METADATA.json`.

## License and third-party attribution

No reuse license has been selected for this release. A license should be chosen by the author before inviting derivative use. PhysioNet data retain their original source attribution and terms. All originally generated figures and code are attributed to Yanzhe Zhao unless otherwise identified in accompanying source metadata.
