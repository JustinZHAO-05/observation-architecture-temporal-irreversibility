# Independent empirical and statistical audit v1

Reviewer: data_scout. Audit completed 2026-11-06 UTC. The initial independent
dataset scout was frozen before this review. This audit reads the established
mathematical review and assesses implementation, reproducibility, and the
scope of empirical inference; it does not claim independent discovery of the
finite-window counterexample.

## Decision

**The recorded empirical results reproduce.** An independent implementation
decoded all 218 original EDF records, recomputed every primary quality-control
decision, and recomputed all 177 retained scores. All inclusion decisions and
all available epoch counts agree. The largest absolute score difference is
**9.864884516902483e-17**, including decimal CSV parsing error. No material EDF
scaling, channel selection, triangle-orientation, aggregation, or participant
counting error was found.

The empirical result is reproducible, coherence-weighted **finite-window
sensor spectral closure across two separated recording intervals**. The
reported sign-flip p values test a conditional finite-window sign-symmetry
null. The mathematical review's explicit reversible-latent, diagonal-LTI
counterexample establishes that this null is narrower than arbitrary latent
reversibility with arbitrary channel filters. The strongest scientific package
combines the exact population theory with the finite-record obstruction and
uses the EEG result to demonstrate the measured phenomenon and its dependence
on spectral resolution and reference.

## 1. Audit implementation and provenance

Reviewed: `theory_v1.md`, `protocols/protocol_v1.md`,
`protocols/freeze_v1.json`, `src/closure_core.py`, `src/eeg_study.py`, the primary
subject/summary/paired results, the four-second, alternating, common-average,
and initially filtered branches, and `reviews/math_review_v1.md`.

The independent code, `src/empirical_audit_independent.py`, imports no other
project module. It implements EDF field decoding and calibration directly,
subtracts the least-squares intercept and slope with a centered-time projection,
constructs the periodic Hann window from its cosine formula, forms spectral
matrices with separate matrix products, and computes all 220 oriented triangle
products. It independently recomputes participant summaries, sign-flip Monte
Carlo tests, binomial sign tests, bootstrap intervals, paired summaries, and
matched-participant sensitivity means. The audit tests are verification outputs,
not a replacement confirmatory analysis or an additional discovery family.

The current protocol SHA-256 exactly matches the freeze file:

`735182a4aa88b16ef9c59bba978099af52172273cd93ec5d0ae6ad47d72bbcce`.

The recorded freeze time precedes the primary run's recorded start time.
This verifies the retained artifact trail; it remains an internal specification,
as explicitly stated in the protocol.

Dataset identity and run mapping were checked against the primary provider:

