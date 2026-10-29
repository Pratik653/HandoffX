# HandoffX v0.3 feasibility study (proof of concept)

Isolated exploratory study on branch `research/v0.3-feasibility`. It reuses the v0.2 library and benchmark code unchanged; nothing here changes the public API, the published results or the manuscript.

Start with `GO_NO_GO_DECISION.md`, then `FINDINGS.md`. Screening: `OPPORTUNITY_MATRIX.md`; hypotheses: `HYPOTHESES.md`; protocol and frozen decision criteria: `EXPERIMENT_PROTOCOL.md`.

## Progress log

- Stage A: v0.2 stored results verified (test: v2 −0.46% [−1.07, +0.09]; bayes_recal −0.63%; oracle −1.94%; no-dependence +5.79%; calibrated +0.92% / biased −1.03%); adaptive tests pass.
- Stage C diagnostics on v0.2 dev environments: headroom decomposition, grid limit, learning plateau, plateau attribution.
- Screening selected candidates A (prevalence learning), B (escalation-targeted sampling), C (Bayes-factor guard). Protocol and thresholds frozen and committed before any candidate run.

## Reproduce

```bash
python research_poc_v03/scripts/headroom_decomposition.py
python research_poc_v03/scripts/grid_limit.py
python research_poc_v03/scripts/learning_limit.py
python research_poc_v03/scripts/plateau_attribution.py
python research_poc_v03/scripts/round1_mechanism.py
python research_poc_v03/scripts/run_poc.py pilot
python research_poc_v03/scripts/run_poc.py confirm
python research_poc_v03/scripts/run_poc.py replicate
python research_poc_v03/scripts/analyze_poc.py pilot confirm replicate
python research_poc_v03/scripts/secondary_checks.py
python research_poc_v03/scripts/make_figure.py
```
- Round 1 mechanism checks: v0.2 runner reproduced exactly; A's prevalence level weakly identifiable; B equivalence holds; C Bayes factor ≈ 0 when calibrated. Found a latent `EpisodeBelief.posterior_models()` underflow issue (not triggered in any run; production code unchanged). Found a "stop at step one" learning trap.
- Round 2 pilot (72 envs, 37 s): A −0.92%, B +0.08%, C +0.41% vs bayes_recal; all survive the drop rule. Frozen confirmation set plus an A-without-learning mechanism diagnostic.
- Round 3 confirmation (300 envs, 128 s): A −0.52% [−0.88, −0.19] but calibrated +0.84% vs nominal (fails GO limit); B +0.53% (NO-GO); C −0.26%; ABC −0.52% (narrow numeric GO, includes harmful B).
- Round 4 pre-registered replication (300 envs, 73 s): A −0.25% [−0.71, +0.17]; AC −0.12%; ABC −0.08%. No replicated pooled gain. Consistent across all rounds: A reduces severe failures 13–17% and shift-environment loss 2–3%.
- Decision: broad v0.3 NO-GO; prevalence-flexible learning CONDITIONAL GO as a tail-risk / shift-robustness direction (see GO_NO_GO_DECISION.md).
- Follow-up `confirmation/` (pre-registered independent confirmation of A; 500 fresh environments, 135 s):
  - Severe-failure RRR 17.8% [12.0, 24.0] vs bayes_recal, confirmed in both new shift families and in every kind.
  - Loss non-inferiority not demonstrated: +0.28% [−0.21, +0.82] against a 0.5% margin. Human-effectiveness shift costs +1.14% loss.
  - Mechanism: evidence-triggered conservatism (more stopping, fewer retries), not prevalence estimation.
  - Decision: CONDITIONAL GO for a risk-sensitive controller, with explicit risk control preferred over A's implicit hedge. See `confirmation/FINAL_RESEARCH_DECISION.md`.
