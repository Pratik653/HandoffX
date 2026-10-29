# Research changelog

## 2026-10-29 — v0.2

- Imported the v0.1 package unchanged as the git baseline (raw `.npz` arrays and the prebuilt wheel kept on disk, excluded from git).
- Reproduced v0.1 on Windows/Python 3.11: raw arrays bit-identical, summaries within 7.1e-15. v0.1 `audit_results.py` string comparison flags a last-digit float difference; recorded, not changed.
- Phase B root-cause analysis (`ROOT_CAUSE_ANALYSIS.md`).
- Added `handoffx.adaptive` (cross-episode belief, conservative controller, scalar episode simulator) and `handoffx.advisor` (simple API, CLI).
- Wrote and hashed the v0.2 protocol before any run. Dev grid -> frozen gate (alpha 0.35, tol 0.03). Validation, test, shift, original replays run once each, in that order.
- Deviation from protocol: none in execution. Note: `analyze_v2.py` gained an explicit UTF-8 encoding after the validation run (output encoding only).
- Findings: modest calibration gains concentrated in biased environments; gate not shown to add value over ungated posterior planning; failure dependence dominant; misspecification counterexample CE9.
- Library defaults set to the frozen gate after the test run (no benchmark code changed).
- Original v0.1 manuscript, results, configs and audits unchanged; v0.2 manuscript in `publication_v2/`.
