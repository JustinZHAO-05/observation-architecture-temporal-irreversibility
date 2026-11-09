# Scientific completion ledger

Completed in the research-challenge conversation on 6 November 2026 UTC.
This ledger records scientific decisions, including the rejected starting
conjecture. The final synthesis is `output/neural_time_arrow_report.md`.

## Central decision

**The initial practical conjecture was falsified.** A positive cross-half
spectral-cycle score does not provide a uniformly valid rejection of every
reversible latent process observed through arbitrary channel-specific LTI
filters. An explicit reversible Gaussian latent model, processed with the
frozen finite-window estimator, produced a positive score and a first-99-record
sign-flip p value of 0.00008.

The completed replacement result identifies both sides of the problem: an
exact population invariant and quantitative bound, and a constructive
finite-record identification obstruction when channel-filter memory is
unrestricted. The empirical EEG result concerns a reproducible finite-window
sensor statistic within that identified boundary.

| Work item | Completed outcome | Evidence |
|---|---|---|
| Population cycle geometry | Established closure-phase and real-gauge results are attributed and specialized to the observation model. | Final report section 2; prior-art reviews |
| Phase-relaxed reversal density | Derived invariance, zero set, and Gaussian-noise contraction. | Final report section 3; independent mathematical audit |
| Explicit triangle lower bound | Proof completed; weak-coherence/weak-phase sharpness and weakest-edge interpretation derived. | Theorem 2; `reviews/math_review_v2_addendum.md` |
| Numerical certificates | Primal/dual intervals computed for 480 matrices; inverse-residual correction retained; higher-dimensional gaps reported. | `results/variational_certificates.csv`; archived v1 table |
| Finite-record representation | Delayed shared innovations reproduce finite moving-average record laws; positive-definite extensions and approximation argument establish the stated no-go consequence. | Theorem 3; independent covariance construction |
| Finite-bandwidth mechanism | Leading amplitude-slope/group-delay term, remainder control, and Hann-window scaling derived. | Final report section 5; exact covariance calculations |
| Conditional finite-error certificate | A quantitative lower bound follows when a simultaneous total spectral error bound is externally justified. | Final report section 5; 1,000 independent checks |
| Calibration and falsification | Ideal spectral and randomized time-domain calibrations completed; a structured within-null failure preserved. | `results/finite_spectral_calibration.csv`; `reviews/adversarial_M0_60s_scores.npy` |
| Prespecified human EEG analysis | Both baseline runs analyzed for all 109 participants; holdout includes 78 eyes-open and 84 eyes-closed records, with 73 complete pairs. | Frozen protocol; subject, summary, and paired tables |
| Independent raw-data reproduction | All 218 records decoded independently; all inclusion decisions and 177 retained scores reproduced within 9.8649e-17. | `reviews/empirical_audit_v1.md` and exact outputs |
| Sensitivity interpretation | Window length, reference, coherence weighting, and sample/epoch changes documented; fixed-original-mask causal filtering added. | Sensitivity tables; `results/matched_filter_summary.json` |
| Reporting | Full report, figures, exact results table, source code, frozen decisions, and independent reviews retained. | `output/`, `figures/`, `src/`, `protocols/`, `reviews/` |
| Reproduction entry point | Portable subprocess driver and dependency versions supplied; driver syntax and dry-run plans checked without rerunning the complete study during packaging. | `src/reproduce_all.py`; `requirements.txt`; `README.md` |

## Interpretation of the completed EEG result

The mean primary Q is 6.984483107226563e-5 in retained eyes-open records and
1.9844179556892353e-4 in retained eyes-closed records. The frozen two-condition
Holm-adjusted p values are 0.00004 under the specified finite-window
sign-symmetry assumptions. Q is dimensionless and weighted by coherency
magnitudes. The paired difference is exploratory and associated with both
eye condition and the dataset's run ordering.

These results support repeatable sensor-level spectral structure. The
finite-record counterexample and representation theorem determine why the
same scores do not identify a unique latent circuit or thermodynamic mechanism
over unrestricted observation filters.

## Originality and external assessment

The targeted primary-literature review found close precedents and explicitly
attributes them. It did not locate an exact match for the proposed
reversal-specific quotient, the stated sharp bound, or the delayed-innovation
finite-record construction within its documented search and reading coverage.
Priority of these candidate contributions remains subject to expanded
literature review and external peer review. Mainstream-journal publication
and editorial acceptance remain external outcomes; this package documents
the completed derivations, calculations, empirical evidence, and revisions.

The independent implementations and adversarial reviews were carried out
within the AI-assisted research workflow. They are retained as reproducibility
evidence and are distinct from external journal peer review.
