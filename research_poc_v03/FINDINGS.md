# Findings — HandoffX v0.3 feasibility study

All results are from synthetic simulations. Losses are artificial units. "vs bayes_recal" is the paired relative change in per-environment mean exact episode loss against ungated posterior recalibration, the strongest deployable v0.2 baseline. Pooled numbers weight the six environment kinds equally; intervals are kind-stratified 95% bootstrap intervals. Tables: `results/TABLES.md`; figure: `figures/effects_by_round.png`.

## 1. Baseline verification (Stage A)

The brief's v0.2 numbers match the stored held-out analysis exactly: v0.2 −0.46% [−1.07, +0.09] vs nominal; ungated −0.63%; oracle −1.94%; no failure dependence +5.79%; calibrated +0.92%, biased −1.03%. The in-loop baselines of this study reproduce the v0.2 runner bit for bit (max difference 0.0).

## 2. Where the headroom is (Stage C, v0.2 dev environments only)

- The model grid is **not** the bottleneck: the best single 5×5 grid model reaches −3.65% vs. the oracle's −3.70%.
- Almost all i.i.d. headroom comes from wrong success probabilities (−2.93% of −3.40%); wrong failure-mode prevalence alone explains −0.12% (but −3.18% under shift). Calibrated environments have no headroom (−0.05%).
- Ungated recalibration **stalls**: regret per 100 episodes 0.185 → 0.150 → 0.144 → 0.139 over 400 episodes, against about 0 for the best grid model. With the true prevalence equal to the supplied one the plateau drops to 0.09.
- 91% of the remaining plateau sits in 6 of 32 environments where the learner almost stops escalating while the oracle escalates: a self-confirming trap (v0.2 Proposition A2; incomplete learning, Harrison et al., 2012).
- A third trap appeared in Round 1: in some environments nominal planning **stops at the first step**, so no policy ever collects data.

## 3. Candidates and results

| | Pilot (n=72) | Confirmation (n=300) | Replication (n=300) |
|---|---|---|---|
| **A** prevalence-augmented learning | −0.92% [−1.97, −0.07] | **−0.52% [−0.88, −0.19]** | −0.25% [−0.71, +0.17] |
| **B** human-targeted posterior sampling | +0.08% [−0.92, +1.05] | **+0.53% [+0.16, +0.90]** | – |
| **C** Bayes-factor reversion guard | +0.41% [−0.73, +1.84] | −0.26% [−0.64, +0.09] | – |
| AC (A + C) | – | – | −0.12% [−0.51, +0.28] |
| ABC (pre-specified combination) | – | −0.52% [−0.95, −0.11] | −0.08% [−0.49, +0.32] |
| handoffx_v2 (reference) | −0.29% | −0.23% [−0.50, 0.00] | −0.29% [−0.54, −0.08] |
| full Thompson sampling (reference) | +0.16% | +0.89% [+0.45, +1.36] | – |
| oracle (diagnostic) | −2.45% | −2.58% | −2.42% |

### What worked

**A in its pre-specified target conditions and on tail risk.** In every independent round A lowered:
- loss in **shift** environments: −3.21% [−6.38, −1.06], −2.48% [−4.15, −1.09], −2.00% [−3.90, −0.54];
- **severe-failure probability** (all kinds) by 0.0027, 0.0020 and 0.0029 absolute (−13% to −17% relative; all intervals exclude 0);
- retries per episode (0.252 → 0.222; 0.237 → 0.197) and last-20-episode regret (0.218 → 0.145; 0.217 → 0.171).

A costs nothing computationally (1.03–1.05× bayes_recal).

**Mechanism.** The mechanism diagnostic (A's augmented prior without learning) was *worse* than bayes_recal (+0.74%, severe failures unchanged), so the benefit requires cross-task learning. A does **not** estimate prevalence better: end-of-stream prevalence error was 0.074 against 0.069 for the fixed supplied value. The extra parameter instead **absorbs misfit** that would otherwise distort the decision-relevant success offsets (the CE9 failure mode). This is decision success without predictive success on the nuisance parameter.

**C in calibrated environments.** C lowered loss vs. bayes_recal in calibrated environments (−0.58% [−1.10, −0.19]) and kept them at nominal performance (+0.03% vs. nominal). The Bayes factor stays near 0 when the estimate is right, as intended.

### What failed

- **A's pooled gain did not replicate.** It shrank from −0.92 to −0.52 to −0.25 (pilot, confirmation, replication). The prevalence-misspecified gain shrank from −1.5% to −0.3%. A remains worse than nominal in calibrated environments (+0.84%, +0.95%) and worse than bayes_recal when human effectiveness is biased (+0.60%, +0.59%). A plausible explanation, not tested: human kernels differ by latent mode, so a human bias can be partly "explained" by a prevalence shift. That confounds learning about the human.
- **B failed.** It was +0.53% worse on confirmation, including in its own target kind (human_bias +0.99%). Exploring only the human offset did not escape the escalation trap at a 100-episode horizon; exploration cost exceeded information value, as with full Thompson sampling.
- **C gives no pooled gain.** It delays acting on genuine bias (human_bias +0.84%), cancelling its calibrated-environment benefit.
- **Combinations did not add up.** AC and ABC had no pooled gain on replication; the guard and the prevalence flexibility partly cancel.

## 4. Statistical reading

- Pilot results were optimistic and regressed toward zero on fresh data, a winner's-curse pattern. Only effects seen in all three independent samples are treated as findings: A's shift-kind gain and A's severe-failure reduction.
- The largest credible pooled effect (A, confirmation) equals the GO threshold and is about 20% of the oracle gap; its replication interval includes zero.
- Nothing here measures real agents or people.

## 5. Other observations

- **Library robustness issue.** `EpisodeBelief.posterior_models()` raises `ModelError` if a model's posterior weight underflows to exactly 0, which can happen in long streams with decisive evidence. It was not triggered in any v0.2 or v0.3 run; it should be fixed (for example by flooring weights or dropping dead models) in any future release. No production code was changed in this study.
- **Compute used.** About 7 minutes on 16 CPU workers for all diagnostics, Round 1, the pilot (37 s), confirmation (128 s) and replication (73 s); far below the 60–120 minute budget.

## References

Harrison, J. M., Keskin, N. B., & Zeevi, A. (2012). Bayesian dynamic pricing policies: Learning and earning under a binary prior distribution. *Management Science, 58*(3), 570–586. https://doi.org/10.1287/mnsc.1110.1426

Kass, R. E., & Raftery, A. E. (1995). Bayes factors. *Journal of the American Statistical Association, 90*(430), 773–795. https://doi.org/10.1080/01621459.1995.10476572

Russo, D., & Van Roy, B. (2018). Learning to optimize via information-directed sampling. *Operations Research, 66*(1), 230–252. https://doi.org/10.1287/opre.2017.1663
