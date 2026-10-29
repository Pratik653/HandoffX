# HandoffX v0.2: mathematics of cross-episode calibration and conservative switching

Established results are attributed; v0.2 adaptations are labelled. Numerical checks: `benchmarks_v2/scripts/validate_v2_mathematics.py` -> `benchmarks_v2/results/mathematical_checks_v2.json` (all passed, maximum error 4.8e-15) and `04_Python_Library/tests/test_adaptive.py`.

## 1. Model (extends v0.1 FM-01 to FM-09)

- Within-episode model: unchanged from v0.1. Actions a in {C (continue), R (retry), H (human), S (stop)}; outcomes o in {0 success/progress, 1 severe, 2 soft failure, 3 hard-signal failure}; H and S are terminal; finite horizon T; losses as in v0.1 FM-03.
- Finite model set M = {1..K}. Model m has latent modes z in Z with conditional prevalence pi(z | m) and kernels k(o | m, z, a). In the v0.2 benchmark K = 25 (a 5 x 5 grid of AI and human success offsets around the supplied estimate) and |Z| = 3 (transient, intermediate, persistent failure).
- **Episode structure (new).** A deployment is a sequence of episodes e = 1, 2, .... The model index m* is fixed across the deployment; the latent mode z_e is drawn independently in each episode from pi(. | m*); within an episode z_e is fixed (v0.1 assumption).
- Data: episode e yields a trajectory tau_e = ((a_1, o_1), ..., (a_n, o_n)), n <= T, without the stop action, which produces no outcome.
- Policy information: the action at step t of episode e may depend on tau_1, ..., tau_{e-1}, the current-episode history, and independent randomisation (e.g. Thompson sampling). It may not depend on m* or z_e.

## 2. Cross-episode posterior

**Proposition A1 (ignorable sequential design; adaptation of Rubin, 1976).** Under the assumptions above, the posterior over the model index after E episodes is

    w_E(m)  proportional to  w_0(m) * prod_{e=1..E} sum_z pi(z | m) prod_{(a,o) in tau_e} k(o | m, z, a).

*Proof.* The joint probability of all actions and outcomes factorises into terms P(a_t | past data, randomisation), which do not involve m, and outcome terms k(o_t | m, z_e, a_t). Integrating each z_e independently gives the bracketed episode marginal. Terms not involving m cancel on normalisation. The policy terms are exactly why the action-selection mechanism is ignorable (Rubin, 1976): no reweighting for the data-dependent choice of actions is required, and unobserved counterfactual outcomes need no imputation. QED.

*Checks.* Sequential and batch updates agree to 4.8e-15; update order changes nothing (1.9e-16); the episode likelihood equals the direct sum (test).

