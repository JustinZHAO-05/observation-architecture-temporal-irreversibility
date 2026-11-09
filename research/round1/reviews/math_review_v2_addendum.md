# Independent mathematical review v2: finite-record limits and sharpness

Reviewer: mechanism_scout. Frozen 2026-11-06. This addendum independently
checks the specific follow-up constructions proposed by root; it makes no
external review or novelty claim. No broad literature search was performed.

Main files:

- `src/math_review_v2_calculations.py` — reusable independent computations;
  imports only the earlier independent audit helper, not root's implementation.
- `reviews/math_review_v2_outputs.json` — all numerical results.
- `reviews/math_review_v2_leakage_partial.json` — complete 1–32-second curve;
  pre-interruption results were retained and only missing durations calculated.
- `reviews/serialization_covariance_example.npz` — exact finite-block example,
  target coefficient tensors, serialized FIR filters, both covariance matrices.
- `reviews/math_review_v2_stdout.txt` — computation log.

## 1. Finite-record no-go by delayed scalar-noise serialization

### Exact theorem for finite moving averages

Fix a finite observation length N, p recorded channels, q independent standard
Gaussian white-noise streams epsilon_a(t), and real coefficients b_ia,k for
k=0,...,L. Consider the stationary target process

    y_i(t)=sum_a sum_{k=0}^L b_ia,k epsilon_a(t-k), t in Z.

Choose nonnegative integer shifts

    D_a=(a-1)(N+L+1), a=1,...,q,

and one scalar standard Gaussian white-noise process xi(t). Define the latent
p-vector x_i(t)=xi(t) for every channel and causal FIR observation filters

    h_i(k)=sum_a b_ia,k-D_a,

where each b coefficient is zero outside 0,...,L. Equivalently,

    z_i(t)=sum_a sum_{k=0}^L b_ia,k xi(t-D_a-k).

Then the **entire joint law** of (z(1),...,z(N)) equals the joint law of
(y(1),...,y(N)). The latent x is stationary, Gaussian and time reversible;
every h_i is a real, causal, stable finite-memory filter. It belongs to the
stated diagonal-observation-filter null.

**Proof.** For target innovation stream a, all indices used in the N-block lie
in J=[1-L,N]. In the serialized process they lie in

    J_a=[1-L-D_a,N-D_a].

The shift separation exceeds the length of each integer interval, so the J_a
are pairwise disjoint. The families {xi(s-D_a):s in J}, a=1,...,q are therefore
independent, with exactly the same joint law as the target innovation families.
The same deterministic coefficient map is applied to both. This proves equality
of the full observed-block law, including every statistic of that block. QED.

An equivalent covariance proof is useful: cross-stream terms in the serialized
process require a lag

    tau=(D_a-D_b)+(k-l).

For a!=b, its absolute value exceeds N-1 because |k-l|<=L. Therefore these terms
are absent from every covariance used inside the N-block; same-stream terms
match the target exactly. Outside this block-length range, extra cross-stream
correlations distinguish the processes.

The frequency-domain serialized spectrum is H(f)H(f)*. Every off-diagonal
cycle product is a product of |H_i(f)|^2 and is real and nonnegative. Meanwhile,
the target can have complex cycle products. This gives an exact finite-data
observational equivalence between a population-cycle-null process and a
population-cycle-alternative process.

The FIR memory is (q-1)(N+L+1)+L. Its growth with N is the essential freedom.
The coefficient l1 norms are bounded by sum_a,k |b_ia,k| independently of the
shifts, so a gain bound alone generally does not exclude this construction.
A substantive memory, delay-spread, or transfer-function-shape restriction does.

The exact innovation-index argument also works for identical independent
non-Gaussian innovation laws. Gaussianity is used below for the broad density
and testing corollary.

### Positive-definite spectra and latent processes

The rank-one latent/signal spectrum is not essential to the conclusion.
Adding identical independent white observation noise of variance sigma^2>0 to
the target and serialized constructions preserves equality of their N-block
laws and makes both observed spectra positive definite everywhere.

If positive definiteness of the *latent* spectrum is additionally required,
let x_i=xi+sqrt(delta) zeta_i with independent white zeta_i. Its spectrum is
11^T+delta I, real and positive definite. Let the independent observation noise
have spectra

    N_i(f)=sigma^2-delta |H_i(f)|^2.

