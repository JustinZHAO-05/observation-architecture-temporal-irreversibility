# Figure captions

Main figures 1–7 and supplementary figures S1–S8.

## Fig1

[Individual caption](03_FIGURE_PRODUCTION/redraw/Fig1/caption.md)

**FIG. 1. From observed temporal asymmetry to observation architecture.** (a) One 25-sample realization of the three-channel Gaussian MA(1) process with spectrum $S_y(\omega)=I-i b\sin\omega\,K$ and $b=0.9$. All three traces use the same vertical scale in population standard deviations (SD), and $t$ is the sample index. The matrices below show the exact population quantities $\Gamma(+1)$, $\Gamma(-1)$, and $\Delta\Gamma=\Gamma(+1)-\Gamma(-1)$, where $\Gamma(\ell)=\mathbb{E}[y_{t+\ell}y_t^\mathsf{T}]$. Both matrix axes follow the trace order $y_1,y_2,y_3$. The row denotes the shifted channel and the column denotes the reference channel. The covariance color scale is in $\mathrm{SD}^2$. Time reversal exchanges $\Gamma(+1)$ and $\Gamma(-1)=\Gamma(+1)^\mathsf{T}$. (b) Real symmetric and imaginary antisymmetric parts of the same spectrum at $\omega=\pi/2$ rad/sample. In both matrices, rows and columns index the observed channels $y_1,y_2,y_3$ in the same order as in (a). At this frequency, $\operatorname{Re}S_y=I$ and $\operatorname{Im}S_y=-\Delta\Gamma$. The complex-plane inset shows the entries $S_{11}$, $S_{12}$, and $S_{21}$ of this matrix. (c) Model A applies each temporal response $h_i$ to an already defined channel $x_i$. Model B first applies source-specific responses and then maps the filtered sources to observations through the real spatial mixer $M$. The blue upper plane carries the direct source vector $u$, and the purple lower plane carries the source vector $v$ through a one-sample delay. With $I_3$ the three-dimensional identity, the mixer $M=[I_3\ I_3]$ adds corresponding entries of the two branches, giving $y_i(t)=u_i(t)+v_i(t-1)$. Thin undirected lines show the nonzero instantaneous cross-covariances between the two source vectors in this example. The small traces show the inputs and outputs of the illustrated operations. The waveform colors identify the three channels.

## Fig2

[Individual caption](03_FIGURE_PRODUCTION/redraw/Fig2/caption.md)

**FIG. 2. Exact observational equivalence from a one-sample delay.** (a) A reversible, six-dimensional Gaussian latent process $x_t=(u_t,v_t)$ has a real, even spectral matrix $G(\omega)$. The blue upper layer and purple lower layer show the $u$ and $v$ components. Fine undirected lines mark the six nonzero instantaneous covariances between the layers. The $u$ paths are direct. On each $v$ path, $z^{-1}$ maps the input sequence $v_i(t)$ to the output $v_i(t-1)$. The ruler marks the source sample times. The left guide marks $v_i(t-1)$ on the delayed branches and the right guide marks $u_i(t)$ on the direct branches. Each sum gives $y_i(t)=u_i(t)+v_i(t-1)$. The output traces show a 25-sample realization. (b) Lag-one covariance $\Gamma(1)$, its transpose $\Gamma(1)^\mathsf{T}$, and their difference $\Delta\Gamma(1)$ for the latent (upper) and observed (lower) processes. All six matrices use the same zero-centered scale. In the original covariance, rows index the shifted channel and columns the reference channel. The latent difference is the $6\times6$ zero matrix. The observed difference has six nonzero entries. Covariances are in squared units of one observed population standard deviation. (c) The $96\times96$ covariance for 32 samples of three channels is represented by its distinct $3\times3$ lag blocks, with $\Gamma_{ij}(\ell)=\mathbb E[y_i(t+\ell)y_j(t)]$. Only the blocks at $\ell=-1,0,+1$ are nonzero. The upper-left and lower-right triangles of each cell give the target and constructed values on a common scale, respectively. The lower trace shows the maximum absolute entrywise residual at all 63 lags, covering all 9,216 covariance entries. The construction equates the population spectra and hence the full centered Gaussian observation laws. (d) Upper, the imaginary cycle of the normalized cross-spectra, $P=C_{12}C_{23}C_{31}$, for the $b=0.9$ target (analytic line) and the mapped latent process (open markers on a subset of a 513-point grid). Lower, the spectral reversal densities $e_x(\omega)$ and $e_y(\omega)$ share the same normalized frequency axis $\omega/\pi$. The dashed guide marks $\omega/\pi=1/2$ in both plots. The six-dimensional latent density is identically zero, so $\mathcal R_x=0$. The orange area gives the three-dimensional observed rate $\mathcal R_y=2[(1-b^2)^{-1/2}-1]=2.588315$ nats/sample to six decimals.

