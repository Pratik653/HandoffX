# 8. Reference library architecture

## 8.1. Purpose and non-goals

<<v01|## ARC-01.|## ARC-02.>>

## 8.2. Components and responsibility boundaries

The integration pipeline runs:

adapter evidence → validated model and state → external action guard → decision engine → auditable recommendation → separately authorized executor.

Simulation and evaluation remain independent of external execution, and the executor is not included. Authorization filtering precedes optimization: expected utility cannot restore a forbidden action. Safe stop is an explicit assumption, not a universal remedy for physical processes where stopping can itself be dangerous.

**Table {T:modules}.** *Modules of the `handoffx` package (version 0.2.1)*

| Module | Implemented responsibility | Not implemented |
|---|---|---|
| `models.py` | Immutable count state; validated costs, kernels and joint priors; log posterior | Learned calibration, arbitrary state transitions |
| `static.py` | Terminal-action expected losses and human threshold (P1) | Sequential control |
| `policies.py` | Action guard, exact Bayes/nominal DP, rectangular robust DP, baselines, explanations | General constrained-POMDP solver; autonomous executor |
| `scenarios.py` | Synthetic kernels, the 38 Study I specifications, serialization | Real-agent dataset adapters |
| `evaluation.py` | Exact expectations and grouped CRN simulation | Real causal counterfactual inference |
| `adaptive.py` | Cross-episode posterior (`EpisodeBelief`), conservative gate (`AdaptiveController`), episode likelihoods, exact per-model losses | Frequentist guarantees; prevalence-augmented or risk-weighted learners (research code only) |
| `advisor.py` | `Advisor` integration API: recommendations with explanations, episode recording, calibrated estimates | Probability estimation from raw model confidence |
| `__main__.py` | Command-line recommendations (`handoffx`, `python -m handoffx`) | Production service |

The Study III–V candidates (A, B, C and catastrophe weighting) exist only as research scripts under `research_poc_v03/`. They are **not** part of the installable package.

## 8.3. Mathematical traceability

<<v01|## ARC-03.|## ARC-04.>>

Cross-episode layer:
- (9) maps to `EpisodeBelief.update` and `posterior_models`;
- (10) maps to `AdaptiveController.select`;
- the `Advisor` composes these with a supplied estimate turned into a finite model set: success offsets crossed with latent failure modes.

## 8.4. Data contracts, validation and error handling

<<v01|## ARC-04.|## ARC-05.>>

<<v01|## ARC-06.|## ARC-07.>>

**Numerical correction in version 0.2.1.** `EpisodeBelief.posterior_models()` previously raised `ModelError` when decisive evidence drove a model's posterior weight below the smallest representable double. The posterior model set then contained a model with zero mass, which `ModelSet` rejects. Version 0.2.1 floors such weights at the smallest normal double ($\approx2.2\times10^{-308}$) before forming the posterior model set:
- the perturbation is below $10^{-307}$ per model;
- weights that did not underflow are bit-for-bit unchanged, which a regression test checks;
- predictions equal those of the model set without the underflowed model to within $10^{-15}$.

The defect was not triggered in any reported run.

## 8.5. State transitions, performance and caching

<<v01|## ARC-05.|## ARC-06.>>

<<v01|## ARC-07.|## ARC-08.>>

## 8.6. The `Advisor` integration API

Version 0.2 added a small API for agent developers. A caller supplies:
- point estimates of AI continuation, retry and human success;
- an uncertainty width;
- costs.

The `Advisor` then:
1. builds the finite model set around those estimates;
2. recommends an action for the current in-episode history;
3. after each episode, updates the cross-episode posterior through `record_episode`.

AI success estimates are interpreted as marginal success probabilities; the success probability without a fault is solved from the supplied persistent-fault rate.

