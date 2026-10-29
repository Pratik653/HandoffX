# Mechanism analysis: why does candidate A reduce severe failures?

Sources:
- §1–4 use the pre-registered confirmation metrics: `results/confirm/analysis.json` (`behaviour`, `per_subtype`, `mechanism_association`, `target_diagnostics`).
- §5 is **exploratory**. It was designed after the confirmation results were seen and run on fresh seeds 850000+: 60 environments per target family and 20 per other kind, 220 in total (`scripts/mechanism_ablation.py`, `results/exploratory_mechanism/`, `figures/risk_loss_frontier.png`). It plays no role in the decision.

## Short answer

A reduces severe failures mainly by **acting more conservatively**:
- it **stops (abandons the task) more** and **retries less**, which reduces exposure on continue steps;
- task success falls by 3.3 points to buy 0.32 points less severe risk.

Two things drive that conservatism:
- **A's prior is asymmetric.** Its three-level prevalence prior raises the expected persistent-fault share above the supplied value: prior mean 0.875·z₂ + 0.0625.
- **The prevalence dimension absorbs misfit.** When evidence does not match the supplied model, part of it is explained as "more persistent faults", which makes the planner more pessimistic about AI continuation.

A really does infer prevalence better only when prevalence itself has shifted. Even then, that improvement does not explain the per-environment severe reduction.

## 1. More accurate persistent-failure inference? Only where prevalence actually shifted; not the driver

End-of-stream total-variation error of the mode distribution, comparing A with the supplied (fixed) prevalence used by bayes_recal:

| Setting | True persistent share | Supplied | A's estimate | TV error A | TV error supplied |
|---|---|---|---|---|---|
| persist / prevalence | 0.294 | 0.173 | 0.224 | 0.116 | 0.174 |
| persist / both | 0.254 | 0.188 | 0.257 | 0.097 | 0.151 |
| persist / dependence (prevalence exact) | 0.151 | 0.151 | 0.172 | 0.048 | 0 |
| human_shift (prevalence exact) | 0.188 | 0.188 | 0.206 | 0.040 | 0 |
| calibrated | 0.195 | 0.195 | 0.205 | 0.036 | 0 |

- A moves toward the truth when prevalence has shifted, recovering about a third to a half of the shift.
- It **adds** error whenever prevalence was right, which is 6 of 7 environment kinds here.
- The per-environment rank correlation between A's severe change and its change in prevalence error is **ρ = 0.02** (target, n = 300).
- **Conclusion:** A cannot be described as a successful persistent-failure estimator. It is a decision method whose benefit does not track prevalence accuracy.

## 2. Better-calibrated AI recovery estimates? Slightly, mostly in Family A; weak association

| | AI root calibration error (bayes_recal → A) | Signed AI bias (bayes_recal → A) |
|---|---|---|
| Target | 0.040 → 0.038 | +0.011 → +0.003 |
| persist_shift | 0.062 → 0.049 | +0.024 → +0.010 |
| human_shift | 0.018 → 0.026 | −0.001 → −0.005 |

- Under persistent-failure shift, the extra parameter removes some of the optimism that bayes_recal builds into AI success. This is the CE9 "misfit absorption" effect from the feasibility study.
- The per-environment association with the severe change is weak: ρ = 0.10.
- In human_shift, AI calibration gets *worse*.
- **Conclusion:** this contributes but is not the main mechanism.

## 3. More conservative action selection? Yes: the main proximate mechanism

Changes vs bayes_recal (target families, exact probabilities):

| | Δ |
|---|---|
| Stop probability | **+0.032** (0.276 → 0.308) |
| Stopping where the oracle would continue | +0.034 (0.052 → 0.085) |
| Task success | **−0.033** (0.654 → 0.621) |
| Severe on continue steps | **−0.0030** of the total −0.0032 |
| Severe on retry steps | −0.0003 |
| Severe on human steps | +0.00005 |

- The per-environment severe change correlates strongly with the change in continue-step severe mass (ρ = 0.93).
- It correlates moderately with fewer retries (ρ = 0.56) and with more stopping (ρ = −0.27).
- Since A's severe probability falls *below the oracle's* (0.0147 vs 0.0158), A is not merely correcting a learning error. It is **more risk-averse than the loss-optimal policy**.

## 4. Fewer retries; more escalation?

- **Retries:** fewer, 0.282 → 0.240 per episode (oracle 0.234). This is part of the conservatism.
- **Escalation:** slightly more overall (0.235 → 0.262), but very unevenly by sub-type. Changes are A minus bayes_recal:

| human_shift sub-type | Δ escalation | Δ stop | Severe RRR | Loss change |
|---|---|---|---|---|
| uniform, human worse (b < 0, n = 23) | **+0.100** | −0.014 | 16.8% | +1.18% |
| uniform, human better (b > 0, n = 33) | +0.033 | +0.016 | 14.8% | −0.27% |
| mode_flat, human worse (n = 24) | **+0.111** | +0.034 | 32.5% | **+4.10%** |
| mode_flat, human better (n = 22) | +0.014 | +0.054 | 19.1% | +0.51% |
| persistent_only, worse (n = 30) | +0.026 | +0.030 | 11.9% | +0.92% |
| persistent_only, better (n = 18) | +0.002 | −0.001 | 0.1% | +0.02% |

