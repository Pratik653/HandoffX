---
title: "HandoffX v0.2"
subtitle: "When does adaptive, uncertainty-aware intervention beat nominal planning? Cross-episode calibration, conservative switching and a pre-registered held-out benchmark"
author: "Pratik653"
date: "October 29, 2026"
lang: en-US
---

# Abstract

Autonomous agents repeatedly face the choice to continue, retry, request human assistance or stop. HandoffX v0.1 compared exact finite-horizon policies for this choice in 38 synthetic scenarios and found that a joint-Bayesian planner was better than nominal planning in 6, equal in 23 and worse in 9. This report explains that result and tests a revised controller. A performance-difference decomposition shows that the nine losses were small (largest +0.70%, total 0.14 loss units against 2.03 for the wins), that nominal planning already attained the oracle loss in 26 scenarios, and that no within-episode method could correct a biased estimate because the prior was centred on the estimate and human effectiveness is observed only after a terminal handoff. HandoffX v0.2 therefore pools evidence across episodes: an exact posterior over a finite model set, valid under adaptive logging by ignorability, feeds a Bayes-adaptive planner, and a conservative gate keeps the nominal plan unless the posterior expected loss falls and the posterior probability of a degradation beyond a tolerance is at most alpha. A deployment-stream benchmark was specified and hashed before any run; the gate was tuned on 60 development environments, frozen, checked on 60 validation environments and evaluated once on 200 held-out test and 100 distribution-shifted environments of 100 episodes each. On the test split the controller reduced mean exact loss relative to nominal by 0.46% (95% bootstrap interval -1.07% to +0.09%; absolute difference -0.052, interval -0.110 to -0.002) and closed 30% of the gap to the oracle, which was itself only 1.94% better than nominal. Gains concentrated where estimates were biased (-1.03%; -2.25% when human effectiveness was over-estimated); the controller lost 0.92% where estimates were already calibrated. Ungated posterior planning was at least as good as the gated controller on test, so the gate is not shown to add value. Removing persistent-failure modelling raised loss by 5.8%, the largest effect observed. Under model misspecification the posterior can concentrate on a wrong model and the gate switches confidently; a counterexample is documented. All evidence is synthetic.

# Research integrity statement

This is an extension of the v0.1 study, which is reproduced unchanged as Part I. All v0.2 numbers come from committed result files in `benchmarks_v2/results/`; the protocol, environment generator, runner and adaptive module were hashed and committed before the first development run, and the held-out splits were run once. Negative results are reported. "Human" outcomes are simulated. Eight new references were verified against Crossref or PMLR metadata on 29 October 2026. No peer review has taken place.

# 15. Motivation for v0.2

The research question is conditional: under what information structures can an adaptive, uncertainty-aware controller make better intervention decisions than nominal sequential planning, and how can that be shown fairly? v0.1 answered part of it: persistent failure modes matter, robust envelopes can fail out of support, and a static joint prior is not generally helpful. It left open why joint-Bayesian planning did not help and whether any adaptive controller could, given equal information.

# 16. Why v0.1 joint-Bayesian planning did not beat nominal planning

The v0.1 study was rerun on Windows with Python 3.11: all 418 raw arrays were bit-identical and all summary values agreed to 7.1e-15. For each scenario, the exact loss difference between the Bayes policy B and nominal policy N was decomposed as

$$L(B)-L(N)=\sum_s d_B(s)\,[Q_N(s,B(s))-Q_N(s,N(s))],$$

where $d_B$ is the true visit probability under B and $Q_N$ the true value of acting once and then following N. The identity held to 1e-8 in every scenario.

*Magnitudes.* At tolerance 1e-9 the counts are 6/23/9; at 0.01 loss units 5/30/3; at 0.05, 2/35/1. Only one loss has a paired interval excluding zero (+0.70%).

*Information asymmetry.* Nominal DP attained the oracle loss in 26 of 38 scenarios, mostly because the supplied estimate was the truth. There, any spread prior can only tie or lose; five of the nine losses are of this kind (+0.01% to +0.05%).

*Non-identifiability within an episode.* In the bias factorial the prior is centred on the biased estimate; at the root the Bayes predictive human success was 0.655, identical to nominal, while the truth was 0.835. An episode yields at most six observations and human assistance is terminal, so the human estimate cannot move before the handoff decision (v0.1 CE6).

