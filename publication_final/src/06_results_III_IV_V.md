# 12. Study III: feasibility screening

## 12.1. Where the remaining headroom was

Diagnostics on Study II development environments located the remaining headroom. The held-out environments were not used.

**Table {T:headroom}.** *Headroom diagnostics (Study II development environments; relative change in mean exact loss versus nominal planning)*

| Diagnostic | Result |
|---|---|
| Oracle, i.i.d. family (60 environments) | −3.40% |
| Oracle with only the true success probabilities | −2.93% |
| Oracle with only the true prevalence | −0.12% (shift family: −3.18%) |
| Calibrated environments | −0.05% |
| Best single model of the 5 × 5 grid (30 environments) | −3.65%, against oracle −3.70%; a 9 × 9 grid also −3.65% |
| bayes_recal regret, successive 100-episode blocks (32 environments, 400 episodes) | 0.185, 0.150, 0.144, 0.139 per episode; with true prevalence supplied 0.138, 0.095, 0.088, 0.090; nominal 0.38 |
| Plateau attribution | 91% of plateau regret in 6 of 32 environments in which the learner almost stopped escalating |

Three conclusions follow:
1. **The model grid was not the principal bottleneck.** The best single grid model already reaches 99% of the oracle's gain.
2. **Learning stalled.** Regret levelled off near 0.14 per episode, whereas almost zero is attainable with the best grid model.
3. **The stall had two visible causes:**
   - a misspecified nuisance parameter (failure prevalence) distorting the decision-relevant success offsets, the CE9 mechanism; about a third of the plateau;
   - the self-confirming escalation trap of Section 7.13 under selective observation; 91% of what remains.

Calibrated environments have essentially no headroom, so any learner can only lose there.

The screening matrix considered ten opportunities and selected three. Rejected opportunities:
- finer grids: no headroom;
- dependent retries and error-type recovery: already represented in the model;
- contextual estimation: the simulator has no task features, so it cannot be evaluated fairly;
- costed diagnostic actions: beyond the minimal scope;
- risk-sensitive intervention as a separate objective.

## 12.2. Results across three rounds

**Table {T:screen}.** *Pooled relative change in mean exact loss versus bayes_recal (kinds weighted equally; kind-stratified 95% bootstrap intervals)*

| Policy | Pilot (n = 72) | Confirmation (n = 300) | Replication (n = 300) |
|---|---|---|---|
| A: prevalence-augmented learning | −0.92% [−1.97, −0.07] | −0.52% [−0.88, −0.19] | −0.25% [−0.71, +0.17] |
| B: human-targeted posterior sampling | +0.08% [−0.92, +1.05] | +0.53% [+0.16, +0.90] | – |
| C: Bayes-factor reversion guard | +0.41% [−0.73, +1.84] | −0.26% [−0.64, +0.09] | – |
| A + C | – | – | −0.12% [−0.51, +0.28] |
| A + B + C (pre-specified combination) | – | −0.52% [−0.95, −0.11] | −0.08% [−0.49, +0.32] |
| handoffx_v2 (reference) | −0.29% | −0.23% [−0.50, 0.00] | −0.29% [−0.54, −0.08] |
| Full Thompson sampling (reference) | +0.16% | +0.89% [+0.45, +1.36] | – |
| A without learning (diagnostic) | – | +0.74% [+0.05, +1.51] | – |
| Oracle (diagnostic) | −2.45% | −2.58% | −2.42% |

![Figure {F:rounds}. Candidate effects versus bayes_recal by round (Study III).](../research_poc_v03/figures/effects_by_round.png){width=6.0in}

**Why average-loss improvements failed to replicate.** A's pooled effect regressed toward zero across independent samples: −0.92%, then −0.52%, then −0.25%. This is a winner's-curse pattern; the pilot was optimistic. The combination A + B + C met the numerical GO thresholds narrowly on confirmation, but did not replicate (−0.08%). By the frozen criteria:
- **A** was CONDITIONAL GO in both confirmation and replication. It met the target-kind criterion but failed the calibrated-environment limit: +0.84% and +0.95% versus nominal.
- **B** was NO-GO: worse in its own target kind (human_bias +0.99%). Its exploration cost exceeded its information value within 100 episodes, as for full Thompson sampling in Study II.
- **C** was NO-GO as a standalone direction. It helped in calibrated environments (−0.58% [−1.10, −0.19]) but delayed acting on genuine bias (human_bias +0.84%), giving no pooled gain.
- **The combinations** were NO-GO: the guard and the prevalence flexibility partly cancelled.

