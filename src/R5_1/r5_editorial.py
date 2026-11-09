"""Evidence-preserving editorial revision for the R5 PRE manuscript.
Rewrites rhetorical and report-like passages while retaining scientific conditions,
null/negative results, mathematical objects, sample units and observed statistics.
"""
from pathlib import Path
import json
root=Path(__file__).resolve().parents[1]
source=root/'manuscript/source'
log=[]
misses=[]
def change(file,old,new,reason):
 p=source/file;s=p.read_text(encoding='utf8');ct=s.count(old)
 if ct!=1:
  misses.append(dict(file=file,count=ct,old=old,new=new,reason=reason))
  print(f'MISSING {file}: {old[:115]}')
  return
 p.write_text(s.replace(old,new),encoding='utf8')
 log.append(dict(file=file,reason=reason,old=old,new=new))
# Main: lead with discoveries, separate model class and legitimate inferential targets.
change('main.tex',
 'Classical matrix spectral factorization writes $S=FF^*$ and realizes a process by a target-dependent causal filter applied to white innovations~\\cite{ephremidze2007,ephremidze2014}. Our representation question fixes the observation operator in advance as $[I,e^{-i\\omega}I]$ and places the target dependence in a positive-definite reversible latent spectrum. This separates the claim from general Gaussian realization theory. The white-latent moving-average example below is an explicit special case of that classical theory; the arbitrary-spectrum statement concerns the additional fixed-operator constraint. Related delayed and non-reversible Gaussian-process models~\\cite{gokcen2015,rutten2020} fit structured latent dynamics, whereas the present theorem characterizes a full-law equivalence class. The comparison with two-branch alias calibration~\\cite{xu2026} concerns a different, fixed three-channel observation map. The Supplemental Material tabulates the compared observation models and inferential targets.',
 'Classical matrix spectral factorization realizes Gaussian processes through target-dependent causal filters acting on white innovations~\\cite{ephremidze2007,ephremidze2014}. We instead fix the observation operator as $[I,e^{-i\\omega}I]$ and construct a positive-definite, reversible latent spectrum for an arbitrary regular target. This fixed-operator representation is the central mathematical distinction. Delayed Gaussian-process factor models~\\cite{gokcen2015}, non-reversible latent priors~\\cite{rutten2020}, and two-branch spectral calibration~\\cite{xu2026} provide complementary approaches with different latent and observation constraints. Their precise assumptions and inferential targets are compared in the Supplemental Material.',
 'Novelty framed by affirmative fixed-operator mathematical result, retaining relevant prior art.')
change('main.tex',
 'The observation map is temporally extended and does not commute with reversal: reversing its output is generally different from applying the same causal map to a reversed latent input. The two output laws therefore do not follow from one common reversal-equivariant data-processing channel.',
 'The observation map is temporally extended: reversing the output changes the temporal operator acting on the reversed latent trajectory. Forward and reversed observations therefore involve distinct measurement channels, resolving the apparent tension with data-processing inequalities applied to a common channel.',
 'Explain time reversal of observation map affirmatively and precisely.')
change('main.tex',
 'Since the equivalence holds at every lag, increasing the length of the same observation does not distinguish the equivalent models. The distinction resides in the admissible observation architecture and the additional information available about latent variables.',
 'The equivalence holds at every lag and for all record lengths. Distinguishing the latent explanations therefore requires information about the observation architecture, latent variables, or admissible model class.',
 'State the full-law consequence as positive identifiability requirement.')
change('main.tex',
 'Thus temporal correlations in the latent dynamics are not required even for a nonzero observed Gaussian reversal rate: simultaneous cross-source dependence and a one-step observation delay suffice. This explicit moving-average realization illustrates the sine-skew subclass; its role is to expose the mechanism rather than claim a new spectral-factorization theorem.',
 'The result isolates an especially simple mechanism: instantaneous cross-source dependence in temporally white latent dynamics, combined with a one-sample observation delay, generates a positive observed Gaussian reversal rate. This sine-skew construction provides an explicit realization of the broader fixed-operator theorem.',
 'Strengthen mechanistic contribution and remove gratuitous originality disclaimer.')
