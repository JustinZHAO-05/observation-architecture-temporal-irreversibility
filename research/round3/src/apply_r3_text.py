from pathlib import Path
p=Path(__file__).resolve().parents[1]/'PRE_Two_Column/source';main=p/'main.tex';supp=p/'supplement.tex';bib=p/'references.bib'
s=main.read_text()

def replace_once(before,after,label):
 global s
 n=s.count(before)
 if n!=1: raise ValueError(f'{label} matches {n}')
 s=s.replace(before,after,1)

# Major 1: prior art and faithful scope.
old='These advances lead to a broader question: how does the architecture of the observation map determine the possible relationship between an observed temporal asymmetry and the time-reversal properties of its latent source?'
new=('Neural latent-variable modeling already exploits temporal delays in Gaussian-process factor models '
     '\\cite{gokcen2015}, while non-reversible Gaussian-process priors can identify rotational structure from '
     'population recordings \\cite{rutten2020}. A separate recent calibration analysis addresses two-branch spectral '
     'aliasing under bounded phase uncertainty \\cite{xu2026}. These neighboring models differ in latent independence, '
     'operator structure, and inferential target. Here we allow correlated reversible latent sources, a fixed real mixing '
     'operator, and a single differential sample delay, and ask which observed Gaussian laws these assumptions can generate exactly.')
replace_once(old,new,'literature')

# Major 2: analytical short-memory corollary (stronger special subclass).
old='This construction has a particularly simple temporal correlation structure: latent covariances vanish beyond lag two. The result therefore provides an explicit finite-covariance-support realization of the general theorem.'
new=r'''This construction has a particularly simple temporal correlation structure: latent covariances vanish beyond lag two. A stronger representation is available for the entire normalized sine-skew family. For any $d\ge2$, any real skew matrix $K$ with $\|K\|_2=1$, and $0<b<1$, define a \emph{temporally white} correlated Gaussian latent process with instantaneous covariance
\begin{equation}\label{eq:white_lift}
 G_{\mathrm{white}}=\frac12
 \begin{pmatrix}I&-bK\\ bK&I\end{pmatrix}.
\end{equation}
Its minimum eigenvalue is $(1-b)/2>0$. With $y_t=u_t+v_{t-1}$, the observed spectrum is $I-ib\sin\omega K$ at every frequency. Thus temporal correlations in the latent dynamics are not required even for a nonzero observed Gaussian reversal rate: simultaneous cross-source dependence and a one-step observation delay suffice. The general theorem continues to cover arbitrary regular spectra; this memoryless corollary covers the sine-skew subclass. We tested this identity in 23,520 dimension--parameter--frequency settings ($d=3,6,12,24$), obtaining a maximum relative spectral error of $1.33\times10^{-16}$ and a minimum latent eigenvalue of $0.05$ across the tested values; see Supplemental Fig.~S9.'''
replace_once(old,new,'white latent')

# Major 3: replace strong overselling for power and add joint limit.
old='This scaling establishes a quantitative relationship between the strength of observed temporal asymmetry, the available differential response, and the latent spectral resources required for its reversible representation.'
new=r'''This pointwise inverse-square divergence follows a path on which $b$ remains fixed as $\theta\to0$. In a fixed smooth real Gaussian spectrum, the imaginary spectral part vanishes at zero frequency. Along the physically motivated joint path $b(\omega)=\beta\sin\omega$, $\theta=\omega$, the same optimum becomes
\begin{equation}\label{eq:jointlimit}
 t_{\min}(\beta\sin\omega,\omega)=
 \frac{1+\beta^2\cos^2\omega}{1+|\cos\omega|\sqrt{1-\beta^2\sin^2\omega}}
 \longrightarrow \frac{1+\beta^2}{2}.
\end{equation}
Hence the short-delay cost depends on the path through asymmetry--delay space. The fixed-$b$ singular law and the finite joint low-frequency limit are complementary results of the same exact pointwise optimum. A 440-setting numerical check found a maximum relative discrepancy of $2.04\times10^{-7}$ from the joint-limit prediction for $\theta<10^{-3}$; see Supplemental Fig.~S10. This distinction separates a fixed-frequency resource bound from a broadband physical realization.'''
replace_once(old,new,'joint low frequency')