**What replicated.** In all three rounds, candidate A:
- reduced loss in the shift kind: −3.21% [−6.38, −1.06], −2.48% [−4.15, −1.09] and −2.00% [−3.90, −0.54];
- reduced pooled severe-failure probability by 0.0027, 0.0020 and 0.0029 in absolute terms, a relative reduction of 13% to 17%, with every interval excluding zero;
- reduced retries per episode, from 0.252 to 0.222 on confirmation and from 0.237 to 0.197 on replication.

Its compute was 1.03–1.05 times that of bayes_recal. Its end-of-stream prevalence error was *not* better than using the fixed supplied value: 0.074 against 0.069 on confirmation. Severe-failure probability was a pre-specified *secondary* metric in Study III, so these reductions motivated Study IV but are not confirmatory.

**Library issue found.** Round 1 found that `EpisodeBelief.posterior_models()` raised an error if a posterior weight underflowed to zero. It was not triggered in any run, and it was corrected in version 0.2.1 (Section 8.4).

# 13. Study IV: independent risk-reduction confirmation

All values in this section were read from the stored analysis files (`research_poc_v03/confirmation/results/confirm/`). The run was executed once (134.7 s on 16 workers), and the candidate and analysis were not changed afterwards.

## 13.1. Sample

- 500 environments, of which 300 are in the target families.
- 100 episodes per stream, giving 50,000 episodes per policy.
- Expected severe events in the target families: 440 for candidate A and 535 for bayes_recal, out of 30,000 episodes each.
- Realized (sampled) severe events over all 500 environments:

**Table {T:realized}.** *Realized severe events in Study IV (all 500 environments)*

| Policy | Realized severe events |
|---|---:|
| Candidate A | 790 |
| bayes_recal | 973 |
| handoffx_v2 | 975 |
| nominal | 947 |
| oracle | 842 |

## 13.2. Primary endpoint and loss non-inferiority

**Table {T:primary}.** *Primary endpoint and loss non-inferiority on the target distribution (persist_shift and human_shift, n = 300)*

| Quantity | Candidate A | bayes_recal | Estimate [95% CI] | Criterion | Met? |
|---|---:|---:|---|---|---|
| Severe-failure probability per episode | 0.0147 | 0.0178 | ARD −0.0032 [−0.0044, −0.0021] | upper bound < 0 | yes |
| Relative risk reduction | | | 17.8% [12.0%, 24.0%] | ≥ 10% | yes |
| Cumulative loss ratio − 1 | | | +0.28% [−0.21%, +0.82%] | upper bound < +0.5% | **no** |
| Mean per-environment relative loss difference (secondary) | | | +0.24% [−0.16%, +0.66%] | – | – |

The primary criterion was met. The absolute reduction corresponds to about 3.2 fewer severe failures per 1,000 episodes; the relative reduction is 17.8%. These are different quantities and should not be interchanged.

Loss non-inferiority was **not demonstrated**: the one-sided 97.5% upper bound (+0.82%) exceeds the 0.5% margin. Inferiority was not demonstrated either: the lower bound is below the margin. The pre-execution precision estimate had anticipated an inconclusive loss test as a real possibility.

## 13.3. Robustness across mechanisms

**Table {T:kinds}.** *Candidate A versus bayes_recal by environment kind (95% CIs)*

