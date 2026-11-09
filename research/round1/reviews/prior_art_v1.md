# Independent prior-art audit: spectral cycle identifiability

**Reviewer:** theory_scout, independent of the mathematical and experimental reviewers.  
**Frozen:** 2026-11-06.  
**Materials reviewed:** `theory_v1.md`, `scouts/root_closure_proposal.md`, `protocols/protocol_v1.md`, and the root's subsequent descriptions of the finite-bandwidth expansion and phase-optimization certificate. I did not inspect the other reviews or experimental results. A brief follow-up on the newest finite-record no-go construction is pending and will be recorded separately.

## 1. Decisive assessment

The project has a potentially useful **observation-identifiability and neural time-series methodology** contribution. Several of its most visually attractive mathematical components are established, with unusually close primary precedents. The strongest remaining candidate contribution is the specific construction and interpretation of a **local-phase-relaxed Gaussian reversal divergence**, its explicit triangle lower bound, and a careful connection between population identifiability and what finite recordings actually permit. The exact finite-record representation/no-go construction proposed after this audit began could strengthen this latter contribution substantially; its prior-art check is still incomplete.

The following claims should be treated as existing foundations:

1. Multiplicative channel phases cancel in cycle products: classical closure phase.
2. All cycle products real characterize a Hermitian matrix that can be made real by diagonal phases: a direct corollary of established Gram-matrix/Bargmann-invariant characterizations, with the same spanning-tree proof, complete-graph triangle simplification, and sparse-graph longer-cycle issue.
3. The unminimized Gaussian spectral reversal density is the entropy-production-factor construction of Seara, Machta, and Murrell.
4. Quadratic optimization over unit-modulus phases, SDP relaxation, the diagonal dual certificate, and its smallest-eigenvalue gap bound all have direct precedents.
5. Averaging over frequency can create closure phase from channel-dependent bandpasses. This phenomenon, including analytic expressions and bandwidth checks, is already explicit in interferometry.

The literature inspected did **not yield an exact match** for the proposed reversal-specific quotient objective, the stated triangle bound, or the precise localized leakage coefficient. This is a scoped search outcome rather than a priority proof. The new finite-record no-go claim requires its own addendum.

## 2. Claim-by-claim comparison

| Proposed element | Closest located primary precedent | Assessment and precise remaining scope |
|---|---|---|
| Cycle products invariant to diagonal complex channel gains | Classical interferometric closure phase; Brinkerink et al. 2016 discusses its failure after band averaging | Existing invariant. Its observation model interpretation for neural spectra can be useful, but cancellation itself is not a new theorem. |
| Real diagonal gauge iff all cycle products are real | Chien & Waldron 2016, Theorem 3.2 and Corollary 4.1; Oszmaniec et al. 2024, Gram reconstruction and imaginarity | Established mathematical characterization specialized to a spectral matrix. Present as an adapted proposition with attribution. |
| Triangles suffice in dense support; longer cycles required in sparse support | Chien & Waldron's projective-frame equivalence and cycle-basis treatment | Already covered structurally. Sparse support is a useful practical implication, not independent novelty. |
| Gaussian spectral reversal density \(\mathcal E(S)=\tfrac12[\mathrm{tr}((S^T)^{-1}S)-n]\) | Seara et al. 2021, Eq. (3) | Existing objective. |
| \(\mathcal E_*(S)=\min_U\mathcal E(USU^*)\) over diagonal unitary \(U\) | No exact match located. Nearby work: phase linking via Gaussian KL and filter-invariant coherence information | Candidate novelty is the **reversal reference**, unrestricted local-phase relaxation, and the resulting conservative interpretation under a specified observation class. |
| Filter-invariant cross-spectral information | Bi & Calhoun 2026 v3, Eq. (5), (8), (9) | Very close motivation but different null. Their KL compares a joint spectrum to independent marginal spectra and can be positive for reversible correlated data. Their two-channel quantity survives; the proposed reversal quotient is zero for every positive-definite two-channel spectrum. |
| Analytic triangle lower bound \(2(\operatorname{Im}abc)^2/[\lambda_{\max}(C)^2(|ab|^2+|bc|^2+|ca|^2)]\) | Bargmann imaginarity witnesses; no identical bound located | A plausible new bound for this particular target. Scientific value depends on tightness/usefulness and rigorous estimator connection; a short inequality alone is a limited contribution. |
| Unit-modulus quadratic formulation | Singer 2011; covariance-fitting/phase-linking work including Grosso et al. 2025 | Mature optimization structure. Deriving the particular matrix \(A=(C^T)^{-1}\odot C^T\) for this reversal problem can be presented as an application/reduction. |
| \(d_i=\Re[(Av)_i\bar v_i]\), PSD certificate, and eigenvalue-shift gap bound | Boumal 2016, Eq. (5), Lemma 2, Eq. (6), with his maximization matrix set to \(-A\) | **Exact existing certificate and gap bound.** Attribute explicitly; do not claim a new certification method. |
| Nonreal closure created by finite frequency averaging | Brinkerink et al. 2016, Section 3 Eq. (1); Lachaume & Berger 2013; related SAR averaging literature | General mechanism is established. |
| Local \(\mu_2\sum_e r_jr_k r'_e d'_e\) leakage coefficient, phase-curvature cancellation, Hann constants/scaling | Adjacent analytic bandwidth-smearing work; no exact identical expression located in inspected portions | Potential specialized derivation. Formula-level priority remains uncertain because the closest 19-page analytic smearing paper was only partially read. Treat as a derived consequence tailored to the estimator, not discovery of the generic phenomenon. |

