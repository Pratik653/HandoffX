# Changelog

All notable changes to this project are documented here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses [Semantic Versioning](https://semver.org/).

## [0.2.1] - unreleased (first PyPI release)

### Fixed
- `EpisodeBelief.posterior_models()` no longer raises `ModelError` when a model's posterior weight underflows to exactly zero after decisive evidence; finite weights that underflow are floored at the smallest normal double (perturbation below 1e-307 per model), and models with exactly zero likelihood are ruled out and omitted from the returned model set. Otherwise the result is bit-for-bit unchanged. Regression tests added (87 tests).

### Added (documentation and research; not part of the installable package)
- Final consolidated research paper (`publication_final/`: Markdown, DOCX, PDF, BibTeX) integrating Studies I-V.
- v0.3 feasibility screening (`research_poc_v03/`) and the pre-registered risk-reduction confirmation with exploratory mechanism analysis (`research_poc_v03/confirmation/`). The experimental candidate algorithms are research scripts only.

### Unchanged
- Public API, CLI and all earlier research artifacts and results.

## [0.2.0] - 2026-10-29 (research snapshot; not published to PyPI)

The code used for the v0.2 pre-registered benchmark (`benchmarks_v2/reproducibility/PRE_REGISTRATION_SHA256.txt` hashes this version of `adaptive.py`).

### Added
- `handoffx.Advisor`, `Costs`, `Recommendation`: simple integration API with explanations, warnings for prior-only parameters, per-call human availability and forbidden actions.
- `handoffx.adaptive`: `EpisodeBelief` (cross-episode posterior over the model index), `AdaptiveController` (conservative posterior gate), `episode_log_likelihood`, `model_losses`, `run_episode`.
- `handoffx` console script and `python -m handoffx` command-line recommendations.
- `py.typed` marker.
- v0.2 deployment-stream benchmark (`benchmarks_v2/`), research documents (`research_v2/`), SQLite agent demo (`demo/`), updated manuscript (`publication_v2/`).

### Changed
- Packaging moved to a root `pyproject.toml` (the v0.1 file is kept as `04_Python_Library/pyproject_v0.1.toml`); the v0.1 package README is kept as `README_v0.1_PACKAGE.md`.

### Unchanged
- The v0.1 core (`models`, `policies`, `scenarios`, `evaluation`, `static`) and all v0.1 research artifacts and results.

## [0.1.0] - 2026-10-28

- Research prototype: exact finite-horizon nominal, Bayes-adaptive and history-rectangular robust planners, baselines, exact evaluator, common-random-number simulator, 38-scenario study.
