# Hypotheses (frozen before any candidate run)

Primary metric everywhere: per-environment mean exact expected episode loss over a 100-episode stream, paired relative difference against `bayes_recal` (strongest v0.2 deployable baseline). "Predictive success" and "decision success" are evaluated separately.

## Candidate A — prevalence-augmented posterior planning

- **Mechanism.** Model set M_A = M_v0.2 × {λ ∈ {−0.25, 0, +0.25}} with mode prevalence z(λ) = (1−|λ|)·ẑ + |λ|·e_k (k = transient for λ<0, persistent for λ>0), prior (0.25, 0.5, 0.25). Consecutive failures and hard error signals are more likely under the persistent mode, so λ is identifiable from AI attempts; explaining extra persistent failures through λ should stop the posterior from distorting the success offsets (CE9).
- **H_A (decision).** Mean relative loss vs. bayes_recal < 0 pooled; largest gains in `prevalence_misspec` and `shift` environments.
- **H0_A.** No difference (or worse) pooled and in the targeted kinds.
- **Predictive.** Total-variation error of the posterior-mean prevalence vs. truth is lower than the fixed supplied prevalence; root success calibration error is no worse.
- **Expected degradation.** Calibrated and success-bias-only environments (extra parameter dilutes the posterior; slower learning).
- **Falsification.** Pooled CI excludes improvement, or no improvement in `prevalence_misspec`, where the mechanism must act.
- **Sanity.** With all prior mass at λ = 0, A is identical to bayes_recal; with truth on the λ-line the posterior concentrates on the right level.

## Candidate B — escalation-targeted posterior sampling

- **Mechanism.** Sample h ~ posterior marginal of the human offset; plan with exact Bayes over models with human offset h (AI uncertainty integrated). Optimistic samples trigger escalations that break the self-confirming trap; sampling stops when the human offset is learned.
- **H_B.** Mean relative loss vs. bayes_recal < 0 pooled; largest gains in `human_bias` (and `success_bias`).
- **H0_B.** No improvement; exploration cost ≥ information value (as for full Thompson sampling in v0.2).
- **Predictive.** Lower end-of-stream human success calibration error; more human observations in under-escalating environments.
- **Expected degradation.** Calibrated environments and early episodes (exploration cost); environments where human help is genuinely poor.
- **Falsification.** Not better than bayes_recal pooled and in `human_bias`; or worse than full Thompson sampling.
- **Sanity.** With a point-mass human posterior, B equals bayes_recal.

## Candidate C — Bayes-factor reversion guard

- **Mechanism.** log BF = log Σ_m w0(m) exp(ℓ_m) − ℓ_centre, ℓ = cumulative episode log-likelihood. Use the posterior planner only if log BF > log 3; otherwise nominal. Occam's razor in the marginal likelihood should keep nominal when the estimate is right.
- **H_C.** Loss vs. bayes_recal in `calibrated` environments < 0 (less drift) with pooled loss not worse than bayes_recal by more than 0.25 percentage points.
- **H0_C.** No calibrated-environment benefit, or the delay in switching costs more in biased environments.
- **Expected degradation.** Biased environments early in the stream (switching delayed); CE9-type misspecification (the centre model is wrong, so the guard opens — it is not expected to fix CE9).
- **Falsification.** No reduction of calibrated-environment regression.
- **Sanity.** log BF is ≤ 0 before data, increases with evidence against the centre.

## Combination

If two or more candidates survive the pilot, the confirmation also evaluates their pre-specified combination (A's model set + B's sampling + C's guard as applicable). No other variants.
