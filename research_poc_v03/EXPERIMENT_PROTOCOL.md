# Experiment protocol (frozen before any candidate run)

## Data separation

| Data | Seeds | Use |
|---|---|---|
| v0.2 dev environments | 100000+ | Stage C diagnostics only (already used for v0.2 tuning) |
| v0.2 validation/test/shift | 200000+, 300000+, 400000+ | **not used** in this study |
| PoC Round 1 (mechanism) | hand-built + 450000+ | sanity checks |
| PoC Round 2 (pilot) | 500000 + 1000·k + i | exploratory; may drop candidates; no tuning planned |
| PoC Round 3 (confirmation) | 600000 + 1000·k + i | run once after freezing; decides GO/NO-GO |

## Environment kinds (`scripts/poc_lib.py::poc_environment`)

Each environment starts from the v0.2 i.i.d. generator (`benchmarks_v2/scripts/common.py::draw_environment`) for costs, deadlines, human availability and supplied estimates; the hidden truth is then set per kind. Equal counts per kind; pooled results weight kinds equally.

| k | Kind | Truth | Why |
|---|---|---|---|
| 0 | calibrated | success, hazard and prevalence exactly as supplied | nominal is optimal; measures regression |
| 1 | success_bias | AI and human success biases U(−0.2, 0.2); prevalence exact | v0.2's target |
| 2 | prevalence_misspec | success exact; prevalence moved toward persistent or transient by U(0.1, 0.35) (sign random) plus Dirichlet(30) noise | correlated/persistent retry failures; incorrect persistence assumption |
| 3 | human_bias | human bias ±U(0.1, 0.25); AI bias U(−0.05, 0.05); prevalence exact | uncertain human effectiveness |
| 4 | mixed | v0.2 i.i.d. family as drawn | continuity with v0.2 |
| 5 | shift | v0.2 shift family as drawn (biases ±0.3, hazards ×1.5, persistence shift) | distribution shift |

## Policies (same supplied information, action guard, costs, horizon, common random numbers)

nominal; handoffx_v2 (frozen v0.2 gate); bayes_recal; ts_recal (full Thompson sampling: comparator for B); **A_prev**; **B_humants**; **C_bfguard**; oracle (diagnostic only). 100 episodes per stream, refresh every 5 episodes (B samples every episode, as ts_recal).

## Metrics

Primary: relative difference in per-environment mean exact episode loss vs. bayes_recal (paired). Secondary: vs. nominal and handoffx_v2; regret vs. oracle; success, human-escalation and severe-failure probabilities; unnecessary-retry proxy (retries per episode, realized); end-of-stream calibration error of root AI/human success; prevalence TV error (A); human observations (B); share of guarded episodes (C); seconds per stream. Intervals: 95% percentile bootstrap over environments (10,000 resamples, seed 11).

## Rounds

1. **Mechanism tests** (`scripts/round1_mechanism.py`): equivalence and concentration checks listed in HYPOTHESES.md; a candidate failing them is discarded.
2. **Pilot**: 12 environments per kind (72). Drop a candidate if its pooled point estimate is worse than bayes_recal by more than 0.25 pp **and** it shows no improvement in its targeted kinds. No hyperparameters will be tuned; if the pilot reveals a defect, the fix and its reason are logged before Round 3.
3. **Confirmation**: 50 environments per kind (300), surviving candidates and their combination, run once.

## Decision criteria (frozen)

Against bayes_recal on Round 3:

- **GO**: pooled mean relative difference ≤ −0.5% with 95% CI upper bound < 0; calibrated kind mean ≤ +0.5% vs. nominal and not worse than bayes_recal by > 0.25 pp; pooled severe-failure probability not > 10% (relative) above bayes_recal; ≤ 5× bayes_recal compute per stream; no privileged information.
- **CONDITIONAL GO**: pooled point estimate < 0 with CI including 0; or a CI-supported improvement ≥ 0.5% in the candidate's pre-specified target kinds (A: prevalence_misspec, shift; B: human_bias, success_bias; C: calibrated) with pooled CI upper bound ≤ +0.25%.
- **NO-GO**: otherwise.

Reference: −0.5% is about one quarter of the v0.2 nominal-to-oracle gap on held-out data (1.94%).

## Budget

Planned compute: pilot ≈ 5 min, confirmation ≈ 15 min on 16 CPU workers; well inside the 60–120 min budget.
