# Response to the PRE-style internal review — Revision R4

Manuscript: *Observation architecture and the identifiability of temporal irreversibility*

Author: Yanzhe Zhao, School of Future Technology, Tianjin University

This document responds to the critical review developed during preparation of the manuscript. It is not a representation of comments received from the journal. All computations reported below were executed for the present revision; inherited results are identified separately. Acceptance and external mathematical assessment remain decisions of the authors and journal referees.

## Major comment 1 — Originality and relation to spectral realization

**Action.** The Introduction and a new Supplementary comparison table now distinguish standard target-dependent spectral factorization from the fixed-operator problem studied here. Classical factorization permits a full target-dependent causal matrix filter acting on white innovations. Our general theorem fixes the observation operator to [I, z^{-1}I] for every target and assigns the target dependence to a positive-definite real even latent spectrum of twice the observed dimension. The finite-order extension preserves this fixed operator. The white-latent MA(1) construction is now explicitly treated as an explanatory special case of standard moving-average realization, rather than a separate foundational novelty claim.

The comparison covers incomplete observation, delayed GPFA, non-reversible Gaussian processes, the cross-spectral hidden-drive witness, directional time-series inference, and two-branch alias calibration. The latter citation was updated to its version-3 title and DOI. We make no unrestricted priority claim. Source access and reading coverage are recorded in SOURCE_AUDIT.md; for the latest Xu preprint the primary repository description was available, but its complete PDF was not retrieved. Consequently no formula-level priority claim rests on an assumed reading of that text.

**Location.** Introduction; Supplementary section “Relation to spectral realization and neighboring observation models”; references.bib.

## Major comment 2 — Dynamical constraints and physical interpretation

**Action.** A new finite-order result addresses the criticism that the general latent representation could require arbitrarily complicated temporal correlations. Every strictly positive spectral trigonometric polynomial admits an exact one-sample reversible lift with a positive spectral trigonometric polynomial as its latent spectrum. Its covariance support is finite, and polynomial matrix spectral factorization supplies a causal finite moving-average realization. The proof uses uniform Fejér approximation within an affine family that preserves the observation identity exactly. It does not claim a target-independent minimum order.

We tested 72 target models, with dimensions 2, 3 and 6 and target MA orders 1, 2 and 3. Every target admitted an accepted finite-order lift; latent covariance orders ranged from 4 to 34. Maximum relative reconstruction error was 1.22e-15. Numerical positivity margins include a derivative allowance between frequency samples. Failed trial degrees and refined verification grids are retained.

We also clarified why a reversible latent process can yield irreversible observations: the time-extended observation map does not commute with reversal. A thermodynamic description of the observation device would involve additional physical variables and is separate from reversibility of the nominated latent Gaussian coordinates.

**Location.** Main Sec. III, “Finite-order latent dynamics”; Appendix “Finite-order reversible representations”; Fig. S13.

## Major comment 3 — Pointwise versus broadband resource optimum

**Action.** The fixed-strength inverse-square law is explicitly distinguished from the joint physical path b(omega)=beta sin(omega). The latter has a finite endpoint limit (1+beta^2)/2. We further establish the exact integrated spectral-trace optimum for the entire rotational spectrum g(omega)[I+i beta sin(omega)J]. An explicit bounded, real even PSD optimizer gives a valid stationary latent process. Continuous strictly positive-definite feasible spectra approach the same integrated optimum, and each has a causal square-summable spectral factor.

The proof treats an important subtlety: the optimal value is continuous, while the optimizer's cross-block parameter can jump where cos(omega)=0. The old assertion that the limiting optimizer is continuous was corrected. A cutoff-and-convex-mixture construction resolves the continuous-spectrum infimum.

Fifteen strength/color settings were evaluated. At beta=0.8, the total minimum trace ratio is 0.854239 for a flat spectrum and 0.829345 for color pole 0.8, compared with 1 for the simple feasible white/common-filtered representation. Reconstruction error was below 1.78e-15. These are exact results for a specified broadband family and fixed observation gains; a prescribed network topology or fixed latent order defines a further optimization problem and is not included in the claim.

**Location.** Main Sec. IV; Appendix “Broadband optimal spectral trace”; Fig. S14; broadband_optima.csv.

## Major comment 4 — Practical calibration without oracle spectral shape

**Action.** The new calibration theorem requires a known dependence-class envelope T_L <= tau_L B_* but does not require the normalized spectrum, covariance shape, scale, or true maximum B_*. On an independent calibration record, a simultaneous Gaussian spectral error bound is inverted to obtain the data-dependent upper confidence bound U_B. If its deterministic resolution denominator is nonpositive, the procedure explicitly abstains. An independent test record then uses B=U_B and T_L=tau_L U_B; the combined failure probability is at most alpha_cal+alpha_test.

The experiment uses 600 independent calibration/test pairs, yielding 1,680 calibration analyses and 8,520 test analyses with nested lengths and separately labeled oracle controls. There were 1,320 finite calibration bounds and 360 deterministic short-record abstentions. All finite bounds covered the diagnostic population grid maximum. All calibrated certificates stayed below the known analytic population lower bound, and no calibrated null analysis produced a positive certificate.

For the b=0.9 unknown-shape MA(1) alternative, 65,536 calibration samples and 32,768 test samples yielded 120/120 positive certificates; 16,384 calibration samples with 131,072 test samples also yielded 120/120. The median U_B/B_* ratio decreased from about 2.68 to 1.20 as calibration length increased. These results materially extend R3, where the normalized spectral shape was supplied.

