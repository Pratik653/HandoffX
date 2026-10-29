# Reproducing the v0.2 benchmark

Executed environment: Windows 11, Python 3.11.9, NumPy 2.3.5, SciPy 1.17.0, Matplotlib 3.10.8, 20 logical CPUs (16 workers). Exact versions: `05_Experiments/requirements-executed.txt` (same pins). Per-split metadata and SHA-256 hashes of every script, config and library module: `benchmarks_v2/results/<split>/run_metadata.json`.

```bash
pip install -e ".[research]"
python benchmarks_v2/scripts/root_cause.py                   # Phase B decomposition of the v0.1 study
python benchmarks_v2/scripts/run_v2.py dev                   # 18 gate settings x 60 environments
python benchmarks_v2/scripts/select_gate.py                  # applies the pre-registered rule -> configs/frozen_gate.json
python benchmarks_v2/scripts/run_v2.py validation
python benchmarks_v2/scripts/run_v2.py test
python benchmarks_v2/scripts/run_v2.py shift
python benchmarks_v2/scripts/run_v2.py original
python benchmarks_v2/scripts/analyze_v2.py validation test shift original
python benchmarks_v2/scripts/make_figures_v2.py
cd benchmarks_v2/scripts && python validate_v2_mathematics.py
```

Use `--workers N` to control parallelism and `--limit N` for a smoke run (writes `<split>_smoke/`). Results are deterministic given the seeds in `configs/study_v2.json`: environments, stream randomness and Thompson-sampling draws all use NumPy PCG64 with fixed seeds, and process-pool scheduling does not affect values.

`PRE_REGISTRATION_SHA256.txt` holds the hashes of the protocol, study config, runner, environment generator and adaptive module taken before the dev run (`sha256sum -c` from the repository root verifies them). Raw per-episode arrays (`results/*/raw/episodes.npz`) are git-ignored and attached to the GitHub release.
