# HandoffX demonstrations

Everything here runs locally on CPU with only `handoffx` installed (SQLite ships with Python). No network access, no paid APIs.

## Order-investigation agent (`runnable_examples/order_agent_demo.py`)

```bash
python demo/runnable_examples/order_agent_demo.py --tasks 10            # step-by-step decisions
python demo/runnable_examples/order_agent_demo.py --tasks 60 --quiet    # summary only
python demo/runnable_examples/order_agent_demo.py --tasks 200 --compare # vs. simple heuristics
```

A deterministic rule-based agent investigates delayed orders in an in-memory SQLite database. Each task has two milestones: look up the order's shipment, then query a carrier tool. Controlled, labelled conditions are injected per task:

| Condition | Share | Tool behaviour | Signal |
|---|---:|---|---|
| normal | 78% | occasional timeouts (database 8%, carrier 15%) | soft failure |
| outage | 15% | carrier returns 503 on 90% of calls | hard failure |
| permission | 7% | carrier returns 403 on every call | hard failure |
| missing data | 10% of orders | shipment row absent | hard failure |

Before each step the agent calls `Advisor.recommend(history)`; after each task it calls `record_episode`, so the advisor recalibrates its success estimates (supplied deliberately optimistic: continue 0.85). Typical behaviour: continue through timeouts, retry once after an ambiguous failure, escalate after repeated hard errors that suggest a persistent fault.

**Simulation disclosure.** The "human" is a seeded random helper that resolves 85% of escalations. Tool failures are injected. Results show the integration pattern and decision logic, not evidence about real operators, real carriers or real LLM agents.

Illustrative `--compare` output (200 tasks; seeds 7, 8, 9):

| Agent | Mean loss | Resolved |
|---|---|---|
| HandoffX | 3.43 / 3.05 / 3.16 | 188 / 194 / 192 |
| Retry twice, then escalate | 3.47 / 3.63 / 3.55 | 193 / 192 / 194 |
| Always continue | 6.12 / 5.83 / 6.04 | 148 / 152 / 150 |

Tool outcomes are drawn per call, so agents that act differently see different draws; use `benchmarks_v2/` for controlled comparisons.

## Command line

```bash
python -m handoffx --continue-success .8 --retry-success .6 --human-success .9 \
    --history continue:hard_failure,retry:hard_failure
python -m handoffx --no-human --history continue:soft_failure --json
```
