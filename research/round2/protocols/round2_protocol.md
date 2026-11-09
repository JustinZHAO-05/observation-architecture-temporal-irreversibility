# Round 2 execution specification
Target: Physical Review E, regular article. Date: 7 November 2026.
This is an internally recorded execution specification, not external preregistration.
The 109 EEG participants were already examined in round 1. All new EEG comparisons are exploratory.

1. Prove a general positive-definite reversible-source representation with a one-sample delay
   followed by fixed spatial mixing. Check 90 VAR networks (3/6/12 dimensions), 83 frequencies each.
2. Supply an exact three-channel example with six reversible sources having covariance support two.
   Compare complete finite-record covariance matrices, not just a selected summary statistic.
3. Derive a finite-sample Gaussian spectral confidence envelope with externally specified spectral
   operator bound and covariance-tail bound. Propagate it to a cycle-based lower confidence bound.
   Simulations: two correlated reversible nulls; three alternative strengths; three delay patterns;
   four record lengths; 128 independent longest trajectories per model/delay, with nested prefixes.
4. Recompute EEG using original quality masks and same participant set. Compare original reference,
   64-channel common average, fixed orthogonal mixing and six regional bipolar channels.
5. Quantify the hidden-power cost of short-delay mimicry. Verify a closed-form optimum numerically.
6. Preserve all negative results, failed tests and remaining publication-readiness questions.

Primary scope: stationary real Gaussian processes with all measured variables even under time reversal.
The original sensor-diagonal observation model and the source-filter-then-mix class are kept separate.
No independent subagent endpoint is exposed. Separate code paths are numerical checks, not human review.

## Execution amendments
- Raw EDF access from the execution container failed (DNS/network); no new raw-data audit is claimed.
  The EEG follow-up uses first-round archived imaginary-cycle arrays and restricts analysis to subjects
  >10 and records with all 12+12 predefined windows accepted under BOTH original and average references.
  Orthogonal-coordinate diagnostics are therefore performed on known population models, not on EEG.
- A universal one-delay reversible representation was derived during this sprint. It became the main
  structural result. A separate covariance concentration certificate was developed for the narrower
  sensor-diagonal observation class.
- The fixed-frequency certificate was extended to a continuous-frequency rate bound using a deterministic
  trigonometric-polynomial net and interval lower sums. After the first 256 analyses showed no positive
  rate bounds for delay 8 at N<=131072, N=524288 was added explicitly to examine restoration at longer
  records. The earlier grid results are retained under results/archive. This extension is exploratory
  numerical characterization of a proved bound; no p-value-based tuning or claim of preregistration.
- A full-matrix SLSQP optimization of the latency-power cost was numerically unreliable (only 7/32
  convergence flags). Its outputs are retained. A separately implemented PSD cutting-plane LP audit
  supplies narrow numerical objective brackets instead; analytic proof is the primary justification.
