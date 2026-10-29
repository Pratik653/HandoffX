# Pre-registered protocol: independent confirmation of candidate A

Written, committed and pushed **before** any confirmation seed was run. The only executions before this commit were:
- a smoke run on seeds 990000+ (2 environments per kind), used solely to check that the code runs, that the outcome decomposition sums to the exact severe probability, and that the runner reproduces the frozen PoC runner;
- the precision estimate in section 6, which uses earlier PoC rounds only.

Smoke-run effect sizes were not inspected.

## 1. Hypothesis

**H1 (risk reduction).** Allowing uncertainty in persistent-failure prevalence (candidate A) reduces severe-failure probability under model misspecification, compared with ungated Bayesian recalibration (`bayes_recal`, the strongest existing HandoffX learning policy). It does so without increasing expected cumulative loss by more than 0.5%.

This is a risk-reduction hypothesis. It does not claim that A estimates prevalence better; earlier data indicate it does not (FINDINGS.md section 3). The earlier severe-failure results (−13% to −17%, a *secondary* metric in rounds 2–4) motivated this study. They are **not** counted as confirmatory evidence here.

## 2. Verified definitions

- **Severe failure**: a catastrophic outcome (kernel outcome index 1) on any executed continue, retry or human step. It ends the episode and costs `catastrophe_loss`. The per-step hazard is `q[action, mode]` (`handoffx.scenarios.kernels`).
- **Severe-failure probability of an episode**: the exact probability, under the hidden true kernel, that the policy in force for that episode ends in a severe failure. It is computed by `handoffx.evaluation.ExactEvaluator` (`metrics()[2]`, accumulated over reachable states). This is the same quantity as `exact_severe` in rounds 2–4.
- **Per-environment endpoint**: the mean of that probability over the 100 episodes of the deployment stream (`exact_severe` in `summary.csv`). Realized (sampled) severe events are recorded as a secondary count.

## 3. Candidate and comparators (frozen; no changes)

| Policy | Definition | Role |
|---|---|---|
| **A_prev** | `poc_lib.prevalence_augmented`: each of the 25 supplied grid models × prevalence levels λ ∈ {−0.25, 0, +0.25}, prior (0.25, 0.5, 0.25); exact posterior over the 75 models; ungated posterior planning refreshed every 5 episodes | candidate (identical to rounds 2–4) |
| bayes_recal | exact posterior over the 25 supplied models; same refresh | **primary comparator** |
| handoffx_v2 | frozen v0.2 gate (α = 0.35, relative tolerance 0.03) | comparator |
| nominal | exact planning on the supplied centre model; no learning | comparator |
| oracle | exact planning on the hidden truth | diagnostic reference only |
| A_static_diag | A's 75-model prior, no cross-episode learning | mechanism diagnostic, not decision-eligible |
| recal_trueprev_diag | bayes_recal whose mode prior is the **true** prevalence (privileged) | mechanism diagnostic, not decision-eligible |

All policies share the same:
- supplied information, action guard, costs and horizon;
- 100 episodes per stream with refresh cadence 5;
- common random numbers (stream seed = 7·env seed + 1).

Candidates never receive `env['truth']`, the true prevalence or future outcomes, except the explicitly privileged diagnostic `recal_trueprev_diag`.

`scripts/confirm_lib.py::run_stream` reproduces `poc_lib.run_stream` bit for bit for nominal, handoffx_v2, bayes_recal and A: maximum |exact-loss difference| was 0.0 in one smoke environment of each kind. It only adds outcome breakdowns. No production library code is changed.

## 4. Environments (`scripts/confirm_lib.py::confirm_environment`)

Each environment takes its task specification (horizon, costs, deadlines, human availability) and supplied estimate from the v0.2 i.i.d. draw (`draw_environment(seed, 'iid')`). The hidden truth is then built from the supplied centre estimate (p[action, mode], q, prevalence z) as follows. The generator stream is PCG64(seed + 31).

| Kind | n | Truth | Purpose |
|---|---|---|---|
| **persist_shift** (Family A) | 150 | sub-type uniformly from: *prevalence* (z moved toward the persistent or transient vertex by s ~ U(0.10, 0.40), random sign, then Dirichlet(50·) noise); *dependence* (AI continue/retry success in the two non-transient modes multiplied by r, log r ~ U(log 0.4, log 1.6); prevalence exact); *both*. Human kernels and hazards unchanged | primary: persistent-failure shift |
| **human_shift** (Family B) | 150 | prevalence exact; AI success ± U(−0.02, 0.02); human shift b = ±U(0.10, 0.30) applied as *uniform* (all modes), *mode_flat* (human success equal in every mode, so it no longer depends on the fault mode), or *persistent_only* (only the persistent-mode human success) | primary: human-effectiveness shift independent of prevalence |
| hazard_shift | 40 | hazards × h, log h ~ U(log 1.3, log 2.5); success and prevalence exact | secondary shift mechanism (hazard without persistence) |
| calibrated | 40 | truth = supplied estimate | control |
| near_nominal | 40 | biases U(−0.03, 0.03), prevalence Dirichlet(200·) noise | control: nominal near optimal |
| ai_bias | 40 | AI success ±U(0.10, 0.25); human and prevalence exact | control: biased AI recovery |
| joint_bias | 40 | AI ±U(0.10, 0.25) and human ±U(0.10, 0.25), independent signs | control: simultaneous AI + human miscalibration |

Seeds: 800000 + 1000·k + i (k = kind index in the order above, i < n). These do not overlap with v0.2 (100000–499999), the PoC rounds (450000–799999) or the smoke run (990000+).

