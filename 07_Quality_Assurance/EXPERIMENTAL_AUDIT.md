# Experimental audit

Executed: 38 scenarios x 11 policies x 24 independent seed batches x 500 episodes = 5,016,000 stored scenario-policy episode executions. All 418 cells also have exact finite-model expectations. A full rerun reproduced every non-timing summary column. A separately written scalar loop matched 16,000 additional trajectories from four scenarios and four policies. The tests and audit are internal, not independent external replication.

Checks passed: terminal outcomes mutually exclusive/exhaustive; stored loss means equal raw arrays; all-policy oracle dominance; expected accumulated oracle action advantage equals excess loss; every supported fixed model is bounded by the rectangular envelope; robust policy minimizes that envelope among the evaluated policies. All 418 reported loss intervals contained their exact reference values in this run. This is not an empirical proof that the interval method has 100% coverage: comparisons share random draws and the finite design is not independent repeated coverage experimentation.

The selected risk guard is only conditional on uncertainty-set coverage. In `shift_unrecalibrated`, true robust-policy loss exceeds its envelope because hazards and latent prevalence changed outside the assumed set. This is preserved as a failure of model coverage, not suppressed as a numerical anomaly.

The main protocol was recorded locally before the main comparative run; it was not publicly preregistered. Correctness pilots and design inspection preceded it. Validation hardening changed input rejection only; a full numerical rerun checked that outcomes did not change. Additional objective-aligned robust comparisons were post-hoc and are labeled as such. No tuning was done on final outcomes.

Threats: hand-designed costs and kernels; often terminal human dominance; duplicated action behavior in some stress cases; limited horizons; no estimated probabilities; no real human participants or live agents; no multiple-comparison-adjusted claims; sampled CVaR-style tail means have no population safety interpretation. Machine-specific performance numbers are not Windows laptop measurements.