```python
from handoffx import Advisor, Costs

advisor = Advisor.from_estimates(continue_success=0.80, retry_success=0.60, human_success=0.90,
                                 uncertainty=0.15, costs=Costs(human=4.0, failure=18.0, stop=12.0))
rec = advisor.recommend([("continue", "hard_failure"), ("retry", "hard_failure")])
print(rec.action)      # 'human'
print(rec.explain())   # expected loss of every admissible action, rationale and warnings
advisor.record_episode([("continue", "hard_failure"), ("retry", "hard_failure"), ("human", "success")])
```

Recommendations list:
- every admissible action's expected loss;
- the admissible set after authorization filtering;
- warnings when a parameter is still prior-only (for example, when no escalation has yet been observed; Proposition A2).

Per call, the human can be marked unavailable and actions forbidden; stop always remains available.

## 8.7. Integrations and security

<<v01|## ARC-08.|## ARC-09.>>

## 8.8. Packaging, distribution and testing

The package is distributed as `handoffx` under the MIT licence:
- Python 3.11 or later;
- one runtime dependency (NumPy);
- a `py.typed` marker;
- a console entry point.

Research datasets, manuscripts and benchmark results are excluded from the wheel. Version 0.2.1 has 86 automated tests. Continuous integration runs them on Linux, Windows and macOS with Python 3.11–3.13, and also checks the command-line interface, the agent demonstration, building and a clean wheel installation. Releases are built and published by a GitHub Actions workflow using PyPI Trusted Publishing (OpenID Connect) from a protected environment, so no long-lived token is stored. Distribution status at the time of writing is recorded in the repository's release report. This paper does not assume publication.

## 8.9. Controlled agent demonstration

A deterministic rule-based agent investigates delayed orders in SQLite, using a carrier tool subject to injected faults:
- timeouts;
- outages (HTTP 503);
- permission errors (HTTP 403).

It calls the `Advisor` before each step and logs each task. The human helper is simulated and resolves 85% of escalations. The advisor continues through timeouts and escalates after repeated hard errors.

In an illustrative comparison over 200 simulated tasks and three seeds:

**Table {T:demo}.** *Illustrative agent demonstration (200 simulated tasks per seed)*

| Policy | Mean loss by seed |
|---|---|
| HandoffX | 3.43, 3.05, 3.16 |
| Retry twice, then escalate | 3.47, 3.63, 3.55 |
| Always continue | about 6 |

This demonstrates integration and behaviour, not real-world effectiveness.

# 9. Experimental methodology

## 9.1. Common principles

All five studies share four design principles:
1. **Equal information.** Every non-oracle policy receives the same supplied estimate, model set, costs, action guard and observations. No policy observes hidden modes, true parameters or future random outcomes.
2. **Exact evaluation.** Expected loss and severe-failure probability are computed exactly under the hidden true model for each policy in force (`ExactEvaluator`). Simulation is used for paired intervals (Study I), realized event counts and to drive learning.
3. **Common random numbers.** Policies share the hidden-mode and outcome uniforms within an environment, which pairs comparisons without exposing future outcomes.
4. **Separation of design and evaluation.** Each study froze its protocol before evaluation data were run, as summarized in Table {T:studies}. Held-out data from earlier studies were never reused for tuning.

**Table {T:studies}.** *Design of the five studies*

| | Study I | Study II | Study III | Study IV | Study V |
|---|---|---|---|---|---|
| Unit | Designed scenario | Environment stream (100 episodes) | Environment stream | Environment stream | Environment stream |
| Sample | 38 scenarios × 11 policies; 24 batches × 500 episodes | dev 60, validation 60, test 200, shift 100 | pilot 72, confirmation 300, replication 300 | 500 (300 target) | 220 |
| Primary endpoint | Exact loss difference vs nominal | Relative change in mean exact loss vs nominal | Relative change in mean exact loss vs bayes_recal | Severe-failure probability vs bayes_recal (ARD, RRR) | None (descriptive) |
| Protocol | Recorded locally before main run | Pre-registered, hashed | Frozen per round | Pre-registered, pushed before run | Post hoc, fresh seeds |
| Seeds | 20261028 + 997i | 100000–499999 | 500000–799999 | 800000–806149 | 850000+ |
| Status | Descriptive | Held-out | Screening | Confirmatory (primary) | Exploratory |