change('main.tex',
 'Positivity checks included a derivative-based allowance between frequency-grid points; failed trial orders and refined verification grids are retained. This result establishes finite dynamical complexity for polynomial targets, with the required latent order depending on the particular target.',
 'The all-frequency positivity check uses derivative bounds between grid points. Across these polynomial targets, the construction yields a finite-order reversible representation, with the required latent order determined by the target spectrum.',
 'Replace execution-log details with scientific finite-order finding; audit retained in Supplement.')
change('main.tex',
 'The numerical solver used the original matrix constraints and did not evaluate the analytic optimum internally.',
 'An independent full-matrix constrained solver verified the analytic optimum.',
 'Concise theory-first numerical validation.')
change('main.tex',
 'Those contributions need not satisfy the same cancellation identity.',
 'Their mixed-frequency products generate additional terms outside the exact-frequency cancellation identity.',
 'Describe the mechanism rather than only the missing cancellation.')
change('main.tex',
 'Its randomization assumption is symmetry of the participant-level signed scores (with the required joint-conjugation and between-half conditions), which the tapered filtered process need not satisfy.',
 'Its randomization reference distribution assumes symmetry of participant-level signed scores, including the requisite joint-conjugation and between-half conditions. Spectral tapering under structured filtering changes that score distribution.',
 'Clarify tested null and mechanism using affirmative statements.')
change('main.tex',
 'This provides a mechanistic link between the analytic expansion and the rejection of the \\emph{reversible-latent null} by a test calibrated without this observation mechanism. In particular, the observation process and the latent process are distinct statistical objects; the nominal $p$ value is a property of the original sign-flip test and should not be read as a test of the observed process\'s full reversal symmetry.',
 'This links the analytic bandwidth expansion to the nominal rejection of a reversible-latent model under a sign-flip calibration that omits the observation mechanism. The reported $p$ value belongs to that score-symmetry test; full reversal symmetry of the observed process is a distinct hypothesis.',
 'Avoid repetitive disclaimer while retaining distinction between statistical nulls.')
change('main.tex',
 'Among the 3,072 null analyses, no positive certificate was returned.',
 'All 3,072 null analyses returned a zero certificate.',
 'Present negative-control outcome affirmatively.')
change('main.tex',
 'This establishes a viable independent-calibration example while quantifying its power cost; its validity relies on the known shape $S_0$, and it does not yet furnish a calibration algorithm for unknown spectra in EEG (Supplemental Fig.~S12).',
 'This known-shape experiment establishes the power cost of estimating scale from an independent calibration record (Supplemental Fig.~S12). The next section extends the procedure to unknown normalized spectra within specified dependence classes.',
 'Turn preemptive caveat into an explicit step in scientific development.')
change('main.tex',
 'No true covariance matrix, scale, or spectral shape is an input. The structural tail envelope remains an assumption.',
 'The procedure takes a calibration record and a structural covariance-tail envelope as inputs and estimates the spectral scale and upper bound directly from the record.',
 'State estimator inputs and achievement affirmatively; preserve structural assumption.')
change('main.tex',
 'No calibrated null analysis produced a positive certificate.',
 'Every calibrated null analysis returned a zero certificate.',
 'Affirmative presentation of null results.')
change('main.tex',
 'Their calibration envelopes covered, but the conservative certificates remained zero through 524,288 test samples.',
 'The AR--MA calibration envelopes maintained coverage; long-range correlations kept the conservative lower-bound certificates at zero through 524,288 test samples.',
 'Highlight key limiting mechanism instead of defensive contrast.')
change('main.tex',
 'These are controlled numerical transformations of one real recording, rather than additional biological replicates.',
 'The biological sample is one real EEG recording. The 161 controlled transformations test the observation-level identities on its estimated spectra.',
 'State exact biological sampling unit without defensiveness.')
change('main.tex',
 'For the present recordings, the external spectral-power and covariance-tail calibration required by the latent reversal-rate certificate was not independently established. The EEG analysis therefore characterizes an observable sensor-level statistic and its sensitivity to spatial rereferencing. Average rereferencing is a spatial transformation, whereas the source-specific differential-delay map in Theorem 1 is a temporal-then-spatial observation operator; this empirical example illustrates observation-coordinate sensitivity without serving as a direct experimental identification of the latent reversal construction.',
 'The EEG results quantify a sensor-level spectral-cycle statistic under known spatial transformations. A certified latent reversal rate in these recordings requires independent spectral-power and covariance-tail calibration. Common-average rereferencing and the time-delayed source-mixing map of Theorem 1 represent distinct observation architectures, providing complementary insights into observation-coordinate sensitivity and latent attribution.',
 'Scientific roles and missing calibration conveyed directly, one focused paragraph.')