For sufficiently small positive delta these spectra are nonnegative because
the finite FIR transfer functions are bounded. Then the observed spectrum
remains H H*+sigma^2 I exactly. Each scalar noise is stationary Gaussian and
reversible, noises are mutually independent and independent of x. Thus exact
block equality with a white-floor target can satisfy positive definiteness of
both latent and observed spectra.

For a target with a nonsingular N-block covariance but no specified white
floor, adding an arbitrarily small independent white floor changes its block
Gaussian law by arbitrarily small total variation. This gives the needed
closure result under a strict positive-definiteness convention.

### Density for regular stationary Gaussian observations

Let a real stationary p-vector Gaussian target have an integrable Hermitian
positive-semidefinite spectral density S(f), with S(-f)=conj S(f), and a
nonsingular N-block covariance. Its principal square root G(f)=S(f)^(1/2) has
finite L2 norm and the same reality symmetry. Fourier-polynomial truncations
G_m converge to G in L2 and have real coefficient matrices. A common integer
frequency phase shift makes every polynomial causal without changing
G_m G_m*. Furthermore,

    ||G_m G_m* - G G*||_L1
      <= ||G_m-G||_L2 (||G_m||_L2+||G||_L2) -> 0.

Thus these real causal finite-MA spectra approximate every target covariance
lag, and in particular its finite N-block covariance. The Gaussian block laws
converge in total variation: covariance convergence to a positive-definite
limit implies Gaussian KL convergence to zero, then Pinsker's inequality
applies. Each finite-MA block is exactly realizable by the scalar serialization
construction, or arbitrarily approximable by its strictly positive-definite
version. Therefore the M0 block laws are dense in the regular stationary
Gaussian block laws.

This statement only needs absolutely continuous finite-variance spectra.
Extensions using smoothing of spectral measures are possible, but are not
required for the present result.

### Statistical impossibility corollary and precise scope

Let phi_N be any measurable randomized test, 0<=phi_N<=1, based on a fixed
finite block, and suppose

    sup_{P in M0} E_P[phi_N] <= alpha,

where M0 permits arbitrary real causal stable FIR channel filters with no
uniform memory bound. For every regular stationary Gaussian alternative Q
above, choose a sequence of null block laws P_m converging to Q in total
variation. Then

    E_Q[phi_N] = lim_m E_Pm[phi_N] <= alpha.

So a test uniformly valid over that unrestricted null has power no greater
than alpha against every such finite-record Gaussian alternative. This is a
full-data result. Tapers, split halves, multiple spectral bins, and any other
measurable transformation inherit the equivalence.

The null filters in the construction depend on N and can have memory longer
than the record. Pointwise asymptotic inference with a fixed filter, externally
bounded filter memory, controlled smoothness, or informative interventions has
a different scope. The result identifies exactly why some such restriction is
needed for a useful finite-record test.

### Independent numerical illustration

A random real 3-input/3-output MA(4), N=16, was matched with shifts (0,21,42)
and causal FIR memory 46. Independent white output noise variance .2 was added
to both. The two separately constructed innovation-to-observation matrices
produce 48x48 block covariance matrices with:

- maximum absolute difference: **4.44089209850e-16**;
- Frobenius difference: **2.87702561427e-15**;
- target block minimum eigenvalue: **0.428752963934**.

Over 501 frequencies, the target's maximum absolute imaginary coherency-cycle
product is **0.0705047943837**, while the serialized null's maximum is
**2.22044604925e-16**. Their full Gaussian distributions for the 16-sample block
are nevertheless identical. All coefficient arrays and covariances are saved
in `serialization_covariance_example.npz`.

## 2. Weak-coherence and weak-closure sharpness

Let the three edge magnitudes be r_e=epsilon a_e, with fixed positive a_e, and
let the cycle phase psi be small. Every phase assignment has edge angles
summing to psi modulo 2pi. For weak coherence, R=I+O(epsilon), so

    E(U C U*) = 2 sum_e r_e^2 theta_e^2
                  *[1+O(epsilon)+O(max_e theta_e^2)]

in the small-angle branch. The leading constrained minimization is

    min_{sum theta_e=psi} 2 sum_e r_e^2 theta_e^2
      = 2 psi^2 / sum_e r_e^(-2),

with optimal residual edge phases

    theta_e = psi r_e^(-2) / sum_j r_j^(-2).

A weighted Cauchy–Schwarz inequality proves the minimum. Since the small-angle
candidate has energy O(epsilon^2 psi^2), an optimal assignment must approach a
real phase assignment as psi->0. Real sign gauges put it into the same local
branch. Consequently,

    E_*(C) = [2 psi^2 / sum_e r_e^(-2)]
               [1+O(epsilon)+O(psi^2)].

