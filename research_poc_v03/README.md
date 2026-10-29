# HandoffX v0.3 feasibility study (proof of concept)

Isolated exploratory study on branch `research/v0.3-feasibility`. It reuses the v0.2 library and benchmark code unchanged; nothing here changes the public API, the published results or the manuscript.

Start with `GO_NO_GO_DECISION.md`, then `FINDINGS.md`. Screening: `OPPORTUNITY_MATRIX.md`; hypotheses: `HYPOTHESES.md`; protocol and frozen decision criteria: `EXPERIMENT_PROTOCOL.md`.

## Progress log

- Stage A: v0.2 stored results verified (test: v2 −0.46% [−1.07, +0.09]; bayes_recal −0.63%; oracle −1.94%; no-dependence +5.79%; calibrated +0.92% / biased −1.03%); adaptive tests pass.
- Stage C diagnostics on v0.2 dev environments: headroom decomposition, grid limit, learning plateau, plateau attribution.
- Screening selected candidates A (prevalence learning), B (escalation-targeted sampling), C (Bayes-factor guard). Protocol and thresholds frozen and committed before any candidate run.

## Reproduce

```bash
python research_poc_v03/scripts/headroom_decomposition.py
python research_poc_v03/scripts/grid_limit.py
python research_poc_v03/scripts/learning_limit.py
python research_poc_v03/scripts/plateau_attribution.py
python research_poc_v03/scripts/round1_mechanism.py
python research_poc_v03/scripts/run_poc.py pilot
python research_poc_v03/scripts/run_poc.py confirm
python research_poc_v03/scripts/analyze_poc.py pilot confirm
```
