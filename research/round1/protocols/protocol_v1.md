# Frozen computational and empirical protocol v1

Time: 2026-11-07 02:26 Asia/Shanghai (2026-11-06 18:26 UTC).
This is an internal, timestamped analysis specification, not an externally registered study.

## Status and pilot exposure

Candidate: filter-invariant spectral cycles as a test between reversible latent
activity with channel-specific observation filters, and temporal structure
outside that model class. Prior-art and independent mathematical review remain
open. This protocol is frozen to protect later empirical tests, even if the
candidate is subsequently rejected.

Only EEGMMIDB S001R01 was read at freeze. Its 12-channel split-cycle score was
2.6595533182013496e-5, using the settings below without amplitude rejection.
This single subject is exploratory and will never enter confirmatory tests.
Reserve S001–S010 for implementation/pilot work. S011–S109 remain unseen and
form the confirmatory sample. Do not change the primary protocol after opening
their neural signals. Source metadata and file availability checks are allowed.

## Rival mechanisms and analytic targets

- M0: a stationary, time-reversible real multivariate process, observed through
  one fixed scalar LTI filter per channel, plus mutually independent additive
  channel noises independent of the latent signal. All population spectral
  cycle products are real at every frequency (phase 0 or pi).
- M1: multivariate dynamics with temporal relations that cannot be made
  time-symmetric by channel-wise phase adjustments. At least one cycle product
  has a nonzero imaginary part. This is a statistical mechanism class, with
  multiple possible recurrent, feedforward, and common-input implementations.
- M2: filtering before spatial mixing, time-varying filters, nonstationarity,
  or correlated observation noise. These can break M0's cycle constraint and
  are explicit alternative explanations for sensor-level findings.

Analytic objectives: prove cycle criterion on arbitrary support graphs, minimal
channel count, invariant phase-minimized Gaussian reversal divergence, and a
computable triangle lower bound. Distinguish the population theorem from the
finite-window spectral estimator. Provide explicit false-negative and mixing
counterexamples; never equate a spectral triangle with an anatomical loop.

## General computational validation

1. Random positive-definite Hermitian matrices, dimensions 3–64, nonzero
   diagonal filters with randomized magnitudes and phases. Verify cycle-phase
   invariance and reversal conjugation to numerical precision.
2. Independent multistart minimization checks of the proposed triangle bound.
   A local optimizer returns an upper bound on the true minimum; it cannot
   certify a mathematical lower bound. Proof supplies that certification.
3. Stable linear stochastic neural-network families, dimensions 3, 8, 24, 64:
   symmetric drift/isotropic innovations (reversible), and symmetric plus
   antisymmetric drift (generic irreversible). Vary asymmetry and randomized
   causal one-pole/delay observation filters. Compare ordinary pairwise
   asymmetry and the population closure quantity.
4. Finite-sample calibration using proper complex Gaussian replicas with
   real-gauge-null covariance, varying coherence and replica count. Test
   signed split-half products at the subject/sample level. Quantify Type I
   error and power. Preserve all tested settings.
5. Time-domain finite-window tests with reversible correlated sources and
   heterogeneous causal filters, using the same epoching/taper as real data.
   Examine leakage, measurement noise, and temporal dependence explicitly.
   If the finite-window null is anticonservative, limit the empirical claim
   or freeze a corrected protocol using only pilot subjects, before holdout.

## Primary empirical analysis

Dataset: PhysioNet EEG Motor Movement/Imagery v1.0.0,
DOI 10.13026/C28G6P, open ODC-By 1.0. Record R01 (eyes open) and
R02 (eyes closed), originally 64 scalp channels at 160 Hz.

Fixed channels: F3, F4, Fz, C3, C4, Cz, P3, P4, Pz, O1, O2, Oz.
Use original reference; no data-adaptive spatial decomposition in the primary
analysis. EDF scaling must be checked against physical units and known layout.

Time windows: nonoverlapping 2-second epochs starting at 2,4,...,24 s in half A
and 34,36,...,56 s in half B. The gap separates the halves. Linearly detrend
each epoch and use a Hann window. Compute each Fourier frequency separately,
with no averaging of complex spectra across frequencies. Reject an epoch if
any selected channel's peak-to-peak amplitude exceeds 500 microvolts, contains
nonfinite samples, or has standard deviation below 0.1 microvolt. A record needs
at least eight surviving epochs per half and at least 58 seconds duration.
No replacement subjects; report every exclusion and missing download.

For each half, estimate the spectral covariance across surviving epochs and
normalize by its own autospectral powers to obtain complex coherency C.
For all 220 unordered channel triples with orientation i<j<k, compute
v=Im(C_ij C_jk C_ki). Primary subject score:

Q_s = mean over frequencies 2–30 Hz inclusive and all triples of v_A * v_B.

This cross-half product avoids the inevitable positive floor from squaring a
single noisy estimate. The theorem concerns population spectra. Under
independent, proper-complex Gaussian spectral replicas of the real-gauge null,
the distribution of Q_s is symmetric about zero. In EEG, independence,
stationarity, and spectral leakage are empirical assumptions tested by the
calibration and sensitivity analyses, not exact consequences of epoching.

Primary tests: one-sided subject-level random sign-flip tests of mean Q>0,
separately for R01 and R02, 49,999 random sign patterns (seed fixed in code),
Holm correction across two tests. Also report means, medians, number positive,
95% subject-bootstrap CIs, and standardized mean/sd. Biological sample unit is
the participant; frequencies, epochs, and triangles are not independent N.

Secondary, exploratory: paired eyes-closed minus eyes-open Q, two-sided
sign-flip test. No positive or negative condition difference is pre-required.
Frequency/topography displays are descriptive; no post hoc selection promoted
to a confirmatory regional or band finding.

## Mandatory sensitivity analyses

- Repeat with 4-second epochs (fewer replicas), and full-record alternating
  2-second blocks; label these sensitivity analyses.
- Repeat with common-average reference as a spatial-mixing sensitivity,
  not as a filter-invariance claim.
- Time reversal should conjugate cycle products; Fourier-domain per-channel
  filter multiplication should leave coherency cycle products invariant.
- Apply mild causal time-domain filters/delays and recompute the estimate;
  quantify finite-window deviations rather than asserting machine-precision
  invariance for windowed time-domain data.
- Report strong mixing/rapid-filter examples where the interpretation fails.

## Scientific decision and reporting

Analytic success supports a general identifiability/measurement result.
Empirical success supports irreducible sensor-level spectral timing under the
specified observation/estimation assumptions. Neural circuit topology, causal
direction, consciousness, and metabolic entropy production require distinct
evidence and are outside the empirical claim. Significance, novelty, and
publication readiness are assessed separately. All negative branches remain.