## 9.2. Study I: original benchmark

<<v01|## EP-01.|## Implementation and baseline fairness|+1|keepstart>>

## 9.3. Study II: deployment-stream benchmark

**Environments.** Each environment draws:
- supplied estimates around the Study I base parameters: success perturbations U(−0.04, 0.04), a hazard multiplier log-uniform on [0.2, 1.5] and Dirichlet mode prevalence;
- a hidden truth that is exactly calibrated with probability 0.25, and otherwise has independent AI and human success biases U(−0.2, 0.2);
- task costs, deadlines (4 to 6 steps), human delays and availability.

The shift family uses biases U(−0.3, 0.3) that can fall outside the model support, hazards 1.5 times higher, and more persistent failures.

**Model set.** A 5 × 5 grid of AI and human success offsets {−0.2, −0.1, 0, 0.1, 0.2} with three latent modes. Prior weights are proportional to (0.1, 0.2, 0.4, 0.2, 0.1) on each axis. Nominal planning uses the centre model.

**Streams and metrics.**
- 100 episodes per environment; learning policies refresh every 5 episodes.
- The primary metric is the per-environment mean exact expected episode loss, relative to nominal planning.
- Secondary metrics are severe-failure probability, human-escalation rate, success, empirical CVaR95 of realized loss (Rockafellar & Uryasev, 2000), calibration error and wall time.
- Inference uses paired environment-level bootstrap intervals (10,000 resamples) and win/tie/loss counts at a 1% practical tolerance.

**Splits.**
- Development (60 environments): the gate grid of 6 α × 3 tolerance values was searched here.
- Validation (60), test (200) and shift (100) use disjoint seed ranges.
- The gate was selected by a pre-registered rule, committed and then validated; test and shift were run once afterwards.
- The protocol, environment generator, runner and adaptive module were hashed before the first development run.
- The 38 Study I scenarios were replayed for diagnosis only.

## 9.4. Study III: feasibility screening

**Diagnostics** were run on Study II development environments only:
- headroom decomposition;
- a grid-resolution limit;
- 400-episode learning curves;
- plateau attribution.

**Environment kinds.** Six kinds, in equal numbers:
- calibrated;
- success_bias: AI and human biases U(−0.2, 0.2);
- prevalence_misspec: prevalence moved toward a vertex by U(0.10, 0.35);
- human_bias: human ±U(0.10, 0.25);
- mixed: the Study II i.i.d. family;
- shift: the Study II shift family.

**Comparisons and metric.** Candidates A, B and C (Section 6.3) and their combinations were compared with bayes_recal, handoffx_v2, nominal, Thompson sampling and the oracle. The primary metric was the paired relative difference in per-environment mean exact loss against bayes_recal, with kinds weighted equally and kind-stratified 95% bootstrap intervals.

**Frozen decision criteria** (against bayes_recal):
- **GO**:
  - pooled mean ≤ −0.5% with the upper confidence bound below 0;
  - calibrated kind ≤ +0.5% vs nominal;
  - pooled severe-failure probability not more than 10% (relative) above bayes_recal;
  - compute ≤ 5× bayes_recal.
- **CONDITIONAL GO**: a CI-supported gain of at least 0.5% in the candidate's pre-specified target kinds, with the pooled upper bound ≤ +0.25%.
- **NO-GO** otherwise.

**Rounds.**
1. Mechanism checks.
2. Pilot: 12 environments per kind, seeds 500000+.
3. Confirmation: 50 per kind, seeds 600000+.
4. Targeted replication: 50 per kind, seeds 700000+, pre-registered after Round 3.

## 9.5. Study IV: pre-registered confirmation

The protocol was committed and pushed to the public repository before any confirmation seed was run.

