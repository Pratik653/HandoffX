# HandoffX v0.2 experimental results

Protocol: `research_v2/EXPERIMENTAL_PROTOCOL.md` (hashed and committed before any run). Raw per-episode arrays: `benchmarks_v2/results/<split>/raw/episodes.npz` (git-ignored, regenerable, archived with releases). Derived: `summary.csv`, `analysis.json`, `learning_curves.json` per split; `benchmarks_v2/results/TABLES.md`. Execution: Windows 11, Python 3.11.9, NumPy 2.3.5, 16 worker processes, CPU only; wall time 126 s (dev, 18 gate settings), 19 s (validation), 68 s (test), 34 s (shift), 12 s (original).

All losses are artificial loss units of a synthetic simulator. "Exact" means each episode's policy was evaluated exactly under the hidden truth; what was learned before that episode remains random. Intervals are 95% percentile bootstrap intervals over environments (10,000 resamples). d_z is the mean paired difference divided by its standard deviation. W/T/L (1%) counts environments with relative change below -1%, within +-1%, above +1%. "Gap closed" is (nominal - policy) / (nominal - oracle), summed over environments.

## 1. Development: gate selection

Eighteen settings were run on the 60 dev environments. The trade-off was monotone: smaller alpha and tolerance gave fewer degraded environments but smaller mean gains (alpha = 0.05, tol = 0: -0.72%, 0% degraded > 1%; alpha = 1: -1.46%, 6.7% degraded). The pre-registered rule selected **alpha = 0.35, relative tolerance = 0.03** (-1.55% on dev, 3.3% degraded). Figure: `benchmarks_v2/figures/v2_gate_tradeoff_dev.png`. Full grid: `benchmarks_v2/configs/frozen_gate.json`.

## 2. Headline

| Split (n) | handoffx_v2 rel. change vs nominal [95% CI] | bayes_recal (ungated) | Oracle headroom |
|---|---|---|---|
| validation (60) | -0.16% [-0.84, +0.39] | +0.60% [-0.40, +1.65] | -2.67% |
| **test (200, primary)** | **-0.46% [-1.07, +0.09]**; absolute -0.052 [-0.110, -0.002] | -0.63% [-1.28, -0.05] | -1.94% |
| shift (100) | -1.06% [-2.76, +0.37] | -0.82% [-2.58, +0.73] | -7.87% |
| original v0.1 scenarios (38, diagnostic) | -0.10% [-1.61, +1.42] | +0.50% [-1.20, +2.35] | -2.98% |

Plain reading:

1. On the primary held-out test split, HandoffX v0.2 lowered mean loss relative to nominal by 0.46% (absolute interval excludes zero; relative interval does not). It closed 30% of the gap between nominal planning and the oracle. Over the last 20 episodes of each stream the regret relative to the oracle fell from 0.173 (nominal) to 0.095 (-45%).
2. The effect is small because the headroom is small: on this distribution nominal planning is within 2% of the oracle on average.
3. **The conservative gate did not add value on test.** The ungated `bayes_recal` was at least as good on mean loss (-0.63%, interval excludes zero), gap closed (37%), wins (28 vs. 26) and worst case (+13.2% vs. +22.1%). On validation the ordering was reversed (gate -0.16%, ungated +0.60%). We do not claim either is better; the gate's measurable effect is to slow early switching (learning-curve figure).
4. The pre-registered negative criteria (protocol section 9): mean improvement on test, yes in absolute terms, not significant in relative terms; share of test environments degraded > 1%: 19/200 = 9.5% (threshold 10%, met narrowly); not dominated by plugin_recal (yes), but **effectively matched or beaten by bayes_recal** (criterion triggered).

## 3. Full tables

### Split `validation` (60 environments)

