from pathlib import Path
import re
P=Path(__file__).resolve().parents[1]/'manuscript/source'
m=(P/'main.tex').read_text();a=(P/'appendices.tex').read_text();s=(P/'supplement.tex').read_text()
# Fix an actual contradiction: * is the adjoint, whereas real-process frequency
# reflection uses entrywise conjugation.
for name,text in [('m',m),('a',a),('s',s)]:
 text=text.replace(r'S_y(-\omega)=S_y(\omega)^*',r'S_y(-\omega)=\overline{S_y(\omega)}=S_y(\omega)^{\mathsf T}')
 text=text.replace(r'S(-\omega)=S(\omega)^*',r'S(-\omega)=\overline{S(\omega)}=S(\omega)^{\mathsf T}')
 if name=='m':m=text
 elif name=='a':a=text
 else:s=text
m=m.replace('The spectral matrix is Hermitian and satisfies the real-process symmetry','We use $A^*$ for the conjugate transpose, $A^{\\mathsf T}$ for the transpose, and $\\overline A$ for entrywise conjugation. The spectral matrix is Hermitian and satisfies the real-process symmetry')
m=re.sub(r'Eq\. \((\d+)\)',lambda x:r'Eq.~\eqref{eq:'+x[1]+'}',m)
m=re.sub(r'Equation \((\d+)\)',lambda x:r'Equation~\eqref{eq:'+x[1]+'}',m)
abstract=r'''Temporal irreversibility in a recording reflects both latent dynamics and the architecture of observation. For every continuously differentiable, positive-definite spectral matrix of a real stationary Gaussian process, we construct an exactly equivalent observation of a reversible latent process with twice the dimension, a fixed real mixing matrix, and one sample of differential delay. For finite-order target spectra, the latent representation can also have finite covariance support. We derive the minimum hidden spectral-trace cost at a fixed frequency and its broadband optimum in a rotational spectral family, distinguishing fixed-strength short-delay divergence from a finite joint low-frequency limit. Under independent filtering of defined channels, spectral cycles instead preserve a quantitative component of time-reversal asymmetry. We characterize the finite-bandwidth bias of these cycles and construct confidence lower bounds from finite recordings. Independent calibration records yield a spectral upper confidence bound without knowing the normalized spectrum, provided a relative covariance-tail envelope is specified. Simulations quantify calibration, power, and the loss of sensitivity for long correlations. Controlled transformations of an archived EEG recording complement a matched-window cohort illustration of reference sensitivity. These results identify the observation assumptions and quantitative resources that connect an observable time arrow to latent dynamics.'''
m=re.sub(r'\\begin\{abstract\}.*?\\end\{abstract\}',lambda _:r'\begin{abstract}'+'\n'+abstract+'\n'+r'\end{abstract}',m,flags=re.S)
# Precise rather than sweeping originality claim.
needle='A particularly consequential distinction concerns the ordering of temporal filtering and spatial mixing.'
prior=r'''Classical matrix spectral factorization writes $S=FF^*$ and realizes a process by a target-dependent causal filter applied to white innovations~\cite{ephremidze2007,ephremidze2014}. Our representation question fixes the observation operator in advance as $[I,e^{-i\omega}I]$ and places the target dependence in a positive-definite reversible latent spectrum. This separates the claim from general Gaussian realization theory. The white-latent moving-average example below is an explicit special case of that classical theory; the arbitrary-spectrum statement concerns the additional fixed-operator constraint. Related delayed and non-reversible Gaussian-process models~\cite{gokcen2015,rutten2020} fit structured latent dynamics, whereas the present theorem characterizes a full-law equivalence class. The comparison with two-branch alias calibration~\cite{xu2026} concerns a different, fixed three-channel observation map. The Supplemental Material records the compared model classes and the literature-reading coverage.

'''
m=m.replace(needle,prior+needle)
m=m.replace('For a dense support graph, triangle cycles suffice.','For a complete support graph, triangle cycles suffice.')
m=m.replace('The general theorem continues to cover arbitrary regular spectra; this memoryless corollary covers the sine-skew subclass.','This explicit moving-average realization illustrates the sine-skew subclass; its role is to expose the mechanism rather than claim a new spectral-factorization theorem.')
finite=r'''\subsection{Finite-order latent dynamics}
The general lift also admits a finite-order refinement. If the target spectrum is a strictly positive trigonometric polynomial, a real even positive-definite \emph{polynomial} latent spectrum can reproduce it through the same one-sample observation map. Approximate the continuous block $V$ in the lift uniformly by even Fej\'er polynomials, while enforcing the other blocks through the exact observation identity. Strict positivity persists once the approximation is sufficiently accurate. Matrix spectral factorization then gives a finite-order causal moving-average realization~\cite{ephremidze2007,ephremidze2014}; Appendix~\ref{app:finiteorderR4} gives the proof.

We tested 72 independently generated target spectra with dimensions $2,3,6$ and moving-average orders $1,2,3$. All admitted positive finite-support lifts at tested latent orders between 4 and 34. The maximum relative reconstruction error was $1.22\times10^{-15}$. Positivity checks included a derivative-based allowance between frequency-grid points; failed trial orders and refined verification grids are retained. This result establishes finite dynamical complexity for polynomial targets, with the required latent order depending on the particular target.

'''
m=m.replace(r'\subsection{The identification consequence}',finite+r'\subsection{The identification consequence}')
broad=r'''\subsection{An exact broadband optimum}
For the entire rotational spectrum $S_\beta(\omega)=g(\omega)[I_2+i\beta\sin\omega J]$, with a positive even scalar spectrum $g$, the resource optimum can be realized consistently across frequency. Over real even integrable positive-semidefinite latent spectra and the fixed observation $[I,e^{-i\omega}I]$, the minimum total latent-to-observed trace ratio is
\begin{equation}\label{eq:broadmain}
 \mathcal T_{\min}=\frac{\int_{-\pi}^{\pi}g(\omega)f_\beta(\omega)\,d\omega}
 {\int_{-\pi}^{\pi}g(\omega)\,d\omega},
\end{equation}
where $f_\beta$ is the finite joint-limit expression in Eq.~\eqref{eq:jointlimit}. An explicit real even optimizer attains the pointwise minimum almost everywhere. Continuous, strictly positive-definite feasible spectra approach the same integrated value, and each admits a causal square-summable spectral factor (Appendix~\ref{app:broadbandR4}). Thus this is an optimization over valid full-process spectra, with unrestricted causal realization order.

For $\beta=0.8$ and $g=1$, the minimum ratio is $0.854239$, compared with 1 for the white-latent representation. For the normalized AR spectrum with pole 0.8 it is $0.829345$. Fifteen strength--color settings were evaluated by quadrature; their explicit optimizing spectra reproduced the target with maximum elementwise discrepancy $1.78\times10^{-15}$. Fixed-strength divergence and the finite low-frequency path describe different resource questions, while Eq.~\eqref{eq:broadmain} supplies the full-band answer for this specified family.

'''
m=m.replace(r'\subsection{Independent numerical optimization}',broad+r'\subsection{Independent numerical optimization}')
cal=r'''\subsection{Independent calibration without a known spectral shape}\label{sec:unknowncalR4}
The preceding simulations supplied $B$ from the generating model. We now remove knowledge of the normalized spectrum. Suppose a deterministic dependence-class constraint gives $T_L\le\tau_L B_*$, where $B_*=\sup_\omega\lambda_{\max}S(\omega)$ is unknown. An independent calibration record of length $m$ yields an upper confidence bound for $B_*$. With $F_c>\pi L$, define
\begin{align}
 c_L&=1-\pi L/F_c,\quad \nu_c=\log(2d^2F_c/\alpha_c),\\
 r_c&=2[\sqrt{V_{m,L}\nu_c}+V_{m,L}\nu_c],\\
 A_c&=\max_j\|\widehat S_L^{\rm cal}(\omega_j)\|_2.
\end{align}
If $\Delta_c=c_L-dr_c-dc_L\tau_L>0$, then
\begin{equation}\label{eq:calUmain}
 U_B=A_c/\Delta_c,\qquad
 \Pr(B_*\le U_B)\ge1-\alpha_c.
\end{equation}
Otherwise the procedure abstains. The proof in Appendix~\ref{app:unknowncalR4} solves a self-consistent bound: the unknown $B_*$ controls the estimation error, and the empirical spectrum bounds $B_*$ once the error coefficient is smaller than one. No true covariance matrix, scale, or spectral shape is an input. The structural tail envelope remains an assumption. With an independent test record, substituting $B=U_B$ and $T_L=\tau_LU_B$ into the original certificate gives total failure probability at most $\alpha_c+\alpha_t$.

We used $\alpha_c=\alpha_t=0.025$ in 600 independent calibration--test pairs. Multiple calibration and test lengths were nested prefixes, producing 1,680 calibration analyses and 8,520 test analyses, including oracle and sensitivity controls. Among the calibration analyses, 1,320 produced finite upper bounds; 360 short-record cases abstained. All finite bounds exceeded the population spectral maximum on the diagnostic grid, and all valid-model certificates remained below their known population triangle bounds. No calibrated null analysis produced a positive certificate.

For the unknown-shape MA(1) alternative with $b=0.9$, a test record of 32,768 samples yielded 120/120 positive certificates after 65,536 independent calibration samples. At 131,072 test samples, 16,384 calibration samples sufficed for 120/120 positives. The median calibration bound divided by the true grid maximum fell from 2.68 at $m=4096$ to 1.20 at $m=65536$. These are distinct from the earlier known-shape scale experiments. The full null, weaker-signal, and oracle comparisons are retained in the Supplemental Material.

We also tested infinite-correlation AR--MA processes with unknown poles within specified bounds. Their calibration envelopes covered, but the conservative certificates remained zero through 524,288 test samples. In a separate delayed reversible-source stress test, falsely imposing finite covariance support caused all 80 spectral envelopes to miss the true spectrum; the valid tail class covered in all 80 repetitions. Both arms returned zero certificates at the tested length. This separates uncertainty about spectral shape from the essential dependence-class assumption and documents the method's current power cost.

\begin{figure*}[t]
\centering
\includegraphics[width=.98\linewidth]{figures/fig_calibration_R4.pdf}
\caption{\label{fig:calibrationR4}\textbf{Independent calibration with unknown spectral shape.} (a) Distribution of $U_B/B_*$ in the strong MA(1) condition; points summarize 120 independent pairs at each length, with medians and 10th--90th percentiles. $B_*$ is evaluated on the population diagnostic grid only for validation, and is not supplied to calibration. The $m=1024$ setting abstains because the deterministic resolution condition fails. (b) Fraction of positive certificates as calibration and test lengths increase, using $b=0.9$; each cell contains 120 pairs. Lengths within a pair are nested, so cells are dependent. (c) Positive-certificate fractions in the colored AR--MA alternatives remain zero at the longest tested length, despite valid calibration coverage. Error bars are two-sided exact 95\% binomial intervals within each setting. Structural pole/tail bounds, rather than the true normalized spectrum, are supplied.}
\end{figure*}

'''
m=m.replace(r'\section{OBSERVATION-COORDINATE SENSITIVITY IN HUMAN EEG}',cal+r'\section{OBSERVATION-COORDINATE SENSITIVITY IN HUMAN EEG}')
controls=r'''\subsection{Known transformations of an archived EEG spectrum}
To test the observation-level transformation laws directly, we reprocessed the archived raw record S011R01. Pooling the 24 predefined two-second windows yielded positive-definite 12-channel spectral estimates at 57 frequencies between 2 and 30 Hz. Across 80 independently drawn complex diagonal frequency responses, the largest change in any normalized triangle product was $1.22\times10^{-15}$. Across 80 real orthogonal channel rotations, the maximum relative change in the raw reversal density was $7.92\times10^{-14}$, while triangle products generally changed. The 64-channel average-reference operation supplied a third, noninvertible comparison.

These are controlled numerical transformations of one real recording, rather than additional biological replicates. The diagonal responses were applied to the estimated spectra \emph{after} windowing; filtering time series before windowing introduces the distinct finite-bandwidth effect analyzed above. Together with the matched-cohort comparison, this experiment connects the exact transformation laws to the data-processing pipeline while keeping the EEG application at the level of observed statistics.

'''
m=m.replace(r'\subsection{Implications for neural time-asymmetry analysis}',controls+r'\subsection{Implications for neural time-asymmetry analysis}')
# Correct the inferential null; p-value is nominal for the old sign symmetry test.
m=m.replace('Thus a reversible-latent observation model generated a highly repeatable, statistically significant windowed closure signal.','The nominal sign-flip test therefore rejects a score-symmetry null in a model with reversible latent dynamics and real population closure. Its randomization assumption is symmetry of the participant-level signed scores (with the required joint-conjugation and between-half conditions), which the tapered filtered process need not satisfy. The false attribution concerns latent reversibility under unknown filtering; the observed process itself may have positive raw reversal divergence.')
m=m.replace('The theorem identifies an observational equivalence class containing latent systems with different time-reversal properties.','The theorem identifies an observational equivalence class containing latent systems with different time-reversal properties. The observation map is temporally extended and does not commute with reversal: reversing its output is generally different from applying the same causal map to a reversed latent input. The two output laws therefore do not follow from one common reversal-equivariant data-processing channel. Statistical reversibility of the latent coordinates specifies their path law; a thermodynamic model of the recording device would be an additional physical description.')
# Minor claim/typography corrections.
m=m.replace('For independent Gaussian latent sources,','For mutually independent Gaussian latent sources,')
m=m.replace('The minimum-power theorem assumes a fixed mixing-gain normalization and a rotational two-channel spectrum.','The resource theorems assume fixed mixing gains and a rotational two-channel spectral family; the broadband result optimizes over complete admissible spectra in that family.')
m=m.replace('The positive statistical certificates concern a channelwise observation class with externally supplied spectral and covariance-tail constraints.','The positive statistical certificates concern a channelwise observation class with quantitative covariance-tail constraints. The new independent calibration method learns a spectral upper bound without knowing its normalized shape, while retaining that dependence-class constraint.')
# Accurate availability statement, no invented repository DOI or author declaration.
m=m.replace('Before journal submission, a permanent repository identifier should be inserted in the final data-availability statement.','The source archive includes fixed seeds, per-repetition outputs, original input checksums, and a manifest identifying this revision. The public EEG source remains separately cited.')
m=m.replace('the archival public release identifier will be supplied by the authors.','the archive supplied with this manuscript contains all code used for the reported computational analyses.')
# State what the new experiments achieved and their negative findings in Discussion.
mark='The human EEG analysis illustrates why these distinctions matter for neural recordings.'
addition=r'''The finite-order corollary shows that exact fixed-operator equivalence persists for targets with finite covariance support, using finite-order latent realizations. The broadband trace result supplies a full-process optimum in the rotational family. Independently calibrated unknown-shape spectra now give a concrete route beyond oracle knowledge of $B$. Their performance also marks a substantive practical boundary: the global spectral envelopes remain too conservative to certify the tested long-correlation alternatives. This behavior motivates sharper frequency-local or model-specific bounds rather than a claim of universal short-record sensitivity.

'''
m=m.replace(mark,addition+mark)
m=m.replace(r'\input{source/appendices}',r'\input{source/appendices}'+'\n'+r'\input{source/r4_appendices}')
# Fix the cost optimizer's jump, not its continuous value.
a=a.replace('the limiting case is continuous.','the optimal value is continuous, but $q$ has different one-sided limits as $\\cos\\theta$ changes sign. At $\\cos\\theta=0$, one may choose $q=0$ and $t=1$.')
# Clarify off-diagonal concentration constants.
a=a.replace('The conservative radius in Eq.~\\eqref{eq:25} bounds these components jointly after a union bound over $d^2F$ real entry components.',r'For each off-diagonal real or imaginary component, these symmetric forms have Frobenius norm at most $\sqrt{V_{N,L}/2}$ and operator norm at most $V_{N,L}/2$. Combining the two component errors by the Euclidean norm yields a radius no larger than Eq.~\eqref{eq:25}. The $d$ real diagonals and $d(d-1)$ off-diagonal real components give $d^2F$ events; their two-sided Gaussian tail bounds and the chosen $\nu$ establish the union bound.')
s=s.replace('All spectral variables are real-valued Gaussian and even under time reversal unless explicitly stated.','The underlying time-domain processes are real-valued Gaussian, with coordinates even under time reversal unless explicitly stated; their spectral matrices may be complex.')
s=s.replace('For a dense support graph, triangles suffice.','For a complete support graph, triangles suffice.')
s=s.replace('23,520 evaluations.','23,520 dimension--parameter--frequency evaluations derived from 120 random skew matrices. These are numerical evaluation counts, not independent statistical replications.')
(P/'main.tex').write_text(m);(P/'appendices.tex').write_text(a);(P/'supplement.tex').write_text(s)
# Bibliography: latest verified record, and exact classical factorization foundations.
b=(P/'references.bib').read_text()
b=re.sub(r'@misc\{xu2026,.*?\n?\}',r'''@misc{xu2026,
 author={Xu, Zihuan}, title={Phase calibration for certifying Gaussian spectral irreversibility under two-branch aliasing},
 year={2026}, doi={10.5281/zenodo.23951714},url={https://zenodo.org/records/23951714},note={Preprint, version 3}}
''',b,flags=re.S)
b+=r'''
@misc{ephremidze2007,
 author={Ephremidze, Lasha and Janashia, Gigla and Lagvilava, Edem},
 title={A Simple Proof of the Matrix-Valued Fej\'er--Riesz Theorem},
 year={2007},eprint={0708.2179},archivePrefix={arXiv},url={https://arxiv.org/abs/0708.2179}}
@misc{ephremidze2014,
 author={Ephremidze, Lasha},title={An Elementary Proof of the Polynomial Matrix Spectral Factorization Theorem},
 year={2010},eprint={1011.3777},archivePrefix={arXiv},url={https://arxiv.org/abs/1011.3777}}
'''
(P/'references.bib').write_text(b)
print('Patched main, supplement, appendices, references.')
