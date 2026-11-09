from pathlib import Path
import json
r=Path(__file__).resolve().parents[1];src=r/'manuscript/source';log=[]
def sub(f,old,new,why):
 p=src/f;s=p.read_text();n=s.count(old)
 if n==1: p.write_text(s.replace(old,new))
 elif n==0 and new in s: print('ALREADY:',f,old[:55])
 else:
  print('MISSED:',f,old[:90]);return
 log.append(dict(file=f,reason=why,before=old,after=new))
sub('supplement.tex',
 '\\begin{figure}[ht]\\centering\\includegraphics[width=.93\\linewidth]{supp_figures/figS09.pdf}\\caption{Temporally white reversible latent representation. (a) Minimum latent covariance eigenvalues remain strictly positive. (b) Reconstruction errors across dimensions and random normalized skew matrices.}\\end{figure}',
 '\\begin{figure}[ht]\\centering\\includegraphics[width=.93\\linewidth]{supp_figures/figS09.pdf}\\caption{Temporally white reversible latent representation. (a) Smallest latent covariance eigenvalue versus asymmetry strength $b$; the analytical value is $(1-b)/2$. (b) Maximum relative spectral-reconstruction error by observed dimension. The test uses 120 random normalized skew matrices, four values of $b$, and 49 frequencies, giving 23,520 matrix--parameter--frequency evaluations.}\\end{figure}',
 'Figure S9 explanatory sample counts moved into self-contained caption.')
sub('supplement.tex',
 '\\begin{figure}[ht]\\centering\\includegraphics[width=.93\\linewidth]{supp_figures/figS10.pdf}\\caption{Joint low-frequency and short-delay path. (a) Exact minimum spectral-power ratio for $b(\\omega)=\\beta\\sin\\omega$. (b) Ratio to the finite limit $(1+\\beta^2)/2$.}\\end{figure}',
 '\\begin{figure}[ht]\\centering\\includegraphics[width=.93\\linewidth]{supp_figures/figS10.pdf}\\caption{Joint low-frequency and short-delay limit. (a) Exact pointwise minimum trace ratio for $b(\\omega)=\\beta\\sin\\omega$ and $\\theta=\\omega$; unlike the fixed-$b$ path, this smooth spectral family has a finite limit as $\\omega\\to0$. (b) The ratio to $(1+\\beta^2)/2$ approaches unity, confirming the analytic joint limit.}\\end{figure}',
 'Figure S10 title information transferred to caption.')
sub('supplement.tex',
 '\\begin{figure}[ht]\\centering\\includegraphics[width=.93\\linewidth]{supp_figures/figS11.pdf}\\caption{Frequency-averaging mechanism controls in a positive-definite local spectral family. The joint amplitude-slope and phase-slope condition generates nonzero closure; either ablation removes it.}\\end{figure}',
 '\\begin{figure}[ht]\\centering\\includegraphics[width=.93\\linewidth]{supp_figures/figS11.pdf}\\caption{Spectral-averaging mechanism in a positive-definite local model. (a) The combined amplitude and phase slopes generate a nonzero averaged imaginary cycle; setting either slope family to zero eliminates the leading effect. The dashed curve is the analytic $O(h^2)$ contribution. (b) The ratio of exact numerical quadrature to the leading term approaches unity as kernel halfwidth $h$ decreases.}\\end{figure}',
 'Clarify S11 panel purpose after removing headings.')
sub('supplement.tex',
 '\\begin{figure}[ht]\\centering\\includegraphics[width=.93\\linewidth]{supp_figures/figS12.pdf}\\caption{Independent calibration of a known-shape Gaussian process. (a) Frequency of positive lower bounds under null and alternative as calibration length increases. (b) Distribution and median of one-sided scale upper bounds; the dashed line is the true scale.}\\end{figure}',
 '\\begin{figure}[ht]\\centering\\includegraphics[width=.93\\linewidth]{supp_figures/figS12.pdf}\\caption{Independent scale calibration within a known-shape MA(1) family. (a) Frequency of positive lower-bound certificates for a reversible null ($b=0$) and an asymmetric alternative ($b=0.9$) across independent calibration lengths $m=16,64,128$; 90 independent pairs contribute to each condition. (b) One-sided upper scale bounds, showing individual runs and medians; the dashed line gives the true scale. Test length $N=32,768$ is fixed.}\\end{figure}',
 'Put all figure-specific conditions and sample sizes in S12 caption.')
