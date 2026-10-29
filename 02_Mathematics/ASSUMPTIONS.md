# Assumptions, implementation coverage and excluded claims

| ID | Assumption | Where used | What fails without it |
|---|---|---|---|
| A01 | Finite action/outcome sets and finite horizon | Exact recursion P5 | No claim of efficient arbitrary POMDP solution |
| A02 | Model index and hidden task mode fixed within each episode | Count sufficiency; P4; simulator | Count compression loses history/order effects |
| A03 | Outcomes conditionally independent given model, mode and action | Posterior likelihood product | Repeated outcomes require a richer state |
| A04 | Human rescue is a terminal action | Time, quota, human ticket logic | Repeated human/agent collaboration not represented |
| A05 | Known deterministic availability schedule and delay | Feasible action calculation | Queues, fatigue and random response times absent |
| A06 | Supplied probabilities are valid categorical probabilities | All optimizers | Raw LLM confidence is not an acceptable substitute |
| A07 | Synthetic priors and ambiguity support are explicitly chosen | Bayesian and robust comparisons | No empirical coverage or estimator-quality claim |
| A08 | Safe stop is externally authorized, has known loss and no catastrophic side effect | Guaranteed nonempty action set | Physical/clinical stopping may not be safe; adapter must reject |
| A09 | Costs and losses share a common artificial utility scale | Expected-loss objective | Numerical ordering has no direct monetary interpretation |
| A10 | Feasibility guard shared by all compared policies | Matched-action comparisons | Oracle advantage could conflate authorization differences |
| A11 | Oracle knows the generative process but not latent realization/future uniforms | Regret comparisons | Hidden-state omniscience would be an unfair baseline |
| A12 | True history kernels covered by envelope | P6 and optional guard P7 | Miscovered uncertainty sets invalidate guarantees |
| A13 | Uniform history-kernel error, unchanged costs/actions as specified | P8 | Structural API compatibility alone gives no performance bound |
| A14 | Independent seed batches, fixed scenario definitions | Monte Carlo confidence intervals | Adaptive tuning on results would undermine their interpretation |
| A15 | Common random numbers are a variance-reduction coupling only | Paired comparisons | They do not identify real individual treatment effects |

## Implemented versus general formulation

Implemented: competing terminal consequences; multi-milestone progress; retry eligibility; persistent latent modes; soft/hard observations; finite joint parameter priors; nominal/Bayesian/rectangular-robust recursion; quota/deadline/availability/action guards; exact evaluation; common-random-number simulation; explicit abstention on missing evidence.

Not implemented: learned probability estimation, training on real traces, full-state transition POMDPs, continuous beliefs with approximate solvers, random human queues, multi-operator routing, endogenous repair of latent mode, within-episode nonstationarity, a general chance-constrained optimizer, a CVaR policy, real-agent control, external SQLGuard-Ninja or RelVector adapters, public PyPI release, or a Windows runtime validation.

The experiment uses Linux CPU execution. The source uses portable Python/NumPy and includes Windows commands; portability is an engineering intention, not an executed Windows test. No GPU, LLM API, internet access, or cloud account is required for running the library and experiments after dependency installation.
