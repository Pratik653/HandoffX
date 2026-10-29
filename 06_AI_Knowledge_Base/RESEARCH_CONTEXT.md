# Trusted handover record

HandoffX is a bounded decision-support research library and comparative simulator, not a new LLM, general POMDP solver or safety-certified controller. Continue from the actual source/configurations/results, not from a presumed winning algorithm.

## Established and adapted findings

Expected-loss deferral, Bayesian belief control, Bayes-adaptive POMDPs and rectangular robust control are prior art. P1-P9 are conditional derivations/adaptations; no mathematical priority is claimed. CE1-CE8 disprove tempting generalizations. The fixed hidden task mode induces temporal dependence; the fixed model index represents epistemic uncertainty. Robust per-history kernel selection is a different, larger uncertainty class.

## Executed evidence

38 scenarios, 11 policies, 24 batches, 500 episodes per batch; 5,016,000 stored policy-episode executions, plus exact evaluation. The entire main numerical table reproduced. A separate scalar loop matched 16,000 trajectories. Sixty pytest tests passed. Bayes vs nominal: six improvements, 23 ties, nine degradations. Coupled vs independent parameter priors: one improvement, 31 ties, six degradations. Dependence-aware vs iid-mode ablation: 15 improvements, 23 ties. A shifted out-of-set environment violates the robust reported bound's coverage premise.

## Never assume

Do not claim real-agent or human benefit, learned probability calibration, autonomous execution, universal thresholds, unconditional robust guarantees, current package-name availability, a public repository, a DOI, external peer review, or Windows testing. Human rescue is terminal. There is no passive wait action, human queue, fatigue model, nonterminal clarification or genuine repair-state transition. Safe stop must be externally authorized. A calibrated status string is not a statistical certificate.

## Evidence provenance

The active bibliography has 22 metadata-verified primary records, six with selected full-text inspection. The original 29-record audit is retained separately. Corrected records include Thede's given name, the HiL-Bench author list/order, Shaikh's arXiv/internal version distinction, and the version-specific Balazadeh record. Ross et al. (2011) strengthens the prior-art equivalence. Do not restore abandoned novelty claims or unverified old metadata.

## Next implementation work

First independently reproduce the code/results using `05_Experiments/REPRODUCIBILITY.md`. Keep primary results immutable when adding new scenarios. Prioritize probability/data contracts, Windows CI, source audit of optional adapters and a prospectively designed real-outcome study. Treat any additional sweeps after seeing these results as exploratory unless separately preregistered. Do not silently expand the accepted mathematical model without new tests and proofs.