- [PhysioNet EEG Motor Movement/Imagery Dataset v1.0.0](https://physionet.org/content/eegmmidb/1.0.0/), DOI 10.13026/C28G6P.
- [Original PhysioNet description](https://archive.physionet.org/pn4/eegmmidb/): 109 volunteers, 64 EEG channels at 160 Hz, run 1 eyes open, run 2 eyes closed.

### EDF channel/scaling checks

S011R01, S011R02, S035R01, and S035R02 each contain 65 EDF signals including
the annotation channel, last 61 seconds, and occupy 1,275,936 bytes. The 12
selected zero-based signal indices are:

| Channel | F3 | F4 | Fz | C3 | C4 | Cz | P3 | P4 | Pz | O1 | O2 | Oz |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Index | 31 | 35 | 33 | 8 | 12 | 10 | 48 | 52 | 50 | 60 | 62 | 61 |

The checked labels have EDF trailing periods, correctly stripped by the
analysis. Their physical and digital ranges are both [-8092, 8092], giving
exactly 1 microvolt per digital unit and zero offset; their unit fields are
`uV`. The selected full-record extrema are [-148,312], [-149,140], [-213,216],
and [-201,173] microvolts respectively. These checks support the numerical
500-microvolt epoch threshold. "Original reference" denotes the as-distributed
signals; the audit does not infer an undocumented hardware reference identity.

| Record | Independent Q | Reported Q | Absolute difference |
|---|---:|---:|---:|
| S011R01 | -2.0474507158285427e-5 | -2.0474507158285500e-5 | 7.12e-20 |
| S011R02 | 3.7383652896388707e-4 | 3.7383652896380000e-4 | 8.71e-17 |
| S035R01 | -4.2077000116851540e-6 | -4.2077000116852670e-6 | 1.14e-19 |
| S035R02 | 2.1400593045127093e-4 | 2.1400593045120000e-4 | 7.09e-17 |

These examples were specified for audit before looking at their Q values;
the all-record comparison is retained in the machine-readable outputs.

## 2. Primary quality control and sample units

There are 99 prespecified holdout participants, S011-S109, and two baseline
records per participant. All 198 holdout files are available. The primary
analysis retains 78 eyes-open records and 84 eyes-closed records, with 73
participants retained in both conditions. The excluded counts are therefore
21/99 and 15/99, and the paired sample consists of 73 independent people.

All holdout epoch exclusions arise from the amplitude criterion. Across the
24 scheduled epochs per record, the independent audit finds 382 rejected
eyes-open epochs and 252 rejected eyes-closed epochs. There are zero flatness
or nonfinite rejections. These counts include both halves even for records
where the main implementation returns early after half A fails. The main
table's unfilled half-B counts for such records are a logging shortcut, not a
different inclusion rule; the audit CSV supplies complete masks and counts.

Eyes-open excluded IDs:
22, 23, 27, 28, 36, 43, 44, 48, 52, 54, 59, 61, 75, 87, 88, 90, 91, 96,
103, 108, 109.

Eyes-closed excluded IDs:
17, 32, 44, 48, 52, 54, 59, 60, 75, 86, 87, 95, 96, 103, 109.

The primary pipeline averages 57 frequency bins and 220 triangles into one
score per participant per condition before inference. No frequency, triangle,
or epoch is counted as an independent biological observation. Separate
condition tests use participant-level sign flips; Holm adjustment is valid
even though the two conditions share participants. The condition contrast
correctly uses complete participant pairs. Pilot participants S001-S010 appear
separately and do not enter the holdout inference.

The retained participants define a quality-controlled sample. Condition-linked
artifact rates affect selection; the paired contrast addresses differences in
participant membership but still uses condition-specific surviving epochs.
The threshold handles large excursions and flat channels, while the analyzed
sensor signals can retain physiological and reference-related contributions.

## 3. Reproduced primary results and conditional inference

Values below are the frozen primary estimates and their original participant
bootstrap intervals. The independent recomputation gives the same means to
roundoff; its separate Monte Carlo intervals differ only by resampling noise.

| Condition | n | Q>0 | Mean Q | Median Q | SD Q | Original 95% bootstrap CI |
|---|---:|---:|---:|---:|---:|---|
| Eyes open | 78 | 62 | 6.984483107226563e-5 | 7.177058264870454e-5 | 7.762243120931906e-5 | [5.274181528040408e-5, 8.689473006291878e-5] |
| Eyes closed | 84 | 77 | 1.9844179556892353e-4 | 1.813311959715070e-4 | 1.6895742129399146e-4 | [1.6300682421205705e-4, 2.3502345491634334e-4] |

Both frozen one-sided sign-flip tests attain their 49,999-draw resolution floor,
p=2e-5, with Holm-adjusted p=4e-5. An independent 99,999-draw implementation
attains its corresponding floor, p=1e-5, for each. Independent exact binomial
sign tests for a zero median yield 7.564890688771694e-8 and
2.5687823496812516e-16. The manuscript should retain its frozen test and avoid
interpreting the numerical Monte Carlo floor as a precise tail probability.

The sign-flip procedure's scientific null is that each participant's finite
window Q has an appropriate distribution symmetric around zero, independently
across participants. The sign test additionally verifies the prevalence of
positive scores under a zero-median reference. Neither calculation controls
Type I error for the entire latent M0 class once that class permits the
finite-window counterexample in the mathematical review. Reporting the
positive EEG signal and the conditional test is justified; an omnibus M0
rejection would contradict the constructed counterexample.

The split-half dot product addresses the positive noise floor from squaring
one spectral estimate. A repeatable bias in each half also gives a positive
product. The primary halves are separated by eight seconds, which is a useful
design choice; their statistical independence and stationarity remain
assumptions about these short recordings. Nonoverlapping epochs and frequency
bins have not been promoted to exact independent Gaussian samples.

## 4. Condition association and coherence weighting

Among the 73 matched holdout participants, the frozen eyes-closed minus
eyes-open mean difference is **1.274752774155147e-4**, with participant-bootstrap
95% CI **[8.533065332642254e-5, 1.7217201772203448e-4]**. The frozen exploratory
two-sided sign-flip p is 2e-5; 52/73 paired differences are positive. This is a
within-participant baseline-condition association. Run number and eye condition
are tied in the documented acquisition scheme, so an isolated causal
eye-closure effect is not identified by this analysis.

For a triangle in half h, write

    v_h = (|C12,h| |C23,h| |C31,h|) sin(Phi_h).

Consequently, the product used in Q equals the product of the six coherency
magnitudes times sin(Phi_A) sin(Phi_B). Q combines the size and consistency of
non-real cycle phase with the strength and estimation reliability of the three
pairwise coherencies. The larger eyes-closed score can reflect changes in
coherence, signal-to-noise ratio, spectral structure, phase organization, and
between-half stability. The directly supported condition result is an increase
in this composite sensor measure. A pure increase in phase frustration or a
quantified increase in latent Gaussian reversal divergence would require a
distinct estimator and validation.

## 5. Sensitivity analyses: sample membership and matched comparisons

The following means use each branch's own retained holdout sample. They are
descriptive sensitivity results, not independent replications.

| Analysis | EO n | EO mean Q | EC n | EC mean Q |
|---|---:|---:|---:|---:|
| Primary, original reference | 78 | 6.984483107226563e-5 | 84 | 1.9844179556892353e-4 |
| Four-second epochs | 64 | 5.530766990319098e-5 | 76 | 1.0679922897060034e-4 |
| Alternating two-second epochs | 86 | 8.168377498945767e-5 | 91 | 2.1201176701507742e-4 |
| Common-average reference | 95 | 3.659573549365262e-4 | 94 | 4.6262742577594105e-4 |
| Initial causal-filter branch, QC recomputed | 84 | 7.122225294308431e-5 | 94 | 2.0485654347747928e-4 |

Matching participant membership supplies the more interpretable comparison:

| Comparison against primary | Condition | Common n | Primary mean in common n | Sensitivity mean in common n | Pearson r of subject scores |
|---|---|---:|---:|---:|---:|
| Four-second epochs | EO | 64 | 6.974191909952347e-5 | 5.530766990319098e-5 | 0.238784010206015 |
| Four-second epochs | EC | 76 | 2.0205298082649946e-4 | 1.0679922897060034e-4 | 0.35249890579411236 |
| Alternating epochs | EO | 78 | 6.984483107224940e-5 | 8.501023893099345e-5 | 0.4429122462816666 |
| Alternating epochs | EC | 84 | 1.9844179556888493e-4 | 2.114860504195037e-4 | 0.694893149511149 |
| Common-average reference | EO | 78 | 6.984483107224940e-5 | 3.659644313749846e-4 | 0.3890699643186473 |
| Common-average reference | EC | 84 | 1.9844179556888493e-4 | 4.891550771487006e-4 | 0.3175369459371902 |
| Initial causal filtering, QC recomputed | EO | 78 | 6.984483107224940e-5 | 7.074842145255713e-5 | 0.9682013950594835 |
| Initial causal filtering, QC recomputed | EC | 84 | 1.9844179556888493e-4 | 1.9738084351136572e-4 | 0.9950991419162379 |

Four-second inclusion is a strict subset of primary inclusion. Its lower Q
therefore persists after matching participants, especially in eyes-closed
recordings. Window length changes the spectral kernel, replica count, finite
sample coherency bias, and epoch rejection. These comparisons document
resolution dependence and give no isolated empirical estimate of a T^-4
leakage law. The four-second exploratory condition difference is weaker:
mean 4.634773136003009e-5 across 61 pairs, with the original sign-flip p=0.04276.

Alternating halves interleave neighboring epochs, change the time coverage,
and increase the number of candidate epochs from 12 to 14 per half. Their
positive scores support within-record repeatability under another split, while
their temporal separation is less suited to justifying independent halves.

Common-average referencing subtracts the average over all 64 EEG channels,
then selects the same 12 channels. It is spatial mixing, outside the diagonal
filter group. Its substantial score increase persists in matched participants;
its modest subject-score correlations show material reference sensitivity.
It also adds 17 EO and 10 EC participants, and changes accepted epoch counts
for 25/78 EO and 21/84 EC participants already retained by the primary analysis.
The result is a sensitivity to the observation coordinates and preprocessing,
not evidence of reference invariance.

The initial causal-filter branch adds six EO and ten EC participants and
changes surviving epoch counts for 21/78 EO and 15/84 EC originally included
participants. Even its intersection-only comparison still changes epochs.
Its high correlations and similar means are useful descriptive checks, but
the clean filter-perturbation comparison should use the original sample and
the original epoch mask. Root is supplying that fixed-mask analysis separately;
the original branch must retain its explicit recomputed-QC label. This audit's
reproduction claim concerns the primary pipeline; it does not independently
reproduce a later fixed-mask implementation.

## 6. Recommended empirical wording and material issues

Recommended result:

> In prespecified EEGMMIDB baseline recordings, the imaginary parts of
> coherency-cycle products show positive cross-interval alignment at the group
> level. This finite-window, coherence-weighted sensor statistic is positive in
> 62 of 78 retained eyes-open records and 77 of 84 eyes-closed records. It is
> higher in the eyes-closed baseline among the 73 retained participant pairs,
> and its magnitude depends on spectral resolution and reference. Independent
> decoding and recomputation reproduce all primary quality-control decisions
> and numerical scores. Finite-window theory and an explicit reversible-latent
> counterexample define the separation between this empirical measure and the
> exact population filter invariant.

Material issues for final reporting are the established finite-window null
failure; the mixture of coherence and closure phase in Q; substantial and
condition-dependent artifact exclusions; changed samples/epochs in several
sensitivity branches; and dependence on the spatial reference. The observed
data and code support the narrower empirical statement above. Anatomical loops,
causal direction, thermodynamic production, and an unrestricted latent M0
rejection are outside the identified empirical quantity.

No additional exploratory hypothesis tests are requested. The completed
independent reproduction and the already available counterexample resolve the
main audit questions.

## Audit artifacts

- `src/empirical_audit_independent.py`: independent executable analysis.
- `reviews/empirical_audit_exact_outputs.json`: exact audit counts, EDF metadata, checksums, and maximum numerical discrepancy.
- `reviews/empirical_audit_primary_recomputed.csv`: every primary record, both QC masks, exclusion causes, and independent Q.
- `reviews/empirical_audit_selected_scores.csv`: four explicit record-level comparisons.
- `reviews/empirical_audit_group_table.csv`: independent descriptive and statistical summary table.
- `reviews/empirical_audit_paired_table.csv`: participant-paired results.
- `reviews/empirical_audit_sensitivity_table.csv`: exact intersection-only means, membership changes, and correlations.