**Hypothesis.** Allowing uncertainty in persistent-failure prevalence (candidate A, frozen exactly as in Study III) reduces severe-failure probability under misspecification compared with bayes_recal, without increasing expected cumulative loss by more than 0.5%.

**Endpoint.** For environment $e$ and policy $p$, let $S_p(e)$ be the 100-episode mean of the exact per-episode severe-failure probability and $L_p(e)$ the cumulative exact loss. On the target distribution $\mathcal T$:

$$\mathrm{ARD}=\frac{1}{|\mathcal T|}\sum_{e\in\mathcal T}\big[S_A(e)-S_R(e)\big],\qquad \mathrm{RRR}=1-\frac{\overline{S_A}}{\overline{S_R}},\qquad \Delta_L=\frac{\overline{L_A}}{\overline{L_R}}-1. \tag{14}$$

Here $R$ denotes bayes_recal and bars denote means over environments with kinds weighted equally. ARD is an absolute difference in probability, and RRR a relative reduction computed as a ratio of means.

**Environments.** Task specifications and supplied estimates come from the Study II i.i.d. draw; hidden truths are set per kind:

**Table {T:s4kinds}.** *Study IV environment kinds*

| Kind | n | Hidden truth |
|---|---|---|
| **persist_shift** (Family A) | 150 | prevalence shift by U(0.10, 0.40), and/or persistence strength scaled by log-uniform [0.4, 1.6] within non-transient modes; human kernels and hazards unchanged |
| **human_shift** (Family B) | 150 | prevalence exact; human success shifted by ±U(0.10, 0.30), uniformly, made independent of the fault mode (*mode_flat*), or only in the persistent mode |
| hazard_shift | 40 | hazards ×1.3–2.5 |
| calibrated | 40 | control |
| near_nominal | 40 | biases ≤ 0.03 |
| ai_bias | 40 | control |
| joint_bias | 40 | AI and human biased |

The target distribution $\mathcal T$ is Families A and B together, 300 environments.

**Statistics.**
- 10,000 paired bootstrap resamples, stratified by kind, seed 13.
- Primary success: ARD 95% upper bound < 0 **and** RRR ≥ 10%.
- Loss non-inferiority: the one-sided 97.5% upper bound of $\Delta_L$ < +0.5%. A point estimate alone is not sufficient.

**Precision estimate.** This was made before execution from Study III data only:
- pooled minimum detectable RRR ≈ 6% at 80% power;
- power for the loss non-inferiority test only 0.63 if the true $\Delta_L=0$.

This estimate raised the sample from about 300 to 500 environments.

**Frozen decision rule.**
- **NO-GO** if any of the following holds:
  - not replicated: upper bound ≥ 0 and RRR < 5%;
  - the loss lower bound exceeds +0.5%;
  - one target family shows no reduction;
  - any kind shows a significant severe-failure increase.
- **GO** if the primary criterion, non-inferiority and robustness (both families RRR ≥ 5%) are all met, and no kind's loss lower bound exceeds +1%.
- **CONDITIONAL GO** otherwise.

The confirmation runner reproduced the frozen Study III runner bit for bit: maximum exact-loss difference 0.0 in one environment of each kind.

## 9.6. Study V: exploratory mechanism analysis

Study V was designed after the Study IV results were seen and played no role in the decision. It used fresh seeds 850000+:
- 60 environments per target family;
- 20 per other kind;
- 220 in total.

Policies compared:
- bayes_recal, candidate A, nominal and the oracle;
- **pess_prior_recal**: bayes_recal with candidate A's prior-mean prevalence fixed;
- catastrophe-weighted planning (13) with $c\in\{1.25,1.5,2,3\}$.

Study V also analyses the pre-registered Study IV mechanism metrics:
- stopping, escalation, retries, success;
- severe failures by action;
- end-of-stream prevalence and calibration errors;
- a privileged diagnostic that knows the true prevalence.