| Policy | Mean loss | Δ vs nominal [95% CI] | Rel. Δ [95% CI] | d_z | W/T/L (1%) | Worst rel. | Gap closed | Severe p | Human rate | CVaR95 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| nominal | 7.339 | +0.000 [+0.000, +0.000] | +0.00% [+0.00, +0.00] | +0.00 | 0/60/0 | +0.00% | 0.0% | 0.0142 | 0.347 | 45.2 |
| bayes_static | 7.351 | +0.012 [-0.013, +0.048] | +0.26% [-0.16, +0.85] | +0.10 | 2/55/3 | +11.88% | -5.2% | 0.0147 | 0.321 | 45.2 |
| robust_static | 7.795 | +0.455 [+0.209, +0.756] | +8.67% [+3.96, +14.35] | +0.41 | 7/24/29 | +102.51% | -205.2% | 0.0142 | 0.127 | 42.8 |
| plugin_recal | 7.353 | +0.014 [-0.082, +0.116] | +0.09% [-1.14, +1.32] | +0.03 | 6/46/8 | +15.19% | -6.1% | 0.0123 | 0.374 | 41.3 |
| bayes_recal | 7.368 | +0.028 [-0.042, +0.100] | +0.60% [-0.40, +1.65] | +0.10 | 4/48/8 | +15.19% | -12.7% | 0.0140 | 0.314 | 44.8 |
| ts_recal | 7.352 | +0.012 [-0.116, +0.115] | +0.41% [-0.92, +1.60] | +0.03 | 9/29/22 | +12.53% | -5.4% | 0.0145 | 0.377 | 45.2 |
| handoffx_v2 | 7.333 | -0.006 [-0.062, +0.046] | -0.16% [-0.84, +0.39] | -0.03 | 4/52/4 | +6.38% | 2.8% | 0.0138 | 0.356 | 44.7 |
| gate_static | 7.333 | -0.007 [-0.020, +0.003] | -0.09% [-0.25, +0.02] | -0.16 | 2/57/1 | +1.31% | 3.1% | 0.0143 | 0.348 | 45.1 |
| v2_iid | 7.691 | +0.352 [+0.196, +0.531] | +5.37% [+3.08, +7.88] | +0.53 | 5/28/27 | +44.80% | -158.6% | 0.0156 | 0.379 | 45.6 |
| oracle | 7.118 | -0.222 [-0.374, -0.099] | -2.67% [-4.22, -1.32] | -0.40 | 17/43/0 | +0.00% | 100.0% | 0.0134 | 0.390 | 41.8 |

### Split `test` (200 environments)

| Policy | Mean loss | Δ vs nominal [95% CI] | Rel. Δ [95% CI] | d_z | W/T/L (1%) | Worst rel. | Gap closed | Severe p | Human rate | CVaR95 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| nominal | 7.573 | +0.000 [+0.000, +0.000] | +0.00% [+0.00, +0.00] | +0.00 | 0/200/0 | +0.00% | 0.0% | 0.0149 | 0.384 | 51.2 |
| bayes_static | 7.569 | -0.004 [-0.041, +0.029] | +0.16% [-0.30, +0.69] | -0.02 | 6/187/7 | +33.67% | 2.4% | 0.0152 | 0.349 | 52.3 |
| robust_static | 8.013 | +0.440 [+0.287, +0.600] | +7.26% [+4.87, +9.86] | +0.39 | 19/86/95 | +126.11% | -254.4% | 0.0130 | 0.177 | 46.1 |
| plugin_recal | 7.541 | -0.032 [-0.079, +0.009] | -0.26% [-0.76, +0.19] | -0.10 | 21/161/18 | +13.00% | 18.7% | 0.0154 | 0.343 | 52.3 |
| bayes_recal | 7.509 | -0.064 [-0.127, -0.010] | -0.63% [-1.28, -0.05] | -0.15 | 28/152/20 | +13.19% | 37.0% | 0.0160 | 0.313 | 53.3 |
| ts_recal | 7.607 | +0.034 [-0.017, +0.084] | +0.66% [+0.06, +1.23] | +0.09 | 22/111/67 | +18.79% | -19.6% | 0.0162 | 0.337 | 53.7 |
| handoffx_v2 | 7.521 | -0.052 [-0.110, -0.002] | -0.46% [-1.07, +0.09] | -0.13 | 26/155/19 | +22.15% | 30.1% | 0.0158 | 0.320 | 53.5 |
| gate_static | 7.559 | -0.015 [-0.039, -0.001] | -0.14% [-0.37, -0.01] | -0.09 | 3/197/0 | +0.73% | 8.4% | 0.0142 | 0.384 | 50.6 |
| v2_iid | 7.981 | +0.408 [+0.291, +0.527] | +5.79% [+4.37, +7.22] | +0.48 | 13/84/103 | +44.18% | -235.9% | 0.0173 | 0.336 | 53.7 |
| oracle | 7.400 | -0.173 [-0.245, -0.112] | -1.94% [-2.69, -1.29] | -0.36 | 48/152/0 | +0.00% | 100.0% | 0.0153 | 0.343 | 53.7 |

