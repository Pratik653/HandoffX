# GO / NO-GO decision — HandoffX v0.3

## Verdict

**Broad v0.3 development aimed at lower average decision loss: NO-GO.** None of the three candidates, nor their combinations, produced a replicated average-loss improvement over ungated posterior recalibration (v0.2's strongest baseline). The best candidate's pooled effect fell from −0.92% to −0.52% to −0.25% across three independent samples, and the last interval includes zero.

**One narrow direction: CONDITIONAL GO** — prevalence-flexible cross-task learning (candidate A), re-scoped as a **tail-risk and shift-robustness** method rather than a general loss improvement.

## Decision table

| Candidate | Mathematical validity | Empirical evidence | Practical value | Decision |
|---|---|---|---|---|
| A — prevalence-augmented learning | Sound; exact Bayes over a larger finite model set. Prevalence only weakly identifiable; the gain comes from absorbing misfit, not from estimating prevalence | Pooled: −0.52% [−0.88, −0.19] (confirmation), −0.25% [−0.71, +0.17] (replication). In all three rounds: shift −2.0% to −3.2% and severe failures −13% to −17%, all CIs exclude 0. Costs: calibrated +0.84% to +0.95% vs. nominal; human-bias +0.6% | Real but narrow: fewer severe failures and better behaviour under shift, at no extra compute; slight cost when estimates are right | **CONDITIONAL GO** (meets the frozen conditional criterion in both confirmation and replication; fails the GO calibrated-environment limit) |
| B — human-targeted posterior sampling | Sound; reduces to posterior planning when the human offset is known | +0.53% [+0.16, +0.90]; worse in its own target kind (+0.99%) | None: exploration cost exceeds information value at this horizon | **NO-GO** |
| C — Bayes-factor reversion guard | Sound; Occam behaviour of marginal likelihoods (Kass & Raftery, 1995) confirmed (log BF ≈ 0 when calibrated) | Calibrated −0.58% [−1.10, −0.19] vs. bayes_recal, but pooled −0.26% [−0.64, +0.09] and human-bias +0.84% | Useful only as a safeguard; no average benefit; with A it cancels A's gains (AC −0.12%) | **NO-GO** as a standalone direction |
| Combinations AC / ABC | – | ABC met numeric GO thresholds narrowly on confirmation (−0.52%), then did not replicate (−0.08% [−0.49, +0.32]); AC −0.12% | No | **NO-GO** |

## Answers

1. **Is HandoffX v0.3 development justified?** Not as a general upgrade. Under the tested assumptions the deployable methods sit within about 0.5% of each other, while the oracle is about 2.5% better. Additional policy or learning machinery of this kind is unlikely to close that gap on average.
2. **Most promising single direction.** Prevalence-flexible (persistent-failure-aware) cross-task learning, evaluated as a severe-failure and shift-robustness method.
3. **Why.** It is the only effect that reproduced in three independent samples (72 + 300 + 300 environments): 13–17% fewer severe failures and 2–3% lower loss under distribution shift, with no compute cost. It addresses a documented failure mode (CE9: misspecified nuisance parameters corrupt learning of decision-relevant parameters), and its benefit disappears without learning, which supports the mechanism.
4. **Evidence.** `results/confirm/analysis.json`, `results/replicate/analysis.json`, `results/secondary_checks.json`, `figures/effects_by_round.png`.
5. **What remains uncertain.**
   - Severe-failure probability was a pre-specified *secondary* metric, and "shift" was one of A's two pre-specified target kinds, so neither has yet been the primary endpoint of a confirmatory test.
   - The shift environments come from one generator designed in v0.2.
   - The calibrated-environment and human-bias regressions are unexplained beyond a plausible confounding hypothesis.
   - Nothing is validated on real agent logs or real operators.
   - The self-confirming escalation trap, which holds 91% of the residual plateau on dev environments, remains unsolved: B did not fix it.
6. **Smallest next experiment.** One pre-registered test of A against bayes_recal on fresh seeds with:
   - severe-failure probability as the **primary** endpoint, plus a loss non-inferiority margin of 0.5%;
   - an independently specified second shift family (e.g. hazard shifts without persistence shift, and persistence shifts without hazard shift) to separate the two mechanisms;
   - human kernels made independent of the prevalence level, to test the confounding explanation of the human-bias regression.

   About 300 environments; minutes of CPU.
7. **Does the expected scientific value justify further effort?** A small amount, yes: the follow-up is cheap and would turn a consistent secondary finding into a defensible, narrow contribution ("nuisance flexibility in cross-task calibration reduces tail risk under shift"). A full v0.3 development cycle is not justified by current evidence. If the follow-up fails, the defensible conclusion is that v0.2's exact planning with persistent-failure modelling already captures most of what this decision structure allows. The remaining headroom then lies in data the simulator does not have (task features, real outcome logs) and in exploration under selective observation.

Not a judgement on HandoffX as a whole: v0.2's core findings (exact cost-aware planning, the importance of persistent-failure modelling, honest characterisation of when calibration helps) stand.
