# 9. Experimental findings

## 9.1. Execution and the primary comparison

The main study evaluated 38 scenarios and 11 policies using 24 independent seed batches of 500 episodes per scenario-policy cell: 12,000 trajectories per cell and 5,016,000 scenario-policy executions. Policies shared common random numbers, so that total is not a count of mutually independent tasks. Exact finite-model expectations were computed for every cell. The selected confidence threshold was 0.50 and the retry limit was two, based on four separate development environments.

Relative to nominal dynamic programming, the joint-Bayesian reference policy had lower exact loss in six scenarios, equal loss within 1e-9 in 23, and higher loss in nine. The greatest improvement was 1.793531 loss units and the greatest degradation was 0.065293. Some differences were numerically small. The count of designed environments favoring a policy is descriptive; it is not an estimate of its probability of winning on a real task population.

| Comparator | Bayes lower loss | Equal | Bayes higher loss | Mean exact difference over this design |
|---|---:|---:|---:|---:|
| nominal_dp | 6 | 23 | 9 | -0.049937 |
| robust_dp | 18 | 20 | 0 | -0.319987 |
| static_loss | 13 | 23 | 2 | -0.408122 |
| bayes_independent | 1 | 31 | 6 | 0.003084 |
| bayes_iid | 15 | 23 | 0 | -0.394996 |
| oracle | 0 | 22 | 16 | 0.205554 |

Negative differences favor the joint-Bayesian policy. The mean gives each deliberately selected scenario equal weight; it has no real-world prevalence interpretation. Robust planning optimizes a different worst-case objective, evaluated separately below. The oracle comparison confirms that extra modeled uncertainty cannot outperform the correctly specified full-information-of-the-model benchmark in expected loss.

**Figure 1**

*Paired differences from nominal planning in every scenario with a nonzero exact difference.*

![](../05_Experiments/figures/figure_01_paired_effects.png){width=6.2in}

Note. Crosses are exact expectations. Points and bars are simulated paired means and pointwise 95% t intervals across 24 seed batches. The other 23 scenarios have equal exact loss. Intervals quantify conditional simulation variability, not uncertainty about real model capability.

## 9.2. Illustrative improvements and degradations

| Scenario | Exact Bayes minus nominal | Paired estimate | 95% paired interval |
|---|---:|---:|---:|
| Both capability estimates low | -1.793531 | -1.790950 | [-2.122071, -1.459829] |
| Human estimate low; AI calibrated | 0.065293 | 0.087875 | [0.026344, 0.149406] |
| Low hazard; human estimate high | -0.148622 | -0.142971 | [-0.229442, -0.056499] |
| Low hazard; both calibrated | 0.000304 | -0.003875 | [-0.008195, 0.000445] |

With both capability estimates biased downward in the base hazard regime, nominal planning continued autonomously and achieved true expected loss 9.308331. The Bayesian reference requested human rescue and achieved 7.514800. This improvement is not evidence that parameter correlation caused it: the independent-prior ablation selected the same root action. It can reflect the broader modeled transition mixture and subsequent decision consequences rather than a unique value of coupling.

When only human success was underestimated, Bayes instead achieved loss 9.373126 versus nominal 9.307833. Its human-use probability was zero, although the correctly specified oracle immediately requested help. Increasing model sophistication did not rescue an inaccurate view of human competence. The same method can therefore improve one misspecified case and worsen another without contradiction to its correct-prior optimality theorem.

**Figure 2**

*Exact expected loss averaged over the fixed scenario design.*

![](../05_Experiments/figures/figure_02_design_means.png){width=6.2in}

Note. This is a descriptive ranking under an explicit artificial weighting, not a general leaderboard. The independent-prior ablation has slightly lower mean loss than the coupled Bayesian reference. No interval across heterogeneous hand-selected scenarios is used to imply population inference.

## 9.3. Human-effectiveness sensitivity

Under the base hazard regime with calibrated AI probabilities, underestimating human success by 0.18 changes the Bayesian decision from immediate rescue to autonomous execution. True expected loss increases from 7.514800 to 9.373126; human-use probability changes from 1 to 0, and severe-failure probability changes from 0.0034 to approximately 0.045786. Overestimating human success in that same regime does not change the root action. The response is therefore asymmetric and piecewise, not a smooth universal sensitivity curve.

In the lower-hazard regime, the calibrated Bayesian controller uses human assistance on approximately 28.21% of episodes rather than always delegating. Human overestimation increases that use to approximately 34.15%, while underestimation reduces it to zero. These rates reflect optimal decisions under supplied estimates, not validated human behavior. Figure 3 shows how the loss response also depends on the policy family.

**Figure 3**

*Sensitivity to supplied human-success probability bias with calibrated AI probabilities and lower hazards.*

![](../05_Experiments/figures/figure_03_human_miscalibration.png){width=6.2in}

Note. Each point is an exact conditional-model expectation, not a fitted empirical curve. The true environment is held fixed while supplied human-success estimates change.

## 9.4. Retry dependence and parameter-coupling ablations

The persistent-mode reference has lower exact loss than the iid-mode ablation in 15 scenarios and equal loss in 23. The largest difference is 1.745502 loss units. This supports the importance of representing persistence in the tested environments, but not a universal preference for persistent models: the independent-modes generating scenario removes the corresponding within-model dependence. The ablation retains uncertainty about the fixed model index; it removes only persistence of task modes within each model.