The analytic triangle bound can be written exactly as

    L(C)=2 sin^2(psi) / [lambda_max(C)^2 sum_e r_e^(-2)].

Since lambda_max(C)=1+O(epsilon), it has the same leading asymptotic expression.
Therefore **E_*/L -> 1** as epsilon and psi tend to zero with the a_e fixed.
The constant 2 in the proposed universal bound is sharp: any larger fixed
constant in the same expression would fail along this family.

The reciprocal-squared sum also identifies a weakest-edge bottleneck. When
one r_e is much smaller than the other two, nearly all residual phase is
assigned to that edge and the leading minimum is 2 r_min^2 psi^2. A missing
edge removes the triangular constraint entirely, consistently with the
support-graph theorem.

### Stable independent numerical verification

Direct trace subtraction loses precision at tiny E. The independent optimizer
instead evaluates the skew-whitened eigenvalues b_j and computes
sum_j b_j^2/(1-b_j^2), avoiding subtraction of n. Across 75 parameter cases,
epsilon and psi range from .1 to .001, with three fixed magnitude ratios.
Representative epsilon=psi=.001 results:

| a | E_* numerical | L | E_*/L |
|---|---:|---:|---:|
| (1,1,1) | 6.68001978e-13 | 6.64007758e-13 | 1.00601532 |
| (1,.7,.25) | 1.05135445e-13 | 1.04755228e-13 | 1.00362957 |
| (1,.7,.05) | 4.96332518e-15 | 4.94994696e-15 | 1.00270270 |

For (1,.7,.25), the leading phase fractions are
(.0525188,.1071811,.8403001); the optimized fractions at .001/.001 are
(.0524018,.1069619,.8406363). For the weakest-edge ratio (1,.7,.05), the weakest
edge carries approximately 99.25% of the residual phase.

### Scope correction for a general gauge-tangent extension

The proposed local expansion about a fixed real R,

    min_Phi ||R^(-1/2)(Y+[Phi,R])R^(-1/2)||_F^2,

is a valid leading weak-asymmetry projection when the support graph of R is
connected, after fixing the irrelevant global phase. Independent examples in
dimensions 3,5,8 converge to this prediction as perturbation size decreases.
For disconnected R, free O(1) relative component phases require an additional
outer minimization. For example R=I_2 and nonzero real skew Y give
[Phi,R]=0, yet a fixed relative phase turns I+i delta Y real and E_*=0.
The general formula should therefore be omitted or explicitly qualified; the
weak-triangle result above is independently valid and needs no such extension.

## 3. Conditional finite-resolution certificate from a valid error bound

Let C be the true 3x3 coherency at a frequency and Chat a valid estimated
coherency, both Hermitian positive-semidefinite with unit diagonal. Suppose a
simultaneous complex-entry error event holds:

    max_ij |Chat_ij-C_ij| <= epsilon.

The error must include finite-window leakage as well as stochastic estimation
error. All coherency entries have modulus at most one. Telescoping the three
factors gives

    |Im Phat-Im P| <= |Phat-P| <= 3 epsilon.

Write w=(|Im Phat|-3epsilon)_+. Since lambda_max(C)<=3 and D(C)<=3,

    E_*(C) >= (2/27) w^2.

A sharper version uses

    r_e^+ = min(1,|Chat_e|+epsilon),
    D^+ = sum_{e<j} (r_e^+ r_j^+)^2,
    lambda^+ = min(3,lambda_max(Chat)+2epsilon).

Then

    E_*(C) >= 2 w^2 / [(lambda^+)^2 D^+],

with value zero when D^+=0. The 2epsilon spectral perturbation bound is valid
because the difference has zero diagonal and at most two off-diagonal errors
per row. The proposed 3epsilon version is also valid, with a looser denominator.

If the entrywise event has probability at least 1-alpha, this lower bound has
the same coverage. Under the project's Gaussian observation assumptions it
also lower-bounds the corresponding latent Gaussian reversal density. An
externally justified error event supplies the information excluded by the
unrestricted-filter no-go theorem; no claim is made that the data alone provide
such a bound uniformly over arbitrary filters.

In 1,000 independent perturbed-coherency examples, the conditional bound never
exceeded the true analytic L. The largest conditional/true-L ratio was
.9995614. This numerical check corroborates the deterministic inequalities.