Independence from earlier generators:
- The *dependence* and *mode_flat* / *persistent_only* mechanisms, and the hazard-only shift, are new.
- The *prevalence* sub-type and the *uniform* human sub-type resemble the earlier `prevalence_misspec` and `human_bias` kinds, with different magnitudes and new seeds.
- Earlier held-out environments are not reused, and nothing was tuned.

## 5. Endpoints and statistical method

Let S_p(e) be the per-environment severe endpoint and L_p(e) the cumulative exact loss over the 100 episodes. Means over environments weight kinds equally; the two primary families have equal n.

**Primary endpoint** (target distribution T = persist_shift ∪ human_shift, 300 environments):
- ARD = mean_e[S_A(e) − S_R(e)] (paired);
- RRR = 1 − mean S_A / mean S_R (ratio of means);
- 95% percentile intervals from 10,000 paired bootstrap resamples of environments, stratified by kind (seed 13).

**Loss non-inferiority** (on T):
- Δ_L = mean L_A / mean L_R − 1.
- A is non-inferior if the one-sided 97.5% upper bound (the upper end of the same 95% interval) is < +0.5%.
- The point estimate alone is not sufficient.
- The mean of the per-environment relative differences is reported as a secondary.

**Robustness**: the same statistics separately for persist_shift, human_shift, hazard_shift and every control kind, and per sub-type. No pooled result is reported without its parts.

**Safeguards and secondaries** (per kind): A vs handoffx_v2 and nominal, and these exact probabilities or expected counts:
- human escalation;
- unnecessary escalation (`excess_handoff`, an escalation the oracle scores worse than an alternative);
- retries;
- stopping;
- stopping where the oracle would not stop;
- escalations the oracle would not make;
- severe failure split by the action on which it occurs (continue / retry / human);
- severe failure at states where the oracle would act differently;
- decision regret;
- seconds per stream;
- expected and realized severe-event counts.

**Mechanism** (section 8 questions; descriptive; no decision role):
- end-of-stream prevalence error, AI and human root calibration error and signed bias;
- per-environment Spearman associations between A's severe change and these changes;
- the A_static_diag and recal_trueprev_diag contrasts;
- sub-type contrasts. *Dependence* is structurally outside A's model family; *prevalence* is close to it.

## 6. Precision estimate (before execution; `scripts/power_analysis.py`, `results/power_analysis.json`)

Inputs: per-environment SDs of the paired differences from the closest earlier kinds, rounds 3–4, 100 environments each:
- persist_shift ≈ prevalence_misspec: SD(ΔS) 0.0058, baseline severe 0.0144;
- human_shift ≈ human_bias: SD(ΔS) 0.0051, baseline 0.0149.

| Quantity | Value |
|---|---|
| Pooled SE(ARD), n = 300 | 0.00031; minimum detectable RRR at 80% power ≈ 6% |
| Pooled power for RRR = 10% | > 0.99 |
| persist_shift alone (n = 150) | min. detectable RRR ≈ 9%; power at RRR 10% ≈ 0.87 |
| human_shift alone (n = 150) | min. detectable RRR ≈ 8%; power at the earlier human_bias effect (RRR ≈ 7%) ≈ 0.76 |
| Loss NI, approx. SE(Δ_L) | 0.22%; power 0.63 if the true Δ_L = 0, 0.89 if −0.2%, 0.28 if +0.2% |
| Control kinds (n = 40 each) | descriptive only: min. detectable RRR roughly 20–25%; they can detect large harms, not small ones |

The sample was raised from the suggested ~300 to 500 environments (300 in the target families) for these reasons:
- with 50 per family, single-family estimates and the loss bound would have been too imprecise;
- the compute cost is a few minutes.

The NI test has only moderate power if A's true loss effect is near zero. In that case an inconclusive loss result is expected and will be reported as such.

## 7. Decision rule (frozen; applied by `scripts/analyze_confirmation.py`)

**NO-GO** if any of:
- (a) *not replicated*: ARD 95% upper bound ≥ 0 and RRR < 5%;
- (b) the loss increase is confirmed beyond the margin: lower bound of Δ_L > +0.5%;
- (c) the benefit is absent in one primary family: that family's ARD point estimate ≥ 0;
- (d) any kind shows a significant severe-failure *increase*: ARD lower bound > 0.

**GO** if all of:
- the primary is met: ARD upper bound < 0 **and** RRR ≥ 10%;
- non-inferiority is met;
- robustness is met: both primary families have ARD < 0 with RRR ≥ 5%, and hazard_shift shows no significant severe increase;
- no kind's loss ratio has a lower bound above +1%.

**CONDITIONAL GO** otherwise.

The comparator is bayes_recal throughout. The comparisons with handoffx_v2 and nominal are reported but do not enter the rule. The run is executed once. Candidate A and the analysis are not changed after the results are seen; any later analysis is labelled exploratory.

## 8. Mechanism questions (answered descriptively in MECHANISM_ANALYSIS.md)

Does the benefit come from:
- more accurate persistent-failure inference: prevalence error of A vs the fixed supplied prevalence;
- better-calibrated AI recovery estimates;
- more conservative actions: stopping and escalation rates;
- fewer retries;
- more escalation;
- compensation for structural misspecification: the *dependence* sub-type vs the *prevalence* sub-type, and A vs recal_trueprev_diag?

## 9. Out of scope

This study covers no real agents or operators, no production library change, no manuscript change, and no PyPI or Zenodo publication.