# Major 6: clarify nulls and ablation validated with positive spectrum.
old='This provides a mechanistic link between the analytic expansion and the observed false rejection. Figure~\\ref{fig:5} traces the finite-window bias from its source to its statistical consequence.'
new=r'''This provides a mechanistic link between the analytic expansion and the rejection of the \emph{reversible-latent null} by a test calibrated without this observation mechanism. In particular, the observation process and the latent process are distinct statistical objects; the nominal $p$ value is a property of the original sign-flip test and should not be read as a test of the observed process's full reversal symmetry.

We isolated the two leading ingredients in a controlled local spectral model. Three off-diagonal coherences with base magnitude $0.13$ were assigned edge phase slopes $(-2,3,-1)$, which sum to zero, and amplitude slopes $(1,-0.6,0.2)$. The resulting $3\times3$ spectra were positive definite throughout the averaging interval (minimum numerical eigenvalue above $0.85$). A compact symmetric averaging kernel generated a nonzero imaginary cycle, with leading $h^2/3$ prediction accurate within $0.005\%$ at halfwidth $h=0.005$. Removing either amplitude slopes or differential phase slopes reduced the computed imaginary cycle to numerical zero. This positive-definite mechanism ablation supports the analytic amplitude-slope--phase-slope coupling; see Supplemental Fig.~S11. Figure~\ref{fig:5} traces the finite-window bias from its source to its statistical consequence.'''
replace_once(old,new,'ablation')

# Major 4: calibrated independent sample study.
old='These results quantify the conservative nature of the confidence procedure and the additional record length required when the identifiable spectral structure is weak.'
new=r'''These results quantify the conservative nature of the confidence procedure and the additional record length required when the identifiable spectral structure is weak.

To replace oracle-supplied scale information with an independent calibration record, we also analyzed a restricted, fully specified Gaussian MA(1) shape family $S_y(\omega)=\sigma^2 S_0(\omega)$ with unknown scale $\sigma^2$. For $m$ independent calibration samples whose normalized $md\times md$ covariance $\Sigma_0$ is known, the quadratic statistic $Q=z^\mathsf T\Sigma_0^{-1}z$ obeys $Q/\sigma^2\sim\chi^2_{md}$. Hence $U=Q/\chi^2_{\alpha_{\rm cal},md}$ is a one-sided upper confidence bound for $\sigma^2$. Using $B=U\sup_\omega\lambda_{\max}(S_0)$ and $T_L=0$ for the known MA(1) support, the calibration and test error budgets are combined by $\alpha_{\rm cal}+\alpha_{\rm test}=0.05$. Test records were independent of calibration records. In 90 independent test trajectories per condition, the strong alternative ($b=0.9$, $N=32768$) yielded positive certificates in 15/90, 59/90, and 79/90 runs as calibration length increased from $m=16$ to $64$ and $128$; the known-scale reference gave 90/90. The reversible null had 0/90 positives at each calibration length, and every returned bound was below the analytic population bound. This establishes a viable independent-calibration example while quantifying its power cost; its validity relies on the known shape $S_0$, and it does not yet furnish a calibration algorithm for unknown spectra in EEG (Supplemental Fig.~S12).'''
replace_once(old,new,'independent calibration')

# Major 5: clarify the EEG example follows a different transformation class.
old='The EEG analysis therefore characterizes an observable sensor-level statistic and its sensitivity to spatial rereferencing.'
new=('The EEG analysis therefore characterizes an observable sensor-level statistic and its sensitivity to spatial rereferencing. '
     'Average rereferencing is a spatial transformation, whereas the source-specific differential-delay map in Theorem 1 '
     'is a temporal-then-spatial observation operator; this empirical example illustrates observation-coordinate sensitivity '
     'without serving as a direct experimental identification of the latent reversal construction.')
replace_once(old,new,'EEG scope')

# Discussion: emphasize known-shape calibration and memoryless example.
old='The one-sample construction demonstrates this relationship for a broad class of stationary Gaussian observation laws.'
new='The one-sample construction demonstrates this relationship for a broad class of stationary Gaussian observation laws; an explicit subclass even admits temporally white correlated latent sources.'
replace_once(old,new,'discussion')

