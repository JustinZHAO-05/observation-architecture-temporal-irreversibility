# Final targeted scientific-claims audit

**Reviewer:** theory_scout. **Date:** 2026-11-06.  
**Scope:** current `output/neural_time_arrow_report.md`, especially the abstract, finite-record theorem, Sections 8–10, and originality statements. I also consulted the independent mathematical addendum and empirical/reporting audits. No new experiments or broad literature searches were performed. The current finite-record theorem is numbered **Theorem 3**; Theorem 2 is the triangle bound.

## Material findings

### 1. Add the Gaussian qualifier to the abstract's universal finite-MA claim

Current wording: “Any multivariate finite moving-average process observed for a finite number of time points …”.

Recommended wording: “Any multivariate finite moving-average **Gaussian** process observed for a finite number of time points …”.

The exact proof in Theorem 3 assumes independent standard Gaussian innovation streams. The same serialization argument extends to identical independent scalar innovation laws, but the abstract's unrestricted wording also includes non-Gaussian vector innovations with dependence or different component distributions. That broader class was not established. The following Gaussian density and testing statements already have the appropriate scope.

### 2. Specify the frequency convention for the Hann moments

Section 5.1 gives

\[
\mu_2=1/(3T^2),\qquad \mu_4=1/(3T^4).
\]

These constants use frequency **f in cycles per second (Hz)** and Fourier kernel \(e^{-2\pi i f t}\). Earlier sections expressly use angular frequency \(\omega\). The leakage section should state that its frequency offset, derivatives, and kernel moments use Hz. If it instead uses angular frequency, the constants are

\[
\mu_2=4\pi^2/(3T^2),\qquad
\mu_4=16\pi^4/(3T^4).
\]

The expansion and its powers of T remain valid under either consistent convention. This is a units clarification with quantitative consequences for any proposed error bound.

### 3. Attach coverage to the lower-confidence-bound statement

Section 8.2 calls the positive-part expression a “quantitative lower confidence bound.” Section 5.2 currently gives an externally justified entrywise error bound without explicitly stating its probability of coverage.

Add a sentence such as: “If the simultaneous error event holds with probability at least 1−alpha, the resulting lower bound has at least the same coverage.” Alternatively call it a “conditional quantitative lower bound” in the table. The deterministic perturbation proof and 1,000 numerical checks do not themselves assign a confidence level. No current EEG estimate of this certified bound is claimed, so this wording adjustment preserves the empirical conclusions.

## Substantive checks passed

- The delayed-innovation proof matches the entire finite record, not merely a chosen statistic. Its disjoint index intervals and dependence of filter memory on N are stated explicitly.
- The positive-definite approximation uses nonsingular finite target covariances, as required for Gaussian total-variation convergence. The exact white-floor version uses bounded FIR transfer functions to keep all independent noise spectra nonnegative.
- The general Gaussian extension has an appropriate spectral approximation class. The testing corollary correctly assumes uniform size over unrestricted channel memory and therefore bounds power at each finite record length. It is not presented as a failure of fixed-filter pointwise asymptotics.
- The numerical covariance example is explicitly an implementation check of the arbitrary-size proof; the general conclusion is not inferred from that example.
- Sections 8–9 distinguish windowed sensor closure from latent irreversibility and distinguish the condition/run association from a biological mechanism. The mathematical counterexample is retained and changes the empirical interpretation.
- Existing closure geometry, spectral reversal divergence, phase optimization/certification, and band-averaging contamination are attributed. The remaining priority statements are restricted to what the concentrated literature search located, with incomplete read coverage disclosed. I found no unsupported “first” or established journal-level novelty claim.
- Section 10's independent-audit claims are consistent with the corresponding audit reports: internal independent implementations and checks are distinguished from external peer review; 177 retained primary scores and 218 decoded files agree with the empirical audit. The current numerical certificate discussion appropriately labels floating-point intervals and retains higher-dimensional gaps.

## Verdict

No conclusion-changing flaw was found in the finite-record construction, its Gaussian testing corollary, the empirical interpretation in Sections 8–10, or the current bounded originality assessment. Resolve the three precise scope/unit/coverage points above. The resulting claim remains a completed theoretical and computational methods result with a reproducible neural-data illustration and a candid, appropriately scoped publication assessment.