Long-correlation alternatives were included rather than discarded: valid AR–MA calibrations returned zero certificates through 524,288 test samples. In a separate stress experiment, the wrong finite-support assumption caused 0/80 spectral-envelope coverage, whereas a valid tail envelope gave 80/80. Both finite-sample arms returned zero certificates. The paper therefore reports a useful guarantee and its substantial long-memory power cost, rather than a universal short-record detector.

**Location.** Main Sec. VI, new independent-calibration subsection and new main figure; Appendix “Independent calibration with unknown spectral shape”; Figs. S15 and S17; full calibration/test CSVs.

## Major comment 5 — Role of the EEG illustration

**Action.** The 71-participant matched-window analysis remains an exploratory observation-level application. We added controlled known transformations to the archived raw S011R01 EEG recording. Eighty diagonal frequency responses preserved normalized cycles to 1.22e-15, and eighty real orthogonal rotations preserved raw reversal density to relative error 7.92e-14 while generally changing cycles. The average-reference comparison is explicitly distinguished from an invertible square rotation.

These are 161 numerical transformations of one recording, not additional independent biological observations. The diagonal operations are applied after windowing; time-domain filtering before estimation is governed by the separate finite-bandwidth analysis. This study directly tests the claimed observation-level transformation rules on an EEG-derived spectrum. It does not claim an independently calibrated latent neural reversal rate or a physiological intervention on latent brain dynamics.

**Location.** Main Sec. VII; new controlled-transformation subsection; Fig. S16. Cohort effect sizes and uncertainty intervals are retained.

## Major comment 6 — Statistical null and finite-window mechanism

**Action.** The nominal sign-flip test is now described by its actual score-symmetry assumption. The structured example concerns a reversible latent model with real population closure under diagonal filtering. Its observed process may nevertheless have nonzero raw reversal divergence. Thus the invalid inference concerns attribution to latent irreversibility, rather than an indiscriminate claim that every test of observed irreversibility is wrong.

The R3 amplitude-slope and differential-phase-slope ablations remain in the Supplement; removing either ingredient eliminates the local imaginary closure at floating-point precision. The present wrong-tail stress study further separates envelope failure from finite-sample rejection. A deterministic population-truncation calculation shows how nonzero closure can appear after incorrect lag truncation; that calculation is labeled as a limiting diagnostic, not a Monte Carlo false-positive count.

**Location.** Main Sec. VI.B; Appendix on finite-bandwidth bias; Figs. S11 and S17.

## Major comment 7 — Proof and implementation verification

**Action.** The notation audit found and fixed an actual error: real-process frequency reflection is S(-omega)=overline{S(omega)}=S(omega)^T, whereas * denotes the conjugate transpose. The resource-optimum proof now distinguishes a continuous optimum value from a discontinuous optimizer selection. The concentration proof explicitly gives the off-diagonal quadratic-form Frobenius and operator norm constants, the d^2 F real-component union bound, and the independence requirement for calibration/test composition.

New proofs are provided in the main Appendices rather than deferred to inaccessible source files. A separately implemented audit checks spectral lag loops against full time-kernel quadratic forms (20 settings, maximum discrepancy 1.22e-15), coefficient-domain latent/output covariance identities (4.44e-16), and a complete block covariance transformation (6.66e-16). Twelve 70-digit evaluations check the cancellation-sensitive joint-limit identity; 150 new random matrix cases check real-coordinate invariance and the triangle/full-vector inequality. Per-repetition counts are reconciled with the output CSVs.

These are analytic arguments and independent computational representations within the present study. They are not described as external human verification or machine-checked formal proofs.

**Location.** Definitions; Appendices; independent_audit.py and independent_audit.json.

## Minor comments — completed editorial and presentation changes

1. The abstract was shortened and now distinguishes fixed-frequency, broadband, and finite-data results.
2. Notation now separates transpose, adjoint and entrywise conjugation, and defines the calibrating spectral norm for indefinite empirical spectra.
3. The broad resource discussion now reports the completed rotational broadband result and reserves fixed-order/anatomical constraints for explicitly different problems.
4. Dense-support wording was replaced by complete-support wording where triangles alone generate the cycle constraints.
5. The known-shape calibration description now refers to an independent calibration record, not independent time samples of a correlated MA process.
6. Duplicate complete proofs were removed from the Supplement and replaced with references to the main Appendices. Numerical designs, negative results, and all original supplementary figures remain.
7. A new main calibration figure and five new supplementary figures were added. The R3 white-latent figure now says “23,520 evaluations,” not “23,520 independent checks.”
8. Original main figures retain their scientific content. The inserted calibration figure changes the later EEG figure number; all text uses LaTeX labels so references update consistently.
9. The Bi–Calhoun title is correct, Xu's version-3 record is cited, and classical matrix-factorization references are added. Full access coverage is recorded separately.
10. Data/code statements accurately identify the supplied archive and original PhysioNet source. A public archival DOI has not been invented. Author-controlled submission declarations and AI disclosure remain for author completion.
11. Original EEG analyses, R3 results, and R4 additions are distinguishable in the package. Fixed seeds, raw example input, per-repetition outputs, build instructions and SHA-256 checksums are included.

## Revision status

The specified theoretical claims, numerical studies and observation-level EEG controls have been revised and tested within their declared model classes. The strongest remaining practical limitation is the conservative power in long-correlation settings, which is now an explicit result. Calibration of a real brain's latent observation operator and unrestricted model-free covariance tails are not claimed as accomplishments of this manuscript. Submission still requires the author's scientific sign-off and journal-specific declarations; external referees determine acceptance and originality.
