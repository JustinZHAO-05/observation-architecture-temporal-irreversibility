# Final reporting and figure QA

Reviewer: data_scout. Completed 2026-11-06 UTC. This is a reporting audit after
the independently frozen empirical audit. Root-authored files were left
unchanged. Reviewed `src/make_figures.py`, all three rendered PNGs, the source
tables, `src/filter_robustness.py`, and the report as it developed through
sections 1-7. No new scientific hypothesis tests were run.

## Deliverable created

`output/scientific_results_table.csv` contains ten compact rows drawn directly
from the actual empirical result files:

- The two primary holdout condition means, original CIs, counts, conditional
  sign-flip p values, and Holm values.
- The two four-second sensitivity means with their corresponding original
  CIs, counts, and conditional p values.
- Both original paired-condition summaries, explicitly exploratory.
- The two participant-intersection-only two-second/four-second comparisons.
- The two causal-filter comparisons with the original accepted-epoch mask
  held fixed.

The table records source filenames, sample definitions, dimensionless Q units,
and the target of each confidence interval. No inferential numbers are added
to the descriptive matched comparisons. `src/build_scientific_results_table.py`
regenerates it from those source files; decimal CSV reads use round-trip float
precision. The two fixed-mask table means were also checked directly against
the record-level fixed-mask CSV.

## Concrete corrections communicated to root

1. **Figure 1C has a stale numerical annotation.** The current
   `results/variational_certificates.csv` has a maximum three-channel primal-dual
   gap of 2.062014e-11, whereas the inspected `make_figures.py` annotation and
   rendered panel say "gaps < 1.6e-11". Use the current file's maximum, for
   example "gaps < 2.1e-11", preferably formatted dynamically. The final
   inverse-residual interval adjustment changed these gaps, so the full figure
   should be rebuilt from the final table.

2. **The inspected PNGs lag the figure source and updated certificate table.**
   Several panel titles still show the earlier wording. Rebuild all figures
   after settling the current data/labels, before exporting the final report.
   Figure 2's leakage data source falls back to a partial JSON when the final
   CSV is absent; its caption should match whichever window-duration grid is
   actually exported. The inspected rendered grid is 1, 2, 4, and 8 seconds.

3. **Figure 2A's calibration parameter is a coherency magnitude.** In
   `finite_sample_study.py`, 0.2, 0.5, and 0.8 are assigned directly to the
   unit-diagonal spectral matrix's off-diagonal entries. Label this quantity
   "coherency magnitude" or |C_ij| to distinguish it from magnitude-squared
   coherence. This is terminology, not a numerical error.

These were sent to root during the audit. They are the only concrete reporting
corrections identified in the inspected material. A later root fix need not
alter the archived observation that these were present at review time.

## Checks passed

### Figure 1

- `network_families.csv` has 192 conditions, including 48 reversible cases.
  Its maximum elementwise cycle change is 9.27818464947112e-17, supporting the
  displayed rounded 9.3e-17. The smaller change between the plotted RMS values
  is a different summary and creates no discrepancy.
- Certificate case counts are 50, 300, 100, and 30 in dimensions 2, 3, 8, and
  24. Figure 1C plots the attained certified upper endpoint against the analytic
  triangle lower bound. For three-channel cases the interval width is negligible
  on the plotted log scale; the caption's bracketed-minimum interpretation is
  appropriate when the final gap annotation is updated.
- Larger-dimensional intervals remain visible. The figure is not presenting
  local numerical minima as exact lower bounds.

### Figure 2

- Ideal-null rates, sample counts, and binomial intervals agree with all nine
  rows of `finite_spectral_calibration.csv`. Each condition has 300 studies
  with 40 independently simulated participants; all intervals include 0.05.
- The leakage panel uses the mean over the full 220-triangle, 12-channel
  construction. Its ordinate is a squared coherency-cycle quantity from the
  expected finite-window spectrum, rather than a finite-epoch Q estimate. The
  T^-4 line is a reference slope anchored to a curve endpoint, not a fitted
  empirical exponent.
- The counterexample histogram's x values are Q multiplied by 10^4, correctly
  labeled with an axis multiplier of 10^-4. Its 500-record mean and first-99
  sign-flip p correspond to the independent mathematical-review outputs.
- The report explicitly identifies this as false rejection under the broad
  latent null, and distinguishes it from ideal spectral calibration.

### Figure 3

- Panel A correctly contains the 73 participants retained in both conditions;
  its reported difference is the exploratory paired difference, not the
  difference between the two unpaired group summaries.
- Panel B correctly uses branch-specific n=78/84 for two-second epochs and
  n=64/76 for four-second epochs. Its intervals are the original subject
  bootstrap intervals. The caption states the sample-size change; the report
  separately supplies matched-participant means.
- Panel C averages triangle products within participants before calculating
  the across-participant mean and standard error. Its shading is explicitly
  pointwise normal 95% intervals and the frequency display is descriptive.
  The float32 cycle archive is adequate for this plotted descriptive summary.
- Panel D reads the fixed-mask result file. The source code derives QC on the
  original signals and reuses those exact masks after causal filtering. Its
  n=78/84 and Pearson values 0.9968254300133562/0.9991734957900741 agree with
  the source data. This was code/data QA, not a second independent EDF-level
  reimplementation of the later fixed-mask analysis.
- All EEG figure axes use dimensionless Q multiplied numerically by 10^4 and
  labeled with the corresponding 10^-4 multiplier. No amplitude or entropy
  units are incorrectly attached to Q.

### Manuscript through section 7

- Primary means, sample counts, positive counts, CIs, standardized effects,
  conditional p values, and Holm values agree with the frozen result files.
- Four-second confidence intervals agree with the original sensitivity
  summaries, rather than the audit's separately resampled verification CIs.
- The reported participant-intersection-only window comparisons agree with
  direct joins of the source subject tables.
- The fixed-mask mean changes of -0.591% and -0.368% agree with the source
  summary. Exact Fourier-domain invariance is correctly separated from the
  approximate time-domain perturbation.
- The primary sign-flip p values are identified as conditional finite-window
  evidence and as the Monte Carlo resolution floor. The empirical prose does
  not promote them to an omnibus rejection of the unrestricted latent null.
- The report distinguishes coherence-weighted Q from E_* and physical
  dissipation, labels the paired contrast exploratory, and identifies the
  condition/run association and reference sensitivity.
- The all-record reproduction claim (218 records, 177 retained scores,
  maximum error 9.8649e-17) agrees with the frozen independent audit.

## Closing assessment

The numerical reporting and sample definitions are consistent. Updating the
certificate-gap annotation, clarifying the calibration axis, and rebuilding
the figures resolves the concrete figure issues. The theory and empirical
interpretation have appropriately distinct scopes. This audit stops after
reporting those actionable issues; it adds no new optional analyses.