## 4. Extended exact leakage curves: 1 to 32 seconds

The original reversible two-mode counterexample, 125-ms delayed channel,
160-Hz sampling, Hann taper and linear detrending was retained exactly. Only
the previously missing 16- and 32-second cases were computed. The 32-second
calculation took approximately 1.77 seconds. These are expected finite-window
spectra from the exact lag covariance, not Monte Carlo estimates.

For the 12-channel repetition pattern, 64 of 220 triples contain the three
distinct channel types. The mean-square score is therefore exactly 64/220
times the distinct 3-channel score.

| T (s) | v at 10 Hz | T^2 v at 10 Hz | 12-channel mean v^2 |
|---:|---:|---:|---:|
| 1 | .05288962 | .05288962 | 3.98390817e-5 |
| 2 | .04359693 | .17438773 | 1.32330293e-5 |
| 4 | .02587651 | .41402422 | 2.43391724e-6 |
| 8 | .00836766 | .53553034 | 1.87908828e-7 |
| 16 | .00210175 | .53804922 | 1.24231602e-8 |
| 32 | .00052248 | .53502404 | 8.02760785e-10 |

The leading leakage expansion predicts T^2 v(10 Hz)->**.533547442688**.
Observed/predicted ratios are .0991,.3268,.7760,1.0037,1.0084,1.0028.
Thus the example enters the approximate T^-2 amplitude regime around 8 seconds;
the 2-second and 4-second estimates have substantial non-asymptotic effects.
The integrated score ratios Q(8)/Q(16)=15.13 and Q(16)/Q(32)=15.48 approach the
predicted factor 16 for T^-4. Tables for 25-ms and 500-ms delays are also saved.
These scales belong to this specified smooth two-mode model; a different
spectral linewidth or filter may enter its asymptotic regime elsewhere.

## 5. Numerical certificate conditioning and resolution

The analytic PSD dual theorem remains correct. Floating-point certification
requires separate treatment of inverse formation, eigenvalues and cancellation.

The existing shift 1e-12 max(1,||A||_2) creates an absolute certificate-gap floor
of n/2 times that amount. Even a well-conditioned weak-coherence matrix can
have E_* below this floor: the balanced .001/.001 case has E_*=6.68e-13 but a
minimum buffer gap of approximately 1.50e-12. Its analytic L remains useful.
This is a resolution issue distinct from ill conditioning.

A seven-case condition sweep found objective disagreement between independent
Cholesky and quadratic evaluations of 2.55e-8 at condition number 6.29e4,
8.64e-5 at 1.00e7, and 2.99 at 8.12e8. The respective eigenvalue buffers were
2.10e-8,3.35e-6,.000271. Thus an eigenvalue buffer alone does not control the
inverse error. A guard such as cond(C)<=1e6 plus returned inverse residuals is
a practical declared scope restriction, not a universal proof of that buffer.

A matrix-specific repair is available. Let Bhat be a Hermitian approximate
inverse of C^T and set rho=||I-C^T Bhat||_2<1. In exact arithmetic,

    ||(C^T)^(-1)-Bhat||_2 <= ||Bhat||_2 rho/(1-rho) = e_A.

Schur multiplication by the unit-diagonal PSD matrix C^T contracts operator
norm on Hermitian matrices: apply the positive Schur map to
-e_A I <= inverse_error <= e_A I. Thus the error in the computed quadratic
matrix Ahat=Bhat elementwise-multiplied by C^T is also bounded by e_A.

Adding e_A to the dual eigenvalue shift makes the dual feasible for the true A;
adding n e_A/2 to the candidate objective produces a valid upper bound. A
fully rigorous floating-point implementation also needs upward-rounded or
conservatively padded residual and eigenvalue error bounds. Otherwise report
the interval as a floating-point certificate for the computed matrix, with its
condition number and residual. No additional conditioning sweep is required.

### Final implementation inspection

The updated `phase_reversal_certificate` was inspected after the residual
propagation repair. It symmetrizes the inverse, forms a padded inverse
residual, propagates its bound through the Schur map, adds this matrix error to
the dual shift, and adds n/2 times the error to the upper endpoint. These
placements, signs and factors are correct. Its returned condition number,
measured/padded residual and propagated matrix error make the numerical scope
reviewable. Rejecting residual_upper>=.1 avoids a rapidly uninformative error
bound. The updated docstring correctly describes ordinary floating-point
numerical certification rather than interval arithmetic. No further broad
computation was needed for this inspection.
