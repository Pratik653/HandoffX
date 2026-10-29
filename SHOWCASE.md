# HandoffX — technical summary

**Problem.** An autonomous agent hits a failure. Continue, retry, ask a human, or stop? Wrong choices waste human time or let failures compound. Most agent stacks use fixed rules ("retry twice, then escalate") or raw model confidence, which is not a calibrated probability.

**Existing approaches.** Learning-to-defer methods train classifiers to route single predictions to experts; POMDP and robust MDP methods plan under uncertainty; safe policy improvement keeps a baseline unless data justify a change. None directly targets the agent's four-way, multi-step intervention decision with persistent failures, deadlines and fallible humans.

**Research gap.** Whether uncertainty-aware intervention control beats plain nominal planning, and when. HandoffX v0.1 found a joint-Bayesian planner was better than nominal in only 6 of 38 scenarios.

**Method.**
1. Diagnosis: an exact performance-difference decomposition showed the v0.1 losses were tiny, nominal already had the true parameters in most scenarios, and within one episode no method can learn human effectiveness before handing off.
2. v0.2 controller: an exact cross-episode posterior over a finite model set (valid under adaptive logging), Bayes-adaptive dynamic programming, and a conservative gate that keeps the nominal plan unless the posterior supports a switch.
3. Pre-registered benchmark: dev/validation/test/shift splits with disjoint seeds, protocol hashed before running, held-out splits run once; exact per-episode evaluation; bootstrap intervals.

**Results.** On 200 held-out synthetic environments the controller cut loss by 0.46% versus nominal (closing 30% of a small 1.9% gap to the oracle). It gained 1.0% when estimates were biased (2.3% when human help was over-estimated) and lost 0.9% when estimates were already right. Modelling persistent failures mattered most (+5.8% loss without it). The conservative gate did not beat ungated posterior planning, and under model misspecification the posterior can become confidently wrong; both are reported.

**Engineering.** `pip`-installable library (NumPy only, typed, 84 tests), `Advisor` API with explanations and warnings, CLI, SQLite agent demo, CI on three OSes, PyPI Trusted Publishing workflow, reproducible scripts with hashes and determinism checks.

**Limitations.** Synthetic environments and simulated humans; no real agents or operators; small effects on the tested distribution.

**Practical implication.** Use exact cost-aware planning with persistent-failure modelling by default; add cross-episode calibration when you suspect your success estimates are biased and you log outcomes; do not expect a confidence gate to protect you from a misspecified model.
