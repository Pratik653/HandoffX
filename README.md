# HandoffX

**Auditable continue / retry / ask-a-human / stop decisions for autonomous agents under uncertainty.**

[![CI](https://github.com/Pratik653/HandoffX/actions/workflows/ci.yml/badge.svg)](https://github.com/Pratik653/HandoffX/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.13-blue)
![License](https://img.shields.io/badge/license-MIT-green)

When an agent's tool call fails, should it push on, retry, escalate to a person, or stop safely? HandoffX answers this with exact finite-horizon decision analysis. It weighs:
- action costs;
- failure and severe-failure losses;
- deadlines and budgets;
- human availability;
- the possibility that a failure is *persistent* rather than transient.

It explains every recommendation. Logged outcomes can recalibrate biased success estimates across episodes.

HandoffX is research software. It recommends; it never executes actions or overrides your authorization rules. All evidence comes from synthetic simulations.

| | |
|---|---|
| **Stable software** | `handoffx` 0.2.1: the exact planners, the cross-episode calibration layer and the `Advisor` API |
| **Research findings** | Five studies: the original framework (v0.1), the v0.2 adaptive-learning evaluation, the v0.3 feasibility screening, a pre-registered risk-reduction confirmation and an exploratory mechanism analysis. See the [final research paper](https://github.com/Pratik653/HandoffX/tree/main/publication_final) |
| **Experimental algorithms** | The v0.3 candidates (prevalence-augmented learning, targeted human exploration, Bayes-factor guard) and catastrophe-weighted planning are research scripts in `research_poc_v03/`. They are **not** included in the installable package |
| **Limitations** | Synthetic evidence only; supplied probabilities may be miscalibrated; no demonstrated universal superiority over nominal planning; no real-world safety claim |

## Install

```bash
pip install handoffx
```

Requires Python 3.11+ and one runtime dependency (NumPy). It runs on CPU only, with no network access and no telemetry. To install the development version from GitHub:

```bash
pip install "git+https://github.com/Pratik653/HandoffX.git"
```

## Quick start

```python
from handoffx import Advisor, Costs

advisor = Advisor.from_estimates(
    continue_success=0.80,   # your estimate that the next autonomous step succeeds
    retry_success=0.60,      # ... that a retry after a failure succeeds
    human_success=0.90,      # ... that a human resolves the task
    uncertainty=0.15,        # how far off those estimates might be (absolute)
    costs=Costs(human=4.0, failure=18.0, stop=12.0),
)

# Inside an episode: pass what has happened so far.
rec = advisor.recommend([("continue", "hard_failure"), ("retry", "hard_failure")])
print(rec.action)       # 'human'
print(rec.explain())    # expected loss of every admissible action, rationale, warnings

# After the episode: log it so estimates recalibrate across episodes.
advisor.record_episode([("continue", "hard_failure"), ("retry", "hard_failure"), ("human", "success")])
print(advisor.calibrated_estimates())
```

Outcomes are:
- `success`;
- `soft_failure`: no diagnosis;
- `hard_failure`: an explicit error signal, such as HTTP 403 or 503;
- `severe_failure`.

Per call you can mark the human unavailable or forbid actions: `advisor.recommend(history, human_available=False, forbidden=["continue"])`. Stop always remains available.

Command line:

```bash
handoffx --continue-success .8 --retry-success .6 --human-success .9 --history continue:hard_failure,retry:hard_failure
```

## What the research found (synthetic evidence)

| Study | Result |
|---|---|
| I. Original framework, 38 designed scenarios | Joint-Bayesian planning vs nominal planning: 6 better, 23 equal, 9 worse. Modelling persistent failures mattered most |
| II. Cross-episode calibration, pre-registered held-out test (n = 200) | Gated controller −0.46% [−1.07, +0.09] mean loss vs nominal; ungated posterior planning −0.63% [−1.28, −0.05]. The gate was not shown to add value. Removing failure persistence: +5.8% |
| III. Feasibility screening of three extensions | No average-loss improvement over ungated recalibration replicated across three independent rounds |
| IV. Pre-registered confirmation (n = 500) | Prevalence-flexible learning cut severe-failure probability by 17.8% [12.0, 24.0], about 3.2 per 1,000 episodes. Loss non-inferiority within 0.5% was **not** demonstrated (+0.28%, upper bound +0.82%), and 3.3 percentage points fewer tasks were completed |
| V. Exploratory mechanism analysis | The reduction comes from more cautious decisions, not better estimation of failure prevalence. Explicit catastrophe-weighted planning gives comparable or larger reductions along a risk–loss trade-off |

**When adaptation helps:** supplied estimates are biased in a way logged outcomes can reveal, especially an over-estimated human.

**When it does not:**
- estimates are already calibrated;
- the model set cannot represent the error, in which case the posterior can become confidently wrong.

**Also beware** that a learner which stops escalating stops learning about the human.

![Learning curves on the held-out test split](https://raw.githubusercontent.com/Pratik653/HandoffX/main/benchmarks_v2/figures/v2_learning_curves_test.png)

## Documentation and research materials

| Material | Location |
|---|---|
| **Final consolidated research paper** (Markdown, DOCX, PDF, BibTeX) | [`publication_final/`](https://github.com/Pratik653/HandoffX/tree/main/publication_final) |
| Study IV pre-registered confirmation | [`research_poc_v03/confirmation/`](https://github.com/Pratik653/HandoffX/tree/main/research_poc_v03/confirmation) |
| Study III feasibility screening | [`research_poc_v03/`](https://github.com/Pratik653/HandoffX/tree/main/research_poc_v03) |
| Study II benchmark and documents | [`benchmarks_v2/`](https://github.com/Pratik653/HandoffX/tree/main/benchmarks_v2), [`research_v2/`](https://github.com/Pratik653/HandoffX/tree/main/research_v2) |
| Earlier manuscripts (preserved, unchanged) | [`publication_v2/`](https://github.com/Pratik653/HandoffX/tree/main/publication_v2) (v0.2), [`01_Publication/`](https://github.com/Pratik653/HandoffX/tree/main/01_Publication) (v0.1) |
| Original v0.1 research package | `01_`–`08_*` |
| Research changelog | [`FINAL_RESEARCH_CHANGELOG.md`](https://github.com/Pratik653/HandoffX/blob/main/FINAL_RESEARCH_CHANGELOG.md) |

## Demonstration: an order-investigation agent on SQLite

```bash
python demo/runnable_examples/order_agent_demo.py --tasks 10
python demo/runnable_examples/order_agent_demo.py --tasks 200 --compare
```

A small rule-based agent investigates delayed orders using SQLite and a carrier tool that suffers injected timeouts, outages and permission errors. HandoffX decides each step and learns across tasks. The tools and the "human" are simulated and labelled as such. See [demo/README.md](https://github.com/Pratik653/HandoffX/blob/main/demo/README.md).

## How it works

```
supplied estimates ± uncertainty ──► finite model set (success offsets × latent failure modes)
                                         │
logged episodes ──► cross-episode posterior (exact Bayes; ignorable adaptive logging)
                                         │
     incumbent: nominal DP on the estimate     candidate: Bayes-adaptive DP on the posterior
                         └──────── conservative gate ────────┘
                                         │
                in-episode exact DP over (progress, failures, failure type)
                                         │
              Recommendation(action, expected losses, admissible set, rationale, warnings)
```

The package has three layers:
- **`handoffx.Advisor`**: the simple API above.
- **The exact finite-horizon core**: `handoffx.Planner`, `ModelSet`, `TaskSpec` and `ActionGuard`.
- **The cross-episode layer, for researchers**: `handoffx.AdaptiveController` and `EpisodeBelief`.

## Reproduce

```bash
python -m venv .venv && . .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -e ".[research]"
pytest                                              # 86 tests
python benchmarks_v2/scripts/run_v2.py test         # Study II held-out test split
python research_poc_v03/confirmation/scripts/run_confirmation.py confirm   # Study IV
```

The complete order for every study is in Appendix F of the final paper.

## Citation and licences

See [CITATION.cff](https://github.com/Pratik653/HandoffX/blob/main/CITATION.cff). Code is MIT-licensed. Research documents, figures and data are CC BY 4.0 ([LICENSE-docs.md](https://github.com/Pratik653/HandoffX/blob/main/LICENSE-docs.md)). The research has not been peer reviewed.