| Kind | n | Severe-failure RRR | Loss change |
|---|---:|---|---|
| persist_shift (Family A) | 150 | 18.4% [10.0, 27.5] | −0.58% [−0.99, −0.19] |
| human_shift (Family B) | 150 | 17.3% [9.3, 25.8] | +1.14% [+0.27, +2.11] |
| hazard_shift | 40 | 23.2% [2.8, 46.8] | −3.29% [−7.90, −0.20] |
| calibrated | 40 | 6.2% [0.4, 15.8] | +0.05% [−0.26, +0.36] |
| near_nominal | 40 | 28.1% [8.3, 48.5] | +0.17% [−1.40, +1.51] |
| ai_bias | 40 | 8.2% [0.8, 20.3] | +0.28% [−0.46, +1.10] |
| joint_bias | 40 | 18.3% [3.6, 36.5] | +1.18% [+0.02, +2.55] |

**Severe failures.** The reduction appeared in every kind, and every interval excluded zero, so it did not depend on one shift generator.

**Loss.** The loss effect depended on the mechanism:
- lower under persistent-failure shift (−0.58%) and hazard shift (−3.29%);
- **higher under human-effectiveness shift** (+1.14%, beyond the margin within that family);
- higher, borderline, under joint AI and human bias (+1.18%).

The pooled target result combines a gain in one family with a cost in the other, and is reported only together with these parts.

**Sub-types** (target families; RRR, then loss change):

**Table {T:subtypes}.** *Study IV sub-type results, candidate A versus bayes_recal*

| Family | Sub-type | Severe-failure RRR | Loss change |
|---|---|---|---|
| Persistent-failure shift | prevalence | 24.6% | −1.33% |
| | dependence | 4.6% [0.1, 12.6] | +0.23% |
| | both | 22.5% | −0.46% |
| Human-effectiveness shift | uniform | 15.8% | +0.40% |
| | mode_flat | 26.3% | **+2.47% [+0.17, +4.98]** |
| | persistent_only | 8.7% | +0.61% |

![Figure {F:forest}. Candidate A versus bayes_recal in Study IV: change in severe-failure probability (left) and cumulative loss (right) by environment kind, with 95% confidence intervals. The dashed line marks the +0.5% non-inferiority margin.](../research_poc_v03/confirmation/figures/confirmation_forest.png){width=6.5in}

## 13.4. Other comparators

**Table {T:othercomp}.** *Candidate A versus other comparators in Study IV (target families; 95% CIs)*

| Comparator (target families) | Severe-failure RRR of A | Loss change of A |
|---|---|---|
| handoffx_v2 | 17.9% [12.0, 24.2] | +0.36% [−0.16, +0.92] |
| nominal | 16.0% [9.8, 22.6] | −0.76% [−1.64, +0.11] |
| oracle (diagnostic) | 7.1% [−0.1, 14.0] | +3.46% [+2.69, +4.34] |

A's severe-failure probability, 0.0147, was *below* the oracle's, 0.0158, while its loss was 3.5% higher than the oracle's. Candidate A therefore does not approach the loss-optimal policy; it moves along the risk–loss trade-off toward more caution.

## 13.5. Safeguards: task completion, stopping, escalation and retries

**Table {T:safeguards}.** *Exact behaviour in the target families (means per episode)*

| Metric | nominal | handoffx_v2 | bayes_recal | Candidate A | oracle |
|---|---:|---:|---:|---:|---:|
| Task success probability | 0.678 | 0.660 | 0.654 | 0.621 | 0.683 |
| Stop (abandon) probability | 0.234 | 0.267 | 0.276 | 0.308 | 0.249 |
| Stopping where the oracle would continue | 0.033 | 0.043 | 0.052 | 0.085 | 0 |
| Human escalation probability | 0.297 | 0.248 | 0.235 | 0.262 | 0.295 |
| Unnecessary escalation (oracle prefers another action) | 0.084 | 0.040 | 0.035 | 0.055 | 0 |
| Retries per episode | 0.277 | 0.281 | 0.282 | 0.240 | 0.234 |
| Severe on continue / retry / human steps | .0152 / .0014 / .0008 | .0157 / .0015 / .0007 | .0157 / .0015 / .0007 | .0127 / .0012 / .0007 | .0138 / .0012 / .0008 |
| Severe where the oracle would act differently | 0.0028 | 0.0024 | 0.0025 | 0.0013 | 0 |
| Seconds per stream | 0.06 | 1.48 | 0.62 | 0.64 | 0.04 |

