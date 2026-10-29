# Baseline specification and fairness

All policies use the same observable state and externally admissible actions. The same supplied nominal kernel, uncertainty support, priors and known costs are available to non-oracles, although each policy may use a subset. Hidden task modes and future outcomes never enter a policy interface.

| Policy | Actual decision mechanism | Interpretation |
|---|---|---|
| always_continue | Continue if authorized, otherwise stop | Weak diagnostic control |
| always_human | Human if available, otherwise continue, otherwise stop | Tests whether full delegation is already sufficient |
| retry_first | Continue initially; up to two retries; then human/stop | Retry limit selected on separate development environments |
| confidence | Compare committed remaining-milestone success to 0.50; use fixed fallback order | Threshold selected on development environments |
| static_loss | Expected loss of committed completion plans; failures terminal in scoring | Bayes-loss principle, not trained learning-to-defer reproduction |
| nominal_dp | Exact dynamic planning with central model and latent-mode posterior | Principal strong comparator |
| robust_dp | Exact history-rectangular minimax DP over supplied model-conditional laws | Different objective; not fixed-model minimax |
| handoffx_bayes | Exact posterior-predictive DP over joint model and mode | Established Bayesian principle in a reference implementation |
| bayes_independent | Same support and marginals; factorized AI/H prior | Coupling ablation, not a weak unrelated baseline |
| bayes_iid | Same initial one-step predictions; mode persistence removed within each model | Dependence ablation; episode-level parameter uncertainty retained |
| oracle | True generating model/prior, same observations and action guard | No hidden-mode or future-outcome knowledge |

Static plans compare task completion fairly: autonomous continuation must finish the remaining milestones, while human rescue handles the remaining task. Merely comparing single-step AI success with terminal human rescue would be invalid. The static policy still omits adaptive recovery choices in its score, which is why exact nominal DP is the principal comparator.

No HULA, neural surrogate learning-to-defer, Cubuktepe controller synthesis, or Shaikh real-model code is represented as reimplemented. The experiment compares reference decision rules in a shared simulator, not published systems on their original datasets. Source-specific guarantees do not transfer automatically.

The post-run robust-objective audit evaluates every policy against the same conditional-kernel envelope and each supported fixed model. This prevents expected-loss rankings from being mistaken for a failure of robust optimization's own objective. It is disclosed as post-hoc analysis and does not tune any policy.
