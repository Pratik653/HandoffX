# HandoffX

**Auditable continue / retry / ask-a-human / stop decisions for autonomous agents under uncertainty.**

[![CI](https://github.com/Pratik653/HandoffX/actions/workflows/ci.yml/badge.svg)](https://github.com/Pratik653/HandoffX/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.13-blue)
![License](https://img.shields.io/badge/license-MIT-green)

When an agent's tool call fails, should it push on, retry, escalate to a person, or stop safely? HandoffX answers that with exact finite-horizon decision analysis: it weighs action costs, failure and severe-failure losses, deadlines, budgets, human availability and the possibility that a failure is *persistent* rather than transient, and it explains every recommendation. Version 0.2 adds **cross-episode calibration**: logged outcomes correct biased success estimates over time, and a conservative gate keeps the nominal plan until the evidence supports a change.

HandoffX is research software. It recommends; it never executes actions or overrides your authorization rules. All evidence so far comes from synthetic simulations (details and limitations below).

## Install

```bash
pip install handoffx            # after the first PyPI release
pip install "git+https://github.com/Pratik653/HandoffX.git"   # until then
```

Python 3.11+, one runtime dependency (NumPy). CPU only, no network access, no telemetry.

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

Outcomes are `success`, `soft_failure` (no diagnosis), `hard_failure` (explicit error signal such as HTTP 403/503) and `severe_failure`. Per call you can mark the human unavailable or forbid actions: `advisor.recommend(history, human_available=False, forbidden=["continue"])`. Stop always remains available.

Command line:

```bash
python -m handoffx --continue-success .8 --retry-success .6 --human-success .9 --history continue:hard_failure,retry:hard_failure
```

## Demonstration: an order-investigation agent on SQLite

```bash
python demo/runnable_examples/order_agent_demo.py --tasks 10
python demo/runnable_examples/order_agent_demo.py --tasks 200 --compare
```

A small rule-based agent investigates delayed orders with SQLite and a carrier tool that suffers injected timeouts, outages and permission errors; HandoffX decides each step and learns across tasks. Tools and the "human" are simulated and labelled as such. See [demo/README.md](https://github.com/Pratik653/HandoffX/blob/main/demo/README.md).

## How it works

```
supplied estimates ± uncertainty ──► finite model set (success offsets × latent failure modes)
                                         │
logged episodes ──► cross-episode posterior (exact Bayes; ignorable adaptive logging)
                                         │
     incumbent: nominal DP on the estimate     candidate: Bayes-adaptive DP on the posterior
                         └──────── conservative gate ────────┘
                 switch only if posterior expected loss falls and
                 P(degradation > tolerance) ≤ alpha under the posterior
                                         │
                in-episode exact DP over (progress, failures, failure type)
                                         │
              Recommendation(action, expected losses, admissible set, rationale, warnings)
```

- `handoffx.Advisor` — simple API above. `handoffx.Planner`, `ModelSet`, `TaskSpec`, `ActionGuard` — the exact finite-horizon core (v0.1). `handoffx.AdaptiveController`, `EpisodeBelief` — the v0.2 cross-episode layer for researchers.
- Mathematics: [research_v2/ADAPTIVE_POLICY_MATHEMATICS.md](https://github.com/Pratik653/HandoffX/blob/main/research_v2/ADAPTIVE_POLICY_MATHEMATICS.md) (v0.2) and [02_Mathematics/](https://github.com/Pratik653/HandoffX/blob/main/02_Mathematics/) (v0.1 model, nine propositions, eight counterexamples).

## Results (synthetic, held-out)

Pre-registered deployment-stream benchmark: 100 episodes per environment, environments drawn from a declared distribution with biased or calibrated estimates; gate tuned on 60 dev environments only; evaluated once on 200 held-out test and 100 distribution-shifted environments. Relative change in mean exact loss versus nominal planning (lower is better):

| Policy | Test (n=200) | Shift (n=100) | Note |
|---|---:|---:|---|
| **HandoffX v0.2** (calibration + gate) | −0.46% [−1.07, +0.09] | −1.06% [−2.76, +0.37] | closes 30% of the nominal→oracle gap on test |
| Ungated posterior planning | −0.63% [−1.28, −0.05] | −0.82% [−2.58, +0.73] | the gate did not add value on test |
| Point-estimate recalibration | −0.26% | −0.26% | |
| v0.1 joint-Bayes (static prior) | +0.16% | +1.10% | reproduces v0.1 finding |
| v0.2 without failure-dependence modelling | **+5.79%** | +5.79% | persistent-failure modelling matters most |
| Robust (worst-case) planning | +7.26% | +3.44% | lowest severe-failure rate and CVaR |
| Oracle (knows the truth) | −1.94% | −7.87% | headroom |

**When it helps:** biased estimates (−1.03% on 142 biased test environments; −2.25% when human effectiveness was over-estimated). **When it does not:** already-calibrated estimates (+0.92%), and model misspecification, where the posterior can become confidently wrong. Full results: [research_v2/EXPERIMENTAL_RESULTS.md](https://github.com/Pratik653/HandoffX/blob/main/research_v2/EXPERIMENTAL_RESULTS.md); root cause of the v0.1 6/23/9 result: [research_v2/ROOT_CAUSE_ANALYSIS.md](https://github.com/Pratik653/HandoffX/blob/main/research_v2/ROOT_CAUSE_ANALYSIS.md).

![Learning curves on the held-out test split](https://raw.githubusercontent.com/Pratik653/HandoffX/main/benchmarks_v2/figures/v2_learning_curves_test.png)

## Reproduce

```bash
python -m venv .venv && . .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -e ".[research]"
pytest                                              # 84 tests
python 05_Experiments/scripts/run_experiments.py    # v0.1 study (≈2 min); overwrites 05_Experiments/results/main
python benchmarks_v2/scripts/run_v2.py test         # v0.2 held-out test split (≈1 min with 16 workers)
python benchmarks_v2/scripts/analyze_v2.py validation test shift original
```

See [benchmarks_v2/reproducibility/README.md](https://github.com/Pratik653/HandoffX/blob/main/benchmarks_v2/reproducibility/README.md) for the full order (dev → freeze → validation → test → shift), hashes and environment.

## Repository layout

| Path | Contents |
|---|---|
| `04_Python_Library/src/handoffx/` | the installable package |
| `04_Python_Library/tests/` | test suite |
| `benchmarks_v2/` | v0.2 configs, scripts, results, figures, reproducibility |
| `research_v2/` | v0.2 research documents |
| `publication_v2/` | updated manuscript (Markdown, DOCX, PDF) and bibliography |
| `demo/` | runnable agent demonstration |
| `01_`–`08_*` | the original v0.1 research package, preserved (manuscript, mathematics, literature, experiments, QA) |

## Limitations

Synthetic simulations only; no real operators, LLM agents or production data. Effects are small on the tested distribution. The model set varies success probabilities but not failure-mode prevalence, which caused the worst degradations. Human effectiveness is learned only from actual escalations. Expected-loss policies did not reduce tail risk. See [research_v2/LIMITATIONS.md](https://github.com/Pratik653/HandoffX/blob/main/research_v2/LIMITATIONS.md).

## Citation

See [CITATION.cff](https://github.com/Pratik653/HandoffX/blob/main/CITATION.cff). Code: MIT. Research documents, figures and data: CC BY 4.0 ([LICENSE-docs.md](https://github.com/Pratik653/HandoffX/blob/main/LICENSE-docs.md)).