*Where the losses occur.* All remaining divergences arise after one or two failures, at visit probabilities of 0.1% to 3.6%, where posterior pessimism prefers stop or retry. The same mechanism produces the wins when the AI really is over-estimated.

No implementation defect was found. The missing ingredient is evidence across episodes.

# 17. Cross-episode formulation

The within-episode model of Part I (FM-01 to FM-09) is unchanged. A deployment is a sequence of episodes sharing a fixed model index $m^*$ from a finite set $M$; each episode draws a latent failure mode $z_e \sim \pi(\cdot\mid m^*)$, fixed within the episode. Episode $e$ yields a trajectory $\tau_e$ of action-outcome pairs. Actions may depend on earlier trajectories, the current history and independent randomisation, but not on $m^*$ or $z_e$.

**Proposition A1 (ignorable sequential design).** The posterior over the model index after $E$ episodes is

$$w_E(m)\propto w_0(m)\prod_{e=1}^{E}\sum_{z}\pi(z\mid m)\prod_{(a,o)\in\tau_e}k(o\mid m,z,a).$$

The action-choice probabilities do not depend on $m$ and cancel, which is the ignorability argument of Rubin (1976): logging that escalates only on observed data needs no propensity correction, and unobserved counterfactual outcomes need no imputation. Sequential and batch updates agreed to 4.8e-15.

**Proposition A2 (no learning without the action).** If two models differ only in the kernel of an action that was never taken, their posterior ratio equals their prior ratio. Consequently a deployment that never escalates never learns the human's effectiveness: this is an exploration problem.

**Conservative switching.** Let $\pi_0$ be nominal DP and $\pi_c$ the Bayes-adaptive DP with prior $w$. For each model $m$ let $\Delta_m = L_m(\pi_0)-L_m(\pi_c)$, computed exactly. The gate deploys $\pi_c$ for the next five episodes if and only if

$$E_w[\Delta]>0 \quad\text{and}\quad P_w(\Delta<-\tau)\le\alpha,$$

with $\tau$ a fraction of the incumbent's posterior expected loss. This follows the logic of high-confidence and safe policy improvement (Thomas et al., 2015; Laroche et al., 2019) but is a posterior statement within a finite model set, not a frequentist guarantee.

**Proposition A3.** The Bayes-adaptive candidate has non-negative posterior advantage, and the gate never increases posterior expected loss (checked: minimum advantage 0.0 and maximum risk increase 0.0 over 30 random environments).

**Proposition A4.** If the gate switches, the posterior probability of a degradation larger than $\tau$ is at most $\alpha$; with $\alpha=0$ and $\tau=0$ it switches only under weak dominance on every supported model; with $\alpha=1$ it reduces to posterior-risk minimisation.

**Counterexample CE9 (misspecification).** Under misspecification the posterior concentrates on the models closest in Kullback-Leibler divergence (Berk, 1966), not on those closest in decision loss. In held-out test environment 300120 the success and hazard estimates were exact, so nominal was optimal, but the persistent-mode prevalence was 0.45 against an estimated 0.31. The grid cannot represent prevalence, so the posterior moved to a wrong human-success offset (-0.10), the gate switched in 80 of 100 episodes and true loss rose by 13.2%. A posterior predictive check (Box, 1980) or a richer model set are the natural remedies; neither was evaluated.

# 18. Experimental methodology

**Environments.** Each environment draws supplied estimates around the v0.1 base parameters (success perturbations U(-0.04, 0.04), hazard multiplier log-uniform on [0.2, 1.5], Dirichlet mode prevalence), a hidden truth that is exactly calibrated with probability 0.25 and otherwise has independent AI and human success biases U(-0.2, 0.2), and task costs, deadlines (4 to 6 steps), human delays and availability. The shift family uses biases U(-0.3, 0.3) that can fall outside the model support, 1.5 times the hazards and more persistent failures.

**Model set.** A 5 x 5 grid of AI and human success offsets {-0.2, -0.1, 0, 0.1, 0.2} with three latent modes; prior weights proportional to (0.1, 0.2, 0.4, 0.2, 0.1) on each axis. Nominal planning uses the centre model.

**Policies.** nominal; bayes_static and robust_static (v0.1 analogues); plugin_recal (plan on the maximum-a-posteriori model); bayes_recal (ungated posterior planning); ts_recal (Thompson sampling, Thompson, 1933; Russo et al., 2018); handoffx_v2 (gated); gate_static (gate on the prior only); v2_iid (handoffx_v2 without persistent modes); oracle. All share the supplied information, the action guard, the cost model and common random numbers.