Relative to bayes_recal, candidate A:
- completed **3.3 percentage points fewer tasks** (0.654 to 0.621);
- **stopped 3.2 percentage points more often** (0.276 to 0.308);
- retried less (0.282 to 0.240 retries per episode).

Its severe-failure reduction occurred almost entirely on continue steps. Severe failures on human steps were unchanged, and stopping cannot cause a severe failure in this model.

Other safeguards:
- **Correct calibration.** Loss was +1.01% [+0.24, +1.98] versus nominal, the optimal policy there, and +0.05% versus bayes_recal.
- **Human misestimation.** Escalation rose by 0.10–0.11 in the sub-types where the human was *less* effective than supplied (uniform and mode_flat with a negative shift), with loss up to +4.10% in one of them. This is the human/prevalence confounding of Section 7.13.
- **Compute.** 1.03 times bayes_recal and 0.43 times handoffx_v2.

## 13.6. Decision

Under the frozen rule:
- the primary criterion was met;
- loss non-inferiority was not demonstrated, but not clearly failed either;
- robustness was met;
- no kind showed a significant severe-failure increase;
- no kind's loss lower bound exceeded +1%.

The outcome is therefore **CONDITIONAL GO**: a confirmed severe-failure reduction, with the loss constraint unresolved.

# 14. Study V: exploratory mechanism analysis

*Everything in this section is exploratory.* It was designed after Study IV results were seen, it does not alter the Study IV decision, and the risk-weight values $c$ were not tuned.

## 14.1. Not more accurate prevalence estimation

**End-of-stream prevalence error.** Total-variation error of the mode distribution, candidate A versus the fixed supplied prevalence:

**Table {T:preverr}.** *End-of-stream prevalence error (total variation), Study IV*

| Setting | A | Supplied |
|---|---:|---:|
| Prevalence shifted | 0.116 | 0.174 |
| Prevalence and dependence shifted | 0.097 | 0.151 |
| Prevalence exact (dependence shift, human shift, calibrated) | 0.036–0.048 | 0 |

- Candidate A moved toward the truth only where prevalence had actually shifted. It added error wherever the supplied prevalence was right, which was 6 of the 7 Study IV kinds.
- Across target environments, the per-environment rank correlation between A's severe-failure change and its change in prevalence error was **0.02**.

**Other correlates of the severe-failure change:**

**Table {T:corr}.** *Per-environment rank correlations with candidate A's severe-failure change (target families)*

| Quantity | Rank correlation with A's severe-failure change |
|---|---:|
| Change in prevalence error | 0.02 |
| Change in AI calibration | 0.10 |
| Change in retries | 0.56 |
| Change in stopping | −0.27 |
| Change in continue-step severe mass | 0.93 |

The evidence does not support describing candidate A as an estimator of hidden failure prevalence.

## 14.2. More cautious decisions

**Proximate mechanism.** The reduction is explained by more cautious action selection: more stopping, fewer retries and less exposure on continue steps. As a result, the severe-failure probability fell below the oracle's.

**Drivers of the caution:**
- *The prior is asymmetric.* A's prior raises the expected persistent-fault share, by about 0.04 when the supplied share is near 0.2, as in these environments (Section 6.3).
- *Misfit is absorbed.* When outcomes deviate from the supplied model, part of the deviation is explained as "more persistent faults", which makes the planner more pessimistic about AI continuation.

**Prior-mean ablation.** Fixing A's prior-mean prevalence without any flexibility (pess_prior_recal) gave a 7.1% [2.4, 13.2] reduction, about 30% of A's 23.5% on the same fresh seeds. Paired with it, A had −17.6% [−27.9, −7.8] lower severe-failure probability. The prior asymmetry therefore explains a minority of the effect, and the flexible prevalence learning the rest.

**Sub-type contrast** (Study IV data). A helped most where the misfit could be absorbed along the prevalence direction, whether or not prevalence was the true cause:

**Table {T:subcontrast}.** *Sub-type contrast for candidate A (Study IV)*

