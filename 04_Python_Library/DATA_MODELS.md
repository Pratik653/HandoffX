# Data models and serialization

## State

`counts = (C_success, C_soft, C_hard, R_success, R_soft, R_hard)`, six nonnegative Python integers. `failed` is a Boolean that preserves retry eligibility when different orderings share counts. Elapsed time is the count sum because C/R last one tick. Progress is `C_success + R_success`. The state does not contain hidden mode, sampled model index, ground-truth probability, or future random outcomes. Constructing states through `next` is preferred to inventing unvalidated histories.

## TaskSpec

Defaults: horizon 6; two milestones; resource quota 7; C/R/H quota use `(1,2,3)`; direct costs `(0.6,1.4,4.0)`; durations `(1,1,2)`; time price 0.15; ordinary failure 18; stop 12; catastrophe 90. Availability is a tuple with `horizon+1` entries. One human ticket is sufficient because human rescue terminates the episode; larger values do not implement repeated assistance. `forbidden_actions` contains executable enum values; STOP cannot be forbidden in this model. Optional `severe_risk_budget` is a conditional-model risk specification, not an empirical estimate.

## ModelSet

`kernels.shape = (number_of_models, number_of_modes, 3, 4)` and `prior.shape = (number_of_models, number_of_modes)`. Every action row sums to one and the full joint prior sums to one. Model labels and a center index identify the nominal member. `evidence_status` is one of synthetic, assumed or calibrated. The synthetic generator explicitly clips its perturbations; the public model validator rejects invalid probabilities instead of normalizing them silently.

## Decision

Action string; action-value mapping; value semantics; explanation; evidence status; assumptions; admissible action names. A missing-evidence decision has an empty value mapping and must not be displayed as a computed risk or certainty. Serialized values use ordinary JSON; prototype versioning is recorded in package metadata. No personal data, API keys or model weights are needed.

## Experimental records

JSON configurations record full true and supplied models. CSV summary records distinguish exact and Monte Carlo measures. NPZ files contain one record per episode for loss, terminal outcome, elapsed time, resources, recovery use, action regret and selected-action diagnostics. These arrays contain synthetic outcomes only. The `batch` integer maps to the seed list in study.json; common random numbers are reproducible from those seeds and are never given to a controller.
