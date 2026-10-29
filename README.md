# HandoffX: completed bounded research package

Version 0.1.0 research artifact | October 28, 2026

## Start here

Read `01_Publication/HandoffX_Executive_Summary.pdf` (2 pages), then `01_Publication/HandoffX_Research_Paper.pdf` (58 pages). Editable narrative is in the DOCX; complete LaTeX and full research content are in the manuscript Markdown and `06_AI_Knowledge_Base/COMPLETE_RESEARCH_FOR_AI.md`.

**Contribution:** a finite-model comparative benchmark and auditable intervention decision-support prototype, not a new general theory of delegation. Continue, retry, fallible human rescue and authorized safe stopping are compared under explicit observations, costs, deadlines, quotas and uncertain capabilities.

## Verified execution

- Nine conditional mathematical propositions and eight counterexamples, with complete stated proofs and executable numerical checks.
- 38 designed scenarios and 11 policies: 418 exact expectations and 5,016,000 stored scenario-policy simulation executions.
- 24 seed batches of 500 episodes per cell; paired random numbers support policy comparisons. These are not 5,016,000 independent real tasks.
- All 418 non-timing numerical rows reproduced on a full rerun; a separate scalar loop matched 16,000 trajectories.
- 60 automated tests passed, examples executed, wheel built and isolated-install smoke tested.
- 22 active primary-source metadata records, with selected full-text methodology examined for six. Original audit records are retained separately.

## Principal findings

The joint-Bayesian reference policy improved nominal planning in 6 scenarios, tied in 23 and was worse in 9. Modeling persistent failure improved the independent-mode ablation in 15 and tied in 23. Explicit cross-capability coupling improved its independent-prior ablation in only 1, tied in 31 and was worse in 6. Robust planning optimized its stated rectangular objective but did not preserve coverage after unsupported distribution shift. These are conditional simulation findings, not deployment claims.

## Install and reproduce

From this extracted directory, with Python 3.11 or newer:

```sh
python -m pip install -e "./04_Python_Library[research]"
python -m pytest -q 04_Python_Library/tests
python 04_Python_Library/examples/basic_usage.py
python 05_Experiments/scripts/run_experiments.py --quick
```

The quick run writes separate outputs. To repeat all main comparisons, use the instructions in `05_Experiments/REPRODUCIBILITY.md`; preserve the supplied reference archive before overwriting result files. The included wheel is in `04_Python_Library/dist/`. Exact executed dependency versions are in `05_Experiments/requirements-executed.txt`.

## Directory map

| Directory | Contents |
|---|---|
| `01_Publication` | Manuscript DOCX/PDF/Markdown, abstract, executive summary and navigation |
| `02_Mathematics` | Formal model, proofs, assumptions, counterexamples and worked examples |
| `03_Literature` | Corrected active literature record, source verification and unchanged Phase 1 audit |
| `04_Python_Library` | Source, tests, actual examples, wheel and architecture/API documentation |
| `05_Experiments` | Protocol, configs, scripts, raw arrays, aggregates, figures and execution logs |
| `06_AI_Knowledge_Base` | Complete research handover, verified findings and open questions |
| `07_Quality_Assurance` | Mathematics, experiments, citations, document checks and internal scientific review |
| `08_Publication_Metadata` | Draft deposit metadata and owner-facing release/licensing checklist |

## Scope and release status

Executed on Linux, Python 3.13.5 and an AMD CPU host, not the user's Windows/Intel laptop. No paid API, GPU, live LLM, human participant or private operational data was used. Probability estimation, real deployment validation and external peer review remain uncompleted. The library recommends actions but never executes them or overrides external authorization. Missing evidence is not silently converted to calibrated confidence.

This is a research-stage report and prototype. The 120-150-page conditional target was not pursued through padding. Final authorship and licensing require owner decisions. No Zenodo deposit, DOI, GitHub/PyPI publication or certified open-source release is claimed. Equations in the DOCX/PDF are high-resolution LaTeX renderings; editable LaTeX is preserved in Markdown.

`MANIFEST.md` describes each file. `SHA256SUMS.txt` covers every other file, including the manifest, and excludes itself. No copyrighted source papers or fonts are bundled. `PROGRESS_LEDGER.md` records actual phase completion and corrections.
