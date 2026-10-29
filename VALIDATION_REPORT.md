# HandoffX v0.2 validation report

Date: 2026-10-29. Environment: Windows 11, Python 3.11.9, NumPy 2.3.5, SciPy 1.17.0, CPU only.

## 1. Original baseline (v0.1)

| Check | Result |
|---|---|
| v0.1 full study rerun (38 scenarios x 11 policies, 5,016,000 episode executions) | reproduced: 418 raw arrays bit-identical; summary/paired/batch tables within 7.1e-15 |
| v0.1 `audit_results.py` | fails on a string comparison of one last-digit float (`retries_exact` ...875 vs ...8754); numerically identical; recorded, script unchanged |
| v0.1 `validate_mathematics.py` | passed |
| Reported comparison handoffx_bayes vs nominal_dp | 6 better / 23 equal / 9 worse reproduced; at a 0.01 tolerance 5 / 30 / 3 |
| Original artifacts | unchanged in git (`01_`-`08_*`); renamed only: `README.md` -> `README_v0.1_PACKAGE.md`, `04_Python_Library/pyproject.toml` -> `pyproject_v0.1.toml` (v0.1 `SHA256SUMS.txt` lists the old paths) |

## 2. Updated policy results (held-out, pre-registered)

Relative change in mean exact episode loss versus nominal, 95% environment-bootstrap intervals.

| Policy | Validation (60) | **Test (200)** | Shift (100) |
|---|---:|---:|---:|
| handoffx_v2 (frozen gate) | -0.16% [-0.84, +0.39] | **-0.46% [-1.07, +0.09]** | -1.06% [-2.76, +0.37] |
| bayes_recal (ungated) | +0.60% [-0.40, +1.65] | -0.63% [-1.28, -0.05] | -0.82% [-2.58, +0.73] |
| plugin_recal | +0.09% | -0.26% | -0.26% |
| bayes_static (v0.1 analogue) | +0.26% | +0.16% | +1.10% |
| robust_static | +8.67% | +7.26% | +3.44% |
| v2_iid (no failure dependence) | +5.37% | +5.79% | +5.79% |
| oracle | -2.67% | -1.94% | -7.87% |

Test, handoffx_v2: absolute difference -0.052 [-0.110, -0.002]; d_z = -0.13; W/T/L at 1%: 26/155/19; worst +22.1%; 30% of the nominal-to-oracle gap closed; regret in the last 20 episodes 0.095 vs. 0.173 for nominal. Biased estimates: -1.03% (n = 142); calibrated: +0.92% (n = 58).

**Measured improvement:** small, conditional on biased estimates, not significant in relative terms on test. **Measured regression:** in calibrated environments and under misspecification (CE9). **Gate:** not shown to add value over ungated posterior planning. Full detail: `research_v2/EXPERIMENTAL_RESULTS.md`.

## 3. Tests and software

| Check | Result |
|---|---|
| `pytest` (v0.1 suite 60 + adaptive 12 + advisor 12) | 84 passed |
| v0.1 examples, CLI, demo (`--tasks`, `--compare`) | executed |
| `python -m build`; `twine check --strict` | sdist and wheel built; PASSED |
| Wheel contents | package modules, `py.typed`, LICENSE, metadata only |
| Clean venv install from wheel (outside repo, `-I`) | import, `Advisor` recommendation and `handoffx` console script work; resolved NumPy 2.4.6 |
| CI matrix (Linux/Windows/macOS x 3.11-3.13) | configured; first run happens on push |

## 4. Mathematical verification

| Item | Status |
|---|---|
| A1 cross-episode posterior (sequential = batch, order invariance) | proved; max error 4.8e-15 |
| A2 no learning without the action | proved; max deviation 1.3e-15 |
| A3 posterior-risk monotonicity of the gate | proved; 0.0 violations in 30 environments |
| A4 credible-degradation statement, boundary cases | proved; 0 dominance violations at alpha = 0 |
| Performance-difference identity (root cause) | holds to 1e-8 on all 38 v0.1 scenarios and 7.9e-16 on v2 checks |
| CE9 misspecification counterexample | verified from stored data (environment 300120) |
| Frequentist guarantees, regret bounds | not established (not claimed) |

## 5. Experimental integrity

| Check | Result |
|---|---|
| Pre-registration hashes (`benchmarks_v2/reproducibility/PRE_REGISTRATION_SHA256.txt`) | all match current files |
| Order dev -> freeze -> validation -> test/shift | recorded in git history |
| Seed overlap between splits | 0 |
| Derived summaries vs. raw arrays (5,180 rows) | max abs difference 0.0 |
| Any policy below the exact oracle | 0 cases |
| Determinism (10 test environments, 3 vs. 16 workers) | 0 differing non-timing cells |
| New citations | 8, verified via Crossref/PMLR metadata |

## 6. Publication safety audit

gitleaks on the full git history: no leaks. Working-tree hits only in the git-ignored `.venv` (third-party test fixtures). Commit identities rewritten before the first push to the GitHub no-reply address. No credentials, tokens or local user paths in tracked files; the v0.1 logs mention the original generation sandbox's pip cache path (`/home/oai/...`), kept as provenance. Raw arrays (about 19 MB v0.1, plus v0.2) and built wheels are git-ignored.

## 7. Known limitations and remaining research

See `research_v2/LIMITATIONS.md`. Most important: synthetic evidence only; small effects; gate unproven; misspecification of failure-mode prevalence; no real agents or operators. Next steps: model sets with prevalence/hazard parameters, posterior predictive reversion checks, costed information-gathering actions, real agent logs.

## 8. Not verified here

DOCX opened in Microsoft Word (Word automation was blocked on this machine; the DOCX was validated by re-reading with python-docx and 237 equations converted without error; the PDF was produced from the same source via Edge). Execution on Linux/macOS (CI will cover). PyPI upload (intentionally not performed).
