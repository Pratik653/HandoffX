# Confirmation results: candidate A vs ungated Bayesian recalibration

Run once on the frozen design (PRE_REGISTERED_PROTOCOL.md; pre-registration commit 4d3cfce, pushed before execution). All results are synthetic; losses are artificial units.

- Sources: `results/confirm/analysis.json`, `results/confirm/summary.csv`, `figures/confirmation_forest.png`.
- Compute: 134.7 s on 16 workers.

## Sample

| | Value |
|---|---|
| Environments | 500 (persist_shift 150, human_shift 150, hazard_shift 40, calibrated 40, near_nominal 40, ai_bias 40, joint_bias 40) |
| Episodes | 100 per stream → 50,000 per policy, 350,000 in total (7 policies) |
| Expected severe events, target families (A / bayes_recal) | 440 / 535, out of 30,000 episodes each |
| Realized (sampled) severe events, all 500 environments | A 790, bayes_recal 973, handoffx_v2 975, nominal 947, oracle 842 |
| Runner equivalence with the frozen PoC runner | max \|Δ exact loss\| = 0.0 |

## Primary endpoint (target = persist_shift ∪ human_shift, n = 300)

| | A | bayes_recal | Difference [95% CI] |
|---|---|---|---|
| Severe-failure probability per episode | 0.0147 | 0.0178 | **ARD −0.0032 [−0.0044, −0.0021]** |
| Relative risk reduction | | | **17.8% [12.0%, 24.0%]** |

**Primary criterion met:** the upper bound is below 0 and the RRR is at least 10%. About 3.2 severe failures are avoided per 1,000 episodes.

## Loss non-inferiority (target)

| Statistic | Estimate [95% CI] | Margin | Result |
|---|---|---|---|
| Cumulative loss ratio − 1 | **+0.28% [−0.21%, +0.82%]** | +0.5% | **not demonstrated**: the one-sided 97.5% upper bound of 0.82% exceeds 0.5%. Inferiority is not shown either: the lower bound is below the margin |
| Mean per-environment relative difference (secondary) | +0.24% [−0.16%, +0.66%] | | |

The pre-execution precision estimate (power 0.63 if the true effect is 0) anticipated this inconclusive outcome as a real possibility.

## Robustness: separate effects (A vs bayes_recal)

| Kind | n | Severe RRR [95% CI] | Loss change [95% CI] |
|---|---|---|---|
| **persist_shift** (Family A) | 150 | **18.4% [10.0, 27.5]** | **−0.58% [−0.99, −0.19]** |
| **human_shift** (Family B) | 150 | **17.3% [9.3, 25.8]** | **+1.14% [+0.27, +2.11]** |
| hazard_shift | 40 | 23.2% [2.8, 46.8] | −3.29% [−7.90, −0.20] |
| calibrated | 40 | 6.2% [0.4, 15.8] | +0.05% [−0.26, +0.36] |
| near_nominal | 40 | 28.1% [8.3, 48.5] | +0.17% [−1.40, +1.51] |
| ai_bias | 40 | 8.2% [0.8, 20.3] | +0.28% [−0.46, +1.10] |
| joint_bias | 40 | 18.3% [3.6, 36.5] | +1.18% [+0.02, +2.55] |

What the robustness table shows:
- **The severe-failure reduction holds in every kind**, and every interval excludes zero. It does not depend on one shift generator: it is about the same under persistent-failure shift and under human-effectiveness shift.
- **The loss effect depends on the mechanism.**
  - A lowers loss under persistent-failure and hazard shifts.
  - It **raises loss under human-effectiveness shift**: +1.14%, which exceeds the 0.5% margin within that family.
  - It also raises loss under joint AI + human bias: +1.18%, with a borderline interval.
  - The pooled target mixes a gain and a cost, and is reported only together with these parts.

### Sub-types (target families; A vs bayes_recal)

