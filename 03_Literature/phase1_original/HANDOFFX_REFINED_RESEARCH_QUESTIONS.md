# Refined HandoffX research questions and pre-specified evaluation focus

**Primary (RQ0):** In bounded multi-step tool-agent workflows with the actions `continue`, `retry`, `request human assistance`, and `stop`, how do joint uncertainty in autonomous recovery and human-assisted resolution, persistent failure dependence and selective outcome visibility change the comparative performance of established intervention policies?

**RQ1 — Structural transfer:** Which observable state, action, cost and terminal-outcome schema can be reused across different tool-agent stacks **without** assuming unchanged conditional outcome probabilities? *Test:* shared API adapters, failure cases and schema coverage; not a novelty claim about generic MDPs.

**RQ2 — Decision timing:** Under what experimentally controlled conditions do dynamic policies outperform static expected-loss, retry-first and confidence-threshold policies? *Test:* matched information and budget; vary time horizon, delays and intervention costs. *Null:* simple policy non-inferior.

**RQ3 — Joint uncertainty:** How does simultaneous estimation error in `p(recover | history)` and `p(resolve by human | history)`, including shared latent causes, affect regret, risk and human workload? *Test:* vary independent vs coupled posterior/ambiguity models. *Null:* no practical value from coupled representation.

**RQ4 — Transfer:** What happens when agent model, tool failures, task type or human availability changes without immediate recalibration? Which diagnostics and simple recalibration restore well-calibrated decision performance? *Test:* synthetic controlled domain swaps; clearly separate real-agent tests if available.

**RQ5 — Reliability limits:** When do guarantees from existing robust MDP/calibration/deferral literature actually apply, and when do unobserved confounding, nonrectangular dependence, nonstationarity and no overlap make them inapplicable? *Test:* assumption stress cases, counterexamples and audit flags; do not assert new universal theorems.

**RQ6 — Lightweight implementation:** Can established policies run as a small, auditable, offline Python decision-support module on 16 GB RAM CPU-only Windows, without neural weights/API access? *Test:* policy correctness relative to enumerated oracle on tiny MDPs, deterministic seeds, memory/runtime, structured trace exports.

**RQ7 — Comparative empirical performance:** What are the loss, tail risk, intervention-load and calibration tradeoffs among strong approaches? *Required baselines:* always continue, retry-first, always human when available, static Bayes loss-based L2D, calibrated threshold, sequential MDP, robust/ambiguity MDP, and simulator-information oracle. *Critical fairness:* identical observable inputs and tuned budgets across policies.

## Pre-specification and limitations

- **Unit:** episode = one bounded task with repeat decision opportunities; human intervention outcome is a stochastic transition, not an oracle answer.
- **Primary effect:** paired episode loss/regret difference with confidence interval; **not** a cherry-picked success rate.
- **Secondary:** severe failures; interventions/episode; false escalations; task success; expected latency; calibration (conditional Brier/log loss where observable); model drift.
- **Stressors:** AI-overconfidence, human-overconfidence, shared difficulty, latent persistent faults, human unavailable, delayed human, irreversibility, constrained budget, selective labels, changed agent/tool distribution.
- **Identifiability:** logged observational outcomes do not reveal unchosen-action outcomes. Simulation ground truth must be labeled as simulation; real data require identification/positivity analysis.
- **Hard safety:** authorization and prohibited actions are filtered before optimization; cost minimization cannot override mandatory safety constraints.
- **New theory:** none promised; define further theorems only if a genuinely non-redundant mathematical problem survives additional close prior-art analysis.
- **Feasibility:** small tabular or factored finite-state simulations on CPU, no LLM necessary. Real-model validation optional and separately scoped.