### Split `shift` (100 environments)

| Policy | Mean loss | Δ vs nominal [95% CI] | Rel. Δ [95% CI] | d_z | W/T/L (1%) | Worst rel. | Gap closed | Severe p | Human rate | CVaR95 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| nominal | 10.013 | +0.000 [+0.000, +0.000] | +0.00% [+0.00, +0.00] | +0.00 | 0/100/0 | +0.00% | 0.0% | 0.0321 | 0.358 | 82.3 |
| bayes_static | 10.089 | +0.076 [+0.001, +0.204] | +1.10% [+0.01, +3.00] | +0.14 | 0/97/3 | +82.82% | -7.7% | 0.0333 | 0.344 | 84.3 |
| robust_static | 10.120 | +0.107 [-0.323, +0.485] | +3.44% [+0.06, +6.93] | +0.05 | 19/45/36 | +81.03% | -10.8% | 0.0252 | 0.146 | 64.4 |
| plugin_recal | 9.834 | -0.179 [-0.502, +0.071] | -0.26% [-2.29, +1.71] | -0.12 | 16/68/16 | +54.30% | 18.0% | 0.0322 | 0.304 | 82.9 |
| bayes_recal | 9.813 | -0.200 [-0.528, +0.043] | -0.82% [-2.58, +0.73] | -0.13 | 18/63/19 | +27.22% | 20.1% | 0.0324 | 0.302 | 82.3 |
| ts_recal | 9.926 | -0.087 [-0.379, +0.143] | +0.42% [-1.38, +2.13] | -0.06 | 21/40/39 | +32.69% | 8.7% | 0.0323 | 0.326 | 82.1 |
| handoffx_v2 | 9.793 | -0.220 [-0.545, +0.017] | -1.06% [-2.76, +0.37] | -0.15 | 18/64/18 | +16.57% | 22.1% | 0.0320 | 0.305 | 82.8 |
| gate_static | 10.019 | +0.006 [-0.001, +0.018] | +0.06% [-0.01, +0.18] | +0.12 | 0/99/1 | +4.78% | -0.6% | 0.0323 | 0.358 | 82.3 |
| v2_iid | 10.454 | +0.441 [+0.012, +0.830] | +5.79% [+2.43, +9.05] | +0.21 | 14/37/49 | +47.23% | -44.4% | 0.0375 | 0.324 | 84.5 |
| oracle | 9.019 | -0.994 [-1.386, -0.658] | -7.87% [-10.12, -5.81] | -0.52 | 47/53/0 | +0.00% | 100.0% | 0.0155 | 0.395 | 49.1 |

### Split `original` (38 environments)

| Policy | Mean loss | Δ vs nominal [95% CI] | Rel. Δ [95% CI] | d_z | W/T/L (1%) | Worst rel. | Gap closed | Severe p | Human rate | CVaR95 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| nominal | 7.698 | +0.000 [+0.000, +0.000] | +0.00% [+0.00, +0.00] | +0.00 | 0/38/0 | +0.00% | 0.0% | 0.0132 | 0.569 | 39.7 |
| bayes_static | 7.648 | -0.050 [-0.149, +0.004] | -0.56% [-1.66, +0.04] | -0.17 | 2/36/0 | +0.70% | 19.5% | 0.0122 | 0.591 | 39.4 |
| robust_static | 7.968 | +0.270 [+0.085, +0.502] | +3.45% [+1.24, +6.18] | +0.40 | 0/28/10 | +28.92% | -105.7% | 0.0126 | 0.507 | 39.8 |
| plugin_recal | 7.781 | +0.083 [-0.095, +0.304] | +0.70% [-1.12, +2.80] | +0.13 | 3/30/5 | +24.39% | -32.6% | 0.0156 | 0.540 | 43.7 |
| bayes_recal | 7.756 | +0.058 [-0.105, +0.248] | +0.50% [-1.20, +2.35] | +0.10 | 3/32/3 | +22.67% | -22.8% | 0.0148 | 0.546 | 42.9 |
| ts_recal | 7.721 | +0.023 [-0.154, +0.240] | +0.01% [-1.81, +1.94] | +0.04 | 8/22/8 | +22.86% | -9.0% | 0.0149 | 0.556 | 40.8 |
| handoffx_v2 | 7.711 | +0.013 [-0.141, +0.194] | -0.10% [-1.61, +1.42] | +0.03 | 3/33/2 | +19.26% | -5.2% | 0.0138 | 0.571 | 41.1 |
| gate_static | 7.648 | -0.050 [-0.149, +0.004] | -0.56% [-1.66, +0.04] | -0.17 | 2/36/0 | +0.70% | 19.5% | 0.0122 | 0.591 | 39.4 |
| v2_iid | 8.076 | +0.378 [+0.161, +0.588] | +5.41% [+2.53, +8.39] | +0.55 | 1/22/15 | +27.08% | -148.1% | 0.0176 | 0.591 | 45.5 |
| oracle | 7.442 | -0.255 [-0.439, -0.100] | -2.98% [-5.00, -1.25] | -0.46 | 10/28/0 | +0.00% | 100.0% | 0.0098 | 0.624 | 35.9 |


