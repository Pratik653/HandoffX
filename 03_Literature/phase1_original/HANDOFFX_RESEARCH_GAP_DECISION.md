# HandoffX Phase 1 decision — ranked research contributions

**Decision date:** 28 October 2026. **Outcome:** **C** as the default publication framing; **B** only if new results survive rigorous comparison. **No claim of a new general optimal-stopping theorem.**

## Rank 1 — Joint-uncertainty and dependent-retry **benchmark + matched comparison** (SELECTED)

**Precise research question:** Across bounded multi-step tool-using tasks, how do calibration errors in **both** autonomous recovery and human-assisted resolution, coupled through persistent failure modes, affect the policy regret, severe-failure rate and intervention cost of static thresholds, calibrated expected-loss, sequential MDP, robust/ambiguity-aware MDP and simple retry-first policies, under equal observations and resource budgets?

**Closest research:** Mozannar & Sontag (2020), Verma & Nalisnick (2022), Verma et al. (2023), Balazadeh Meresht et al. (2022), Cubuktepe et al. (2021), Alves et al. (2025), Shaikh (2026), Fanconi & van der Schaar (2025), HiL-Bench (2026).

**Distinction:** not new Bellman mathematics; rather, a reproducible evaluation protocol with a **four-action, action-dependent tool-agent simulation**, controlled correlated retry failures, imperfect operator response, joint calibration and limited outcome visibility. Each baseline must receive the same observation channels, tune/compute budget and allowed actions. Report oracle comparisons only when the simulator provides ground truth; report identifiability limits for real traces.

**Evidence for gap:** existing works separately cover switching control, L2D, human capacity, uPOMDP robustness, LLM model escalation, help-seeking tests. In the *inspected source set*, none explicitly validates all these conditions simultaneously. **This is not proof of global nonexistence.**

**Laptop fit:** High. 16 GB RAM, CPU, Windows 11, NumPy/SciPy/pandas/pytest; tabular finite-state simulation, exact small-state dynamic programming and Monte Carlo. No local 7B+ model or expensive API required for Phase 2.

**Open source:** High — simulator + baseline suite + calibration audit + experiment manifests + JSON decisions. Maintain separation from LLM frameworks. Clear outputs `recommendation`, `expected_loss_by_action`, `assumptions`, `uncertainty`, `safety_policy_overrides`.

**Redundancy risks:** Very high for any claim that four actions or robust optimization themselves are new; medium-high for benchmark concept because OpenL2D/HiL-Bench/τ² exist. Distinctiveness must be demonstrated by the controlled *joint-estimation + retry dependence* comparison and transparent counterfactual design.

**Effort estimate (not a delivery promise):** literature expansion 40–80 person-hours; simulator/test harness 50–90; baselines 40–80; calibration/shift experiments 50–100; analysis/write-up 40–80; total approximately **220–430 person-hours** depending on depth.

## Rank 2 — Selective-label estimation of joint AI and human rescue effectiveness

**Question:** Under what logged action-selection mechanisms can a controller calibrate both `P(retry resolves | history)` and `P(human resolves | history)` with partially missing counterfactual outcomes, and what abstention/uncertainty flags should prevent unjustified optimization?

**Closest:** Ghoummaid & Shalit (2024), Hemmer et al. (2023), Charusaie et al. (2022), Rosenthal et al. (2011), OpenL2D (2025).

**Distinction:** target post-failure state-dependent recovery/rescue estimation, heterogeneous human availability and selection bias in tool-agent traces. The causal theory is not new; a careful calibrated estimator and negative findings could be valuable.

**Evidence:** literature explicitly flags lack of human labels and confounded outcomes; the missing specific after-failure intervention setting is plausible in this targeted corpus, not verified globally.

**Laptop fit:** High for synthetic data and small tabular models. **Open source:** strong calibration/propensity diagnostics. **Risk:** positivity violations, unverifiable no-unmeasured-confounding, borrowed causal results, insufficient real traces. **Effort:** approximately 260–520 person-hours, mostly study design, estimation and sensitivity.

## Rank 3 — Transfer and recalibration audit across model-agnostic tool-agent adapters

**Question:** Which decision variables and policies remain valid when changing model/tool/operator under action-conditional drift, and what inexpensive recalibration or refusal rules recover defensible performance?

**Closest:** Raghu et al. (2019), Verma et al. (2023), Jitkrittum et al. (2023), Cortes et al. (2026), Huq et al. (2026), Shaikh (2026), MAP (2026).

**Distinction:** external standardized logs and cross-environment controlled swaps with same decision core. **Evidence:** distribution shift and operator composition influence deferral performance; little direct proof of model-agnostic *outcome* transfer in reviewed papers. **Laptop fit:** High for simulated swaps; medium for actual LLM trace production. **Open source:** adapter contracts and drift dashboards; **Risk:** thin novelty, dataset domain mismatch. **Effort:** approximately 180–350 person-hours for synthetic experiments; more if collecting new real-agent traces.

## Selected bounded scientific contribution

> A source-traceable, CPU-reproducible benchmark and comparative evaluation of **four-action, model-agnostic intervention policies for multi-step tool agents**, focusing on **jointly misestimated AI recovery and human rescue outcomes**, **dependent retries**, selective observation and cross-context calibration — with no assumption that robust policies are best and with established MDP/L2D methods as strong baselines.

**Primary outcome:** cumulative loss relative to simulator oracle at matched information. **Secondary outcomes:** severe failure probability; human load; task success; time; empirical and conditional calibration error; cost; robustness gap after shift. **Negative result is acceptable.**

**Success criterion:** reproducible effect estimates with uncertainty intervals and no dominated/broken baseline. **Failure criterion:** no distinct effect beyond straightforward well-calibrated established methods; publish as careful replication and evaluation rather than mathematical breakthrough.

## Publication claim ceiling

Before results: **research gap hypothesis and source-grounded Phase 1 decision only**. After simulation: only simulation evidence. After real-user or real-agent validation: claim only the measured domains. Mathematical reliability cannot be marketed as broad real-world safety. Zenodo DOI is not peer review.