**Streams and metrics.** 100 episodes per environment; learning policies refresh every 5 episodes. The primary metric is the per-environment mean exact expected episode loss. Secondary metrics include severe-failure probability, human-escalation rate, success, empirical CVaR95 of realised loss (Rockafellar & Uryasev, 2000), calibration error and wall time. Inference uses paired environment-level bootstrap intervals (10,000 resamples), standardized effects and win/tie/loss counts at a 1% practical tolerance.

**Splits.** Development (60 environments, gate grid of 6 alpha x 3 tolerance values), validation (60), test (200) and shift (100) use disjoint seed ranges. The gate was selected by a pre-registered rule, committed, then validated; test and shift were run once afterwards. The 38 v0.1 scenarios were replayed for diagnosis only.

# 19. Results

**Gate selection.** On development data the trade-off was monotone; the rule selected alpha = 0.35 and tolerance 3% (-1.55%, 3.3% of environments degraded by more than 1%).

**Validation.** handoffx_v2 -0.16% [-0.84, +0.39]; ungated bayes_recal +0.60% [-0.40, +1.65]. The development gain did not replicate in magnitude.

**Held-out test (primary, n = 200).**

| Policy | Mean loss | Relative change vs. nominal [95% CI] | W/T/L at 1% | Worst | Gap closed |
|---|---:|---:|---:|---:|---:|
| nominal | 7.573 | 0 | 0/200/0 | 0 | 0% |
| bayes_static | 7.569 | +0.16% [-0.30, +0.69] | 6/187/7 | +33.7% | 2% |
| robust_static | 8.013 | +7.26% [+4.87, +9.86] | 19/86/95 | +126% | -254% |
| plugin_recal | 7.541 | -0.26% [-0.76, +0.19] | 21/161/18 | +13.0% | 19% |
| bayes_recal | 7.509 | -0.63% [-1.28, -0.05] | 28/152/20 | +13.2% | 37% |
| ts_recal | 7.607 | +0.66% [+0.06, +1.23] | 22/111/67 | +18.8% | -20% |
| handoffx_v2 | 7.521 | -0.46% [-1.07, +0.09] | 26/155/19 | +22.1% | 30% |
| gate_static | 7.559 | -0.14% [-0.37, -0.01] | 3/197/0 | +0.7% | 8% |
| v2_iid | 7.981 | +5.79% [+4.37, +7.22] | 13/84/103 | +44.2% | -236% |
| oracle | 7.400 | -1.94% [-2.69, -1.29] | 48/152/0 | 0 | 100% |

Over the last 20 episodes, regret relative to the oracle fell from 0.173 (nominal) to 0.095 for both handoffx_v2 and bayes_recal.

**Shift (n = 100).** handoffx_v2 -1.06% [-2.76, +0.37], bayes_recal -0.82%, plugin_recal -0.26%, oracle -7.87%. Biases outside the model support: -2.16% (n = 57).

**Subgroups (test, pre-specified).** Calibrated estimates +0.92% (19% of environments degraded); biased -1.03%; human over-estimated -2.25% (34% improved); human under-estimated -0.56%; AI over-estimated -1.33%; AI under-estimated -0.94%.

**Calibration.** Mean absolute error of root success probabilities fell from 0.084 to 0.057 (AI) and 0.067 to 0.052 (human) over 100 episodes.

**Tail risk.** Severe-failure probability: nominal 0.0149, handoffx_v2 0.0158, robust 0.0130; CVaR95 of realised loss 51.2, 53.5 and 46.1.

**Computation.** Per 100-episode stream: nominal 0.04 s, bayes_recal 0.58 s, handoffx_v2 1.39 s on one CPU core.

**Protocol criteria.** Mean improvement on test: yes in absolute terms, not significant in relative terms. Environments degraded by more than 1%: 9.5% (threshold 10%). Not dominated by point-estimate recalibration; effectively matched or beaten by ungated posterior planning.

# 20. Ablations

Cross-episode calibration carries most of the benefit (gate_static: -0.14%). Joint uncertainty helps relative to a point estimate (37% versus 19% of the gap closed). Persistent-failure modelling is essential (+5.8% without it, on every split). Exploration by posterior sampling was harmful at this horizon. The gate is not shown to change average performance; it delays switching. Robust planning trades mean loss for tail risk.

# 21. Controlled agent demonstration

