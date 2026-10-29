# Adversarial mathematical equivalence and novelty audit

**Audit date:** 2026-10-28. **Verdict:** provisional **C** (comparative empirical / reproducible engineering); **B** possible only after new comparative evidence. **Theoretical novelty A:** not established. **D:** applicable if a complete review finds an equivalent existing joint-recovery benchmark and framework.

## Claims HandoffX must not make

| Tempting claim | Contrary established prior art | Disposition |
|---|---|---|
| First algorithm deciding to defer from AI to human | Madras 2018; Mozannar & Sontag 2020 | REJECT |
| First to estimate both human and AI error | Raghu 2019; Verma & Nalisnick 2022; Fuchs 2023 | REJECT |
| First model-agnostic intervention policy | General MDP/POMDP control and two-layer switching MDP (Balazadeh Meresht 2022) | REJECT as mathematical novelty |
| First robust policy for uncertain transition probabilities | Iyengar 2005; Nilim & El Ghaoui 2005 | REJECT |
| First robust policy with hidden state and uncertain observation | Suilen 2020; Cubuktepe 2021 | REJECT |
| First sequential help-seeking agent | Rosenthal 2011; Singi 2023; Shaikh 2026; HiL-Bench 2026 | REJECT |
| First LLM escalation based on optimal stopping and calibration | Shaikh 2026 (preprint) | REJECT as unsupported |
| First multiple-tier LLM to human routing | Fanconi & van der Schaar 2025 | REJECT |
| First benchmark for imperfect capacity-limited experts | Alves et al. 2025 (OpenL2D) | REJECT |
| First to predict human intervention in browser agents | Huq et al. 2026 | REJECT |
| First to address missing causal deferral outcomes | Ghoummaid & Shalit 2024 | REJECT |

## Equivalence crosswalk

**Static special case:** One-step classifier/expert loss in Mozannar & Sontag. If no retry/history and success is binary with symmetric consequences, HandoffX reduces to existing Bayes deferral, not a new handoff rule.

**Sequential, observed states:** Encode current controller, task progress, budget, failure mode and operator condition as `s`; encode actions as `continue,retry,human,stop`. The problem becomes an MDP / switching control problem. The human need not be perfect: its action has its own transition law. Compare to Balazadeh Meresht and classical robust DP.

**Partial observability:** If persistent error state or human availability is hidden, use belief `b_t`; this is a POMDP. Observation and transition uncertainty yield uPOMDPs. Adding uncertain recovery and human success rates to one transition kernel does **not** create a new mathematical class.

**Joint uncertainty:** Separate confidence bounds for AI recovery and human rescue can define a joint uncertainty set `U` over transition probabilities. If AI and human effectiveness share latent environment factors, a *coupled* (possibly non-rectangular) set is necessary. Classical robust Bellman recursions may require rectangularity or a state-augmented/adversarial model. **Potential research value:** demonstrate empirically when simple independent intervals mislead vs coupled estimates; not invent minimax control.

**Retry dependence:** A naïve model that resamples success iid with probability `p` wrongly expects success chance `1-(1-p)^k` after `k` retries if a latent persistent fault exists. Markov state augmentation or hidden-mode POMDPs are established solutions. **Potential research value:** quantify estimation and decision consequences on agent traces.

**Transferability:** Reusing transition/action *schema* across LLMs is structural transfer; reusing trained probabilities is statistical transfer; retaining outcomes and guarantees is performance transfer. Only the first is built into generic control. The others require new empirical evidence and revalidation.

## Strongest non-equivalence arguments still available

1. A **benchmarking protocol**, not a new equation, targeted at *joint probability estimation error plus correlated retries, selective labels, delay, and changing tools/operators*, and evaluating whether robust models actually beat parsimonious static and sequential baselines.
2. A **practical auditable CPU-only library**, with transparent outcome assumptions and a formal adapter interface, that maps established methods onto tool-agent traces and enforces external safety constraints.
3. A **bounded empirical/algorithmic contribution** if data establish that a joint-vs-independent calibration or uncertainty-set estimator significantly improves decisions when compared under equally informative observations and matched tuning budgets.

These are **candidate gaps**, not verified absences across the full literature. OpenL2D and the 2025/2026 agent benchmarks narrow the available novelty and should be reused where licensing and data semantics permit.

## Identifiability challenge (central issue)

An observed failure log usually contains only the action actually selected, so human outcomes on autonomously recovered tasks, autonomous outcomes on escalated tasks, and repeat outcomes under different retries may be missing. Interventions may correlate with unobserved difficulty and operator workload. Merely fitting `p_human` or `p_retry` to observed conditional success can be biased. Ghoummaid & Shalit already show causal confounding is part of deferral research; HandoffX should add careful propensity logging, randomized permissible evaluation or simulator ground truth, uncertainty intervals and refusal to produce an unwarranted point estimate.

## Falsification criteria

- If a directly equivalent policy-and-simulation package already offers matched joint recovery/human evaluation, downgrade to reproducibility/integration contribution or D.
- If simple well-calibrated static expected-loss performs as well as complex methods across varied scenarios, report negative result and choose simpler design.
- If joint effectiveness cannot be identified from real logs without unacceptable interventions, limit empirical claims to controlled synthetic experiments; do not imply real safety.
- If a claimed robust bound fails due to nonrectangular uncertainty, do not report it; state assumption violation.
- If a model-agnostic schema cannot capture policy-relevant hidden state, restrict the supported task class.

## Novelty gate status

**C — confirmed as the conservative research direction, pending more exhaustive negative search.** A compelling gap may exist in *evaluating practical policies* for this conjunction, but **lack of a paper explicitly named HandoffX is not evidence** of novelty. No new theorem, lemma, code or empirical performance result is claimed here.