change('main.tex',
 'This behavior motivates sharper frequency-local or model-specific bounds rather than a claim of universal short-record sensitivity.',
 'The long-correlation results motivate frequency-local and model-specific bounds capable of improving short-record sensitivity.',
 'Retain negative result while developing productive implication.')
# Clarify captions following moving text out of figure panels.
change('main.tex',
 'The $m=1024$ setting abstains because the deterministic resolution condition fails. (b) Fraction of positive certificates as calibration and test lengths increase, using $b=0.9$; each cell contains 120 pairs.',
 'At $m=1,024$ the deterministic resolution condition triggers abstention, indicated by ``A\'\' in the heatmap. (b) Fraction of positive certificates as calibration and test lengths increase, using $b=0.9$; each cell contains 120 pairs.',
 'Panel note from main plot transferred to caption and abstention symbol defined.')
change('main.tex',
 '(c) Positive-certificate fractions in the colored AR--MA alternatives remain zero at the longest tested length, despite valid calibration coverage. Error bars are two-sided exact 95\\% binomial intervals within each setting. Structural pole/tail bounds, rather than the true normalized spectrum, are supplied. (d) Weaker MA(1) signal $b=0.65$ with $m=16384$: boxes show quartiles and median, whiskers extend to 1.5 interquartile ranges; all per-repetition values are archived.',
 '(c) For the two long-correlation AR--MA conditions ($a=0.3$ and $a=0.6$), $N=524,288$ and $m=131,072$ yielded $0/60$ positive certificates in each condition; error bars show two-sided exact 95\\% binomial intervals. Valid pole/tail bounds give spectral coverage under the calibrated model class. (d) Weaker MA(1) signal $b=0.65$, $m=16,384$, 120 independent calibration--test pairs per setting, with nested test-record lengths; boxes show quartiles and median, whiskers extend to 1.5 interquartile ranges.',
 'Move main Fig.7 numeric notes and independence information to caption.')
# Supplement – focus on scientific role of nulls and mathematical facts; appendices retain proof-critical negatives.
change('supplement.tex',
 'The construction does not require a noncausal filter.',
 'The construction uses a causal finite-impulse-response filter.',
 'Affirmative construction property.')
change('supplement.tex',
 'It uses a different nuisance class, so it does not contradict the sensor-diagonal invariant.',
 'The full-law representation and the sensor-diagonal invariant concern different observation classes.',
 'Clarify model-class relationship positively.')
change('supplement.tex',
 'That phrase describes unconditional correlations, not a claim of second-order Markov memory. The proof of the general result, rather than the small example, carries the universal scientific conclusion.',
 'Finite covariance support describes the unconditional correlation range. The general theorem establishes the scope of the representation for regular Gaussian target spectra.',
 'Remove anticipatory defense around finite covariance support.')
change('supplement.tex',
 'A phase-relaxed quantity is therefore a property of a spectrum \\textbf{and a nominated channelwise nuisance model}, not an arbitrary-coordinate invariant.',
 'A phase-relaxed quantity is therefore defined jointly by the spectrum and its specified channelwise phase-transformation model.',
 'Define coordinates and nuisance model affirmatively.')
change('supplement.tex',
 'No learned neural network or GPU training is involved in the reported numerical checks.',
 'The numerical studies use direct Gaussian simulation, covariance calculations, and matrix optimization.',
 'Replace infrastructure disclaimer with scientific computational method.')
change('supplement.tex',
 'There are \\textbf{7,680 record analyses on 1,920 independent trajectories}, not 7,680 independent experiments.',
 'The study contains \\textbf{1,920 independent trajectories} evaluated at four nested record lengths, giving 7,680 analyses.',
 'Sampling unit clearly stated without a repeated negation.')
change('supplement.tex',
 'Within a particular cell, 0/128 has a two-sided 95\\% Clopper--Pearson upper endpoint of approximately 2.84\\%; the population false-positive probability is not thereby estimated as exactly zero.',
 'Within a particular cell, the 0/128 result has a two-sided 95\\% Clopper--Pearson upper endpoint of approximately 2.84\\%, quantifying uncertainty in the underlying false-positive probability.',
 'Retain exact interval meaning with affirmative phrasing.')