## 4. When does adaptive HandoffX help? (pre-specified subgroups, test split)

| Subgroup | n | handoffx_v2 | share improved > 1% | share degraded > 1% | bayes_recal | plugin_recal |
|---|---:|---:|---:|---:|---:|---:|
| estimates calibrated | 58 | +0.92% | 0% | 19% | +0.57% | +0.96% |
| estimates biased | 142 | -1.03% | 18% | 6% | -1.12% | -0.76% |
| human effectiveness over-estimated | 50 | **-2.25%** | 34% | 4% | -2.43% | -1.45% |
| human effectiveness under-estimated | 60 | -0.56% | 12% | 5% | -0.70% | -0.69% |
| AI success over-estimated | 53 | -1.33% | 19% | 6% | -1.16% | -0.92% |
| AI success under-estimated | 54 | -0.94% | 19% | 9% | -1.38% | -0.72% |

Shift split: biased -1.20% (n = 91), out-of-model-support biases -2.16% (n = 57), calibrated +0.34% (n = 9), in-support +0.40% (n = 43).

**Favourable conditions:** systematically biased supplied estimates, especially an over-estimated human (the learner sees failed handoffs and stops escalating), and larger biases including ones outside the model grid. **Unfavourable conditions:** estimates that are already correct; then nominal is near-optimal and any learner can only drift, and under model misspecification it drifts confidently (CE9 in ADAPTIVE_POLICY_MATHEMATICS.md). Human under-estimation is learned slowly because a policy that rarely escalates rarely observes the human (Proposition A2).

## 5. Calibration

Mean absolute error of root first-attempt success probabilities (test): AI 0.084 -> 0.057 (-32%) and human 0.067 -> 0.052 (-22%) after 100 episodes for handoffx_v2; nearly identical for bayes_recal and plugin_recal (shift: AI 0.123 -> 0.082, human 0.116 -> 0.085). See CALIBRATION_RESEARCH.md.

## 6. Tail risk and escalation

Expected-loss policies did not reduce tail risk: on test, severe-failure probability 0.0149 (nominal) vs. 0.0158 (handoffx_v2), CVaR95 of realised episode loss 51.2 vs. 53.5; the learners escalate less (human rate 0.384 -> 0.320). The robust planner is the only policy that cut tail risk (severe 0.0130, CVaR95 46.1) at +7.3% mean loss. Choosing between them is a risk-preference decision, not something the benchmark settles.

## 7. Computation

Mean wall time per 100-episode stream (one process): nominal 0.04 s; bayes_recal 0.58 s; handoffx_v2 1.39 s (25 exact evaluations of the candidate per refresh). A single cached recommendation is in the microsecond range (v0.1 timing); a refresh is tens of milliseconds. Memory is dominated by the planner caches (v0.1 measured 0.3 MB peak Python allocation per planner).

## 8. Historical comparison with v0.1

Replaying the 38 original scenarios as 100-episode streams (diagnostic only; they were never used for tuning): bayes_static reproduces the v0.1 direction (-0.56%, 2 wins, 0 losses at 1%); handoffx_v2 is neutral (-0.10%, 3/33/2); 26 of the 38 are scenarios in which nominal is already the oracle.

## 9. Leakage checks

Disjoint seed ranges (dev 100000+, validation 200000+, test 300000+, shift 400000+); the protocol, configuration, scripts and adaptive module were hashed before the dev run (`benchmarks_v2/reproducibility/PRE_REGISTRATION_SHA256.txt`); the gate was frozen and committed before validation, validation committed before test and shift; test and shift were each run once. Git history records the order. The library's `Advisor` defaults are the frozen gate, set after the test run without changing the benchmark code.
