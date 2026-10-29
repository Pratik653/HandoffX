# Final research changelog

This is a chronology of the HandoffX research programme, recording what each stage established and how later stages refined earlier interpretations. No earlier numerical result has been altered; every stage's documents and results remain in the repository.

## Study I: original framework (v0.1, 28 October 2026)

- **Materials:** `01_Publication/`, `02_Mathematics/`, `05_Experiments/`; commit a7722f8 (imported baseline).
- **Formulation:** finite-horizon continue / retry / human / stop model with latent persistent modes, joint AI/human uncertainty, and nominal, Bayesian and history-rectangular robust planners. Propositions P1–P9 and counterexamples CE1–CE8.
- **Design:** 38 designed scenarios, 11 policies, exact expectations and 5,016,000 paired simulated executions.
- **Results:**
  - Bayes vs nominal: 6 better / 23 equal / 9 worse.
  - Persistence modelling better than the iid ablation in 15 scenarios, equal in 23.
  - The coupled prior was not generally helpful.
  - The robust bound failed out of support.

## Study II: adaptive learning (v0.2, 29 October 2026)

- **Materials:** `research_v2/`, `benchmarks_v2/`, `publication_v2/`; commits 5adacea–e07c0c2.
- **Root cause of the 6/23/9 result:** small losses (largest +0.70%), nominal already optimal in 26 scenarios, and within-episode non-identifiability. This refines Study I's interpretation without changing its numbers.
- **Method:** cross-episode Bayesian calibration (Propositions A1–A4) and a conservative gate. Pre-registered dev/validation/test/shift splits.
- **Held-out results:** gated −0.46% [−1.07, +0.09] vs nominal; ungated −0.63% [−1.28, −0.05]. The gate was not shown to add value. Removing persistence cost +5.8%.
- **New counterexample:** CE9, confident convergence to a wrong model under misspecification.

## Study III: feasibility screening (v0.3 study, 29 October 2026)

- **Materials:** `research_poc_v03/`; commits bd8e512–ecab8b2.
- **Diagnostics:**
  - the model grid is not the bottleneck;
  - learning stalls through a self-confirming escalation trap and misspecified prevalence.
- **Candidates:** A (prevalence uncertainty), B (targeted human exploration), C (Bayes-factor guard), and combinations, each over pilot, confirmation and replication rounds.
- **Outcome:**
  - no replicated average-loss gain;
  - B NO-GO; C NO-GO standalone; combinations NO-GO;
  - A CONDITIONAL GO, because it reduced severe failures 13–17% in all rounds (secondary metric).

## Study IV: pre-registered risk-reduction confirmation (29 October 2026)

- **Materials:** `research_poc_v03/confirmation/`. Protocol commit 4d3cfce, pushed before the run; results commit d9e9c58.
- **Result:**
  - severe-failure RRR 17.8% [12.0, 24.0] vs bayes_recal, ARD −3.2 per 1,000 episodes, in both shift families;
  - loss non-inferiority not demonstrated (+0.28% [−0.21, +0.82]; margin 0.5%);
  - task success −3.3 percentage points.
- **Decision:** CONDITIONAL GO under the frozen rule.

## Study V: exploratory mechanism analysis (29 October 2026)

- **Materials:** same directory, `MECHANISM_ANALYSIS.md`; fresh seeds 850000+; post hoc.
- **Finding:** the reduction comes from more cautious decisions, not more accurate prevalence estimation. Catastrophe-weighted planning produces comparable or larger reductions along a risk–loss trade-off.
- **Refinement:** "A learns failure prevalence" is replaced by "A applies evidence-triggered caution".
- **Not performed:** the proposed matched-risk confirmation.

## Consolidation and release (29 October 2026)

- `publication_final/`: the final consolidated paper (Markdown, DOCX, PDF, BibTeX). It integrates Studies I–V, preserves all original mathematics and results verbatim through include directives, and adds five verified references.
- `handoffx` 0.2.1: fixes the posterior-underflow defect found in Study III Round 1. It is the first version prepared for PyPI. The public API is unchanged, and no experimental algorithm was added to the package.
- Earlier manuscripts are preserved unchanged: `01_Publication/` and `publication_v2/`.
