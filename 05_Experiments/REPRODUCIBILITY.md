# Reproducibility guide

## Recorded environment

See `results/main/run_metadata.json` for actual Python, NumPy, SciPy, OS, processor, process memory, timing and configuration/source SHA-256 hashes. Computation occurred on a Linux AMD EPYC host, not on Windows or the user's Intel laptop. The algorithm is CPU-only and uses no external APIs; actual Windows execution remains unverified.

## Windows PowerShell, from the archive root

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".\04_Python_Library[research]"
$env:OPENBLAS_NUM_THREADS="1"
$env:OMP_NUM_THREADS="1"
$env:MKL_NUM_THREADS="1"
python -m pytest -q .\04_Python_Library\tests
python .\04_Python_Library\examples\basic_usage.py
python .\05_Experiments\scripts\validate_mathematics.py
python .\05_Experiments\scripts\run_experiments.py
python .\05_Experiments\scripts\audit_results.py
python .\05_Experiments\scripts\analyze_results.py
```

The PowerShell activation policy is a local system setting; using `.venv\Scripts\python.exe` directly avoids needing activation. Python 3.11+ is the declared compatibility target; the exact tested version is recorded in metadata. Pin dependencies to `requirements-executed.txt` for the closest software reproduction; use a clean environment instead of altering an unrelated project.

## Quick check

`python 05_Experiments/scripts/run_experiments.py --quick` runs two scenarios, two batches and 50 episodes per batch, writing `results/quick/` rather than overwriting the main results. Main execution overwrites the main numerical outputs; copy the supplied reference archive before running it. Reproduce from the stored JSON, rather than regenerating defaults after editing code.

## What is deterministic

The 24 PCG64 seeds and all kernel/prior/cost parameters are stored. Conditional simulation results are reproducible in the recorded environment. Every non-timing column of all 418 summary rows was identical on a complete rerun after input-validation hardening. Platform/library changes can alter floating-point ties or low-level random-number implementations; exact numerical identity on all future versions is not promised. Wall time, memory measurements, timestamps and ZIP metadata are not deterministic research outcomes.

## Files and audits

- `configs/study.json`: study names, seeds and sample sizes.
- `configs/*.json`: true environment and supplied information for each scenario.
- `results/main/raw/*.npz`: 418 compressed episode arrays, 12,000 records each.
- `summary.csv`: exact and sampled loss/outcome measures, action and timing data.
- `batch_results.csv`: 24 independent seed-batch summaries per cell.
- `paired_effects.csv`: pointwise paired differences versus six comparators.
- `robust_bound_checks.csv`: supported-model coverage and true-environment check.
- `robust_objective_evaluation.csv`: objective-aligned post-hoc fairness audit.
- `tuning.csv` and `development_configs/`: all heuristic tuning candidates.
- `results/mathematical_checks.json`: computational supplements to written proofs.
- `results/reproduction_audit.json`: stored-array checks and 16,000 scalar matches.

The complete package's checksum file covers static deliverables and explicitly excludes itself. No external scholarly paper PDFs or copyrighted fonts are bundled.
