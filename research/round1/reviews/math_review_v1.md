# Independent adversarial mathematical review v1

Reviewer: mechanism_scout. Frozen 2026-11-06. Reviewed theory_v1.md,
scouts/root_closure_proposal.md, protocols/protocol_v1.md and
src/closure_core.py. No peer review output or root simulation output was read.
The independent implementation imports no project code.

## Decision

**The population mathematics survives this review. The frozen empirical test
has a substantial finite-window counterexample within M0.** Its positive result
can establish reproducible sensor-level *windowed* spectral closure. Rejection
of arbitrary reversible latent dynamics with arbitrary diagonal LTI observation
filters requires additional regularity/scale restrictions and control of the
window bias. Selected random-filter calibrations establish performance for the
selected families, rather than this entire composite null.

Artifacts: src/math_review_independent.py; reviews/math_review_exact_outputs.json;
reviews/math_review_stdout.txt; reviews/adversarial_M0_60s_scores.npy.
The script uses independent Cholesky whitening for reversal divergence,
differential evolution for phase searches, permutation enumeration for Wick
pairings, an exact finite-time covariance calculation for tapered spectra, and
an independent complex-AR simulation of reversible Gaussian oscillators.

## 1. Population proof audit

### Cycle criterion and filter scope

The arbitrary-support-graph spanning-tree proof is correct. Real cycle products
include either sign. All triangles suffice only on complete nonzero support;
a sparse chordless cycle needs its own constraint. Two-channel real-gauge
reduction is correct. Pointwise phase functions need not admit causal stable
realizations. The project's broad two-sided relaxation makes the positive
obstruction conservative; the existing statement of this distinction is sound.
For a real process, phases may be selected with U(-f)=conj(U(f)); measurable
selection from the finite set of possible spanning trees handles changing
support. Claims involving an integrated KL rate still require the ordinary
existence/integrability assumptions for that rate.

### Reversal divergence and factor of two

Let Z=R+iY, B=R^(-1/2) Y R^(-1/2). The pair of eigenvalues +/-b of iB
contributes 2b^2/(1-b^2) to E. Consequently E>=||B||_F^2; the factor in
L=2(Im P)^2/(lambda_max(C)^2 D) is correct. The norm inequality and
lambda_max(Re Z)<=lambda_max(Z) are valid. The trigonometric and
Cauchy–Schwarz steps are valid even with negative real edges or zero edges.
The convention E=.5[tr((S^T)^(-1)S)-n] is consistent with integration over
both positive and negative frequencies. Positive-frequency-only numerical
integration must include the corresponding factor of two.

An independent useful 3x3 identity is

    E(Z)=2[det(Re Z)/det(Z)-1].

It follows because the whitened skew matrix in dimension three has only one
nonzero eigenvalue pair, and det Z=det R(1-b^2). The independent numerical
check agrees to 5.4001e-12 in 300 random positive-definite matrices.

### Noise contraction

For fixed phase U, proper complex Gaussian KL between covariance Z and Z^T
is 2E(Z). Adding the same independent real diagonal Gaussian noise to both
laws contracts KL and commutes with the relevant conjugation/reversal.
Thus E(U(S+N)U*)<=E(USU*) for every U. Minimizing both sides gives the stated
contraction. Diagonal positive rescaling invariance and diagonal unitary orbit
invariance are correct. Triangle subvector data processing yields a valid
lower bound on full-vector latent Gaussian reversal density. Dependent
triangle bounds should not be added.

### Independent numerical stress test

- 300 random 3x3 Hermitian positive-definite matrices, each with independent
  differential-evolution phase minimization: smallest attained minimum minus
  analytic L = 6.8162742e-7; no inequality violation.
- Maximum cycle invariance error under arbitrary diagonal magnitude/phase
  filters: 6.6844278e-16.
- Noise contraction checked in dimensions 2,3,4,8,16. Largest observed change
  E(S+N)-E(S) = -4.6410613e-5.
- Numerical phase minima remain upper bounds, consistent with the project text.

## 2. Wishart identity and split-half inference

I independently enumerated the six Wick pairings. For a permutation pi, the
replica-index constraints supply K^(number_of_cycles(pi)-3); multiplying the
three corresponding covariance entries gives exactly the proposed formula.
The largest floating-point discrepancy was 5.55e-17. Monte Carlo with 60,000
replications at K=1,2,3,8,24 agrees within sampling error. At K=1 the imaginary
cycle is zero to roundoff (maximum residual 1.34e-14).

