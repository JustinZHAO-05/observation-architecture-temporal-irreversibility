# Major/Minor Revision Response Matrix — work completed in this turn

Status legend: **implemented & verified** = a deliverable exists with code and output; **partially addressed** = scientific limitations or an outstanding step remain; **open** = requires evidence not generated here. None of these statuses asserts journal acceptance.

| Referee issue | Status | Action / evidence | Remaining question |
|---|---|---|---|
| M1 literature priority | Partially addressed | Corrected Bi–Calhoun title; added Lakshmanan et al. (TD-GPFA), Rutten et al. (NeurIPS 2020), Xu (2026) and model-class comparison in Introduction/Discussion | Exhaustive formula-level priority and independent expert judgment |
| M2 latent dynamical constraints | Implemented for a new subclass | New **temporally white** correlated Gaussian representation for $S=I-ib\sin\omega K$ in any $d$; 23,520 numerical checks, S9 | General arbitrarily restricted network structures, minimal latent dimension |
| M3 joint low-frequency and broadband power | Partially addressed | Exact bounded joint limit and 440 checks; S10; text restricts optimum to pointwise/fixed gain | Global optimal total spectral power with physical causal constraints |
| M4 independent $B,T_L$ calibration | Implemented in restricted known-shape class | 540 separately calibrated test analyses, alpha split, S12 | Unknown normalized spectral shape, real EEG calibration |
| M5 EEG relevance | Partially addressed | Revised precise statement about rereferencing vs source-delay map | Independent neural experiment discriminating latent models |
| M6 finite-window null and mechanism | Implemented | Clarified observed vs latent null; PD local spectral ablation with both slopes removed separately; S11 | More realistic device-specific multi-frequency calibration |
| M7 mathematical audit | Partially addressed | Algebraic derivations and independent experiments; previous code-checks retained | External independent proof verification incl. confidence constants |
| Minor: abstract economy | Partially addressed | Maintained coherent revised story | Editorial length reduction possible |
| Minor: theory/physical scope | Addressed | Distinct fixed-$b$, joint-$b(\theta)$, and source-vs-sensor operator claims | Broad physical model generalization |
| Minor: phase notation | Partially addressed | Added new exact notation and spectrum checks | Full notation audit |
| Minor: figures | Partially addressed | Supplementary S9–S12 generated; main Fig1–7 preserved | Integrate new visual story into final redesigned main figures |
| Minor: EEG statistics | Addressed in interpretation | Scope, exploratory status retained | Independent measurement calibration |
| Minor: references | Addressed for identified entries | Corrected Bi title and new verified citations | Final reference DOI/author audit across entire list |
| Minor: data deposit & disclosure | Open by author | Existing package and reproduction code provided | Permanent versioned public repository, author disclosures |

## Revision figure edit instructions

- **Existing Fig. 2:** retain observation-equivalence and the 6D correlated-latent construction. Add a small visual inset or complementary Supplement S9 showing the stronger *temporally white* latent subclass, with constant positive latent covariance and the one-sample observation delay. Do not relabel the old exact-latent-lag curves as white-latent curves.
- **Fig. 3:** retain fixed-$b$ $\theta^{-2}$ asymptotic plot, but label it explicitly as a fixed-strength path. Add a separate curve or inset from S10 following $b=\beta\sin\omega$, $\theta=\omega$; draw its finite endpoint $(1+\beta^2)/2$. Use different linestyles, not only color.
- **Fig. 5:** retain the original 9.75/10.25 Hz counterexample. S11 shows the independent PD local spectral ablation: both amplitude and phase slopes active vs each one removed. Present as two results from distinct model settings with separate caption language.
- **Fig. 6:** supplement existing oracle-$B$ power heatmap with S12, an independent calibration-power panel. Plot $m\in\{16,64,128\}$ and positive fractions $15/90,59/90,79/90$ for $b=.9$, plus the null and oracle conditions. State the calibration data are independent and the MA shape is known.
- **Fig. 7:** the EEG rereferencing evidence remains illustrative and exploratory; retain exact matched windows and label the operation as spatial rereferencing, not a direct physical test of Theorem 1.
