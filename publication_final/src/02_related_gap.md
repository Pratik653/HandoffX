# 2. Related work

This section is a targeted synthesis, not a systematic review. The first prior-art audit and its source-by-source mapping are preserved in Appendix E. Bibliographic records were verified against publisher, Crossref or proceedings metadata. Older records were verified on 28–29 October 2026; the five references added for the consolidated paper were verified on 29 October 2026.

## 2.1. Sequential decision-making under partial observability and parameter uncertainty

Belief-state control of partially observable Markov decision processes (POMDPs) supplies the basic language: a policy acts on a posterior distribution over hidden states (Kaelbling et al., 1998). Bayes-adaptive POMDPs extend the hidden state with unknown model parameters, so that information gathering and exploitation are traded off within one Bayesian objective (Ross et al., 2011).

HandoffX's joint belief over a finite model index and a latent failure mode is a small, finite-support specialization of these formulations. Its exact recursion is standard dynamic programming on a sufficient count state.

## 2.2. Deferral, selective prediction and human–AI complementarity

The decision to hand a case to a human is closely related to selective prediction with a reject option. Chow (1970) characterized the optimal error–reject trade-off for classification. Learning-to-defer methods extend this to a fallible downstream expert:
- consistent surrogate losses for deferral (Mozannar & Sontag, 2020);
- fairness-sensitive deferral (Madras et al., 2018);
- calibrated and multi-expert deferral (Verma & Nalisnick, 2022; Verma et al., 2023);
- complementarity-oriented learning (Charusaie et al., 2022);
- learning with limited expert labels (Hemmer et al., 2023).

Related benchmarks and analyses show that synthetic experts and capacity constraints are established evaluation devices (Alves et al., 2025). Confidence-only cascades can fail (Jitkrittum et al., 2023), and hidden confounding complicates learning from deferral logs (Ghoummaid & Shalit, 2024).

HandoffX reuses the Bayes decision principle behind these methods; Proposition P1 is the static deferral rule. It differs in three ways:
- it studies repeated, sequential recovery decisions rather than one-shot classification;
- it does not train a surrogate;
- it treats the human as a costly, fallible, terminal action whose effectiveness is itself uncertain.

## 2.3. Help-seeking agents and human-in-the-loop control

Robots that request help from imperfect and sometimes unavailable humans have long been studied (Rosenthal et al., 2011). Other prior work covers:
- uncertainty-aware querying of an expert under a call budget (Singi et al., 2023);
- switching control among agents in a team (Balazadeh et al., 2023);
- Bayesian self-escalation in hierarchical language-model agents (Shaikh, 2026);
- benchmarks of when agents ask for help (Trinh et al., 2026);
- benchmarks of tool–agent–user interaction (Yao et al., 2025).

These works show that help-seeking, escalation timing and imperfect helpers are not new concepts. HandoffX instead isolates a costed synthetic decision model in which exact optimal values are computable. It therefore complements, rather than competes with, benchmarks of real agents.

## 2.4. Robust and risk-sensitive control

Robust dynamic programming under rectangular uncertainty sets is established (Iyengar, 2005; Nilim & El Ghaoui, 2005), as are robust policies for uncertain POMDPs (Suilen et al., 2020; Cubuktepe et al., 2021). The rectangularity assumption is consequential: Counterexample CE5 shows a factor-of-two gap.

Risk-sensitive alternatives to expected-loss minimization include:
- exponential-utility Markov decision processes (Howard & Matheson, 1972);
- constrained Markov decision processes (Altman, 1999/2021);
- conditional value-at-risk optimization (Rockafellar & Uryasev, 2000);
- distribution-free conformal risk control (Angelopoulos et al., 2024).

HandoffX does not implement a constrained or CVaR optimizer. Its risk tools are:
- a union-bound per-action catastrophe guard (P7);
- a robust planner;
- in Study V only, an exploratory catastrophe-weighted planning objective.

## 2.5. Safe improvement, Bayesian learning and misspecification

Studies II–IV use the following established results:
- the conservative gate of Study II follows the logic of high-confidence and safe policy improvement (Thomas et al., 2015; Laroche et al., 2019), but makes a posterior rather than a frequentist statement;
- cross-episode learning relies on the ignorability of data-dependent action selection (Rubin, 1976);
- exploration is compared with Thompson sampling (Thompson, 1933; Russo et al., 2018);
- under misspecification, posteriors concentrate on the Kullback–Leibler-closest model (Berk, 1966), which motivates posterior predictive checking (Box, 1980);
- Study III's reversion guard uses Bayes factors (Kass & Raftery, 1995);
- its "learning trap" diagnosis corresponds to incomplete learning in Bayesian sequential decisions (Harrison et al., 2012).

# 3. Research gap and contributions

## 3.1. Gap