## 3. Most important primary sources and actual read coverage

### 3.1 Chien and Waldron: cycle products and real gauge

**Tuan-Yow Chien and Shayne Waldron (2016).** “A Characterization of Projective Unitary Equivalence of Finite Frames and Applications.” *SIAM Journal on Discrete Mathematics* **30**, 976–994. DOI: [10.1137/15M1042140](https://doi.org/10.1137/15M1042140). Author preprint: [arXiv:1312.5393](https://arxiv.org/pdf/1312.5393).

**Coverage:** primary PDF; abstract/introduction; Theorem 3.2 and its reconstruction proof; Corollary 4.1 and surrounding discussion; sparse-cycle Example 2.5. The PDF is 20 pages; this was a targeted proof-level read, not a claim to have read every application.

**Comparison:** any positive-definite spectral matrix is a Gram matrix. Their characterization by cyclic products, including reconstruction using a spanning tree, directly supplies the underlying equivalence relation. The real-gauge criterion is a corollary obtained by comparing a Gram matrix with its conjugate or constructing real edge representatives when all cycle phases are 0 or π. Root should attribute this mathematical foundation even if restating and proving the specialization for readers.

### 3.2 Oszmaniec, Brod, and Galvão: imaginary cyclic invariants

**Michał Oszmaniec, Daniel J. Brod, and Ernesto F. Galvão (2024).** “Measuring relational information between quantum states, and applications.” *New Journal of Physics* **26**, 013053. [Author preprint arXiv:2109.10006](https://arxiv.org/pdf/2109.10006).

**Coverage:** primary PDF introduction; the Gram reconstruction/tree-gauge argument; imaginarity section explaining that a nonreal Bargmann invariant obstructs a representation of all states by real amplitudes. Targeted sections of the 12-page PDF.

**Comparison:** the same cyclic scalar is already an invariant witness of a real-representation obstruction. The physical problem is quantum-state relational information, not stationary neural spectra, filter ambiguity, or Gaussian reversal density. This distinction supports application-level originality while removing a claim of a newly discovered imaginary-cycle obstruction.

Related primary reference: **R. R. Fernandes, R. Wagner, L. Novo, and E. F. Galvão (2024)**, “Unitary-Invariant Witnesses of Quantum Imaginarity,” *Physical Review Letters* **133**, 190201; [DOI 10.1103/PhysRevLett.133.190201](https://doi.org/10.1103/PhysRevLett.133.190201); [arXiv:2403.15066](https://arxiv.org/pdf/2403.15066). Coverage: abstract/introduction and main witness discussion, with selected references; no exhaustive appendix audit.

### 3.3 Seara, Machta, and Murrell: Gaussian spectral reversal

**Daniel S. Seara, Benjamin B. Machta, and Michael P. Murrell (2021).** “Irreversibility in dynamical phases and transitions.” *Nature Communications* **12**, 392. [DOI 10.1038/s41467-020-20281-2](https://doi.org/10.1038/s41467-020-20281-2). [Open primary full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC7810704/).

**Coverage:** abstract/introduction; spectral entropy-production-factor derivation, especially Eq. (1)–(4); discussion; methods Eq. (12)–(13) on cross-spectral estimation/smoothing. Full-text keyword search for filtering and related terms.

**Comparison:** Eq. (3) is the unminimized spectral Gaussian reversal density used here. Their physical explanation already connects complex relative phases to time-reversal asymmetry. I found no minimization over independent channel phases in the inspected paper. The new proposal should start from this known objective and state exactly which observational equivalence class is being removed.

### 3.4 Bi and Calhoun: a very recent filter-free cross-spectral witness

**Yuda Bi and Vince D. Calhoun (2026).** “Cross-Spectral Witness for Hidden Nonequilibrium Beyond the Scalar Ceiling.” [arXiv:2604.03775, latest version v3](https://arxiv.org/abs/2604.03775); [primary HTML](https://arxiv.org/html/2604.03775); [PDF](https://arxiv.org/pdf/2604.03775). The latest title differs from v1.

**Coverage:** v1 abstract/introduction and main derivation; latest v3 introduction, Sections II–III including Eq. (5), (8), (9), selected appendix theorem/scope passages, and full-text searches for phase, filter, diagonal, and irreversibility. Not an exhaustive verification of all thermodynamic derivations.

**Comparison:** v3 explicitly allows arbitrary diagonal causal stable channel filters in its separable model and cancels them through squared coherence. Its information reference is the product of scalar marginals. It measures retained cross-channel dependence; the thermodynamic bridge invokes an additional one-way coupling model. The proposed \(\mathcal E_*\) instead compares an observation orbit with its time reversal and vanishes on all reversible correlated spectra. This is a substantive distinction, though both papers frame cross-spectral invariants as overcoming scalar observational ambiguity. Cite the latest version and explain the two null models directly.

### 3.5 Grosso and colleagues: phase linking with KL covariance fitting

**Elena Grosso, Florent Bouchard, Frédéric Brigui, Guillaume Ginolhac, and Arnaud Breloy (2025).** “Interferometric Phase Linking with Riemannian Distances on Covariance Matrices.” *EUSIPCO 2025*. [Primary conference PDF](https://eusipco2025.org/wp-content/uploads/pdfs/0002602.pdf).

**Coverage:** the complete main text of the five-page PDF through its conclusions, particularly Eq. (3), (5), (6), (10), (11); selected bibliography.

**Comparison:** their model is \(\Sigma=\Psi\odot ww^*\), with real nonnegative \(\Psi\); they project observed complex covariance onto closure-consistent phase structure using matrix distances. Gaussian KL reduces to the phase quadratic \(w^*(\Psi^{-1}\odot S)w\). Thus covariance KL, phase torus optimization, and a closure constraint already occur together. Their reference covariance differs from the proposed conjugate/time-reversed spectrum, and their model uses zero cycle phase whereas real-gauge reversibility also allows π cycles.

Related framework: **Phan Viet Hoa Vu, Arnaud Breloy, Frédéric Brigui, Yajing Yan, and Guillaume Ginolhac**, “Covariance Fitting Interferometric Phase Linking: Modular Framework and Optimization Algorithms,” [arXiv:2403.08646](https://arxiv.org/abs/2403.08646), subsequently listed as a 2025 IEEE TGRS paper. [Author publication page](https://reped-sarix.univ-smb.fr/publication/journal-article6/). **Coverage limitation:** abstract and author metadata only; the large PDF failed retrieval. The detailed comparison above rests on Grosso et al.'s accessible primary paper.

### 3.6 Singer and Boumal: exact optimization precedent

**Amit Singer (2011).** “Angular Synchronization by Eigenvectors and Semidefinite Programming.” *Applied and Computational Harmonic Analysis* **30**, 20–36. [DOI 10.1016/j.acha.2010.02.001](https://doi.org/10.1016/j.acha.2010.02.001). [Author PDF](https://web.math.princeton.edu/~amits/publications/angular_synchronization.pdf).

**Coverage:** abstract/introduction, graph/tree discussion, and Eq. (8)–(10) giving the complex unit-diagonal SDP. This establishes the standard optimization setting.

**Nicolas Boumal (2016).** “Nonconvex Phase Synchronization.” *SIAM Journal on Optimization* **26**, 2355–2377. [DOI 10.1137/16M105808X](https://doi.org/10.1137/16M105808X). [Primary preprint arXiv:1601.06114v3](https://arxiv.org/pdf/1601.06114).

**Coverage:** abstract/introduction through Lemma 2 and its proof, Eq. (5)–(6), and the discussion of SDP duality. Lemma 2 directly yields the parent's certificate: put Boumal's maximization matrix equal to \(-A\). His slack becomes \(A-\mathrm{diag}(d)\), and his gap bound becomes the parent's eigenvalue-shift lower bound. The certificate, including the quantified gap, is therefore prior art, not merely analogous to prior art.

### 3.7 Brinkerink and colleagues: frequency mixing creates closure

**Christiaan D. Brinkerink et al. (2016).** “Asymmetric Structure in Sgr A* at 3 mm from Closure Phase Measurements with VLBA, GBT and LMT.” *Monthly Notices of the Royal Astronomical Society* **462**, 1382–1392. [DOI 10.1093/mnras/stw1743](https://doi.org/10.1093/mnras/stw1743). [Primary publisher full text](https://academic.oup.com/mnras/article/462/2/1382/2589703); [arXiv:1608.06515](https://arxiv.org/abs/1608.06515).

**Coverage:** primary publisher abstract/introduction and data-reduction material; Section 3's bandpass paragraph and Eq. (1) were read through the publisher's indexed primary-text result. Repeated full-text opens redirected/failed, so this was not a complete paper read.

**Comparison:** Section 3 explicitly states that frequency-varying channel bandpass phases can create nonzero measured closure even for an intrinsically point-like source. Its expression sums the arguments of the three band-integrated products \(g_i g_j^*\). It also checks separate subbands. This directly precludes novelty claims for either the generic frequency-mixing contamination mechanism or the generic idea of bandwidth sensitivity checks. The root's localized derivative coefficient and Hann scaling may still be useful specialized results.

### 3.8 Analytic bandwidth-smearing and SAR neighbors

**Régis Lachaume and Jean-Philippe Berger (2013).** “Bandwidth Smearing in Infrared Long-Baseline Interferometry. Application to Stellar Companion Search in Fringe-Scanning Mode.” *MNRAS* **435**, 2501–2519. [DOI 10.1093/mnras/stt1462](https://doi.org/10.1093/mnras/stt1462). [Primary publisher article](https://academic.oup.com/mnras/article/435/3/2501/1029844); [publisher PDF](https://academic.oup.com/mnras/article-pdf/435/3/2501/3431815/stt1462.pdf); arXiv:1307.2907.

**Coverage:** primary PDF introduction and model through the instrumental chromatic phase expressions; publisher-indexed Section 2.4 with closure/smearing formulas Eq. (21)–(31). The PDF has 19 pages; many later details were not read because subsequent fetches failed. This is the closest analytic source still warranting more complete formula comparison before claiming priority for the derivative expansion.

**Y. E. Molan, Z. Lu, and J.-W. Kim (2020).** “Influence of the Statistical Properties of Phase and Intensity on Closure Phase.” *IEEE Transactions on Geoscience and Remote Sensing* **58**, 7346–7354. [DOI 10.1109/TGRS.2020.2982062](https://doi.org/10.1109/TGRS.2020.2982062). [NASA author-record abstract](https://espo.nasa.gov/spade/content/Influence_of_the_Statistical_Properties_of_Phase_and_Intensity_on_Closure_Phase). **Coverage:** primary repository abstract only. It connects averaging-induced closure to amplitude/phase statistics and covariance; it is an adjacent warning against claiming generic novelty for amplitude–phase mixing.

**Y. Zheng, H. Fattahi, P. Agram, M. Simons, and P. Rosen (2022).** “On Closure Phase and Systematic Bias in Multilooked SAR Interferometry.” *IEEE TGRS* **60**, article 5226611. [DOI 10.1109/TGRS.2022.3167648](https://doi.org/10.1109/TGRS.2022.3167648). [Caltech author repository](https://authors.library.caltech.edu/records/ksehb-esr90). **Coverage:** repository abstract and indexed primary-PDF passages only; PDF retrieval timed out. This documents the broader averaging/closure-bias literature, not an exact formula-level duplication claim.

## 4. Neural scope and scientific contribution

I searched combinations of closure phase, cyclic cross spectra, Bargmann invariants, holonomy, gauge, triadic phase, EEG, MEG, fMRI, electrophysiology, time reversal, irreversibility, local filters, and phase-minimized entropy. I located no clear primary neuroscience paper using exactly this reversal quotient or the triangle lower bound. That restricted outcome supports further development; it does not establish global priority or an unfilled neuroscience gap by itself.

The mathematical observable is a product of **second-order** cross-spectral quantities at one frequency. Neural third-order bispectra and generic higher-order-interaction papers should not be presented as the same statistic. Equally, a three-channel observable can encode a consistency condition among pairwise spectra without establishing a three-way physiological interaction.

The positive scientific story is an identifiable component of temporal asymmetry under explicitly modeled observation uncertainty. In that story, existing invariants establish what information survives calibration; the reversal quotient quantifies it; the triangle bound gives an accessible certificate; finite-window analysis determines the assumptions needed to observe it reliably. This is a coherent methods contribution.

The anatomical interpretation depends sharply on where mixing and filters occur. Sensor-specific filtering after observation is covered; source-specific filtering before volume conduction generally is a different class. The paper should make that distinction once, using an explicit observation equation. A sensor-level EEG finding is informative evidence about the measured spectral geometry under the chosen calibrated null. The validation needs to establish why the finite-record estimator corresponds to the stated population property.

## 5. Publication readiness

**Assessment of the proposal, before independent inspection of its new results:** a credible focused computational-neuroscience or neural-methods manuscript is plausible if the observation theorem, useful quantitative bounds, estimator calibration, and empirical demonstration form one complete argument. The project currently has stronger support as an identifiability/methodology result than as a validated biological mechanism. Reproducible statistical significance in EEG and many simulations alone do not establish a substantial new biological explanation.

The publication case should lead with the filter-relaxed reversal target and finite-observation consequences. It should credit the real-gauge characterization, astronomy invariant, phase-linking precedents, and optimization certificate explicitly. This makes the actual remaining contribution easier to assess and protects it from a reviewer discovering close precedents first.

The newly proposed finite-record no-go theorem could be the most substantial conceptual result: if unrestricted channel memory can reproduce arbitrary finite Gaussian data laws from a reversible scalar source, it identifies exactly why population closure invariance alone cannot justify a uniform finite-sample inference. That claim is under mathematical review and has not yet received a sufficient prior-art search in this audit. Its strongest potential narrative is the pairing of a population identifiable quantity with a finite-data impossibility result and explicit assumptions that recover testability.

## 6. Search and inference limits

This was a concentrated primary-literature audit, not a systematic bibliometric review. Exact theorem-level duplication was established where a proof or formula was actually read. Abstract-only and partially read sources are labeled above. Search absence is never used as evidence of originality. Additional recent source arXiv:2608.13431, supplied near the audit's close, and the finite-record delayed-innovation construction will be handled in a short separate addendum.

No publication venue or acceptance outcome is guaranteed by this assessment. The concrete conclusion is that several initial novelty claims should be removed or narrowed, while the reversal-specific construction and finite-observation theory retain a scientifically meaningful, sharply delimited research opportunity.