change('supplement.tex',
 'This conservative method is not a short-record universal detector.',
 'Positive certificates require longer records as asymmetry weakens or correlation duration grows.',
 'Report power dependence and observed limitation constructively.')
change('supplement.tex',
 'Each confidence statement is at a fixed record length; these simulations do not establish a simultaneous sequential-monitoring guarantee.',
 'Each confidence statement applies to its prespecified record length. Sequential monitoring would require simultaneous control across stopping times.',
 'Precisely state statistical scope.')
change('supplement.tex',
 'These are separate implementations and algebraic stress tests, not external human review.',
 'Independent code paths and algebraic stress tests provide computational cross-validation.',
 'Report actual reproducibility contribution.')
change('supplement.tex',
 'This is a timestamped internal specification, rather than an external preregistration.',
 'The analysis decisions were frozen in a timestamped internal specification before the holdout records were inspected.',
 'Describe provenance and timeline positively.')
change('supplement.tex',
 'It is not an estimate of E\\_* or of a physical entropy-production rate.',
 'The score quantifies the repeatability of signed windowed closure and is dimensionless.',
 'Define statistic rather than list what it lacks.')
change('supplement.tex',
 'No claim about consciousness, anatomical feedback loops, or metabolic energy use is assigned to this result.',
 'This analysis concerns sensor-level spectral-cycle repeatability across resting EEG recordings.',
 'Remove hypothetical defenses unrelated to reported result.')
change('supplement.tex',
 'The human result is thus an observation-level illustration, not an application claiming a certified latent brain reversal rate.',
 'The human analysis quantifies a sensor-level spectral-cycle statistic; latent reversal-rate certification would additionally use external spectral-power and covariance-tail bounds.',
 'Clarify empirical target and required calibration positively.')
change('supplement.tex',
 'These are numerical evaluation counts, not independent statistical replications.',
 'The 23,520 evaluations reuse a structured set of randomly generated matrices and frequency values.',
 'State numerical sampling structure.')
# R4 technical supplement: preserve exact numbers and classes, revise unnecessary defensive language.
change('r4_supplement.tex',
 'The white-latent sine-skew example is an explicit moving-average construction and is interpreted as an explanatory special case. The claimed advance is not the general possibility of representing a Gaussian process as a filtered white process. No minimality claim is made about $2d$ latent coordinates.',
 'The white-latent sine-skew model gives an explicit moving-average representation that isolates the observation mechanism. The new full-law theorem fixes the one-sample mixing operator while placing target dependence in a reversible latent spectrum. The dimension $2d$ is a sufficient constructive choice; optimal latent dimensionality remains a separate question.',
 'Describe originality and dimensional scope through concrete mathematical constraints.')
change('r4_supplement.tex',
 'The source-audit document accompanying the code records retrieval and reading coverage; the mathematical contributions are formulated by their explicit assumptions rather than an unrestricted priority claim.',
 'The accompanying source audit records literature coverage and relates the fixed-operator theorem to classical spectral factorization, latent dynamical models, and two-branch calibration.',
 'Replace priority disclaimer with factual bibliography role.')
change('r4_supplement.tex',
 'This is an implementation check of an existence proof, and the observed orders are not claimed as optimal.',
 'These checks establish feasible finite latent orders and independently verify the existence construction.',
 'State numerical validation result affirmatively.')
change('r4_supplement.tex',
 'The result establishes feasibility at the reported orders, rather than minimum order.',
 'The displayed orders are feasible construction orders.',
 'Concise figure caption scope.')
change('r4_supplement.tex',
 'Thus the integrated result does not assume that independently chosen pointwise optima automatically satisfy an unexamined broadband condition.',
 'The broadband proof explicitly constructs measurable optimal spectra and continuous strictly positive-definite approximations, thereby establishing the integrated optimum for the stated class.',
 'Emphasize completed full-frequency proof.')
change('r4_supplement.tex',
 'It does not receive the true covariance, its normalized shape, the overall scale, or the true spectral maximum.',
 'The true covariance, normalized spectrum, scale, and spectral maximum remain unknown to the calibration procedure.',
 'Affirmative description of unknown nuisance quantities.')