## Fig3

[Individual caption](03_FIGURE_PRODUCTION/redraw/Fig3/caption.md)

**FIG. 3. The spectral-power cost of observational equivalence.** At a fixed frequency, the observation uses unit gains, \(y=u+e^{-i\theta}v\), with target \(S=I_2+ibJ\) and \(J_{12}=1=-J_{21}\), \(J_{11}=J_{22}=0\). **(a)** Two real positive semidefinite latent spectra \(G_1,G_2\) attain the same target at \(b=0.8\). The circle marks \(\theta_1=0.80\) rad and the diamond marks \(\theta_2=0.05\) rad. The unit phasors show the phase of the \(v\) transfer factor relative to the positive real axis. The colored bars end at \(\operatorname{tr}G_k/\operatorname{tr}S=t_{\min}\), approximately 1.1309 and 160.4336, on the same logarithmic ruler. Both bars start at \(t_{\min}=0.5\). **(b)** The analytic minimum for \(b=0.2,0.5,0.8,0.9\). The short black dashed segment gives the \(b=0.8\) small-phase asymptote \(0.4/|\theta|^2\). At every fixed \(0<b<1\), \(t_{\min}\sim(1-\sqrt{1-b^2})/|\theta|^2\) as \(\theta\to0\). **(c)** The color encodes \(\log_{10}t_{\min}\) and the contours label \(t_{\min}=1,10,100,1000\) on the positive phase branch. The circle and diamond locate the same two optima in (a) and (b). Phase is given in radians and the spectral trace ratio is dimensionless. The 32 full-matrix optimization checks are in Fig. S4.

## Fig4

[Individual caption](03_FIGURE_PRODUCTION/redraw/Fig4/caption.md)