sub('supplement.tex',
 '\\section{Additional constrained-latent and calibration experiments (revision round)}',
 '\\section{Constrained latent representations and independent calibration}',
 'Remove internal revision process language from scientific supplement.')
sub('supplement.tex',
 'These checks use different computational representations of the observation identity.',
 'The coefficient-domain and block-covariance checks confirm the same observation identity through independent numerical representations.',
 'Use evidence-first computational validation sentence.')
sub('r4_supplement.tex',
 '\\section{Independent computational checks and reproducibility of this revision}',
 '\\section{Independent numerical validation and reproducibility}',
 'Replace revision diary heading with scholarly method heading.')
sub('r4_supplement.tex',
 'The archived figures from the preceding analyses are retained. New figures show the additional experiments, including the white-latent study with 23,520 frequency--matrix evaluations from a structured set of generated matrices. All quantitative captions name the sampling unit. Main-text mathematical notation now consistently distinguishes entrywise conjugation, transpose, and adjoint. A manifest and a clean-build script accompany this revision. Source paths in the earlier sections are relative to the preserved original archive under \\texttt{inputs}; the current revision\'s new source data are under \\texttt{results}.',
 'All numerical results are accompanied by fixed seeds, per-repetition source tables, and a SHA-256 manifest. The plots separate independent random matrices, repeated frequency evaluations, independently calibrated records, and nested trajectory lengths. Source data for the initial analyses are archived under \\texttt{inputs}; the additional experiment records are under \\texttt{results}.',
 'Move engineering change-log material out of the scientific supplement while retaining data provenance.')
sub('r4_supplement.tex',
 'Its purpose is to check known observation-level identities on an actual estimated spectrum. The post-window diagonal transformation is deliberately distinguished from causal time-domain filtering before spectral estimation, for which the finite-bandwidth mechanism applies.',
 'The transformed empirical spectra verify the known observation-level identities. Post-window spectral transformations and causal time-domain filtering are distinct operations; the latter is governed by the finite-bandwidth analysis.',
 'Make experimental result and operator distinction explicit.')
sub('r4_supplement.tex',
 'The power conclusion and the coverage conclusion are therefore reported separately.',
 'The experiment separates two outcomes: spectral-envelope validity and the power of the resulting certificate.',
 'State competing scientific metrics in positive form.')
# update S15 caption with moved counts and notations
sub('r4_supplement.tex',
 'Calibration validity and sensitivity. (a) Numerical coverage under the valid finite-support and AR--MA model classes, and under incorrect versus valid tail assumptions in 80 paired stress trials. Abstaining calibrations are excluded from the finite-bound validation.',
 'Calibration validity and sensitivity. (a) Coverage under finite-support and AR--MA classes, and an 80-pair stress test contrasting misspecified lag-1 support (0/80 covered) with a valid tail envelope (80/80 covered); abstention cases are excluded from finite-bound coverage calculations.',
 'Move 0/80 and 80/80 count labels to S15 caption.')
# r4 supplement S16 caption remove redundant defense
sub('r4_supplement.tex',
 'All transformations use the same estimated spectrum, with no additional biological sample or model of latent brain reversibility.',
 'All transformations act on one estimated EEG spectrum; the biological sample is a single recording.',
 'Succinct biological sampling provenance.')
(r/'docs/EDIT_LOG_R5_POLISH.json').write_text(json.dumps(log,indent=2,ensure_ascii=False))
print('Applied',len(log),'more editorial refinements')