The unnormalized identity should remain explicitly separated from normalized
coherency. The split-half symmetry argument is correct when the **whole joint
replicate law within each half** has a common appropriate conjugation symmetry,
and halves are independent. Real-gauge covariance at each frequency alone is
insufficient to establish that joint property in finite windowed data. The
project text largely captures this, but the code docstring's reference to
independent replicas 'at each frequency' should be tightened to joint symmetry
or independent frequency bins, in addition to independent halves.

The cross-half product removes the positive squaring floor caused by independent
estimation noise. It retains any reproducible bias in the expected halfwise
closure, including finite-window leakage. The next construction quantifies it.

## 3. Strong counterexample within the stated M0

Construct two independent real Gaussian stationary modes with covariance

    R_m(tau)=exp(-2*pi*.15*|tau|) cos(2*pi*f_m*tau),
    f_1=9.75 Hz, f_2=10.25 Hz.

Their variances are 1 and .4. At 160 Hz, these are the real parts of stable
circular-complex AR(1) modes. Twelve latent channels mix them with real spatial
loadings u=(1,1,1) repeated four times and v=(1,1,-1) repeated four times.
Every latent cross-covariance is even; the full Gaussian latent process is
therefore exactly time reversible. Observe each channel through a causal pure
delay, with delays (0,125,0) ms repeated four times, and add mutually independent
sensor noise of variance .2. This follows the observation model exactly:
reversible latent mixture first, one scalar filter per recorded channel second.
At every true Fourier frequency all population cycle products are real.

For the precise 2-second Hann window and linear detrending in the frozen
protocol, I evaluated expected periodograms using the exact lag covariance,
not a spectrum-grid convolution approximation. The weighting vector is

    a_f = M [w_t exp(-2*pi*i*f*t/fs)],

where M projects out the intercept and linear trend. The exact expectation is

    E[I_ij(f)] = sum_tau corr(a_f,a_f)(tau) R_y,ij(tau) / sum_t w_t^2.

Normalizing this expected spectral matrix, then averaging across 2–30 Hz and
all 220 channel triples, gives:

- peak absolute expected imaginary coherency-cycle product: 0.0435969328447;
- mean square expected cycle imaginary part: **1.32330292647e-5**.

This is the limiting cross-half score with infinitely many independent epochs.
The construction demonstrates population bias in the finite-window target,
rather than a positive squaring noise floor.

### Actual 60-second records using the frozen analysis

An independent simulation of **500** stationary 60-second records uses exactly
12 two-second epochs at starts 2,4,...,24 seconds and 12 at 34,36,...,56 seconds,
Hann taper, linear detrending, the 12 channels and all 220 triangles. Result:

- mean Q = **1.01172962917e-5**;
- standard error = **8.66060859923e-7**;
- 95% normal Monte Carlo CI for the mean = **[8.41981700626e-6,1.18147755772e-5]**;
- 70.6% of records have Q>0;
- first 99 simulated records, one-sided participant sign-flip test with 49,999
  random signs: **p=0.00008**.

Thus an EEG-sized sample rejects this fully reversible-latent, causal diagonal
observation-filter model under the proposed significance procedure. Random
families that pass calibration can coexist with this structured counterexample.
The fixed function-local seed is 732419, so rerunning the full audit preserves
these specific finite-record outputs.

### Window length diagnostic

For the three distinct channel types, exact expected mean v^2 is:

| Hann duration | 25-ms delayed channel | 125-ms delayed channel | 500-ms delayed channel |
|---|---:|---:|---:|
| 1 s | 6.3466e-6 | 1.3695e-4 | 4.1021e-4 |
| 2 s | 1.9360e-6 | 4.5489e-5 | 2.7408e-4 |
| 4 s | 3.4264e-7 | 8.3666e-6 | 9.2289e-5 |
| 8 s | 2.6000e-8 | 6.4594e-7 | 9.3668e-6 |
| 16 s | 1.7108e-9 | 4.2705e-8 | 6.6705e-7 |

With zero delay all results are zero to floating-point precision. Increasing
window length progressively resolves the two spatial modes and removes their
filter-induced spectral mixture. This example uses smooth Lorentzian spectra;
'smooth' without a derivative/scale bound is too weak to calibrate the test.

## 4. Derived leading leakage term and an explicit remainder

