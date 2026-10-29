# Candidate A: independent confirmation

Read in this order:
1. `PRE_REGISTERED_PROTOCOL.md`: frozen before the run (commit 4d3cfce).
2. `CONFIRMATION_RESULTS.md`: confirmatory results and the frozen decision rule.
3. `MECHANISM_ANALYSIS.md`: why A reduces severe failures. §5 is exploratory.
4. `FINAL_RESEARCH_DECISION.md`: decision and next step.

Reproduce from the repository root with the project venv (raw `.npz` arrays are git-ignored):

```
python research_poc_v03/confirmation/scripts/power_analysis.py
python research_poc_v03/confirmation/scripts/run_confirmation.py smoke
python research_poc_v03/confirmation/scripts/run_confirmation.py confirm
python research_poc_v03/confirmation/scripts/analyze_confirmation.py confirm
python research_poc_v03/confirmation/scripts/mechanism_ablation.py      # exploratory, seeds 850000+
python research_poc_v03/confirmation/scripts/make_figures.py
```

Machine-readable outputs:
- `results/confirm/{summary.csv,analysis.json,run_metadata.json}`
- `results/exploratory_mechanism/{summary.csv,analysis.json}`
- `results/power_analysis.json`

Figures: `figures/confirmation_forest.png`, `figures/risk_loss_frontier.png`.
