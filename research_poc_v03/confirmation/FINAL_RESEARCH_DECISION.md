# Final research decision: candidate A

## Decision: **CONDITIONAL GO**, re-scoped

The frozen pre-registered rule returns CONDITIONAL GO.

| Criterion | Result |
|---|---|
| Primary: severe-failure reduction vs ungated Bayesian recalibration | **Confirmed.** RRR 17.8% [12.0, 24.0]; ARD −3.2 per 1,000 episodes [−4.4, −2.1]; n = 300 fresh target environments |
| Robustness across shift mechanisms | **Met.** 18.4% under persistent-failure shift, 17.3% under human-effectiveness shift, 23.2% under hazard shift; reduction in all 7 kinds, no kind with a severe increase |
| Loss non-inferiority (0.5% margin, one-sided 97.5% bound) | **Not demonstrated.** +0.28% [−0.21, +0.82] |
| Unacceptable trade-offs | Two real costs: +1.14% [+0.27, +2.11] loss under human-effectiveness shift, and +1.01% [+0.24, +1.98] vs nominal when estimates are correct. Both are below the pre-set "unacceptable" threshold (a lower bound above +1%) but are not negligible |

The severe-failure reduction is real and robust within the tested model families. Within them it is not a statistical accident and not tied to one generator.

What it *is* changes the development case. A reduces severe failures by becoming more conservative:
- it stops more, retries less, and completes about 3 fewer tasks per 100;
- it reaches a severe-failure rate below that of the loss-optimal oracle;
- its prevalence estimates do not explain the gain (MECHANISM_ANALYSIS.md).

It also misattributes human-effectiveness errors to persistent faults, and then escalates more to a human who is worse than assumed.

## Answer to the study question

**Should HandoffX v0.3 be developed specifically as a risk-sensitive intervention controller?**

**Yes, as a risk-sensitive controller, but not by shipping candidate A as the mechanism.**

The evidence supports the *goal*: a controller that trades a small amount of expected loss, or task completion, for materially fewer severe failures under misspecification. It does not support A's *implementation* as the product, for three reasons:
1. **Its conservatism is implicit and fixed.** A's risk level comes from an asymmetric prior and from absorbing misfit. Users cannot set it. In the exploratory frontier, an explicit catastrophe weight reaches 20–75% reductions with a monotone, predictable loss cost.
2. **It confounds human errors with fault prevalence.** That produces the Family-B loss cost (+1.1%, up to +4.1% in one sub-type), an identifiability problem rather than a tuning problem.
3. **It does not estimate what its name suggests.** A has no claim to "persistent-failure prevalence estimation".

The one exploratory result in A's favour: at matched risk it beat a uniform catastrophe weight by 0.8% in loss [0.19, 1.49]. This suggests that *evidence-triggered* conservatism has value beyond a fixed penalty. It is the hypothesis worth confirming next.

Further development of *average-loss* improvements on this decision structure should stop: three studies now agree the deployable methods sit within about 0.5% of each other.

## Smallest justified next step

- **This outcome (CONDITIONAL GO).** Run one more pre-registered, fresh-seed test of the *explicit-risk* framing, about 300 target environments and minutes of CPU:
  - Arms: A against bayes_recal with a fixed catastrophe weight chosen on the exploratory set (×1.25), at matched severe risk.
  - Primary endpoint: loss at matched risk.
  - Include A with a symmetric prevalence prior (mean prevalence = supplied) to remove the prior asymmetry.
  - Report Family B separately.
  - If A's matched-risk loss advantage holds, build v0.3 as "explicit risk weight + prevalence-flexible learning", with the human/prevalence confound documented. If it does not, build v0.3 on the explicit risk weight alone. The existing `Advisor` already exposes `severe_risk_budget`, so this is small.
- **If it had been GO.** Prototype a risk-sensitive `Advisor` mode behind a flag, with the calibration cost in the docs. Not applicable.
- **If it had been NO-GO.** Stop algorithm work. Document v0.2 as final for average loss, and recommend explicit catastrophe weights as the risk control. Not applicable.

## Integrity notes

- Primary endpoint, comparator, thresholds, environments, seeds, sample size and statistics were committed and pushed (4d3cfce) before the confirmation run. They were run once and not changed afterwards.
- The sample was raised from about 300 to 500 environments *before* execution, because of the precision estimate (§6 of the protocol).
- The mechanism ablations (prior-mean, catastrophe-weight frontier) are post hoc, run on separate fresh seeds, and do not enter the decision.
- Synthetic environments only. Nothing here measures real agents, real operators or real costs, and no claim of generalization to real systems is made.
- Production library, manuscript, PyPI, Zenodo and `main` are unchanged.