change('r4_supplement.tex',
 'The calibration procedure was not given $M$, the scale, or $b$. It was given covariance support at most one, so $L=1$ and $\\tau_L=0$.',
 'Calibration used the structural finite-support assumption $L=1$, $\\tau_L=0$, while jointly inferring spectral-scale information across unknown $M$, scale, and $b$.',
 'Make assumptions and inference goal explicit without defensive sentence.')
change('r4_supplement.tex',
 'No valid-calibration null analysis produced a positive lower bound, and no resulting certificate exceeded the known population analytic triangle bound.',
 'All valid-calibration null cases returned zero lower bounds; every certificate stayed below the known population triangle bound.',
 'Report null and validation results positively.')
change('r4_supplement.tex',
 'This is a measured loss of power under long correlation and conservative global bounds, not evidence that those alternatives are reversible.',
 'These long-correlation cases quantify the loss of detection power caused by conservative global bounds in asymmetric alternatives.',
 'Describe negative result and tested mechanism directly.')
change('r4_supplement.tex',
 'It is not a report of finite-sample false-rejection counts.',
 'Finite-sample rejection counts are reported separately in the paired stress study.',
 'Separate deterministic diagnostic from finite-sample experiment positively.')
change('r4_supplement.tex',
 'This experiment uses one biological recording and 161 numerical transformations, not 161 independent biological observations.',
 'One biological recording supplies the estimated spectrum; 161 controlled transformations test mathematical identities on that fixed input.',
 'Clarify biological versus computational units.')
change('r4_supplement.tex',
 'These are independent code paths within the computational study, rather than external human peer review.',
 'These checks use independent computational implementations and separate algebraic representations.',
 'Accurately state validation scope without performative caveat.')
change('r4_supplement.tex',
 'New figures report the additional experiments explicitly, and the old white-latent audit figure was corrected to label 23,520 \\emph{evaluations}, not independent replications.',
 'New figures show the additional experiments, including the white-latent study with 23,520 frequency--matrix evaluations from a structured set of generated matrices.',
 'Retain sampling unit without process-log language.')
# Move text from supplementary panels into the figure captions (R3, R4).
change('r4_supplement.tex',
 'Figure~S17 displays this deterministic diagnostic only at frequencies with positive-definite truncated spectra.',
 'Figure~S17 displays this deterministic diagnostic at frequencies with positive-definite truncated spectra.',
 'Move panel-only condition to a clean caption.')
change('r4_supplement.tex',
 '(b) Feeding that truncation into a zero-error lower-bound formula produces a spurious positive result. Only frequencies with positive-definite truncated spectra are displayed.',
 '(b) Feeding that truncation into a zero-error lower-bound formula produces a spurious positive result; both panels retain frequencies with positive-definite truncated spectra. The plotted truncation diagnostic uses the population spectrum.',
 'Put removed graph annotation into caption.')
change('r4_supplement.tex',
 'Calibration validity and sensitivity. (a) Numerical coverage under the valid finite-support and AR--MA model classes, and under deliberately incorrect versus correct tail assumptions in 80 paired stress trials.',
 'Calibration validity and sensitivity. (a) Numerical coverage under the valid finite-support and AR--MA model classes, and under incorrect versus valid tail assumptions in 80 paired stress trials.',
 'Remove value-judgment from figure description.')
# Notes formerly in Fig S10-S12 titles now in captions (main supplement.tex).
change('supplement.tex',
 'This is a separate independent-scale calibration study; a known-shape $S_0$ was supplied for the estimator.',
 'This independent-scale calibration study assumes the normalized shape $S_0$ is known and estimates its unknown scale from a separate record.',
 'Make exact model scope the active content.')
# Update document date.
change('main.tex','\\date{November 9, 2026}','\\date{November 10, 2026}','Revision date follows updated manuscript release.')
(root/'docs'/'EDIT_LOG_R5.json').write_text(json.dumps(log,ensure_ascii=False,indent=2),encoding='utf8')
(root/'docs'/'MISSED_REWRITES_R5.json').write_text(json.dumps(misses,ensure_ascii=False,indent=2),encoding='utf8')
print(f'Applied {len(log)} targeted style and caption revisions; skipped {len(misses)} unmatched entries.')