When the human is *less* effective than supplied, the evidence that the human fails is partly explained by "more persistent faults". In the supplied model, those are the faults the human is best placed to fix, so A escalates **more** to a human who is worse than assumed. This confirms the confounding explanation proposed in the feasibility study (FINDINGS.md section 3): human kernels differ by latent mode, so human misestimation and prevalence are not separately identifiable from these logs. It is the source of A's loss cost in Family B.

## 5. Compensation for structural misspecification? Partly; and is A just disguised risk aversion? (exploratory)

**Sub-type contrast (confirmatory data).** A's benefit is large where the misspecification resembles its own extra parameter:
- prevalence: RRR 24.6%;
- both: 22.5%;
- mode_flat human shift: 26.3%.

It is small where the misfit is structural and outside A's family: *dependence*, where persistence strength changes inside the modes, gives 4.6% [0.1, 12.6]. So A does not compensate for arbitrary structural misspecification. It helps when the misfit can be absorbed into the prevalence direction, whether or not prevalence is the true cause.

**Privileged diagnostic.** recal_trueprev_diag is bayes_recal told the true prevalence.
- It equals bayes_recal exactly wherever prevalence was exact.
- Under prevalence shift it reduces severe failures by 33.7%, more than A, and with lower loss (−2.11%).
- Knowing prevalence is therefore valuable in Family A, and A captures part of that value.
- In Family B, A's benefit cannot come from prevalence knowledge, because the true prevalence equals the supplied one.

**Prior-mean ablation (exploratory).** `pess_prior_recal` is bayes_recal with A's prior-mean prevalence fixed: no flexibility, no learning of prevalence.
- It gives 7.1% [2.4, 13.2] RRR, about 30% of A's 23.5% on the same seeds.
- A beats it by −17.6% [−27.9, −7.8] in severe probability, at −0.71% [−1.87, +0.30] in loss.
- **Conclusion:** the asymmetric prior explains a minority of the effect; the flexible prevalence learning explains the rest.

**Explicit risk-aversion frontier (exploratory).** `riskcost_c` is bayes_recal planning with catastrophe loss × c; evaluation always uses the true costs.

| Policy | Severe RRR vs bayes_recal | Loss change | Δ success |
|---|---|---|---|
| riskcost ×1.25 | 19.9% [11.0, 29.2] | +0.34% [−0.67, +1.39] | −0.034 |
| riskcost ×1.5 | 33.3% [22.2, 44.4] | +0.54% [−1.13, +2.16] | −0.057 |
| riskcost ×2 | 51.8% [40.8, 62.2] | +2.37% [+0.17, +4.56] | −0.096 |
| riskcost ×3 | 74.8% [66.6, 81.7] | +5.93% [+2.81, +9.16] | −0.141 |
| **A** | 23.5% [13.6, 33.9] | −0.47% [−1.67, +0.67] | −0.039 |

Paired against riskcost ×1.25, which has nearly the same severe level, A has severe −4.5% [−14.0, +5.2] and **loss −0.80% [−1.49, −0.19]**.

- At matched risk, A lies slightly *better* than the simple cost-penalty frontier: its conservatism is evidence-triggered rather than uniform. Where on the environment space it gains was not analysed.
- But the frontier also shows that **far larger severe reductions are available from an explicit, tunable risk weight**. A sits at one fixed, uncontrolled point on it.
- This is exploratory, one fresh sample of 120 target environments. It needs confirmation before being claimed.

## 6. Summary table

| Proposed mechanism | Supported? | Evidence |
|---|---|---|
| More accurate persistent-failure inference | **No** as the driver; true only under real prevalence shift | ρ = 0.02; error added in 6 of 7 kinds |
| Better-calibrated AI recovery estimates | Minor, Family A only | AI optimism +0.024 → +0.010; ρ = 0.10 |
| More conservative action selection | **Yes, main proximate cause** | stop +3.2 pts, success −3.3 pts, severe below oracle |
| Fewer unnecessary retries | Yes, part of the conservatism | 0.282 → 0.240 |
| More human escalation | Mixed; harmful when the human is worse than supplied | +0.10 to +0.11 escalation in human-worse sub-types; loss up to +4.1% |
| Compensation for structural misspecification | Partly: only misfit along the prevalence direction | dependence 4.6% vs prevalence 24.6%, mode_flat 26.3% |
| Prior asymmetry | Minor contributor | prior-mean-only ablation gives 7.1% of A's 23.5% |

**Interpretation.** A is best described as **evidence-triggered pessimism**: a model-uncertainty hedge that becomes more conservative when outcomes deviate from the supplied model. It is not an estimator of persistent-failure prevalence.
