from pathlib import Path
import re
p=Path(__file__).resolve().parents[1]/'manuscript/source'
m=(p/'main.tex').read_text()
start=m.index(r'\subsection{Construction of the reversible latent spectrum}')
end=m.index(r'\subsection{Mechanism and interpretation}',start)
core=r'''\subsection{Construction of the reversible latent spectrum}
Write $S=R+iY$, with $R$ real symmetric positive definite and $Y$ real skew symmetric. Set $s=\sin\omega$, $c=\cos\omega$, $A=R^{-1/2}(Y/s)R^{-1/2}$, $a=\|A\|_2$, and $\beta=|s|a<1$. Define
\[
 \eta=(1-\beta^2)/2,\quad k=(a^2+\eta)/2,\quad V=kR,\quad J=Y/(2s),
\]
\[
 Q=-cV+J,\qquad P=R+(2c^2-1)V.
\]
The candidate latent spectrum is
\begin{equation}\label{eq:7}
 G(\omega)=\begin{pmatrix}P&Q\\Q^{\mathsf T}&V\end{pmatrix}.
\end{equation}
For $H=[I,e^{-i\omega}I]$, direct multiplication gives
\begin{equation}\label{eq:8}
 HGH^*=P+V+c(Q+Q^{\mathsf T})+is(Q-Q^{\mathsf T})=S.
\end{equation}
The required positivity follows from the Schur complement
\begin{equation}\label{eq:9}
 P-QV^{-1}Q^{\mathsf T}=R-s^2V+JV^{-1}J.
\end{equation}
After whitening by $R$, its minimum eigenvalue exceeds $(1-\beta^2)/4>0$, since $a^2/(4k)<1/2$ and $s^2k\le(1+\beta^2)/4$. Thus $G>0$. Real-process symmetry makes $R$ even and $Y$ odd. At $0$ and $\pi$, differentiability provides finite limits of $Y/\sin\omega$, so all blocks extend continuously to a real even positive-definite spectrum. It defines a reversible stationary Gaussian process, and Eq.~\eqref{eq:8} supplies equality of the complete observed Gaussian laws. Appendix~\ref{app:lift} gives the full positivity and endpoint argument.

'''
m=m[:start]+core+m[end:]
# Concise body reporting; all estimates and confidence intervals retained.
start=m.index(r'\subsection{Rereferencing changes the magnitude of spectral-cycle structure}')
end=m.index(r'\subsection{Condition contrasts across reference schemes}',start)
m=m[:start]+r'''\subsection{Rereferencing changes the magnitude of spectral-cycle structure}
Under the original reference, mean $Q$ was $7.4189\times10^{-5}$ for eyes open and $1.9855\times10^{-4}$ for eyes closed. Under 64-channel average reference these means were $3.8283\times10^{-4}$ and $5.2276\times10^{-4}$, respectively: ratios of group means of 5.16 and 2.63. With 20,000 participant-level bootstrap resamples, the paired mean increases were $3.0864\times10^{-4}$ (95\% interval $[2.5625,3.6244]\times10^{-4}$) and $3.2421\times10^{-4}$ ($[2.5814,3.9207]\times10^{-4}$). Thus rereferencing changes the observable substantially even with participants and windows fixed.

'''+m[end:]
start=m.index(r'\subsection{Condition contrasts across reference schemes}')
# preserve subsequent inserted metric-decomposition/figure/table by limit to explicit first newsubsection or figure
end=m.index(r'\subsection{Known transformations of an archived EEG spectrum}',start)
chunk=m[start:end]
# preserve figures/tables and any decomposition paragraph from current original chunk.
blocks=re.findall(r'\\begin\{(?:figure\*?|table\*?)\}.*?\\end\{(?:figure\*?|table\*?)\}',chunk,flags=re.S)
# Preserve any added q=amplitude*alignment material if present.
metric=''
if 'amplitude' in chunk.lower():
 for para in chunk.split('\n\n'):
  if 'amplitude' in para.lower() or 'alignment' in para.lower():metric+=para+'\n\n'
