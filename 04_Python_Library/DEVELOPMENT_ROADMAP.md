# Development roadmap and MVP boundary

## Completed research MVP

Finite joint-belief planning; static terminal decisions; rectangular robust planning; explicit stop/availability/budget/authorization guard; persistent-mode simulator; 11 comparison policies; exact evaluator; deterministic and Monte Carlo tests; actual examples; source/configuration hashes; raw results; reproducible plots and mathematics. A neutral policy comparison, rather than a guaranteed winning algorithm, is the completed research product.

## Release blockers

Author and license confirmation; independently reviewed proof and code audit; Windows 11 CI; broad supported-version testing; hostile-input/schema limits; API stability review; resource-limit tests at horizon extremes; package-name availability; accessibility/editorial review; domain-specific safety analysis. No claimed deadline or completed status is attached to these tasks.

## Next empirical study

Collect a consented low-risk benchmark with complete action/outcome semantics and a prospectively specified evaluation split. Validate AI recovery, human effectiveness, failure dependence and observation models separately. Include real human capacity/delay and selection effects. Fit or calibrate a probability model without using final outcomes to select the policy. Evaluate expected loss and severe-failure probability jointly with explicit costs. An observational log alone generally does not identify unobserved rescue outcomes.

## Extensions requiring new mathematics or solvers

Nonterminal clarification; actions that change latent failure mode; operator fatigue and queues; multiple concurrent tasks; learned ambiguity sets; continuous beliefs; partial identification; robust nonrectangular optimization; distributionally robust risk; online adaptation and causal off-policy evaluation. None can be advertised as already supported merely because the high-level action names are similar.

## Explicitly excluded

Autonomous SQL execution, remote desktop control, automatic safety-policy bypass, general-purpose agent orchestration, confidential data ingestion, guaranteed model calibration, universal transfer, production safety certification, deployment monitoring and fabricated model adapters.
