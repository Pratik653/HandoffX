# Final PyPI release report: handoffx 0.2.1

**Publication status: NOT YET PUBLISHED.** The release is prepared and validated, and awaits the owner's final approval. This file will be updated with independently verified PyPI results after publication.

## Package

| Item | Value |
|---|---|
| Distribution name | `handoffx` (PyPI: HTTP 404 on 29 October 2026, so the name is unclaimed) |
| Version | 0.2.1 (0.2.0 was a research snapshot, never published) |
| Licence | MIT (`License-Expression: MIT`, `LICENSE` included) |
| Python | ≥ 3.11; classifiers 3.11, 3.12, 3.13 |
| Dependencies | `numpy>=1.24,<3`; extras `test`, `research` |
| Entry points | `handoffx` console script; `python -m handoffx` |
| Wheel contents | `handoffx/*.py`, `py.typed`, licence and metadata only; no research data, manuscripts or results |
| Author metadata | `Pratik653`; no e-mail address in the package metadata |
| Project URLs | Homepage, Repository, Issues, Changelog, Paper (all `github.com/Pratik653/HandoffX`) |

## Library changes since the research snapshot

- **Fixed:** `EpisodeBelief.posterior_models()` underflow. Posterior weights that underflow to 0 are floored at the smallest normal double.
  - Regression tests prove two things: the old code fails the new test, and non-underflowing weights are bit-for-bit unchanged.
  - The defect was never triggered in any reported experiment.
- **Unchanged:** the public API (`Advisor`, `Planner`, `ModelSet`, `TaskSpec`, `ActionGuard`, `EpisodeBelief`, `AdaptiveController`, …) and the CLI.
- **Not added:** none of the experimental candidates (A, B, C, catastrophe weighting) is in the package.

## Validation performed locally (29 October 2026)

| Check | Result |
|---|---|
| Test suite (`pytest`) | 86 passed |
| `python -m build` | sdist and wheel built |
| `twine check --strict` | PASSED (both) |
| Fresh virtual environment, Python 3.11, install from the built wheel | OK (numpy 2.4.6 resolved) |
| Import, version, `py.typed` present | 0.2.1; yes |
| README quick-start example | recommends `human`; `record_episode` and `calibrated_estimates` work |
| CLI: `handoffx --history …` and `python -m handoffx --json --no-human` | OK |
| Secrets scan (gitleaks) and personal-data check | see the commit audit in the release PR |
| GitHub Actions CI on the release branch | see the PR checks |

## Publishing infrastructure

- **Workflow:** `.github/workflows/release.yml`.
  - Triggered by a *published* GitHub Release.
  - Checks that the tag equals `v` + the package version.
  - Builds, runs `twine check --strict` and uploads the artifact.
  - Publishes with `pypa/gh-action-pypi-publish` using OIDC (`id-token: write` only in the publish job). No token is stored.
- **GitHub environment `pypi`:**
  - required reviewer: Pratik653;
  - deployment policy: tags matching `v*`;
  - administrator bypass allowed by GitHub default.
- **PyPI Trusted Publisher.** It must be registered by the owner as a *pending publisher* (cannot be verified from here):
  - PyPI project name: `handoffx`;
  - owner: `Pratik653`;
  - repository: `HandoffX`;
  - workflow: `release.yml`;
  - environment: `pypi`.

## Exact publication steps (after approval)

1. Merge the release pull request into `main`.
2. Create and push tag `v0.2.1` on the merge commit.
3. Publish GitHub Release `v0.2.1`. This triggers the Release workflow.
4. Approve the `pypi` environment deployment in the workflow run.
5. Verify:
   - `https://pypi.org/pypi/handoffx/json` shows 0.2.1;
   - `pip install handoffx==0.2.1` works in a clean environment;
   - the quick start and CLI run;
   - the project page metadata matches GitHub.

## Outstanding issues

- The owner must add the PyPI pending trusted publisher before step 3; otherwise the publish job fails with an OIDC authorization error.
- Author full name and ORCID are not set; the handle is used.