**FIG. 4. Filter-invariant spectral cycles and quantitative reversal bounds.** **(a)** The same three observed channels are shown before and after independent temporal filters, with \(h_i=|h_i|e^{i\phi_i}\). The coherencies transform as \(C'_{ij}=e^{i(\phi_i-\phi_j)}C_{ij}\), so the phase increments sum to zero around \(1\to2\to3\to1\). Arrows on the triangles indicate the traversal used to form the product. The phasors show the corresponding complex entries at \(\omega/\pi=1/2\), marked by vertical guides on the frequency axes. At every frequency, the closure phase \(\psi=\arg(C_{12}C_{23}C_{31})\) coincides before and after filtering. **(b)** Reversal density for the positive-definite family with \(r_{12}=r_{23}=r_{31}=0.30\). The orange curve uses the midpoints of the 181 archived primal–dual intervals for \(\mathcal E_*\), and circles mark a subset. The maximum interval width is \(2.57\times10^{-12}\) nats. The green dashed curve gives the analytic lower bound \(L(C)\). The endpoints \(\psi=0,\pi\) have real cycles and attain \(\mathcal E_*=0\). The inset follows 32 joint weak-coherence and small-phase settings with \(r_{ij}=\rho\) and \(\psi=\rho\) rad. The band spans \(L/\mathcal E_{\mathrm{upper}}\) to \(L/\mathcal E_{\mathrm{lower}}\), and the dashed line indicates the limiting ratio 1. **(c)** With \(r_{12}=r_{23}=0.12\) and \(\psi=0.20\) rad, the circle, square, and diamond correspond to \(r_{31}=0.12,0.06,0.024\), respectively. Edge width is proportional to coherency magnitude. The orange bars and percentages give the fraction \(\theta_{31}^\ast/\psi\), where \(\theta_{31}^\ast\) is the phase on edge \(31\) in the numerically minimizing gauge with edge phases reduced modulo \(\pi\) near zero. The matching markers show the minimized reversal densities. The orange curve is the joint weak-coherence, small-phase approximation \(2\psi^2/(r_{12}^{-2}+r_{23}^{-2}+r_{31}^{-2})\).

## Fig5

[Individual caption](03_FIGURE_PRODUCTION/redraw/Fig5/caption.md)

**FIG. 5. Finite-bandwidth mixing generates repeatable apparent closure.** **(a)** The same three population coherencies enter both paths. With \(P=C_{12}C_{23}C_{31}\), the upper path computes \(\langle P\rangle_w\), which is real. The lower path computes \(\prod_e\langle C_e\rangle_w\), giving nonzero imaginary closure. The normalized weights \(w_f(\nu)\propto K_{\mathrm{Hann},f}(\nu)S_{ii}(\nu)\) combine the 2 s, linearly detrended Hann power response at center frequency \(f\) with the common autospectrum of the model. Averaging coherencies with these weights equals averaging the spectral matrix and then normalizing. The orange line evaluates this expectation at a dense set of center frequencies, and the open points give the exact covariance-based results at Fourier bins. **(b)** The reversible sources have peaks at 9.75 and 10.25 Hz, linewidth 0.15 Hz and variances 1 and 0.4, respectively. Both source power spectra are scaled by the peak of the first. The gray Hann response is scaled by its own peak and centered at 10 Hz. The lower traces show the delay phases relative to 10 Hz for edges \(12,23,31\) in blue, purple and gray. The channel delays are \((0,125,0)\) ms. For the raw cross-spectral product, the leading term is \(\mu_2\sum_e(\prod_{j\ne e}r_j)r'_e d'_e\), where \(r_e\) are signed real cross-spectral amplitudes, \(d_e\) are phase offsets, and \(\mu_2\) is the frequency kernel’s second moment. Normalization divides by the product of the smoothed autospectra. **(c)** Exact discrete, detrended Hann expectations at \(T=1,2,4,8,16,32\) s. The upper plot shows the absolute imaginary coherency cycle at 10 Hz. The lower plot shows \(Q_{\mathrm{bias}}\), the mean of squared expected cycles over the 2–30 Hz bins and 220 triangles of the 12-channel model. The dashed \(T^{-2}\) guide uses the analytic coefficient at 10 Hz, and the \(T^{-4}\) guide is anchored at 32 s. **(d)** The histogram shows one \(Q\) per independent 60 s simulated record. The rug shows 42 rank-spaced archived records. The orange line is the mean over 500 records, \(1.0117\times10^{-5}\), with a 95% Monte Carlo interval of \([0.8420,1.1815]\times10^{-5}\). The diamond marks the frozen first-99 mean and links it to the nominal one-sided sign-flip result, \(p=0.00008\) from 49,999 flips. This is a false rejection under the structured reversible-latent null.

## Fig6

[Individual caption](03_FIGURE_PRODUCTION/redraw/Fig6/caption.md)

**FIG. 6. Calibrated inference of temporal irreversibility.** **(a)** The first archived no-delay Gaussian MA(1) trajectory at \(b=0.9\) and \(N=524{,}288\). From left to right, the panels show the first 48 samples of all three channels (vertically offset), the largest absolute entry of each estimated lag covariance with cutoff \(L=1\), the imaginary part of \(\widehat S_{12}\) with the simultaneous spectral radius \(\epsilon_\infty\), the absolute estimated raw-cycle imaginary part with its error allowance, and the interval lower sum on the full frequency circle. The spectral and cycle plots show the positive-frequency half. The dashed curves show the population cross-spectrum, the propagated raw-cycle error allowance, and the population triangle density in the last three stages, respectively. The green region in the cycle panel is the excess above the allowance. For the cellwise calculation, a derivative margin \(\Delta_{\mathrm{cell}}\) is added to \(\epsilon_\infty\). Each step is a lower bound throughout one of 2,048 cells. Its normalized integral is \(\underline{\mathcal R}=0.008317\) nats/sample. The generating model supplies \(B=1.9\) and \(T_L=0\), and \(1-\alpha=0.95\) is the conditional confidence level. **(b)** Fraction of trajectories with at least one positive lower bound among five prespecified frequencies, at each of four record lengths and three maximum delays. Each cell has 128 independent longest trajectories, and lengths within a model and delay use nested prefixes. Across all five families there are 7,680 analyses on 1,920 independent trajectories. The two null families produce zero positive certificates in 3,072 analyses on 768 independent long trajectories. Cell counts appear in Fig. S7. **(c)** Continuous-frequency rate lower bounds at \(b=0.9\). The 384 points, including zeros, use 128 independent long trajectories with 64 per delay condition. Each trajectory contributes three nested prefixes. Symbols encode the maximum delay. Black marks show the median and 10th–90th empirical percentiles. The vertical scale is linear within \(8\times10^{-5}\) nats/sample of zero and logarithmic above that threshold. The gray dashed line is the population triangle integral, \(0.02977\) nats/sample, for both delay conditions.

## Fig7

[Individual caption](03_FIGURE_PRODUCTION/redraw/Fig7/caption.md)

**FIG. 7. Observation-coordinate dependence of spectral-cycle structure in human EEG.** **(a)** The 64 scalp EEG channels are shown on a standard 10–05 template with the 12 analysis channels highlighted. The traces show the same 2–3 s segment of Fz from EEGMMIDB record S011R01 at 160 Hz on a common voltage scale. The 64-channel average reference subtracts the instantaneous mean across all 64 EEG signals before selecting the 12 analysis channels. Scalp outline adapted from Peter Kraemer, *EEG_10_20*, SciDraw, [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). [Original drawing](https://doi.org/10.5281/zenodo.3926093) · [EEGMMIDB](https://doi.org/10.13026/C28G6P)

**(b)** Identical accepted windows in the original and average references for the example record. Each analysis segment contains twelve 2 s windows, beginning at 2, 4, …, 24 s in A and 34, 36, …, 56 s in B. In each segment, \(P_A\) or \(P_B\) is the array of products \(C_{ij}C_{jk}C_{ki}\) from the coherencies estimated over those windows. The score \(Q\) averages the products of the two imaginary parts over 57 frequency bins from 2 to 30 Hz and 220 channel triplets.

**(c)** Original- and average-reference \(Q\) for 113 matched recordings from 71 participants. Open circles indicate 52 eyes-open recordings and filled triangles indicate 61 eyes-closed recordings. Both axes have the same scale and the dashed line indicates equality. The ratios of the average-reference to original-reference group means are 5.16 for eyes open and 2.63 for eyes closed.

**(d)** With \(\mathbf v_A=\operatorname{vec}(\operatorname{Im}P_A)\) and \(\mathbf v_B=\operatorname{vec}(\operatorname{Im}P_B)\), \(Q=\operatorname{mean}(\mathbf v_A\odot\mathbf v_B)=A\cos\varphi\), where \(A=\operatorname{RMS}(\mathbf v_A)\operatorname{RMS}(\mathbf v_B)\) and \(\cos\varphi=(\mathbf v_A\cdot\mathbf v_B)/(\|\mathbf v_A\|\|\mathbf v_B\|)\). The two-dimensional diagram preserves the norm ratio and angle of the S011R01 average-reference vectors. Each line in the scatter connects the two reference representations of the same recording. The dotted curves are contours of constant \(Q\). Amplitude and alignment are computed per recording. Each group mean of \(Q\) averages the per-record products.

**(e)** Closed-minus-open \(\Delta Q\) for the 42 participants with both conditions and both references. Lines connect each participant's two reference representations. Diamonds and bars show the mean and the 95% percentile interval from 20,000 bootstrap draws at the participant level. The mean and interval are \(1.329\,[0.798,1.860]\times10^{-4}\) for the original reference and \(1.263\,[0.811,1.734]\times10^{-4}\) for the 64-channel average reference. This exploratory contrast follows the fixed recording order in the source data.

## FigS1

[Individual caption](03_FIGURE_PRODUCTION/redraw/FigS1/caption.md)

**Figure S1. Phase geometry and allocation.**
(a) A five-vertex example has four spanning-tree edges and two closing edges. Channel phases make the tree edges real. The two closing edges carry the fundamental-cycle phases.
(b) After the tree gauge, the two example cycle phases are $0.83$ and $\pi$ rad. A real gauge requires every fundamental-cycle phase to be $0$ modulo $\pi$.
(c) Archived sharpness scans along the joint path $\epsilon=\psi$, with $r_e=\epsilon a_e$. The triangle lower bound and the numerical phase minimum agree to leading order as $\epsilon$ decreases. The full 75-point scan is provided.
(d) Fractions of the closure phase borne by each edge at $\epsilon=\psi=0.003$. Bars give the numerical phase optimum and black marks the leading weights $a_e^{-2}/\sum_j a_j^{-2}$.

## FigS2

[Individual caption](03_FIGURE_PRODUCTION/redraw/FigS2/caption.md)

**Figure S2. Finite-record serialization and population spectral differences.**
(a) With $N=16$ and MA order $L=4$, shifts of 0, 21 and 42 samples select disjoint blocks of one white-noise stream. Pale segments are the four additional innovations before each record.
(b) Target and serialized $48\times48$ covariance matrices in time-major order, with maximum absolute discrepancy $4.44\times10^{-16}$. The common color scale gives covariance in the model's variance units.
(c) Imaginary cycle and spectral-matrix Frobenius discrepancy on a common angular-frequency grid, including independent output noise of variance 0.2 in each construction. The serialized cycle is real.

## FigS3

[Individual caption](03_FIGURE_PRODUCTION/redraw/FigS3/caption.md)

**Figure S3. General construction and coordinate audit.**
(a–c) Thirty independent VAR(1) networks at each observed dimension $d=3,6,12$, evaluated at 83 frequencies per network. Each point is one network. The three panels show its maximum relative reconstruction error, minimum latent spectral eigenvalue and maximum observed Gaussian reversal density across the grid. Black marks give medians.
(d) Six hundred three-channel spectra and their paired real orthogonal rotations, replayed with seed 341903. Changes are rotated minus original. Raw reversal varies at floating-point scale. Phase-relaxed changes are midpoints of numerical primal–dual change intervals, computed with seed 261112. The CSV gives both endpoints. These are floating-point optimization bounds.

## FigS4

[Individual caption](03_FIGURE_PRODUCTION/redraw/FigS4/caption.md)

**Figure S4. Spectral-power optimization and feasibility.**
(a) All 32 independent linear-programming checks of the closed form. Marks are the bracket midpoints, with lower and PSD-feasible upper endpoints. The widths are smaller than the markers at this scale.
(b) Relative bracket width $(t_{\mathrm{upper}}-t_{\mathrm{lower}})/t_{\min}$ in parts per million. The maximum is 2.30 ppm.
(c) Equality residual and smallest latent eigenvalue for each feasible LP upper endpoint and each earlier SLSQP output. A zero residual on the log axis would be plotted at $10^{-18}$. Negative eigenvalues identify indefinite SLSQP outputs. The vertical axis is symmetric log with a linear interval near zero.
(d) Analytic $t_{\min}(b,\theta)$ on an extended deterministic grid, with fixed unit gains. Lines denote contours of the untransformed ratio.

## FigS5

[Individual caption](03_FIGURE_PRODUCTION/redraw/FigS5/caption.md)

**Figure S5. Finite-window mechanism and reversible-null behavior.**
(a) Exact expected detrended Hann spectra and imaginary coherency cycles for the 125-ms differential-delay example, at four window lengths. Dashed curves give the population cross-spectrum and zero imaginary cycle. Exact expectations are displayed on each window's discrete frequency grid.
(b) The magnitude of the expected 10-Hz imaginary cycle at six window lengths for delays of 25, 125 and 500 ms. The dashed line uses the analytic coefficient for the 125-ms delay.
(c) Top: the scaled cycle magnitude divided by the corresponding leading coefficient $a_2$. Bottom: $T^4Q_{\rm bias}$, divided by its numerical value at 32 s for each delay. Colors match (b). The archived 12-channel expected score is the mean squared expected imaginary cycle.
(d) Nominal one-sided sign-flip p values for four randomized reversible filter controls (240 records per regime) and the frozen first 99 records of the structured reversible model ($p=8\times10^{-5}$). The dashed line marks 0.05. Each point is one group test under its own simulation design. The 500 structured-record scores are included in the data.

## FigS6

[Individual caption](03_FIGURE_PRODUCTION/redraw/FigS6/caption.md)

**Figure S6. Confidence envelopes and their numerical validity.**
(a) Representative known-mean MA(1) spectrum, estimated from the same $N=524{,}288$ trajectory as Fig. 6a. The band gives the simultaneous radius $\epsilon$ for the imaginary cross-spectrum.
(b) Unknown-mean extension, checked by replaying 300 global-centering simulations (100 independent records per length). The largest normalized error is 0.284. The dashed line is the theoretical threshold.
(c) All 2,500 seeded Hermitian perturbations. The diagonal marks the population triangle bound. There were 1,713 positive certificates and all certificates were below their population bound, including trials with indefinite estimates. Both axes retain zero with symmetric-log scaling.
(d) Theoretical simultaneous coverage corresponds to an error-to-radius ratio at most one. Every one of the 7,680 fixed-grid analyses was within that threshold. They use 1,920 independent long trajectories, with nested lengths within each model–delay setting. The CDF pools lengths and delays descriptively. The nominal coverage level is 95%.

## FigS7

[Individual caption](03_FIGURE_PRODUCTION/redraw/FigS7/caption.md)

**Figure S7. Sample complexity at fixed and continuous frequencies.**
(a) All 12 fixed-grid cells at $b=0.35$, with counts out of 128 independent trajectories per cell.
(b) Positive-certificate fractions at $b=0.65$ and $0.90$, stratified by maximum delay. The three series have small fixed horizontal offsets for visibility. All lengths within a model–delay setting use the same trajectories. The 24 null cells are supplied as a separate table, with zero positive certificates out of 128 in each cell.
(c) All 384 continuous-rate estimates, including zeros, from 128 independent long trajectories. Black marks give median and central 95% empirical quantiles. The dashed line gives the common population triangle integral.
(d) Each thin line links three prefixes of the same trajectory within one delay group (64 per group). Points show deviations from the median for their delay and prefix length, making individual variation visible. The two delay panels use the same units with different vertical limits. Panel (c) uses a symmetric-log scale with a linear region around zero.

## FigS8

[Individual caption](03_FIGURE_PRODUCTION/redraw/FigS8/caption.md)

**Figure S8. EEG selection and observation-coordinate sensitivity.**
(a) The archived acquisition and QC funnel, counting records and distinct participants at each step. Status OK under both references precedes the restriction to complete windows.
(b) Observed complete-window membership among the 99 post-pilot participants per eye condition. A complete record has status OK and all 12 predefined windows in each half. The joint cells contain 52 eyes-open and 61 eyes-closed records.
(c) The mean within-record reference difference for each of the 71 participants, using the matched runs available to that participant. Markers distinguish 29 participants with one matched run and 42 with both.
(d) The signed contribution of alpha (8 to below 13 Hz) versus full $Q$, across all 226 record–reference combinations. The band contribution uses the full frequency–triplet denominator and equals $10/57$ times the alpha-band mean. The diagonal marks equality with full $Q$. The comparison is exploratory and eye condition follows the source recording order.
