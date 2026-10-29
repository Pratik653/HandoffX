# HandoffX v0.2 experimental protocol (pre-registered internally)

Status: written and hashed **before** any development, validation or test run of the v0.2 benchmark. The git commit that adds this file and `benchmarks_v2/reproducibility/PRE_REGISTRATION_SHA256.txt` is the time-stamped record. It is not a public preregistration.

## 1. Question

Under what conditions does an adaptive, uncertainty-aware controller that pools evidence across episodes make better continue/retry/human/stop decisions than nominal sequential planning on supplied estimates, and how large are the effects?

The v0.1 benchmark evaluated single episodes in which every policy had to act on a fixed supplied estimate. Phase B (`ROOT_CAUSE_ANALYSIS.md`) showed that in that information structure no policy can correct a systematic estimation error, because human effectiveness is only observed after a terminal handoff and an episode yields at most six observations. v0.2 therefore evaluates **deployment streams**: repeated episodes in a fixed environment in which logged outcomes may be used.

## 2. Environments

`benchmarks_v2/scripts/common.py::draw_environment(seed, family)` defines the distribution. Per environment:

- supplied estimates: v0.1 base success probabilities perturbed by U(-0.04, 0.04); hazard multiplier log-uniform on [0.2, 1.5]; mode prevalence Dirichlet(20 x v0.1 prevalence);
- hidden truth: with probability 0.25 the estimate is exactly calibrated; otherwise AI and human success biases are independently U(-0.2, 0.2) (continuous, so the truth is generally *off* the model grid); true mode prevalence Dirichlet(30 x estimate);
- task: horizon in {4, 5, 6}; human cost U(1, 8); retry cost U(0.8, 2); failure loss U(10, 30); stop loss U(0.4, 0.8) x failure loss; severe loss U(40, 180); human delay 1/2/3 ticks with probabilities 0.3/0.5/0.2; human available only from tick 2 with probability 0.2; no human with probability 0.1.

The model set supplied to every model-based policy is a 5 x 5 grid of AI/human offsets {-0.2, -0.1, 0, 0.1, 0.2} around the supplied estimate, each with the three latent failure modes, prior weights proportional to (0.1, 0.2, 0.4, 0.2, 0.1) per axis. The centre model is the supplied estimate; nominal planning uses it alone.

**Shift family** (held-out only): biases U(-0.3, 0.3) (can lie outside the model support), calibrated probability 0.10, true hazards x1.5, and 15% of mode prevalence moved to the persistent mode.

## 3. Splits and leakage control

| Split | Family | Seeds | Environments | Use |
|---|---|---|---|---|
| dev | iid | 100000-100059 | 60 | gate hyperparameter selection only |
| validation | iid | 200000-200059 | 60 | confirm frozen gate; no retuning |
| test | iid | 300000-300199 | 200 | primary held-out evaluation, run once |
| shift | shift | 400000-400099 | 100 | held-out distribution-shift evaluation, run once |
| original | v0.1 | 38 frozen configs | 38 | historical diagnosis only, never used for tuning |

Seed ranges are disjoint. The selected gate is written to `benchmarks_v2/configs/frozen_gate.json` and committed before validation is run; test and shift are run only after validation results are committed. Any deviation is recorded in `research_v2/RESEARCH_CHANGELOG.md`.

## 4. Streams

100 episodes per environment; learning policies refresh their plan every 5 episodes from all episodes so far (`recalibration_cadence`). Common random numbers: within an environment all policies share the latent-mode and outcome uniforms for episode t. Thompson sampling uses a separate seeded stream.

## 5. Policies (equal supplied information, shared action guard)

| Policy | Learns across episodes | Description |
|---|---|---|
| nominal | no | exact DP on the supplied estimate (v0.1 `nominal_dp`) |
| bayes_static | no | exact Bayes-adaptive DP on the fixed grid prior (v0.1 `handoffx_bayes` analogue) |
| robust_static | no | history-rectangular robust DP over the grid (v0.1 `robust_dp`) |
| plugin_recal | yes | DP on the current maximum-a-posteriori grid model (simple recalibration) |
| bayes_recal | yes | Bayes DP with the cross-episode posterior as prior; no gate |
| ts_recal | yes | posterior (Thompson) sampling of a grid model each episode |
| **handoffx_v2** | yes | conservative gate: incumbent nominal; candidate bayes_recal; switch only if posterior expected advantage > 0 and posterior probability of a relative degradation > tolerance is <= alpha |
| gate_static | no | ablation: the same gate evaluated once on the prior, never updated |
| v2_iid | yes | ablation: handoffx_v2 with the failure-dependence (persistent mode) structure removed |
| oracle | n/a | exact DP on the hidden truth; lower bound, not deployable |

## 6. Metrics

Primary: per-environment mean **exact** expected episode loss over the stream (each episode's policy is evaluated exactly under the hidden truth; this removes outcome noise but keeps the randomness of what was learned). Secondary: first-20 and last-20 episode loss, exact severe-failure probability, success probability, human-escalation probability, realized loss and realized rates, empirical CVaR95 of realized episode losses (pooled), calibration error of root success probabilities at stream start and end, number of switched episodes, wall time.

## 7. Analysis

Paired differences versus nominal by environment. Report mean difference and mean relative difference with 95% percentile bootstrap intervals over environments (10,000 resamples, seed 7), standardized paired effect size (mean / SD), wins/ties/losses at exact tolerance 1e-9 and at the practical relative tolerance 1%, worst relative degradation, and subgroup results (calibrated vs. biased; in-support vs. out-of-support; human under- vs. over-estimated). No subgroup is selected after seeing test results; all of these subgroups are listed here in advance.

## 8. Gate selection rule (dev only)

Grid: alpha in {0.05, 0.1, 0.2, 0.35, 0.5, 1.0} x relative tolerance in {0, 0.01, 0.03}. Among settings for which at most 10% of dev environments show a relative degradation versus nominal greater than 1%, choose the smallest mean relative loss difference versus nominal; ties go to smaller alpha, then smaller tolerance. If no setting qualifies, choose the setting with the fewest such degradations and record it.

## 9. What would count as a negative result

handoffx_v2 not improving mean loss over nominal on test, or degrading more than 10% of test environments by more than 1%, or being dominated by the simpler `plugin_recal` or `bayes_recal`. Any of these will be reported as found.
