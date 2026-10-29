# Ablation analysis (held-out test split, 200 environments; validation and shift in brackets)

Relative change in mean exact episode loss versus nominal, 95% bootstrap intervals in EXPERIMENTAL_RESULTS.md. Each row removes or changes one component of the full controller `handoffx_v2` (cross-episode posterior + Bayes-adaptive candidate + joint uncertainty over a model grid + persistent failure modes + conservative gate).

| Variant | What changes | Test | [Validation; Shift] | Verdict |
|---|---|---:|---|---|
| handoffx_v2 | full controller | -0.46% | [-0.16%; -1.06%] | reference |
| bayes_recal | remove the gate | -0.63% | [+0.60%; -0.82%] | gate not shown to help or hurt on average; it slows early switching |
| gate_static | remove cross-episode calibration (gate evaluated once on the prior) | -0.14% | [-0.09%; +0.06%] | calibration provides most of the gain; static gating is extremely safe (0 test environments degraded > 1%, worst +0.73%) but nearly inert |
| plugin_recal | remove joint uncertainty (plan on MAP model) | -0.26% | [+0.09%; -0.26%] | posterior-averaged planning beats point-estimate recalibration (gap closed 37% vs. 19% for bayes_recal) |
| bayes_static | remove calibration and gate (v0.1 joint-Bayes analogue) | +0.16% | [+0.26%; +1.10%] | reproduces v0.1: a static joint prior does not beat nominal |
| v2_iid | remove failure dependence (iid modes) | **+5.79%** | [+5.37%; +5.79%] | largest effect in the study: modelling persistent failure is essential |
| ts_recal | replace exploitation by posterior sampling | +0.66% | [+0.41%; +0.42%] | exploration cost exceeds information value at 100 episodes |
| robust_static | worst-case objective, no learning | +7.26% | [+8.67%; +3.44%] | worse mean loss, lower tail risk (severe 0.0130 vs. 0.0149; CVaR95 46.1 vs. 51.2) |

## Component decisions

- **Keep:** cross-episode calibration (A1), joint uncertainty, persistent-mode modelling.
- **Keep but demote to an option:** the conservative gate. It is retained in the `Advisor` because it bounds posterior risk (A3) and delays switching until evidence accumulates, which is the behaviour an operator would audit; but the benchmark does not show an average benefit over ungated posterior planning, and under misspecification its credible statement can be badly wrong (CE9). The gate parameters are exposed; `alpha=1` gives ungated behaviour.
- **Do not adopt by default:** Thompson sampling (harmful here), robust planning (only for tail-risk-averse objectives), static joint priors (no benefit).
- **Not implemented:** value-of-information probe actions (no fair evaluation designed); prevalence/hazard parameters in the model grid (the identified next step, CE9).
