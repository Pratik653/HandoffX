# Probability calibration in HandoffX v0.2 (C3)

## Problem

HandoffX needs P(success | action, state) for continue, retry and human assistance. Three facts constrain how these can be estimated:

1. **Raw model confidence is not a probability.** v0.1 already refused uncalibrated scores (`ModelSet` accepts only `synthetic`, `assumed` or `calibrated` evidence). Modern neural models are often miscalibrated (Guo et al., 2017, is the usual reference; not newly re-verified here and therefore not added to the v0.2 bibliography).
2. **Outcomes are observed only for actions taken.** Human success is observed only after a handoff; retry recovery only after a failure was retried. Standard post-hoc calibration (Platt scaling, isotonic regression) assumes labelled outcomes for the scored cases and is not directly applicable to counterfactual actions.
3. **Data are few and sequential.** A deployment produces one episode at a time.

## Approach adopted

Calibration is posed as Bayesian inference over a finite model set (ADAPTIVE_POLICY_MATHEMATICS.md, A1): the supplied estimate defines the centre of a grid of success offsets for AI actions and for the human; every completed episode updates the posterior by its marginal likelihood, integrating the latent failure mode.

- **Selection bias** is handled by ignorability (Rubin, 1976): when actions depend only on logged data, the likelihood is valid without propensity weights. It is *not* handled if escalations depend on unlogged information; integrators must log every action and outcome, including escalations' results.
- **Missing counterfactuals** are not imputed. Proposition A2 makes the consequence explicit: an action never taken keeps its prior. The `Advisor` warns when human or AI parameters are still prior-only (`Recommendation.warnings`).
- **Discreteness.** The grid represents bias in success probabilities only; prevalence of persistent failure and hazard rates are fixed at their supplied values. CE9 shows this misspecification is the main failure mode.

## Evidence

Held-out test split (200 environments, 100 episodes each): mean absolute error of root first-attempt success probability fell from 0.084 to 0.057 (AI) and 0.067 to 0.052 (human) for handoffx_v2; shift split 0.123 -> 0.082 and 0.116 -> 0.085. Point-estimate recalibration (`plugin_recal`) reached similar calibration error but worse decisions (gap closed 19% vs. 37% for posterior planning): decision quality depends on retaining uncertainty, not only on the point estimate.

## What remains impossible from the available observations

- Estimating human effectiveness without ever escalating (A2).
- Distinguishing a high prevalence of persistent failures from a low success probability with the current grid (CE9).
- Calibrating against real operators: no human data were used; all "human" outcomes are simulated.

## Practical guidance

Supply your best estimates with an honest `uncertainty`, log every episode with `Advisor.record_episode`, and read `calibrated_estimates()` and the warnings. Treat recommendations as decision support until enough escalations have been logged for the human estimate to move away from the prior.
