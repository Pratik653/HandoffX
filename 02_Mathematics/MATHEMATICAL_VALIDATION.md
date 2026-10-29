# Mathematical validation report

**Status:** nine stated propositions with complete written derivations; eight explicit counterexamples; computational checks executed. These are established/adapted results in a bounded model, not claims of novel mathematical priority. This is an automated self-review, not independent external proof certification.

| Claim | Executed supplementary check | Outcome |
|---|---|---|
| P1 static threshold | SymPy simplification of the loss difference | Exact symbolic residual zero |
| P2 sensitivity/stability | 5,000 random trials; 3,306 strict-gap cases | All asserted inequalities held |
| P3 joint dependence | Equal-marginal two-model posterior examples | Human-after-failure probabilities 0.32 versus 0.68 |
| P4 persistent retry mixture | 5,000 random mixtures; variance identity and Jensen check | All assertions held; example 0.65225 versus iid 0.875 |
| P5 Bayesian recursion | Independent small history-tree recurrence and exact oracle evaluation | Agreement within stated numerical tolerances |
| P6 robust envelope | 418 policy-scenario objective audits and supported fixed-model checks | Bound and rectangular optimality checks held |
| P7 conditional guard | 99 policy/fixed-model checks | Maximum exact severe probability 0.0034 under a 0.05 cap |
| P8 transfer bound | 376 reachable states and uniform conditional TV | Actual regret 0; bound 483.288756, practically loose |
| P9 information value | Direct finite calculations | Loss 5 without information, 1 with perfect, 2.6 with noisy signal |

CE1-CE8 were evaluated directly by `validate_mathematics.py`; their arithmetic is in `results/mathematical_checks.json`. Boundary cases include zero failure loss, impossible conditioning histories, stopping dominance, completion exactly at the deadline, and lack of causal identification when rescue outcomes are never observed.

The validation establishes code/calculation consistency for the tested instances. Finite random checks do not prove a theorem. The written proofs, definitions and assumptions are the mathematical arguments; numerical checks are supplementary. There is no unproved conjecture used as an implemented guarantee. The transfer bound's numerical weakness is a negative finding, not hidden by reporting only its existence.
