# Implemented API reference

All interfaces below exist in the supplied code. Proposed integrations are documented separately and must not be presented as working APIs.

## Public types and operations

| Interface | Contract |
|---|---|
| `Action` | `CONTINUE=0`, `RETRY=1`, `HUMAN=2`, `STOP=3` |
| `State(counts=(0,0,0,0,0,0), failed=False)` | Observable sufficient-count state, not hidden environment state |
| `State.next(action, outcome)` | Update a nonterminal continue/retry result; outcomes 0, 2 or 3 only |
| `TaskSpec(...)` | Immutable horizon, milestones, budget, costs, durations, availability and restrictions |
| `ModelSet(kernels, prior, names, evidence_status, center=0)` | Finite joint probability specification; copied read-only arrays |
| `ModelSet.posterior(state)` | Posterior over model and mode |
| `ModelSet.predict(state)` | Bayesian predictive array `(3,4)` |
| `ModelSet.conditionals(state)` | Model-conditional predictive laws for possible models |
| `ModelSet.one_model(index)` | Nominal conditional model |
| `ModelSet.iid_modes()` | Explicit ablation that removes within-model mode persistence |
| `ModelSet.to_dict()` / `ModelSet.from_dict(data)` | JSON-compatible data conversion |
| `ActionGuard(spec, uncertainty).allowed(state)` | Observable feasibility plus optional worst-model risk cap |
| `Planner(spec, models, mode='bayes', guard=None, name=None)` | Exact finite-horizon planning; mode `bayes` or `robust` |
| `Planner.scores(state)` | Read-only action-to-value mapping |
| `Planner.value(state=State())` | Optimal value under declared planning model |
| `Planner.action(state=State())` | Feasible action; terminal state raises |
| `Planner.recommend(state=State())` | `Decision` with values, semantics, reason and assumptions |
| `Decision.to_json()` | Stable-key JSON with no NaN values |
| `recommend_or_stop(planner, state=State())` | Explicit unscored fallback for missing/invalid model evidence |
| `Baseline(...)` | Benchmark heuristic or static committed-plan policy |

The policy protocol used by evaluation requires `name`, `spec`, and `action(state)`. The current simulator additionally uses `policy.models.predict` for its selected-action Brier diagnostic; a new policy without that field must provide a compatible predictive model or use an extended evaluation adapter. This is a research implementation constraint, not a fully generic plugin system.

## Actual supplied-model example

```python
import numpy as np
from handoffx import Action, ModelSet, Planner, State, TaskSpec

# One supplied model, one hidden mode, three actions, four outcomes.
# Outcome order: success/progress, catastrophe, soft failure, hard failure.
kernels = np.array([[[[0.70, 0.01, 0.20, 0.09],
                      [0.75, 0.01, 0.15, 0.09],
                      [0.85, 0.01, 0.14, 0.00]]]])
models = ModelSet(kernels, np.array([[1.0]]), ("elicited_example",),
                  evidence_status="assumed")
spec = TaskSpec(action_cost=(0.6, 1.4, 4.0))
planner = Planner(spec, models)
state = State()
print(planner.recommend(state).to_json())
# Only after an actual authorized continue action returned hard failure:
observed_state = state.next(Action.CONTINUE, 3)
print(planner.recommend(observed_state).to_json())
```

These example probabilities are illustrative assumed inputs. They are not estimates of an actual agent or human. A single-model input has no parameter uncertainty; supply multiple complete kernels and a joint prior to model it. Setting `mode="robust"` changes the objective and value semantics, not the evidence quality.

## Static functions

```python
from handoffx.static import expected_losses, human_threshold
# See examples/static_decision.py for the exact argument names.
```

`expected_losses` evaluates terminal-action losses; `human_threshold` implements P1 with explicit validation. They do not value future retries. Do not substitute a milestone probability for task-completion probability in a terminal-action formula.

## Error and safety behavior

Invalid probabilities, unsupported model shapes and impossible all-model likelihoods raise `ModelError`. Terminal recommendations raise `TerminalStateError`. The core does not authorize, execute, pause or roll back external actions. An unavailable action is absent from the optimized set. Tie-breaking uses rounded values at 12 decimals and the deterministic conservative order stop, human, retry, continue; sub-picounit differences are not operationally meaningful in this prototype.