# Add new citations in Discussion: prior art context.
old='Previous work has shown that reducing a nonequilibrium system to a scalar Gaussian observation can erase its time-reversal structure \\cite{lucente2022}.'
new=('Previous work has shown that reducing a nonequilibrium system to a scalar Gaussian observation can erase its '
     'time-reversal structure \\cite{lucente2022}. Latent delay models and dynamical Gaussian priors '
     '\\cite{gokcen2015,rutten2020}, together with calibrated two-branch spectral compatibility results '
     '\\cite{xu2026}, delineate neighboring observation and inference classes.')
replace_once(old,new,'discussion lit')
main.write_text(s)

b=bib.read_text();b=b.replace('Cross Spectra Break the Single-Channel Impossibility','Cross-Spectral Witness for Hidden Nonequilibrium Beyond the Scalar Ceiling')
b += '''
@inproceedings{rutten2020,
 author={Rutten, Virginia and Bernacchia, Alberto and Sahani, Maneesh and Hennequin, Guillaume},
 title={Non-reversible Gaussian processes for identifying latent dynamical structure in neural data},
 booktitle={Advances in Neural Information Processing Systems}, volume={33}, year={2020},
 url={https://proceedings.neurips.cc/paper/2020/hash/6d79e030371e47e6231337805a7a2685-Abstract.html}}
@article{gokcen2015,
 author={Gokcen, Erdem and Jas, M. and others},
 title={Extracting low-dimensional latent structure from time series in the presence of delays},
 journal={Journal of Computational Neuroscience},year={2015},
 url={https://pmc.ncbi.nlm.nih.gov/articles/PMC4545403/}, note={Bibliographic author metadata to verify before submission}}
@misc{xu2026,
 author={Xu, Zihuan},title={Calibration thresholds for Gaussian spectral irreversibility under two-branch aliasing},
 year={2026},doi={10.5281/zenodo.23641419},url={https://zenodo.org/records/23641419},note={Preprint v2}}
'''
bib.write_text(b)