A deterministic rule-based agent investigates delayed orders in SQLite with a carrier tool subject to injected timeouts, outages (HTTP 503) and permission errors (HTTP 403). It calls the HandoffX `Advisor` before each step and logs each task. The human helper is simulated (85% resolution). The advisor continues through timeouts and escalates after repeated hard errors. In an illustrative comparison over 200 simulated tasks and three seeds, mean loss was 3.43, 3.05 and 3.16 for HandoffX, 3.47, 3.63 and 3.55 for retry-twice-then-escalate, and about 6 for always-continue. This demonstrates integration and behaviour, not real-world effectiveness.

# 22. Software

The `handoffx` package (v0.2.0, MIT licence, NumPy only) adds `Advisor.from_estimates(...)`, `recommend(history, human_available, forbidden)` returning an explained `Recommendation`, `record_episode(...)` for cross-episode calibration, a command-line interface, and the research-level `EpisodeBelief` and `AdaptiveController`. 84 automated tests pass.

# 23. Discussion and limitations

The answer to the research question is conditional. Adaptive intervention helps when supplied success estimates are systematically wrong and logged outcomes can reveal it, most clearly when human help has been over-estimated. It does not help when estimates are already right, and it can hurt when the model set is misspecified in a direction it cannot represent. The gain over nominal planning is bounded by a small oracle gap on the tested distribution. Simpler policies are preferable when estimates are known to be calibrated (nominal) or when tail risk dominates (robust planning). The conservative gate, the component most likely to be presented as a safety feature, did not show a measurable average benefit, and its credible statement fails under misspecification. All evidence is synthetic; there is no real-agent, cross-model or human-subject validation.

# 24. Conclusions and future research

HandoffX v0.2 contributes a diagnosis of the v0.1 result, an exact cross-episode calibration layer, a pre-registered held-out deployment benchmark and an honest characterisation of when adaptive intervention is worth it. Priorities for future work are model sets that include failure-mode prevalence and hazards, posterior predictive checks that revert to the incumbent, costed information-gathering actions, and evaluation with real agent logs and real operators.

# References (new in v0.2)

Berk, R. H. (1966). Limiting behavior of posterior distributions when the model is incorrect. *The Annals of Mathematical Statistics, 37*(1), 51-58. https://doi.org/10.1214/aoms/1177699597

Box, G. E. P. (1980). Sampling and Bayes' inference in scientific modelling and robustness. *Journal of the Royal Statistical Society: Series A (General), 143*(4), 383-430. https://doi.org/10.2307/2982063

Laroche, R., Trichelair, P., & Tachet des Combes, R. (2019). Safe policy improvement with baseline bootstrapping. In *Proceedings of the 36th International Conference on Machine Learning* (Vol. 97, pp. 3652-3661). PMLR. https://proceedings.mlr.press/v97/laroche19a.html

Rockafellar, R. T., & Uryasev, S. (2000). Optimization of conditional value-at-risk. *Journal of Risk, 2*(3), 21-41. https://doi.org/10.21314/JOR.2000.038

Rubin, D. B. (1976). Inference and missing data. *Biometrika, 63*(3), 581-592. https://doi.org/10.1093/biomet/63.3.581

Russo, D. J., Van Roy, B., Kazerouni, A., Osband, I., & Wen, Z. (2018). A tutorial on Thompson sampling. *Foundations and Trends in Machine Learning, 11*(1), 1-96. https://doi.org/10.1561/2200000070

Thomas, P., Theocharous, G., & Ghavamzadeh, M. (2015). High confidence policy improvement. In *Proceedings of the 32nd International Conference on Machine Learning* (Vol. 37, pp. 2380-2388). PMLR. https://proceedings.mlr.press/v37/thomas15.html

Thompson, W. R. (1933). On the likelihood that one unknown probability exceeds another in view of the evidence of two samples. *Biometrika, 25*(3-4), 285-294. https://doi.org/10.2307/2332286

References cited in Part I are listed in the Part I reference section.

# Figures (v0.2)

![Learning curves on the held-out test split: mean exact loss minus oracle by episode (10-episode moving average).](../benchmarks_v2/figures/v2_learning_curves_test.png){width=6.2in}

![Per-environment relative loss versus nominal on the held-out test split.](../benchmarks_v2/figures/v2_relative_loss_test.png){width=6.2in}

![Gate trade-off on the development split.](../benchmarks_v2/figures/v2_gate_tradeoff_dev.png){width=5.5in}
