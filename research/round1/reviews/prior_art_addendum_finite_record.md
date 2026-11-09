# Targeted addendum: finite-record no-go under unrestricted channel filters

**Reviewer:** theory_scout. **Date:** 2026-11-06. This adds to `prior_art_v1.md`; it is a short targeted check prompted by the root's new construction, not an exhaustive priority search. Mathematical correctness is being checked independently by the mathematical reviewer.

## 1. Result of the targeted search

I did not locate an exact published duplicate of the following specific construction: given a multivariate finite moving-average Gaussian target and a fixed observation length, replace its independent innovation streams by sufficiently separated shifts of one scalar white-noise stream, then combine those shifts inside channel-specific causal FIR filters. This gives the same complete finite-record Gaussian law from a reversible common scalar source.

Queries covered finite-dimensional distributions, finite covariance matching, scalar white-noise representation, spectral rank/multiplicity, rank-one density, local filtering, unknown filters, time reversal, and observational equivalence. Relevant neighboring sources are documented below. This search result supports treating the construction as a **candidate original contribution with a clear prior-art boundary**. It establishes no global priority claim.

The finite-record construction is more informative than a single example of spurious closure. It specifies an entire observational equivalence class and therefore applies to every statistic of the given finite record. Its particularly useful scientific implication is that an unrestricted claim of robustness to channel filters needs a filter-memory or frequency-regularity condition to become a uniformly valid finite-sample inference.

## 2. Closest directly inspected no-go precedent

**D. Lucente, A. Baldassarri, A. Puglisi, A. Vulpiani, and M. Viale (2022).** “Inference of Time Irreversibility from Incomplete Information: Linear Systems and Its Pitfalls.” *Physical Review Research* **4**, 043103. [DOI 10.1103/PhysRevResearch.4.043103](https://doi.org/10.1103/PhysRevResearch.4.043103). [Author preprint arXiv:2205.08961](https://arxiv.org/pdf/2205.08961). [CNR author repository](https://iris.cnr.it/handle/20.500.14243/412169).

**Read coverage:** primary preprint abstract/introduction; Section III opening and its scalar-versus-multivariate argument; full-text search for filtering. I did not read the entire 24-page preprint.

**Scope:** the central result concerns the inability to infer underlying nonequilibrium from one scalar stationary Gaussian observable. Their Section III explicitly distinguishes a multivariate correlation matrix, whose antisymmetry can expose observable time reversal, from a scalar covariance, which is always symmetric. The paper also separates observed correlation from unobserved response/noise mechanisms. The parent's proposed result concerns an arbitrary number of observed channels, a fixed finite record, and unknown channelwise FIR kernels. It uses a different ambiguity and gives a different quantifier structure. No serialized-innovation construction appeared in the portions inspected.

The same authors' later account is useful for context: **Dario Lucente et al. (2025)**, “Conceptual and Practical Approaches for Investigating Irreversible Processes,” *New Journal of Physics*, [DOI 10.1088/1367-2630/adc6ab](https://doi.org/10.1088/1367-2630/adc6ab), [arXiv:2410.15925](https://arxiv.org/pdf/2410.15925). **Coverage:** introduction and Section 3.3 with Eq. (36)–(39), plus the source reference to the 2022 paper. It discusses the nonuniqueness of response/noise factorization and scalar observation. For the substantive prior result cite the original 2022 paper; the 2025 article is a review.

## 3. A superficially close approximation theorem has a different target

**Tamás Szabados (2022).** “Regular Multidimensional Stationary Time Series.” *Journal of Time Series Analysis* **43**, 263–284. [DOI 10.1111/jtsa.12611](https://doi.org/10.1111/jtsa.12611). [Primary full text](https://onlinelibrary.wiley.com/doi/full/10.1111/jtsa.12611).

**Read coverage:** introduction and Wold/rank formulation; Section 3, particularly Theorem 3.1 and Eq. (3.3), (3.10), (3.11). The publisher lists a corrigendum; I did not audit the article's general regularity characterization or the corrigendum.

**Scope:** lower-rank approximation here is frequency-domain PCA in mean-square error, using a linear transform of the original process. Its error is the integral of discarded spectral eigenvalues. This differs from matching a fixed collection of finite-time covariances using a different process whose long-range correlations can change arbitrarily. It is therefore useful to explain why familiar spectral-rank results do not immediately settle the proposed finite-record universality claim. The new result should state the topology—finite-record law or total variation for nonsingular finite Gaussian laws—rather than call it simply a rank-one approximation.

## 4. Recent arXiv:2608.13431: metadata verified, primary full text unavailable

**Avishek Bhandari (2026).** “Measuring the Arrow of Time: Identification, Estimation, and Inference for Directional Structure in Multivariate Time Series.” Submitted 13 August 2026. [Primary arXiv record](https://arxiv.org/abs/2608.13431); [primary PDF endpoint](https://arxiv.org/pdf/2608.13431).

**Read coverage:** the primary arXiv abstract was returned by the scholarly search index. Direct arXiv abstract/PDF/HTML and export-arXiv fetches all failed. Therefore I cannot report a primary full-text audit of its Section 4.2. The supplied mirror excerpt about reversing raw data before recomputing preprocessing remains a lead rather than independently primary-verified evidence in this review.

**Verified abstract scope:** it studies lagged-covariance circulation, cross-fitted estimation, randomization, and sampling/clock effects. These themes are adjacent. A known preprocessing operation that can be reapplied to raw data is conceptually distinct from unknown acquisition filters and a null class allowing arbitrarily long channel memory. This logical distinction does not establish that its inaccessible full text lacks the new no-go result. Do not make a strong comparative absence claim about this preprint.

## 5. Strongest appropriate novelty claim

Subject to mathematical review, a precise claim would be:

> We construct, for every finite moving-average Gaussian multichannel model and every fixed record length, a reversible scalar Gaussian source and channel-specific causal finite filters that reproduce its complete record law. This yields a finite-observation nonidentifiability result for latent time reversal under unrestricted filter memory. We then distinguish this finite-data limitation from the population spectral invariants and derive explicit conditions controlling leakage at finite resolution.

The proposed exact construction is the potentially new mathematical ingredient. The testing consequence follows by the usual observation-equivalence/total-variation argument: if a level-α test must control rejection over the whole null class and a target law belongs to its closure, power at that target cannot exceed α. Present that inference as a corollary, not as a new general testing principle.

## 6. Essential quantifiers for the manuscript

The counterexample filter can depend on record length. Accordingly, the result concerns **uniform validity over unrestricted filter memory at each finite sample size**. A fixed, sufficiently regular filter observed for increasing duration is a separate asymptotic regime. Keeping these quantifiers explicit reconciles the population identifiability result with finite-record indistinguishability.

The exact finite-MA statement uses a singular common scalar latent source. If the formal null requires a positive-definite latent spectral matrix, the manuscript should spell out the small independent reversible-noise perturbation and resulting total-variation approximation for a nonsingular target record covariance. The extension beyond finite MA likewise needs a stated approximation class. These are proof components, not empirical issues.

This result would materially strengthen the publication case by making the central contribution a useful identification boundary with constructive witnesses. Its neuroscience significance would be the assumptions required to infer latent temporal asymmetry from finite neural recordings, supported by the population bounds and calibrated data analysis. Biological circuit mechanisms remain a separate inference problem.
