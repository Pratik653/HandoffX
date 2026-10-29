# Phase B root-cause analysis: why joint-Bayesian HandoffX v0.1 did not beat nominal planning

Source data: the frozen v0.1 configurations in `05_Experiments/configs/` (unchanged) and the reproduced v0.1 outputs. Script: `benchmarks_v2/scripts/root_cause.py`; outputs: `benchmarks_v2/results/root_cause/root_cause.json` and `root_cause_summary.csv`.

## 1. Reproduction

The full v0.1 study was rerun on Windows 11, Python 3.11.9, NumPy 2.3.5, SciPy 1.17.0 (the original ran on Linux, Python 3.13.5). All 418 raw episode arrays were bit-identical; all 418 summary rows, 228 paired-effect rows and 10,032 batch rows agreed with the stored files to at most 7.1e-15 (floating-point representation of the last digit). The v0.1 `audit_results.py` compares numbers as strings and therefore reports one such last-digit difference as a failure; numerically the reproduction is exact to machine precision. The reported 6 better / 23 equal / 9 worse comparison of `handoffx_bayes` against `nominal_dp` is reproduced. The original result files were restored from git after the rerun and are unmodified.

## 2. Method

For each scenario, with the true environment `truth`, the Bayes policy `B` and the nominal policy `N`, the exact loss difference is decomposed with the performance-difference identity

    L(B) - L(N) = sum over states s of d_B(s) * [ Q_N(s, B(s)) - Q_N(s, N(s)) ],

where `d_B(s)` is the true probability of visiting `s` under `B` and `Q_N(s, a)` is the true expected loss of taking `a` once and following `N` afterwards. The script verifies the identity to 1e-8 in every scenario, lists every state where the two policies act differently, and reports the supplied and true root success probabilities.

## 3. Findings

### 3.1 The 9 "losses" are small; the 6 wins include one large one

| Tolerance on exact loss difference | Better | Equal | Worse |
|---|---:|---:|---:|
| 1e-9 (v0.1 reporting) | 6 | 23 | 9 |
| 0.001 | 6 | 25 | 7 |
| 0.01 | 5 | 30 | 3 |
| 0.05 | 2 | 35 | 1 |

The nine losses sum to 0.136 loss units; the six wins sum to 2.033. The largest relative loss is +0.70% (`ai_calibrated__human_under`, the only loss whose paired 95% interval excludes zero); the largest win is -19.3% (`ai_under__human_under`). Win/tie/loss counts at tolerance 1e-9 overstate the practical difference.

### 3.2 Information asymmetry in favour of nominal planning (5 of 9 losses)

In 26 of the 38 scenarios nominal DP attains exactly the oracle loss, mostly because the supplied centre estimate equals the hidden truth (all calibrated sensitivity scenarios). In those scenarios no other policy can do better; the joint prior can only tie or lose by spreading mass over models that are not true. Five of the nine losses (`human_unavailable`, `weak_human`, `expensive_human`, `human_available_late`, `low_hazard__ai_calibrated__human_calibrated`) are of this kind, with relative losses of +0.01% to +0.05%. This is a property of the scenario design, not an implementation defect: a correctly specified point estimate is optimal and any spread prior is (mildly) misspecified.

### 3.3 The prior cannot correct a biased estimate within one episode (all bias-factorial cells)

In the factorial cells the joint prior is centred on the same biased estimate that nominal uses. At the root, the Bayes predictive success probabilities are almost identical to nominal (AI 0.570-0.704 vs. 0.574-0.719; human 0.655 vs. 0.655 when the human is under-estimated, while the truth is 0.835). Two structural facts prevent correction within an episode:

1. at most `horizon` (six) observations arrive, so the posterior over model offsets moves little;
2. human assistance is terminal, so human effectiveness is never observed before the decision to hand off (this is v0.1 counterexample CE6 applied to the planner itself).

Hence in `ai_calibrated__human_under` both policies refuse a human whose true success probability is 0.835 (oracle loss 7.515 vs. 9.31-9.37 for both); the Bayes policy additionally loses 0.065 because, after a soft failure (visit probability 0.019), posterior pessimism makes it retry where nominal escalates (true Q gap +3.25).

### 3.4 Where losses occur: rare, pessimistic post-failure states

Every remaining divergence occurs after one or two observed failures, at visit probabilities between 0.1% and 3.6%. After failures the posterior shifts toward pessimistic AI models, so the Bayes policy prefers stop/retry over continue (or retry over human) when the true environment favours the opposite. These are genuine decision trade-offs of a misspecified prior, not defects: the same mechanism produces the wins in `low_hazard__ai_over_*` (posterior pessimism is correct when the AI is truly overestimated, true Q gap -0.20 to -0.35).

### 3.5 Classification of causes

| Category | Finding |
|---|---|
| Genuine mathematical limitation | Within-episode non-identifiability of human effectiveness (terminal handoff) and of systematic bias with <= 6 observations |
| Incorrect assumptions | Prior centred on the biased estimate; prior spread is itself misspecified when the estimate is correct |
| Implementation defects | None found. Policies share the action guard, cost model and information; the performance-difference identity, oracle lower bound and robust envelope checks all hold |
| Poor calibration | Supplied estimates are biased by design in 24 of 38 scenarios and nothing in v0.1 can learn the bias |
| Objective mismatch | None for Bayes vs. nominal (both minimise expected loss); robust DP optimises a different (worst-case) objective, as v0.1 disclosed |
| Information asymmetry | Nominal is handed the exact truth in 26 of 38 scenarios |
| Over-conservatism | Post-failure posterior pessimism (Section 3.4) |
| Scenario-specific trade-off | Low-hazard cells where pessimism helps or hurts depending on bias sign |

## 4. Improvement opportunity identified

The decisive missing ingredient is **evidence across episodes**. Logged outcomes from earlier tasks can identify systematic AI and human bias, including human effectiveness once some handoffs have occurred. That motivates v0.2: a cross-episode posterior over the model index (C3), a conservative switch rule that keeps nominal planning unless the posterior supports a change (C1/C2), and a deployment-stream benchmark in which such learning is possible and fairly comparable (Phase E). Persistent failure modes (C4) were already modelled in v0.1; v0.2 tests whether removing them matters in the new setting.