| Sub-type | n | Severe RRR [95% CI] | Loss change [95% CI] |
|---|---|---|---|
| persist / prevalence | 50 | 24.6% [6.8, 41.6] | −1.33% [−2.20, −0.59] |
| persist / dependence | 46 | 4.6% [0.1, 12.6] | +0.23% [−0.28, +0.88] |
| persist / both | 54 | 22.5% [8.9, 37.0] | −0.46% [−1.01, +0.11] |
| human / uniform | 56 | 15.8% [5.7, 28.5] | +0.40% [−0.64, +1.45] |
| human / mode_flat | 46 | 26.3% [7.9, 43.3] | **+2.47% [+0.17, +4.98]** |
| human / persistent_only | 48 | 8.7% [0.4, 18.2] | +0.61% [+0.01, +1.53] |

## Other comparators (target, A vs …)

| Comparator | Severe RRR [95% CI] | Loss change [95% CI] |
|---|---|---|
| handoffx_v2 | 17.9% [12.0, 24.2] | +0.36% [−0.16, +0.92] |
| nominal | 16.0% [9.8, 22.6] | −0.76% [−1.64, +0.11] |
| oracle (diagnostic) | 7.1% [−0.1, 14.0] | +3.46% [+2.69, +4.34] |

A's severe-failure probability, 0.0147, is **below the oracle's** (0.0158), while its loss is 3.5% above the oracle's. A is therefore more risk-averse than the loss-optimal policy. It does not approach the oracle; it moves along the risk–loss trade-off.

## Safeguards (exact means; target families unless noted)

| Metric | nominal | handoffx_v2 | bayes_recal | **A** | oracle |
|---|---|---|---|---|---|
| Task success probability | 0.678 | 0.660 | 0.654 | **0.621** | 0.683 |
| Stop (abandon) probability | 0.234 | 0.267 | 0.276 | **0.308** | 0.249 |
| Stopping where the oracle would continue | 0.033 | 0.043 | 0.052 | **0.085** | 0 |
| Human escalation probability | 0.297 | 0.248 | 0.235 | 0.262 | 0.295 |
| Unnecessary escalation (`excess_handoff`) | 0.084 | 0.040 | 0.035 | 0.055 | 0 |
| Retries per episode | 0.277 | 0.281 | 0.282 | **0.240** | 0.234 |
| Severe on continue / retry / human steps | .0152/.0014/.0008 | .0157/.0015/.0007 | .0157/.0015/.0007 | **.0127/.0012/.0007** | .0138/.0012/.0008 |
| Severe at states where the oracle acts differently | 0.0028 | 0.0024 | 0.0025 | **0.0013** | 0 |
| Seconds per stream | 0.06 | 1.48 | 0.62 | 0.64 | 0.04 |

Notes on the safeguards:
- **Calibrated environments:** A is +1.01% [+0.24, +1.98] in loss vs nominal, the optimal policy there. Against bayes_recal it is +0.05%. Rounds 3–4 showed the same calibration cost (+0.84%, +0.95%).
- **Human misestimation:** see human_shift above. A escalates *more* when the human is worse than supplied, +0.10 to +0.11 in the uniform and mode_flat sub-types with b < 0 (MECHANISM_ANALYSIS.md §4). This is the source of the human-family loss.
- **Severe failures from inappropriate stopping or escalation:** stopping cannot cause a severe failure in this model. Severe failures on human steps are unchanged (0.0007). The reduction is almost entirely on continue steps, and it halves the severe mass at states where A acts differently from the oracle (0.0025 → 0.0013).
- **Compute:** 1.03× bayes_recal; 0.43× handoffx_v2.

## Frozen decision rule

| Condition | Result |
|---|---|
| Primary met (ARD upper bound < 0 and RRR ≥ 10%) | yes |
| Loss non-inferiority (upper bound < +0.5%) | **no** (+0.82%) |
| Loss clearly worse than the margin (lower bound > +0.5%) | no |
| Robustness (both families ARD < 0, RRR ≥ 5%; hazard no harm) | yes |
| Benefit in one family only | no |
| Significant severe increase in any kind | none |
| Any kind with loss lower bound > +1% | none |
| **Decision** | **CONDITIONAL GO** |

The candidate and analysis were not changed after the results were seen. Everything in MECHANISM_ANALYSIS.md beyond the pre-registered metrics is labelled exploratory.
