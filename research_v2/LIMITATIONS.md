# Limitations of HandoffX v0.2

1. **Synthetic evidence only.** All benchmark environments, "humans" and tool failures are simulated. No real operator, real LLM agent or production workflow was evaluated. Effects are in artificial loss units.
2. **Small effects.** On the primary held-out test split the controller improved mean loss by 0.46% relative to nominal (relative interval includes zero), because nominal planning was already within 2% of the oracle. Practical value depends on how biased real estimates are; it is unknown.
3. **The gate is not shown to help.** Ungated posterior planning matched or beat the gated controller on test; the ordering reversed on validation. The gate's credible statement is only valid inside the model set.
4. **Misspecification.** The model grid varies success probabilities only. When the truth differs in persistent-failure prevalence or hazards, the posterior can concentrate on a wrong model and the gate switches confidently (CE9). This produced the worst degradations (up to +22% in one test environment; 19% of calibrated test environments degraded by > 1%).
5. **Hurts when estimates are already right.** Calibrated subgroup: +0.92% on test.
6. **Exploration.** Human effectiveness is not learned unless escalations occur (A2). Thompson sampling did not solve this at the tested horizon.
7. **Tail risk.** Expected-loss policies did not reduce severe-failure probability or CVaR; only the robust planner did, at a mean-loss cost.
8. **Scale.** Exact DP over count states limits horizons to 12 and actions to the four-action model; the model set is finite and hand-specified.
9. **Logging assumption.** Calibration requires that every action and outcome is logged and that escalation decisions depend only on logged information.
10. **No external validation.** No peer review, no cross-model or cross-domain agent evidence, no human-subject study. The demo is a deterministic simulation and is labelled as such.
11. **Environment differences.** v0.2 ran on Windows/Python 3.11; v0.1 on Linux/Python 3.13. The v0.1 study reproduced to 7e-15; v0.2 was run on one platform only.
