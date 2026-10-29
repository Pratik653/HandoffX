# handoffx 0.1.0 - research prototype

CPU-only finite-horizon intervention decision support. The core requires Python 3.11+ and NumPy. It does not use a network, LLM, API key or GPU, and it does not execute agent actions. It is not a general POMDP solver or a production safety system.

## Install and run

From this directory:

```console
python -m pip install -e ".[research]"
python -m handoffx
python examples/basic_usage.py
python examples/static_decision.py
python -m pytest -q
```

Without the research extras, `python -m pip install -e .` installs the NumPy-only decision core. The supported execution model is a stationary hidden task mode and fixed finite model index during an episode, with one-tick continue/retry actions and terminal human rescue. Short-horizon exact planning can become expensive as the number of reachable states increases. Horizons 1..12 are accepted; the main evaluation uses 3 and 6 ticks.

## Small actual API example

```python
from handoffx import Planner, State
from handoffx.scenarios import make_scenario

case = make_scenario("demonstration")  # Explicitly synthetic, not real estimates.
controller = Planner(case["spec"], case["models"], mode="bayes")
decision = controller.recommend(State())
print(decision.to_json())
```

`ModelSet` accepts outcome kernels and a joint prior. It does not infer those quantities from a raw model-confidence score. `evidence_status="calibrated"` is a caller declaration, not a statistical certificate issued by the library. The safe-stop option must be authorized externally. Missing quantitative evidence may be handled with `recommend_or_stop(None)`, whose result is explicitly unscored.

## Evidence and release status

The packaged research study contains 38 scenarios, 11 policies and 5,016,000 stored episode executions, plus an exact finite-model evaluation. Sixty deterministic tests passed on the recorded Linux host. Windows execution was not performed; the code and pathlib-based scripts avoid mandatory Unix-only dependencies. Named real LLMs and real people were not evaluated. This is an unreleased prototype; package-name availability, licensing, external security review and deployment certification have not been established.

The complete archive's `05_Experiments/REPRODUCIBILITY.md` gives end-to-end reproduction instructions. See `API_REFERENCE.md`, `DATA_MODELS.md`, and `ARCHITECTURE.md` before integrating.
