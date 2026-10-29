# Final PyPI release report: handoffx 0.2.1

**Publication status: PUBLISHED and independently verified (29 October 2026).**

| | |
|---|---|
| PyPI project | https://pypi.org/project/handoffx/0.2.1/ |
| GitHub release | https://github.com/Pratik653/HandoffX/releases/tag/v0.2.1 |
| Installation | `pip install handoffx` (or `pip install handoffx==0.2.1`) |
| Verified version | 0.2.1 (the only version on PyPI) |
| Release commit | a762b6b, the merge of PR #1 into `main`; annotated tag `v0.2.1` |
| Release workflow | https://github.com/Pratik653/HandoffX/actions/runs/40852910419: `build` success, `publish-pypi` success |

## Publication sequence

1. CI on PR #1 passed: 10/10 checks (build, plus tests on Linux, Windows and macOS × Python 3.11–3.13).
2. PR #1 was merged into `main`.
3. Tag `v0.2.1` was pushed, and GitHub Release `v0.2.1` was published, which triggered `release.yml`.
4. The `build` job checked that the tag matches the package version (`v0.2.1`), built the sdist and wheel, and passed `twine check --strict`.
5. The `publish-pypi` job waited at the protected `pypi` environment until the owner approved the deployment in GitHub. Protection was not bypassed.
6. Trusted Publishing:
   - the GitHub OIDC token was exchanged for a short-lived PyPI upload credential, and no stored token was used;
   - `twine check` passed inside the publish action;
   - PEP 740 publish attestations were generated for both files;
   - both files were uploaded to `upload.pypi.org`.
7. No other tag, release or version was created.

## Independent verification of PyPI

These checks used the public PyPI JSON API, the Simple index and the project page (HTTP 200).

| Field | Published value |
|---|---|
| Name / version | `handoffx` / `0.2.1`, not yanked |
| Summary | Auditable continue / retry / ask-a-human / stop decision support for autonomous agents under uncertainty |
| Author | `Pratik653`; no author or maintainer e-mail |
| Licence | `License-Expression: MIT`, licence file included |
| Requires-Python | `>=3.11`; classifiers 3.11, 3.12, 3.13; `Typing :: Typed` |
| Dependencies | `numpy>=1.24,<3`; extras `test`, `research` |
| Project links | Homepage, Repository, Issues, Changelog, Paper (all `github.com/Pratik653/HandoffX`) |
| Description | README, `text/markdown`, 8,852 characters |

**Files.** SHA-256 digests are identical to the attested digests in the workflow log:

| File | Size | SHA-256 |
|---|---|---|
| `handoffx-0.2.1-py3-none-any.whl` | 29,264 bytes | `c38dd1ad79c4e755368e05f37daadad51085520b5a9261a6128da29753299985` |
| `handoffx-0.2.1.tar.gz` | 24,951 bytes | `c15351613d8a2b2c64ad427bbc152149400259eb338ac3d1d316f6cfc65b7c37` |

**Content audit of the downloaded published files.**
- The wheel contains only `handoffx/*.py`, `py.typed`, the licence and metadata. There is no research data, manuscript or results; the sdist has 26 members.
- No AI-assistant names or co-author trailers in the files or the PyPI metadata.
- No personal name, e-mail address, local filesystem path, or PyPI/GitHub token pattern.

## Clean installation from PyPI

- **Environment:** a fresh Python 3.11 virtual environment outside the repository.
- **Command:** `python -m pip install --no-cache-dir --index-url https://pypi.org/simple handoffx==0.2.1`
- **Source:** pip downloaded `handoffx-0.2.1-py3-none-any.whl` (29 kB) and `numpy-2.4.6` from PyPI. The package was imported from the venv's `site-packages`, and the test asserted it was not loaded from the repository checkout.

| Check | Result |
|---|---|
| Import and `handoffx.__version__` | 0.2.1 |
| README quick start (`Advisor.from_estimates`, `recommend`, `explain`) | action `human`; explanation printed |
| `record_episode` and `calibrated_estimates()` | OK (continue 0.773, human 0.900) |
| Per-call options (`human_available=False`, `forbidden=["retry"]`) | action `continue`; admissible `continue`, `stop` |
| Research API import (`handoffx.adaptive.EpisodeBelief`) | OK |
| Console script `handoffx --history continue:hard_failure,retry:hard_failure` | `Recommended: human`, with expected losses for all actions |
| `python -m handoffx --json --no-human` | valid JSON recommendation |

## Library content of 0.2.1

- **Fixed:** `EpisodeBelief.posterior_models()` underflow.
  - Finite posterior weights that underflow to 0 are floored at the smallest normal double.
  - Models with exactly zero likelihood are omitted, because they are ruled out rather than improbable.
  - Otherwise results are bit-for-bit identical to 0.2.0.
  - 87 tests.
- **Unchanged:** the public API and CLI. No experimental v0.3 algorithm is included.

## Unresolved items

- Author full name, affiliation and ORCID are not set; metadata uses the handle `Pratik653`. They can only change in a future release, because PyPI metadata is immutable per version.
- Zenodo: not deposited, by decision; the GitHub–Zenodo integration is not enabled.
- `pip show` displays an empty `License:` line because the licence is declared with the newer `License-Expression` field (shown as MIT on PyPI). This is cosmetic.
- The release workflow logs a GitHub notice that `actions/download-artifact@v4` targets the deprecated Node.js 20 runtime. It did not affect this release; updating the action version can be done in a later maintenance change.