The literature supplies the mathematics for each component. It does not supply a single, executable, exactly evaluable benchmark of continue/retry/human/stop decisions that allows all of the following to be compared on equal information:
- nominal, Bayesian, robust and adaptive interpretations;
- persistent failures and fallible terminal human rescue;
- pre-registered held-out evaluation;
- explicit separation of average loss, task completion and severe-failure risk.

Without such a benchmark it is hard to say when uncertainty-aware or adaptive intervention is worth its complexity, and what kind of benefit it delivers when it is. The reviewed material did not show an identical matched implementation, but the absence of a title in a targeted search is not proof of originality. No novelty is claimed for established Bayesian or decision-theoretic principles.

## 3.2. Contributions

The contributions are limited to those supported by the evidence:

1. **A unified mathematical decision framework.** A finite-horizon formulation of continue, retry, human rescue and stop with:
   - latent persistent failure modes and uncertain AI and human effectiveness;
   - Bayesian, nominal and history-rectangular robust semantics;
   - a cross-episode extension.

   Nine conditional propositions (P1–P9), four adaptive-layer propositions (A1–A4) and nine counterexamples (CE1–CE9) state exactly what holds and what does not.
2. **A reproducible benchmark and Python reference implementation.** The benchmark has exact finite-model evaluation, common-random-number simulation and pre-registered protocols. The open-source library has a small integration API and runnable examples.
3. **Controlled evaluation of Bayesian adaptation and uncertainty.** Joint-Bayesian, robust, cross-episode-calibrated, gated, Thompson-sampling and three extended learners are compared against nominal planning and an oracle under equal information.
4. **Identification of learning failures** caused by:
   - selective observation: no learning about an action that is not taken;
   - a self-confirming escalation trap;
   - model misspecification: confident convergence to a wrong model.
5. **Empirical characterization of the trade-off** between severe-failure reduction, expected loss and task completion. This includes an independently confirmed severe-failure reduction and an inconclusive loss non-inferiority test.
6. **Transparent negative findings and practical limitations.** These include:
   - no uniform improvement over nominal planning;
   - a gate with no demonstrated value;
   - failed replication of average-loss gains;
   - a risk reduction obtained by caution rather than better estimation.

## 3.3. Kinds of evidence

**Table {T:evidence}.** *Kinds of evidence used in this paper*

| Label | Meaning | Examples |
|---|---|---|
| Theoretical | Proved under stated assumptions; adapted from established theory | P1–P9, A1–A4 |
| Constructed counterexample | Exact arithmetic on a specified example | CE1–CE8 |
| Exact finite-model calculation | Expected values computed exactly for a specified synthetic model | All "exact loss" and "severe-failure probability" values |
| Synthetic simulation | Monte Carlo trajectories from the specified generator | Paired intervals in Study I; realized-event counts |
| Pre-registered held-out evidence | Protocol and code frozen before the evaluation data were run once | Study II test and shift splits; Study IV |
| Confirmatory | Pre-registered primary endpoint, comparator, threshold and sample size | Study IV primary endpoint only |
| Exploratory | Designed or examined after results were seen | Study V; post-pilot diagnostics in Study III |
| Real-world generalization | Not established | None |

## 3.4. Research questions

The eight original questions (RQ1–RQ8) are retained; their final answers are in Section 15.3. Studies II–V add three questions:

**Table {T:rqs}.** *Research questions*

| ID | Question | Evidence required |
|---|---|---|
| RQ1 | Can a common probability/cost interface support architecture-independent intervention decisions? | Formal state/action contracts and executable APIs |
| RQ2 | When do continue, retry, human rescue and stop minimize the specified objective? | Bellman recursion, thresholds in valid special cases and worked examples |
| RQ3 | How do errors and dependence in AI/human capability estimates change decisions? | Controlled bias factors and prior-factorization ablation |
| RQ4 | How do persistent modes and dependent retries affect loss and escalation? | Posterior derivation and iid-mode comparison |
| RQ5 | Which stability, coverage and transfer statements can be established conditionally? | Complete proofs, counterexamples and numerical checks |
| RQ6 | What transfers when the environment or agent changes? | Structural API reuse versus a deliberately shifted model |
| RQ7 | How do established/reference policies compare under matched information? | Exact expectations, paired intervals and all negative results |
| RQ8 | Is a lightweight, auditable prototype usable without paid infrastructure? | Actual package, examples, tests, installation and runtime records |
| RQ9 | Can cross-episode learning improve on nominal planning on held-out environments, and does a conservative gate help? | Pre-registered held-out benchmark (Study II) |
| RQ10 | What limits further adaptive improvement in average loss? | Headroom diagnostics and candidate screening (Study III) |
| RQ11 | Can severe-failure risk be reduced without unacceptable loss, and by what mechanism? | Pre-registered confirmation (Study IV); exploratory mechanism analysis (Study V) |
