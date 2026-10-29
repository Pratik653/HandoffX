# 10. Study I: original benchmark results

The results in this section are reported exactly as in the original study (v0.1, 28 October 2026). Every numerical value was reproduced bit for bit on a later Windows rerun: all 418 raw arrays were identical and all summary values agreed to $7.1\times10^{-15}$. Sections 11 and 15 explain how later studies refine their interpretation.

<<v01|## 9.1. Execution and the primary comparison|# 10. Python architecture and implemented functionality|0|keepstart|sec=9:10>>

# 11. Study II: adaptive learning experiments

## 11.1. Why joint-Bayesian planning did not beat nominal planning

<<v2|# 16. Why v0.1 joint-Bayesian planning did not beat nominal planning|# 17. Cross-episode formulation>>

## 11.2. Gate selection and validation

On development data the trade-off between average gain and the share of degraded environments was monotone. The pre-registered rule selected $\alpha=0.35$ and tolerance 3%, giving −1.55% with 3.3% of environments degraded by more than 1%. On validation the gain shrank:
- handoffx_v2: −0.16% [−0.84, +0.39];
- ungated bayes_recal: +0.60% [−0.40, +1.65].

The development gain did not replicate in magnitude.

## 11.3. Held-out test results

**Table {T:v2test}.** *Held-out test split (n = 200 environments, 100 episodes each): relative change in mean exact loss versus nominal planning, with paired 95% bootstrap intervals*

| Policy | Mean loss | Relative change vs nominal [95% CI] | W/T/L at 1% | Worst | Gap closed |
|---|---:|---:|---:|---:|---:|
| nominal | 7.573 | 0 | 0/200/0 | 0 | 0% |
| bayes_static | 7.569 | +0.16% [−0.30, +0.69] | 6/187/7 | +33.7% | 2% |
| robust_static | 8.013 | +7.26% [+4.87, +9.86] | 19/86/95 | +126% | −254% |
| plugin_recal | 7.541 | −0.26% [−0.76, +0.19] | 21/161/18 | +13.0% | 19% |
| bayes_recal | 7.509 | −0.63% [−1.28, −0.05] | 28/152/20 | +13.2% | 37% |
| ts_recal | 7.607 | +0.66% [+0.06, +1.23] | 22/111/67 | +18.8% | −20% |
| handoffx_v2 | 7.521 | −0.46% [−1.07, +0.09] | 26/155/19 | +22.1% | 30% |
| gate_static | 7.559 | −0.14% [−0.37, −0.01] | 3/197/0 | +0.7% | 8% |
| v2_iid | 7.981 | +5.79% [+4.37, +7.22] | 13/84/103 | +44.2% | −236% |
| oracle | 7.400 | −1.94% [−2.69, −1.29] | 48/152/0 | 0 | 100% |

*Note.* "Gap closed" is the share of the nominal-to-oracle loss gap removed. W/T/L counts environments improved, tied and degraded by more than 1%.

The gated controller changed mean exact loss by −0.46%. Its 95% interval (−1.07% to +0.09%) includes zero; the absolute difference was −0.052 loss units, interval −0.110 to −0.002. The relative and absolute intervals differ because relative changes are averaged per environment. The controller closed 30% of a nominal-to-oracle gap that was itself only 1.94%. Over the last 20 episodes, regret relative to the oracle fell from 0.173 (nominal) to 0.095 for both handoffx_v2 and bayes_recal.

![Figure {F:v2curves}. Learning curves on the held-out test split: mean exact loss minus oracle loss by episode (10-episode moving average).](../benchmarks_v2/figures/v2_learning_curves_test.png){width=6.0in}

![Figure {F:v2rel}. Per-environment relative loss versus nominal planning on the held-out test split.](../benchmarks_v2/figures/v2_relative_loss_test.png){width=6.0in}

## 11.4. Shift, subgroups, calibration, risk and computation

- **Shift split (n = 100).**
  - handoffx_v2: −1.06% [−2.76, +0.37];
  - bayes_recal: −0.82%;
  - plugin_recal: −0.26%;
  - oracle: −7.87%;
  - environments whose biases fell outside the model support (n = 57): −2.16%.
- **Pre-specified subgroups (test split).**
  - calibrated estimates: +0.92%, with 19% of these environments degraded;
  - biased estimates: −1.03%;
  - human over-estimated: −2.25%, with 34% improved;
  - human under-estimated: −0.56%;
  - AI over-estimated: −1.33%;
  - AI under-estimated: −0.94%.
- **Calibration.** Over 100 episodes, the mean absolute error of root success probabilities fell from 0.084 to 0.057 for AI and from 0.067 to 0.052 for the human.
- **Tail risk.**
  - severe-failure probability: nominal 0.0149, handoffx_v2 0.0158, robust 0.0130;
  - CVaR95 of realized loss: 51.2, 53.5 and 46.1 respectively.
- **Computation**, per 100-episode stream on one CPU core: nominal 0.04 s, bayes_recal 0.58 s, handoffx_v2 1.39 s.
- **Protocol criteria.**
  - The mean improvement on test held in absolute terms but was not significant in relative terms.
  - 9.5% of environments were degraded by more than 1%, within the 10% threshold.
  - The controller was not dominated by point-estimate recalibration, but was matched or beaten by ungated posterior planning.

![Figure {F:v2gate}. Gate trade-off on the development split.](../benchmarks_v2/figures/v2_gate_tradeoff_dev.png){width=5.2in}

## 11.5. Ablations

- **Cross-episode calibration carries most of the benefit.** The gate on the prior alone (gate_static) gave −0.14%.
- **Joint uncertainty helps relative to a point estimate**: 37% versus 19% of the gap closed.
- **Persistent-failure modelling is essential.** Removing it raised loss by 5.8% on every split, the largest effect observed in Study II.
- **Exploration by posterior sampling was harmful** at this horizon.
- **The gate is not shown to change average performance**; it delays switching.
- **Robust planning trades mean loss for tail risk.**

## 11.6. Interpretation and refinement of Study I

Study II refines, but does not overturn, Study I:
- The 6/23/9 counts stand as reported. Study II shows the nine losses were small, the largest +0.70%.
- Five of the nine losses arose where nominal planning was already optimal.
- Within one episode, no method could correct an estimate the prior was centred on.

Adaptive intervention helps when supplied success estimates are systematically wrong and logged outcomes can reveal it, most clearly when human help has been over-estimated. It does not help when estimates are already right. It can hurt when the model set is misspecified in a direction it cannot represent (CE9). The conservative gate, the component most likely to be presented as a safety feature, showed no measurable average benefit.