new=r'''\subsection{Condition contrasts across reference schemes}
For the 42 participants with both conditions, the mean eyes-closed minus eyes-open difference was $1.3288\times10^{-4}$ under the original reference (95\% bootstrap interval $[0.7981,1.8597]\times10^{-4}$) and $1.2634\times10^{-4}$ under average reference ($[0.8114,1.7345]\times10^{-4}$). The positive direction of this group contrast persists under both references, although the baseline contrast is associated with the dataset's fixed condition/run ordering. Absolute score sensitivity and persistence of a particular contrast are distinct empirical observations.

'''+metric+'\n\n'.join(blocks)+'\n\n'
m=m[:start]+new+m[end:]
m=m.replace('The Supplemental Material records the compared model classes and the literature-reading coverage.','The Supplemental Material tabulates the compared observation models and inferential targets.')
(p/'main.tex').write_text(m)
s=(p/'supplement.tex').read_text()
# Remove proof duplication, keep definitions specific to supplementary algorithms.
start=s.index(r'\subsection{Reversibility and cycle obstruction}')
end=s.index(r'\subsubsection{Numerical intervals using established phase synchronization}',start)
s=s[:start]+r'''\subsection{Population results used by the numerical study}
The main text and Appendix A give the real-gauge characterization, the reversal-specific triangle bound, and its weak-coherence sharpness proof. These results use real cycle products, including negative products of phase $\pi$. For a complete support graph triangles suffice; sparse graphs can require longer cycles. Figure~\ref{fig:s1} illustrates the geometry and retained sharpness checks. The numerical procedure below estimates the same phase-relaxed functional and preserves its unresolved optimization gaps.

'''+s[end:]
start=s.index(r'\subsection{Constructive proof and regularity}')
end=s.index(r'\subsection{Scope and mechanisms}',start)
s=s[:start]+r'''\subsection{Construction and regularity}
The complete construction and its positivity and endpoint proofs appear in main-text Appendix B. Here we retain its numerical instances, model-scope checks, and coordinate transformations. The extension to finite-order latent models appears in the new main-text Appendix F.

'''+s[end:]
start=s.index(r'\subsection{Proof}',s.index(r'\section{Fixed-gain trace-budget'))
end=s.index(r'\begin{figure}',start)
# retain numerical validation sentence from R3 if it appears in removedproof; regenerate relevant verified data.
s=s[:start]+r'''\subsection{Optimization verification}
The exact rotational-symmetrization proof is in main-text Appendix C. The numerical study uses the original full-matrix constraints rather than the scalar formula. Thirty-two parameter settings give a maximum relative primal--dual bracket width of $2.31\times10^{-6}$ and maximum equality residual of $6.00\times10^{-15}$. Early SLSQP attempts with unreliable convergence remain archived and are excluded from correctness claims. The joint low-frequency and full-band extensions are reported below.

'''+s[end:]
start=s.index(r'\subsection{Why exact cancellation can fail after estimation}')
end=s.index(r'\subsection{Computational validation and adversarial tests}',start)
s=s[:start]+r'''\subsection{Population-window relation and uncertainty}
Main-text Appendix D supplies the local amplitude-slope/group-delay expansion, explicit fourth-order remainder, and continuous Hann-window moments. Its coefficient concerns separately averaged raw cross spectra; coherency normalization divides by positive smoothed diagonal powers. The archived exact discrete implementation incorporates linear detrending and the actual sampling grid. The following tests examine algebraic invariance, finite-replica sampling, and the structured filtered-latent counterexample as separate questions.

'''+s[end:]
start=s.index(r'\section{Finite-record simultaneous Gaussian confidence radius}')
end=s.index(r'\begin{figure}',start)
s=s[:start]+r'''\section{Finite-record simultaneous Gaussian confidence radius}
The main text defines the lag estimator, finite-grid confidence radius, raw-cycle perturbation bound, and sufficient signal-strength condition. Main-text Appendix E gives the Gaussian quadratic-form proof, including dependence between overlapping lags and adjacent observations, the $d^2F$ real-component union bound, and the unknown-constant-mean allowance. The computed bound refers to fixed choices of record length, lag cutoff, and frequency grid. The diagnostic figure below records the independent implementation and perturbation checks; all parameter-level outputs are supplied in the archive.

'''+s[end:]
start=s.index(r'\section{Continuous-frequency lower sum and power simulations}')
end=s.index(r'\subsection{Numerical experiments and complete outcomes}',start)
s=s[:start]+r'''\section{Continuous-frequency lower sum and power simulations}
The main-text rate construction uses a simultaneous all-frequency error event and an explicit within-cell derivative allowance. Appendix E gives the proof. The following subsections report the fixed-grid and continuous-frequency sampling designs, including nested prefixes, zero-power settings, and implementation checks. These numerical outcomes are separate from the analytic probability guarantee.

'''+s[end:]
# Replace garbled source-conversion arithmetic with mathematical notation.
s=s.replace('For any unit-modulus candidate v, define $d_{i}$ = Re{[}conjugate($v_{i}$)(Av)\\_i{]}. Shift d downward until A minus diag(d) is positive semidefinite.',r'For a unit-modulus candidate $v$, define $d_i=\operatorname{Re}[\overline{v_i}(Av)_i]$. Shift $d$ downward until $A-\operatorname{diag}(d)$ is positive semidefinite.')
(p/'supplement.tex').write_text(s)
p2=p/'r4_supplement.tex';t=p2.read_text();start=t.index('The comparison identifies the mathematical problem');end=t.index(r'\section{Finite-order reversible latent models}',start)
t=t[:start]+'''The comparison specifies operator constraints, latent classes, and inferential targets. Classical factorization, delayed latent-variable fitting, and the fixed-operator representation theorem answer distinct mathematical questions. The source-audit document accompanying the code records retrieval and reading coverage; the mathematical contributions are formulated by their explicit assumptions rather than an unrestricted priority claim.

'''+t[end:];p2.write_text(t)
# Move original operation counts to correct wording.