This derivation was independently checked after root proposed the expansion.
Let K be a normalized symmetric frequency kernel, with moments mu2 and mu4.
Remove channel phases at the central frequency. Write the three directed
cross-spectra locally as z_e(delta)=r_e(delta) exp[i d_e(delta)], with real
signed r_e, d_e(0)=0, and sum_e d_e(delta)=0. Assume z_e has bounded fourth
derivative on the integration domain and the needed integrals exist. Taylor's
theorem gives

    zbar_e = r_e + (mu2/2) z_e'' + rho_e,
    |rho_e| <= (mu4/24) sup |z_e''''|.

The imaginary part of z_e'' is 2 r_e' d_e' + r_e d_e''. Expanding the cycle
product and using sum_e d_e''=0 yields

    Im(product_e zbar_e)
      = mu2 sum_e (product_{j!=e} r_j) r_e' d_e' + remainder.

The coefficient is polynomial, so negative/zero real cross-spectra create no
singularities. Let

    epsilon_e = mu2 |z_e''|/2 + mu4 sup|z_e''''|/24.

A direct absolute remainder bound is

    |remainder| <=
       sum_e (mu4 sup|z_e''''|/24) product_{j!=e}|r_j|
       + sum_{e<j} epsilon_e epsilon_j |r_k|
       + product_e epsilon_e,

where k is the remaining edge. This is O(mu4+mu2^2). For coherency cycles the
raw product is divided by the positive product of the three smoothed diagonal
spectra; lower-bounding those spectra transfers the same order to coherency.

For the continuous Hann window w(t)=sin^2(pi*t/T), 0<t<T, Parseval gives

    mu2 = [integral |w'|^2]/[4*pi^2 integral |w|^2] = 1/(3T^2),
    mu4 = [integral |w''|^2]/[16*pi^4 integral |w|^2] = 1/(3T^4).

Hence the leading bias in v is O(T^-2), and the infinite-independent-half
product bias is O(T^-4), provided the fixed underlying spectra and filters
obey the derivative and positive-power conditions. These exact constants apply
to the un-detrended continuous Hann kernel. Finite discrete sampling and
frequency-dependent linear detrending modify the kernel; the exact numerical
counterexample above already incorporates both. A 2-second to 4-second
comparison may sit outside the asymptotic regime; the table illustrates this.

This expansion supplies a scientifically useful leakage mechanism and a
bandwidth diagnostic. It supplies a numerical correction only when the required
derivative terms can be estimated accurately or bounded independently. A finite
set of window durations cannot certify the unrestricted composite null.

## 5. Additional exact quadratic formulation checked at root's request

Let A=(C^T)^(-1) elementwise-multiplied by C^T, and let v_i=exp(2i phi_i).
Cyclically moving the diagonal unitaries inside the trace gives exactly

    E(U C U*) = .5 [v* A v - n].

Both factors defining A are Hermitian positive definite, so A is positive
definite by the Schur-product theorem. The stated indices are correct.
For any unit-modulus candidate v, define

    d_i=Re[(Av)_i conj(v_i)], M=A-diag(d),
    delta=max(0,-lambda_min(M)), d'=d-delta.

Then A-diag(d')>=0, hence .5(sum_i d'_i-n) is a valid dual lower bound on E_*.
The attained objective .5(v*Av-n) is its upper bound. This is a useful
certification step beyond local optimization. For n=3 the complex correlation
elliptope's extreme-point rank constraint r^2<=n implies every extreme point
has rank one, and therefore the corresponding SDP relaxation is exact.
That rank theorem is prior mathematical literature and needs primary citation
before being described in the research manuscript. Numerical eigenvalue
roundoff should be padded in any claimed certified bound.

## Recommended final scope

Retain the exact population identifiability theorem, analytic lower bound,
Gaussian contraction result and estimator identity, subject to the separate
novelty audit. Add the explicit finite-window counterexample and leakage
expansion as substantive results. Report empirical Q as reproducible windowed
sensor timing and its dependence on bandwidth, channel mixing, and selected
filters. An unrestricted M0 rejection is contradicted by the example above.

### Section 5 independent numerical addendum

After inspecting the new phase_reversal_certificate implementation, I checked
200 further independent random matrices in dimensions 2,3,8,24 with an
independent implementation. Maximum quadratic-versus-Cholesky identity error
was 1.98951966e-13; maximum central finite-difference gradient discrepancy was
1.07146144e-8 at step 1e-6. All shifted dual matrices were positive definite,
with minimum eigenvalue 1.01146522e-12. Every dual lower bound lay below its
corresponding candidate upper bound. The implemented gradient is correct for
theta=2phi. Near-singular inputs call for explicit conditioning/residual checks:
the floating-point certificate concerns the computed quadratic matrix, with a
conservative eigenvalue buffer, rather than an interval-arithmetic proof.
