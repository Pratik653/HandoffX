# Opportunity matrix (Stage C screening)

## Evidence gathered before screening (v0.2 dev environments only; held-out results not used)

| Diagnostic | Result | File |
|---|---|---|
| Headroom decomposition, iid family (60 dev envs) | nominal→oracle −3.40%; success-only oracle −2.93%; prevalence-only oracle −0.12%; calibrated envs −0.05% | `results/headroom_decomposition.json` |
| Same, shift family | oracle −8.19%; success-only −7.38%; prevalence-only −3.18% | same |
| Grid resolution limit (30 dev envs) | best single 5×5 grid model −3.65% vs oracle −3.70%; 9×9 grid −3.65% | `results/grid_limit.json` |
| Learning plateau, 400-episode streams (32 dev envs) | bayes_recal regret by 100-episode block 0.185, 0.150, 0.144, 0.139; with true prevalence = supplied: 0.138, 0.095, 0.088, 0.090; nominal 0.38 | `results/learning_limit.json` |
| Plateau attribution (prevalence matched) | 91% of plateau regret in 6 of 32 envs where the learner escalates far less than the oracle (e.g. late human rate 0.01 vs oracle 1.0, 7 human observations) | `results/plateau_attribution.json` |

Interpretation: the grid is not the bottleneck; v0.2 leaves headroom because learning stalls. Two stall mechanisms are visible: (i) a misspecified nuisance parameter (failure-mode prevalence) misleads the posterior about decision-relevant success offsets; (ii) a self-confirming escalation trap — once pessimistic about the human, the policy stops escalating and never observes the human again (v0.2 Proposition A2; incomplete learning, Harrison et al., 2012). Calibrated environments have essentially no headroom, so any learner can only lose there.

## Matrix

Scores 1 (weak) to 3 (strong) for the six ranking criteria: R rationale, E existing HandoffX evidence, F fair evaluability, S simplicity, P practical relevance, C defensible contribution.

| # | Opportunity | Observable / identifiable? | Already a baseline? | R | E | F | S | P | C | Decision |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Learn persistent-failure prevalence across tasks | Yes: consecutive failures and hard error signals inform the mode; identifiable from AI attempts (not from human outcomes) | No (v0.2 fixes prevalence per model) | 3 | 3 (plateau 0.14→0.09; CE9) | 3 | 3 (augment model set, reuse planner) | 3 | 2 | **Select — Candidate A (primary)** |
| 3 | Human-effectiveness learning with targeted exploration | Only when escalating (selective observation) | Partly: full Thompson sampling (`ts_recal`) — harmful in v0.2 | 3 | 3 (91% of plateau) | 3 | 3 (sample only the human offset) | 3 | 2 | **Select — Candidate B** |
| 4 | Misspecification guard (data must favour departing from the estimate) | Yes: marginal likelihoods | Partly: v0.2 gate (within-model credible rule; failed under CE9) | 2 | 2 (calibrated subgroup +0.57% to +0.92%) | 3 | 3 | 2 | 2 | **Select — Candidate C** |
| 5 | Informative failures / dependent retries | Yes | **Yes** — the latent-mode model already updates after every failure; removing it costs +5.8% | – | 3 | – | – | – | 0 | Reject: already implemented |
| 2 | History-dependent retry recovery by error type | Yes | **Yes** — hard vs. soft diagnostic and per-mode retry kernels already in the model | – | 1 | – | – | – | 0 | Reject: represented; no headroom evidence |
| 6 | Contextual probability estimation | Requires task features | No | 2 | 0 (simulator has no features) | 1 (new feature generator would be built to favour it) | 2 | 3 | 1 | Reject: cannot be evaluated fairly in this simulator |
| 7 | Costed diagnostic observation (VOI) | Would need a new action and observation model | No | 2 | 1 (v0.1 P9 only) | 1 | 1 (simulator, planner and guard changes) | 3 | 2 | Reject for this PoC: exceeds minimal scope |
| 8 | Risk-sensitive intervention | Yes | Partly: robust planner, severe-risk cap | 2 | 2 (robust: lower tail, +7% mean) | 2 | 2 | 2 | 1 | Reject: trade-off already characterised; separate objective |
| 9 | Alternative learners (contextual bandits, conservative improvement, BAMDP) | – | Bayes-adaptive DP, Thompson sampling, conservative gate are already baselines | – | – | – | – | – | – | Used as baselines, not candidates |
| 10 | Finer model grid | Yes | – | 1 | 3 (negative: 5×5 already reaches 99% of oracle) | – | – | – | 0 | Reject: no headroom |

## Selected candidates

- **A — prevalence-augmented posterior planning** (primary): add three persistent-failure prevalence levels to each grid model; otherwise identical to ungated `bayes_recal`.
- **B — escalation-targeted posterior sampling**: each episode, sample only the human-success offset from its posterior marginal and plan by exact Bayes over the AI offsets conditional on it. Exploration is confined to the parameter that suffers from selective observation; the full Thompson sampler that failed in v0.2 is the comparator.
- **C — Bayes-factor reversion guard**: act on the posterior only when the marginal-likelihood Bayes factor of "estimate may be biased" (full model set) against "supplied estimate is right" (centre model) exceeds 3 (Kass & Raftery, 1995); otherwise act nominally.

The strongest deployable baseline from v0.2 (ungated `bayes_recal`) is the primary comparator for all three.