| Sub-type | Severe-failure RRR |
|---|---:|
| Prevalence shift | 24.6% |
| Human success made mode-independent (mode_flat) | 26.3% |
| Persistence strength changed (dependence; structurally outside A's family) | 4.6% |

**Privileged diagnostic.** bayes_recal given the *true* prevalence:
- reduced severe failures by 33.7% under prevalence shift, with lower loss (−2.11%);
- was identical to bayes_recal wherever prevalence was exact.

Knowing prevalence is valuable in Family A, and A captures part of that value. In Family B the true prevalence equals the supplied one, so A's benefit there cannot come from prevalence knowledge.

## 14.3. Catastrophe-weighted planning and the risk–loss trade-off

**Table {T:frontier}.** *Exploratory frontier on the two target families (120 fresh environments; changes versus bayes_recal with 95% CIs)*

| Policy | Severe-failure RRR | Loss change | Change in task success |
|---|---|---|---|
| Catastrophe weight × 1.25 | 19.9% [11.0, 29.2] | +0.34% [−0.67, +1.39] | −3.4 pp |
| Catastrophe weight × 1.5 | 33.3% [22.2, 44.4] | +0.54% [−1.13, +2.16] | −5.7 pp |
| Catastrophe weight × 2 | 51.8% [40.8, 62.2] | +2.37% [+0.17, +4.56] | −9.6 pp |
| Catastrophe weight × 3 | 74.8% [66.6, 81.7] | +5.93% [+2.81, +9.16] | −14.1 pp |
| A's prior mean only | 7.1% [2.4, 13.2] | +0.24% [−0.51, +0.99] | −2.4 pp |
| Candidate A | 23.5% [13.6, 33.9] | −0.47% [−1.67, +0.67] | −3.9 pp |

![Figure {F:frontier}. Exploratory risk–loss frontier on fresh seeds: candidate A and A's prior mean alone, compared with bayes_recal planning under increasing catastrophe weights. Error bars are unpaired 95% intervals against bayes_recal.](../research_poc_v03/confirmation/figures/risk_loss_frontier.png){width=5.6in}

**Simple catastrophe weighting reproduces the benefit.** Weighting catastrophes 1.25 times more in planning gave about the same severe-failure reduction as candidate A, with the same kind of mechanism: less success and more stopping. Larger weights gave much larger reductions at monotonically rising loss and falling task completion.

**At approximately matched risk**, candidate A had lower loss than the 1.25 weight in this single exploratory sample:
- severe-failure change −4.5% [−14.0, +5.2];
- loss change −0.80% [−1.49, −0.19].

This does **not** establish that candidate A outperforms a tuned risk-sensitive controller at matched risk:
- the weights were not tuned;
- the risks were matched only approximately;
- the comparison is post hoc and was run once on 120 environments.

A pre-registered matched-risk comparison was proposed but **has not been performed** (Section 18).

## 14.4. Summary of the mechanism evidence

**Table {T:mechsum}.** *Summary of the mechanism evidence (Study V)*

| Proposed mechanism | Supported? | Evidence |
|---|---|---|
| More accurate persistent-failure inference | No, as the driver; true only under real prevalence shift | correlation 0.02; error added in 6 of 7 kinds |
| Better-calibrated AI recovery estimates | Minor; Family A only | AI optimism +0.024 → +0.010; correlation 0.10 |
| More conservative action selection | **Yes, main proximate cause** | stop +3.2 pp, success −3.3 pp, severe risk below the oracle's |
| Fewer retries | Yes, part of the caution | 0.282 → 0.240 per episode |
| More human escalation | Mixed; harmful when the human is worse than supplied | +0.10 to +0.11 in human-worse sub-types; loss up to +4.1% |
| Compensation for structural misspecification | Partly: only misfit along the prevalence direction | dependence 4.6% vs prevalence 24.6% and mode_flat 26.3% |
| Prior asymmetry | Minor contributor | prior mean alone 7.1% of A's 23.5% |

Candidate A is best described as **evidence-triggered pessimism**: a model-uncertainty hedge that becomes more cautious when outcomes deviate from the supplied model.
