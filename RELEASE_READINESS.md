# Release readiness (v0.2.0)

## Status

| Target | Status |
|---|---|
| GitHub (public repository) | see the repository; pushed after the safety audit |
| PyPI `handoffx` | **ready, not published.** Name unclaimed on PyPI and TestPyPI (HTTP 404, 2026-10-29). Artifacts build and pass `twine check --strict`. Awaiting owner approval. |
| Zenodo | metadata prepared (`.zenodo.json`, `CITATION.cff`); no deposit made |
| GitHub Release | not created (creating one triggers the PyPI workflow) |

## First PyPI release: checklist (owner actions marked)

1. **Owner:** on https://pypi.org/manage/account/publishing/ add a *pending* Trusted Publisher: project `handoffx`, owner `Pratik653`, repository `HandoffX`, workflow `release.yml`, environment `pypi`.
2. Confirm the `pypi` GitHub environment requires your approval (configured with you as required reviewer).
3. Confirm CI is green on `main`.
4. Review `CHANGELOG.md`; set the 0.2.0 date.
5. Tag and release: `git tag v0.2.0 && git push origin v0.2.0`, then publish a GitHub Release for `v0.2.0` (attach `benchmarks_v2/results/*/raw/episodes.npz` and the v0.1 raw arrays as research assets if desired).
6. **Owner:** approve the `pypi` environment deployment in the Actions run. The workflow builds, checks that the tag matches the package version, runs `twine check` and publishes via OIDC (no stored token).
7. Verify: `pip install handoffx==0.2.0` in a clean environment; `python -m handoffx --history continue:hard_failure`.

## Optional dry run on TestPyPI

Add a TestPyPI trusted publisher and a job using `repository-url: https://test.pypi.org/legacy/` before step 5.

## Zenodo

Enable the GitHub-Zenodo integration for the repository before creating the release; Zenodo then archives the release and mints a DOI using `.zenodo.json`. Add the DOI to `CITATION.cff` and the README afterwards.

## Decisions for the owner

- Author name: metadata uses the handle `Pratik653`; replace with your preferred full name/ORCID in `pyproject.toml`, `CITATION.cff`, `.zenodo.json` and the manuscript if desired.
- Licences: MIT (code) and CC BY 4.0 (documents, figures, data) follow the v0.1 recommendation; confirm.
- Version: 0.2.0 marked Alpha.