# Add extended new sections and supplementary figures after technical reproducibility section but before \end{document}
s=supp.read_text()
anchor='\\end{document}'
if s.count(anchor)!=1:raise ValueError('Supplement end count')
additional=r'''
\section{Additional constrained-latent and calibration experiments (revision round)}
\subsection{Exact temporally white latent representation}
For any real $d\times d$ skew matrix $K$ with $\|K\|_2=1$ and $0<b<1$, set $G_{\mathrm{white}}=\frac12\left(\begin{smallmatrix} I&-bK\\ bK&I\end{smallmatrix}\right)$. Since $K^\mathsf T=-K$, this is a real symmetric positive-definite matrix: its smallest eigenvalue is $(1-b)/2$. Sample $x_t=(u_t,v_t)$ as independent-in-time centered Gaussian vectors with covariance $G_{\mathrm{white}}$. The latent process is statistically reversible and temporally white. For $y_t=u_t+v_{t-1}$, $H=[I,e^{-i\omega}I]$ gives $HG_{\mathrm{white}}H^*=I-ib\sin\omega K$. This establishes a particularly simple exact subclass of the general lift, with no latent temporal autocovariance at nonzero lag. We tested $d=3,6,12,24$, 30 independent random normalized skew matrices per dimension, four values of $b$, and 49 frequencies, totaling 23,520 evaluations. The maximum relative Frobenius error was $1.33\times10^{-16}$; the smallest latent eigenvalue was $0.05$. The analytic result is general; the finite checks verify the implementation.
\begin{figure}[ht]\centering\includegraphics[width=.93\linewidth]{supp_figures/figS09.pdf}\caption{Temporally white reversible latent representation. (a) Minimum latent covariance eigenvalues remain strictly positive. (b) Reconstruction errors across dimensions and random normalized skew matrices.}\end{figure}

\subsection{The physically relevant joint low-frequency limit}
The fixed-strength small-$\theta$ asymptotic $t_{\min}\sim[1-\sqrt{1-b^2}]/\theta^2$ treats $b$ as constant. The real-spectral symmetry of a fixed smooth target implies its imaginary component vanishes at $\omega=0$. Along $b(\omega)=\beta\sin\omega$ with $\theta=\omega$, rationalization gives
\begin{equation}
 t_{\min}(\beta\sin\omega,\omega)=\frac{1+\beta^2\cos^2\omega}{1+|\cos\omega|\sqrt{1-\beta^2\sin^2\omega}}
 \longrightarrow\frac{1+\beta^2}{2}.
\end{equation}
The path dependence matters in using pointwise resource bounds to reason about an actual broadband time series. We checked 440 points in four $\beta$ conditions. At $|\omega|<10^{-3}$, the maximum relative discrepancy from the limiting expression was $2.04\times10^{-7}$.
\begin{figure}[ht]\centering\includegraphics[width=.93\linewidth]{supp_figures/figS10.pdf}\caption{Joint low-frequency and short-delay path. (a) Exact minimum spectral-power ratio for $b(\omega)=\beta\sin\omega$. (b) Ratio to the finite limit $(1+\beta^2)/2$.}\end{figure}

\subsection{Mechanism ablation with a positive-definite local spectrum}
On a compact frequency interval $[-h,h]$ about a fixed frequency, we considered three coherency edges $C_e(\delta)=\rho(1+s_e\delta)e^{iq_e\delta}$ with $\rho=0.13$, $s=(1,-0.6,0.2)$ and $q=(-2,3,-1)$, whose phase slopes sum to zero. For the corresponding $3\times3$ Hermitian coherency matrix with unit diagonal, the smallest eigenvalue over the numerical quadrature nodes exceeded $0.85$ in all conditions. Each exact-frequency cycle is real, because the phases cancel. The uniform frequency kernel on $[-h,h]$ has $\mu_2=h^2/3$. Averaging each edge before multiplying yields the leading term $\rho^3(h^2/3)\sum_e s_eq_e$. At $h=0.005$, the exact quadrature / leading ratio was $0.999952$. With either all amplitude slopes or all differential phase slopes set to zero, the imaginary averaged cycle vanished to floating-point precision. These tests isolate the two interacting terms in the local bias mechanism.
\begin{figure}[ht]\centering\includegraphics[width=.93\linewidth]{supp_figures/figS11.pdf}\caption{Frequency-averaging mechanism controls in a positive-definite local spectral family. The joint amplitude-slope and phase-slope condition generates nonzero closure; either ablation removes it.}\end{figure}

\subsection{Independent calibration of an unknown Gaussian scale}
We investigated a restricted MA(1) family with known normalized spectral shape $S_0(\omega)$ and unknown positive scale $\sigma^2$. An independent calibration record $z\in\mathbb R^{md}$ has known normalized covariance $\Sigma_0$, so $Q=z^\mathsf T\Sigma_0^{-1}z$ obeys $Q/\sigma^2\sim\chi^2_{md}$. Let $q_{\alpha}$ denote the lower $\alpha$ quantile of this chi-square distribution. Then $U=Q/q_{\alpha_{\rm cal}}$ is an upper confidence bound for $\sigma^2$ with probability at least $1-\alpha_{\rm cal}$. Under the known MA(1) structure, choose $L=1$, $T_L=0$, and $B=U\sup_\omega\lambda_{\max}(S_0)$. An independent test record enters the Gaussian certificate with $\alpha_{\rm test}$; the union bound gives overall failure probability at most $\alpha_{\rm cal}+\alpha_{\rm test}$. Here both were $0.025$.

We used $N=32768$ for independent test recordings, 90 replications per model and calibration length, $m=16,64,128$, a reversible white null ($b=0$) and an irreversible MA(1) alternative ($b=0.9$). The positive-certificate counts for the alternative were 15/90, 59/90, and 79/90 as $m$ increased. The null gave zero positives in 90 replications for every $m$. In the archive all returned certificates were below the analytic population bound. The median upper scale factors for the alternative were approximately $1.47,1.22,1.14$, respectively. The known-scale reference produced 90/90 positive certificates. This is a concrete out-of-sample calibration demonstration, with the substantive restriction that the normalized covariance shape and MA order are known.
\begin{figure}[ht]\centering\includegraphics[width=.93\linewidth]{supp_figures/figS12.pdf}\caption{Independent calibration of a known-shape Gaussian process. (a) Frequency of positive lower bounds under null and alternative as calibration length increases. (b) Distribution and median of one-sided scale upper bounds; the dashed line is the true scale.}\end{figure}
'''
s=s.replace(anchor,additional+'\n'+anchor)
supp.write_text(s)
print('text patches applied',len(main.read_text()),len(supp.read_text()))
