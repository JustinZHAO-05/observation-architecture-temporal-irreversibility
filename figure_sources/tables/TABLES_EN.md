# Manuscript tables and table captions

Identifiers below are package labels. Final numbering follows manuscript integration. The eight display tables retain the working drafts' precision. The source index also links the full-precision archives.

## T01_observation_regimes

Identification under different observation architectures.

[Editable CSV](T01_observation_regimes.csv)

| Observation regime | Identification statement |
| --- | --- |
| Separate filters applied at the defined sensor channels; exact population spectrum available | Real-gauge cycle obstructions survive. The phase-relaxed reversal quantity and triangle lower bound remain informative. |
| Same sensor-diagonal class; arbitrary filter memory; fixed finite record | The first-round serialization construction gives finite-record nonidentifiability uniformly over this unrestricted class. |
| Source filters followed by real spatial mixing; correlated reversible latent sources allowed | The new one-delay construction can match the entire target Gaussian process. More data alone do not resolve this population ambiguity. |
| Sensor-diagonal class plus externally bounded observed spectrum and covariance tail | The new finite-record and continuous-frequency confidence certificates give conditional, statistically valid lower bounds. |

## T02_one_sample_construction

Checks of the three-channel one-sample population construction.

[Editable CSV](T02_one_sample_construction.csv)

| Quantity | Result |
| --- | --- |
| Observed / latent dimensions | 3 / 6 |
| Observation delay | 1 sample |
| Maximum covariance difference for the complete 32-point record | 0.0 in double precision |
| Maximum spectral difference on 513 frequencies | $2.25\times10^{-16}$ |
| Minimum latent spectral eigenvalue on that grid | 0.0475 |
| Maximum absolute imaginary triangle | 0.140296 |
| Maximum observed reversal density | 8.526316 |

## T03_rate_certificates

Positive continuous-rate certificates and median rate bounds in nats/sample.

[Editable CSV](T03_rate_certificates.csv)

| Maximum delay | Samples | Positive bounds / 64 | Median rate lower bound |
| --- | --- | --- | --- |
| 0 | 32,768 | 3 | 0 |
| 0 | 131,072 | 64 | 0.002067 |
| 0 | 524,288 | 64 | 0.008313 |
| 8 | 32,768 | 0 | 0 |
| 8 | 131,072 | 0 | 0 |
| 8 | 524,288 | 64 | 0.000256 |

## T04_matched_eeg

Mean scores by reference for the same complete-window EEG recordings.

[Editable CSV](T04_matched_eeg.csv)

| Condition | Matched records | Original-reference mean Q | Average-reference mean Q | Ratio of means |
| --- | --- | --- | --- | --- |
| Eyes open | 52 | $7.4189\times10^{-5}$ | $3.8283\times10^{-4}$ | 5.1602 |
| Eyes closed | 61 | $1.9855\times10^{-4}$ | $5.2276\times10^{-4}$ | 2.6329 |

## TS_population_checks

First-round population and algebraic validation summarized in the supplement.

[Editable CSV](TS_population_checks.csv)

| Validation | Scope | Observed result |
| --- | --- | --- |
| Random positive-definite matrices | 540 matrices; dimensions 3, 8, 24, 64 | Maximum cycle-invariance error 1.87e-16 |
| Stable linear stochastic network ensemble | 192 conditions; dimensions 3, 8, 24, 64; 12 networks per dimension; 4 asymmetry levels | Maximum cycle change after causal pole/delay filters 9.28e-17 |
| Reversible members of the network ensemble | 48 symmetric networks | Mean filtered pairwise imaginary-coherency RMS 0.1068; maximum cycle RMS 2.08e-17 |
| Independent mathematical implementation | 300 random 3 by 3 matrices | No violation of the triangle inequality; minimum numerical margin 6.82e-7 |
| Phase optimization certificates | 480 matrices; dimensions 2, 3, 8, 24 | Numerical intervals reported explicitly; higher-dimensional gaps retained |
| Wick-moment calculation | All six pairings; Monte Carlo at 5 replica counts | Exact algebra agrees to 5.55e-17; simulations agree within sampling error |

## TS_eeg_primary

Primary held-out EEG results under the original reference and first-round eligibility rule.

[Editable CSV](TS_eeg_primary.csv)

| Condition | Included participants | Positive Q | Mean Q | 95% subject-bootstrap interval | Holm-adjusted sign-flip p |
| --- | --- | --- | --- | --- | --- |
| Eyes open | 78 | 62 | 6.9845e-5 | [5.2742e-5, 8.6895e-5] | 0.00004 |
| Eyes closed | 84 | 77 | 1.9844e-4 | [1.6301e-4, 2.3502e-4] | 0.00004 |

## TS_eeg_window_sensitivity

Four-second window sensitivity for held-out EEG.

[Editable CSV](TS_eeg_window_sensitivity.csv)

| Sensitivity | Condition | N | Mean Q | 95% subject-bootstrap interval | Holm p |
| --- | --- | --- | --- | --- | --- |
| 4-second window | Open | 64 | 5.5308e-5 | [2.4288e-5, 8.5545e-5] | 0.00046 |
| 4-second window | Closed | 76 | 1.0680e-4 | [7.5198e-5, 1.3780e-4] | 0.00004 |

## TS_eeg_fixed_mask_filter

Causal-filter perturbation with participants and accepted-window masks fixed.

[Editable CSV](TS_eeg_fixed_mask_filter.csv)

| Same-mask perturbation | Open | Closed |
| --- | --- | --- |
| N | 78 | 84 |
| Pearson correlation of original and filtered Q | 0.99683 | 0.99917 |
| Spearman correlation | 0.99530 | 0.99719 |
| Relative change in group mean | -0.591% | -0.368% |
| Maximum exact Fourier-domain cycle change | 7.82e-16 | 8.50e-16 |

## TS1_gaussian_models

Gaussian model settings and analysis units for the finite-record construction and Round 2 population and certificate studies.

[Editable CSV](TS1_gaussian_models.csv)

5 rows. The complete table is in the CSV.

## TS2_eeg_inclusion

Record-level EEG selection and complete-window decisions under both references.

[Editable CSV](TS2_eeg_inclusion.csv)

218 rows. The complete table is in the CSV.

## TS3_audit_metrics

Archived numerical-audit metrics and check flags. Per-case records retain optimizer outcomes.

[Editable CSV](TS3_audit_metrics.csv)

97 rows. The complete table is in the CSV.