The coupled parameter prior is less successful. It improves one scenario, ties 31 and worsens six relative to a prior with the same marginal offset distributions but independent AI/human offsets. Both priors still share the hidden task mode, so this is not an ablation of every possible form of AI-human dependence. Incorrect additional coupling can propagate an autonomous failure into a misleading belief about a helper. The selected prior-predictive and opposite-coupling root states both immediately request human rescue; their equality cannot establish that learning correlation is unnecessary or beneficial in more informative tasks.

**Figure 4**

*Posterior recovery probability after repeated failures in the two-mode worked example.*

![](../05_Experiments/figures/figure_04_retry_dependence.png){width=6.2in}

Note. This figure is a deterministic illustration of P4, not additional real-agent data. The iid line and persistent model have the same initial mean probability, but very different predictions after failures.

## 9.5. Robust optimization evaluated under its own objective

The Bayesian reference has lower generating-environment expected loss than the robust policy in 18 scenarios and ties it in 20. That finding alone is not a fair assessment of minimax optimization, because its objective is an envelope over multiple possible environments. A disclosed post-hoc audit therefore evaluates every policy under both the same history-rectangular envelope and the worst supported fixed model, without changing policies or scenarios.

The robust policy's envelope value is no greater than any compared policy's envelope value in all 38 cases. However, when evaluated against the worst supported fixed model, robust planning has lower loss than the Bayesian reference in eight scenarios, equal loss in 20, and higher loss in ten. The largest gap between the robust envelope value and its own worst supported fixed-model loss is 0.485778. This difference is the cost of the larger uncertainty semantics, not evidence that the Bellman calculation failed.

All supported fixed-model bound checks pass. In the out-of-set shift case, the robust policy reports envelope loss 10.754800 while its true generating-environment loss is 13.194520. The shift changed success probabilities, catastrophe probabilities and mode prevalence, whereas the retained uncertainty set primarily perturbed success. The guarantee's coverage premise was false. Reporting only a wide success interval would obscure that failure.

**Figure 5**

*Robust envelope values, supported fixed-model losses and true-environment losses.*

![](../05_Experiments/figures/figure_05_robust_coverage.png){width=6.2in}

Note. The stale-parameter shifted environment lies outside the asserted conditional-kernel family. The reported envelope is not a valid upper bound for that unsupported environment.

## 9.6. Loss, success and risk are different outcomes

In the calibrated lower-hazard environment, the Bayesian reference has exact loss 5.975357 and success probability approximately 0.874395. Always asking the human has higher loss 7.318960 and lower success probability 0.835, but its severe-failure probability is only 0.000680 rather than approximately 0.010040. An expected-loss improvement can coexist with substantially greater catastrophic risk. The empirical worst-5% loss means are 36.16525 and 22.78, respectively, under the common random-number sample. These tail summaries are descriptive, not optimized risk bounds.

When low failure penalties make safe abandonment cheap, the optimal reference policies stop immediately. Success is then zero even though expected loss is minimal. This is not a contradiction: the objective values abandonment explicitly. A real organization must choose whether those costs and constraints represent its priorities before accepting any recommendation.

## 9.7. Transfer, runtime and reproducibility

The stale-parameter shifted environment causes the principal planners to request human rescue, yielding loss 13.194520. Supplying exact updated parameters changes their decision to stop at loss 12. This demonstrates parameter dependence, not the practical feasibility of learning the new parameters. The same code runs on both specifications; structural transfer succeeds while performance protection fails without an adequate model.

The full recorded main run took 27.976 seconds on the specified Linux AMD EPYC host, with numerical-library thread limits set to one. The median cold root computation for the joint-Bayesian policy was 10.269 ms and its median cached recommendation call was 4.088 microseconds. The process peak resident memory reported by the operating system was 176.12 MiB; a separate base-case Python-allocation trace peaked at 291.67 KiB. These are different measurements and exclude any promise about a user's laptop or a larger decision model.

**Figure 6**

*Cold root-decision runtime across the 38 scenarios.*

![](../05_Experiments/figures/figure_06_runtime.png){width=6.2in}

Note. Timings were measured on the execution host, not on Windows. Cached results are reported separately. Small-horizon timing does not establish scalability to arbitrary POMDPs.

Every non-timing value in the 418 main summary rows was identical on a complete rerun after validation hardening. A separate scalar simulation loop matched 16,000 trajectories. Raw episode means and terminal partitions were checked for all stored records. All 418 Monte Carlo loss intervals contained their exact expectations in this run; this observed containment is not an estimate of universal coverage, because cells share random draws and the finite design was not a dedicated coverage experiment.

## 9.8. Hypotheses and negative outcomes

H1's conditional claim that uncertainty modeling is not uniformly better is supported by both improvements and degradations. H2's mathematical possibility of correlation-sensitive sequential decisions is established, but the selected coupling is not generally helpful empirically. H3 is supported within persistent-mode scenarios, with 15 beneficial dependence-aware comparisons and no claim beyond the specified processes. H4 is supported under model coverage and falsified as an unconditional interpretation by the shifted case. H5 is supported: changing parameters matters even when solver structure is unchanged.

The findings do not establish that a sophisticated controller is always necessary. Many scenarios are dominated by immediate rescue or immediate stopping, and simple policies can tie the optimal reference. The exact nominal dynamic program is extremely competitive when its supplied model is right. These negative and null findings constrain the HandoffX contribution more strongly than an isolated favorable example would.