*Meaning.* This is what handles selection bias from "humans are only consulted when the policy escalates": as long as escalation decisions depend only on logged data, the posterior is valid without propensity weighting. It fails if escalation also depended on information not logged (for example an operator's private judgement); see LIMITATIONS.md.

**Proposition A2 (no learning without the action; formalises v0.1 CE6 for the planner).** If models m and m' have identical mode prevalences and identical kernels for every action except a, and a was never taken in the observed data, then w_E(m) / w_E(m') = w_0(m) / w_0(m').

*Proof.* Every factor in A1 other than the prior is identical for m and m'. QED.

*Checks.* Over 25 episodes without a handoff, ratios within each fixed-AI group stayed at their prior ratios to 1.3e-15; with only handoffs, AI offsets keep their prior ratios (unit test).

*Meaning.* Two consequences. (i) Within one episode, human effectiveness is never learned before handing off, which is the main reason v0.1 joint-Bayes could not correct a biased human estimate (ROOT_CAUSE_ANALYSIS.md 3.3). (ii) Across episodes, a policy that never escalates never learns that escalation would have been better. That is an exploration problem; v0.2 tested Thompson sampling (Thompson, 1933; Russo et al., 2018) for it (Section 5).

## 3. Conservative switching rule (v0.2 adaptation)

Let pi_0 be the incumbent (nominal DP on the supplied estimate) and pi_c a candidate built from the posterior (v0.2: exact Bayes-adaptive DP with w_E as the model prior). For each model m let L_m(pi) be the exact expected episode loss of pi under model m (computed by exact evaluation, v0.1 P5), and Delta_m = L_m(pi_0) - L_m(pi_c). With posterior w = w_E, the gate deploys pi_c for the next `cadence` episodes iff

    E_w[Delta] > margin   and   P_w( Delta < -tol ) <= alpha,

otherwise it keeps pi_0. With `relative=True`, tol and margin are fractions of E_w[L(pi_0)]. The frozen v0.2 setting is alpha = 0.35, tol = 0.03 relative, margin = 0 (selected on the development split only).

This is in the spirit of safe/high-confidence policy improvement (Thomas et al., 2015; Laroche et al., 2019), with an important difference: those methods give frequentist guarantees from data under a fixed MDP class; the HandoffX gate makes a **posterior** statement inside a finite, possibly misspecified model set.

**Proposition A3 (posterior-risk monotonicity).** (a) If pi_c is the Bayes-adaptive DP policy for prior w, then E_w[Delta] >= 0. (b) For any margin >= 0, the deployed policy has posterior expected loss no larger than the incumbent's.

*Proof.* (a) Exact DP on the sufficient count state with prior w minimises E_w[L_m(pi)] over all history-dependent policies with the same admissible actions (v0.1 P5); pi_0 is such a policy. (b) The gate switches only when E_w[Delta] > margin >= 0. QED.

*Checks.* Over 30 random environments and posteriors: minimum posterior advantage 0.0, maximum posterior risk increase of the gate 0.0.

**Proposition A4 (credible degradation statement and boundary cases).** If the gate switches, then under the posterior w, P_w(L_m(pi_c) > L_m(pi_0) + tol) <= alpha. With alpha = 0 and tol = 0 it switches only if pi_c weakly dominates pi_0 on every model with positive posterior weight. With alpha = 1 and margin = -inf it reduces to posterior-risk minimisation over {pi_0, pi_c} (ungated `bayes_recal`).

*Proof.* Direct from the rule. QED. *Checks.* 0 dominance violations in 30 environments at alpha = 0.

*What A4 does not say.* It is not a frequentist bound on the true environment. If the truth is not in M, the posterior concentrates on the models closest in Kullback-Leibler divergence (Berk, 1966), which need not be the models closest in decision loss. The gate then becomes *more* confident precisely when it is wrong.

**Counterexample CE9 (observed on held-out test environment 300120).** The supplied success and hazard estimates are exactly correct (bias 0), so nominal DP is optimal, but the true persistent-mode prevalence is 0.45 against an estimated 0.31 (transient 0.20 vs. 0.20; intermediate 0.35 vs. 0.49). Mode prevalence is not a free parameter of the grid, so the posterior accommodates the extra persistent failures by moving to a wrong success offset (final MAP model: AI +0.00, human -0.10, weight 0.43); the gate's within-model degradation probability falls below alpha and it switches in 80 of 100 episodes. True loss rises 13.2% above nominal, which here equals the oracle. The same mechanism produces the largest degradations in the calibrated subgroup (EXPERIMENTAL_RESULTS.md). Remedy candidates (not evaluated): model sets that include prevalence and hazard parameters, or a posterior predictive check against held-out outcomes (Box, 1980) that reverts to the incumbent when the model set is rejected.

## 4. Persistent failure (C4)

v0.1 P4 and CE3 already show that an iid model over-estimates retry recovery under a persistent mixture. In v0.2 the ablation `v2_iid` replaces both the belief model and planner by their iid-mode counterparts (one-step marginals preserved). The ablation is large and consistent on every split (+5.4% to +5.8% loss vs. nominal; ABLATION_ANALYSIS.md), the strongest single effect in the study.

## 5. Exploration (C5, partial)

Posterior (Thompson) sampling of a grid model per episode (`ts_recal`) is the standard remedy for the exploration problem in A2. In this setting it was harmful on the i.i.d. test split (+0.66%, 67 of 200 environments degraded by > 1%): with 100 episodes and a coarse 25-model grid, the cost of acting on implausible sampled models exceeds the information gained. No explicit value-of-information or probe action was added to the model; v0.1 P9 (free information cannot increase optimal Bayes loss) remains the only VOI result, and costly observation actions remain future work.

## 6. Risk (C6)

Expected loss remains the objective. Severe-failure probability and empirical CVaR95 of realised episode loss (Rockafellar & Uryasev, 2000) are reported for every policy. The history-rectangular robust planner trades mean loss for tail risk: on the test split it raised mean loss by 7.3% but lowered severe-failure probability (0.0130 vs. 0.0149) and CVaR95 (46.1 vs. 51.2). Mandatory authorisation constraints remain outside the optimisation (v0.1 `ActionGuard`); the optional per-action severe-risk cap of v0.1 P7 is unchanged.

## 7. Claim ceiling

Established here: A1-A4 (elementary, with checks) and CE9. Not established: any frequentist improvement guarantee, regret bounds for the deployment stream, consistency under misspecification beyond Berk's (1966) KL-projection result, or optimality of the gate hyperparameters outside the benchmark distribution.

## References

Berk, R. H. (1966). Limiting behavior of posterior distributions when the model is incorrect. *The Annals of Mathematical Statistics, 37*(1), 51-58. https://doi.org/10.1214/aoms/1177699597

Box, G. E. P. (1980). Sampling and Bayes' inference in scientific modelling and robustness. *Journal of the Royal Statistical Society: Series A (General), 143*(4), 383-430. https://doi.org/10.2307/2982063

Laroche, R., Trichelair, P., & Tachet des Combes, R. (2019). Safe policy improvement with baseline bootstrapping. In *Proceedings of the 36th International Conference on Machine Learning* (Vol. 97, pp. 3652-3661). PMLR. https://proceedings.mlr.press/v97/laroche19a.html

Rockafellar, R. T., & Uryasev, S. (2000). Optimization of conditional value-at-risk. *Journal of Risk, 2*(3), 21-41. https://doi.org/10.21314/JOR.2000.038

Rubin, D. B. (1976). Inference and missing data. *Biometrika, 63*(3), 581-592. https://doi.org/10.1093/biomet/63.3.581

Russo, D. J., Van Roy, B., Kazerouni, A., Osband, I., & Wen, Z. (2018). A tutorial on Thompson sampling. *Foundations and Trends in Machine Learning, 11*(1), 1-96. https://doi.org/10.1561/2200000070

Thomas, P., Theocharous, G., & Ghavamzadeh, M. (2015). High confidence policy improvement. In *Proceedings of the 32nd International Conference on Machine Learning* (Vol. 37, pp. 2380-2388). PMLR. https://proceedings.mlr.press/v37/thomas15.html

Thompson, W. R. (1933). On the likelihood that one unknown probability exceeds another in view of the evidence of two samples. *Biometrika, 25*(3-4), 285-294. https://doi.org/10.2307/2332286
