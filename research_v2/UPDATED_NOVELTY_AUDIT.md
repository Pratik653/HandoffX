# Updated novelty audit (v0.2)

v0.1 concluded (03_Literature/NOVELTY_AUDIT.md) that HandoffX is a finite-model comparative benchmark and auditable decision-support prototype, not a new theory of delegation; that conclusion stands.

## What v0.2 adds, and how it relates to prior work

| v0.2 element | Closest established work | Status |
|---|---|---|
| Cross-episode posterior over a finite model set with ignorable adaptive action selection | Bayesian inference with ignorable missingness (Rubin, 1976); Bayes-adaptive POMDP learning (Ross et al., 2011, in v0.1 bibliography) | Application, not new theory |
| Conservative switching from an incumbent | High-confidence / safe policy improvement (Thomas et al., 2015; Laroche et al., 2019) | Adaptation: posterior credible rule over exact per-model losses, without a frequentist guarantee |
| Posterior sampling across episodes | Thompson sampling (Thompson, 1933; Russo et al., 2018) | Evaluated baseline; negative result here |
| Misspecification failure (CE9) | KL-projection of posteriors under misspecification (Berk, 1966); model checking (Box, 1980) | Concrete counterexample in this decision setting |
| Deployment-stream benchmark with pre-registered dev/validation/test/shift splits and exact per-episode evaluation | Learning-to-defer benchmarks (Alves et al., 2025, v0.1 bibliography); agent benchmarks (Yao et al., 2025; Trinh et al., 2026) | Benchmark design contribution, synthetic |

## Defensible contribution statement

An open, exactly-evaluated benchmark and library for continue/retry/human/stop decisions that (i) diagnoses why within-episode Bayesian planning cannot correct biased estimates, (ii) shows that cross-episode calibration recovers part of the gap to the oracle when estimates are biased and costs a little when they are not, (iii) shows that modelling persistent failure is the dominant factor, and (iv) documents a failure mode of conservative credible gating under misspecification. No claim of state-of-the-art performance on real agents is made.

Searches for this audit were targeted (the eight new references were verified by DOI/PMLR metadata on 2026-10-29); no new systematic review was performed.
