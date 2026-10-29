# HandoffX executable experimental protocol

**Status:** locally recorded before the main comparative run. This is NOT an independently timestamped public preregistration. The included protocol/configuration hashes preserve the executed specification. Small implementation-correctness examples preceded this recording; no final comparative Monte Carlo outcomes were used to select the study design.

## EP-01. Objective and hypotheses

Primary outcome: cumulative operational loss per episode, in the artificial common utility units of `TaskSpec`. The primary comparison is `handoffx_bayes` minus `nominal_dp`; negative values favor the Bayesian joint-model reference policy. Exact finite-model expected values accompany Monte Carlo estimates. Oracle excess loss is a derived outcome, not a separate claim of learned regret convergence.

H1: A joint uncertainty model is not uniformly better than certainty-equivalent sequential control. Null: no mean-loss difference within a fixed scenario. Directional improvements, degradations and ties will all be reported.

H2: Uncertainty correlation can matter after observations even when initial one-step marginals match. Compare coupled and independent priors on identical supports. The prediction is conditional, not that coupled uncertainty always wins.

H3: Resampling hidden modes changes recovery decisions relative to fixed persistent modes. The iid ablation preserves one-step marginals. It need not help or harm on every cost regime.

H4: The rectangular robust policy upper-bounds fixed-model loss under coverage, but can sacrifice expected performance. Root envelope values must not be mislabeled fixed-parameter minimax optima.

H5: Structural transfer alone does not protect outcomes under changed success, hazards and mode prevalence. Perfect recalibration is an upper-bound control, not an implemented learning method.

## EP-02. Design

There are 38 fixed synthetic scenarios: an 18-cell factorial (three AI probability biases x three human biases x two hazard regimes) plus 20 named sensitivity/structural checks. Biases are -0.18, 0 and +0.18; positive means the controller is overconfident. The lower-hazard regime multiplies all catastrophe probabilities by 0.2 while retaining the other base parameters. This regime was added during pre-main-run design inspection to avoid making the entire factorial a single high-risk routing setting; its results were not known when chosen.

The 20 checks vary persistent-mode prevalence, independent modes, response duration, delayed availability, absence of human tickets, high/low failure consequences, limited quota, deadline, diagnostic information, human effectiveness/cost, joint distribution shift with and without exact parameter refresh, irreversible-action authorization, a conditional severe-risk cap, and correct/opposite parameter-prior coupling. They are not independent random samples of real applications.

The base process requires two milestones within six ticks and seven resource units. The three latent modes have prior (0.50,0.30,0.20). Full kernels, priors, restrictions and costs are stored in JSON; those machine-readable configurations are authoritative.

## EP-03. Information and policies

All non-oracle policies receive the same observable outcome counts, failure flag, quota/deadline, availability schedule, supplied nominal kernel, nine-model uncertainty support and externally imposed action guard. They differ in how much of that supplied information their decision rule uses. No policy observes the realized model/mode or any future random number.

Eleven policies: always continue; always human when available; tuned retry-first; tuned confidence threshold; static committed-plan expected loss; exact nominal belief-state dynamic programming; exact history-rectangular robust dynamic programming; HandoffX Bayesian joint-model reference; independent-parameter-prior ablation; iid-mode ablation; and a generative-model oracle. The oracle has the true conditional model and prior but the same observed histories and action restrictions. In prior-predictive scenarios it knows the true prior, not the realized episode-level model index.

The static policy implements the Bayes-loss decision principle from learning to defer, not a reproduction of trained neural surrogate losses. No claim that this study beats published learning-to-defer implementations is permitted. The exact nominal dynamic program and robust dynamic program are the principal strong comparators.

## EP-04. Development versus evaluation

Tune the confidence threshold over (0.20,0.35,0.50,0.65,0.80) and the retry limit over (1,2,3) using exact expected loss on four separately specified development environments (five ticks; distinct mode prevalence/cost/hazard combinations). Use the lowest average loss; break ties toward the smaller numeric hyperparameter. Save all tuning scores. Do not tune the final policy priors, support width, costs, or scenario weights using final results.

Evaluate 24 independent PCG64 seed batches, 500 episodes per batch, per scenario/policy: 12,000 episodes per cell and 5,016,000 scenario-policy episode executions overall. Seeds are `20261028 + 997*i` for i=0,...,23. Within a scenario/seed, policies share the hidden-mode uniform and a pre-generated outcome-uniform array indexed by absolute tick and action. This common-random-number construction induces pairing without exposing future outcomes to policies. It does not establish individual-level causal counterfactuals.

## EP-05. Statistical analysis

For every scenario/policy, save raw episode records, 24 batch means and exact expectations. Monte Carlo 95% confidence intervals use the Student-t quantile with 23 degrees of freedom applied to independent seed-batch means. For policy differences, subtract within the same scenario/seed before forming intervals. These are pointwise conditional-simulation intervals, not simultaneous intervals or uncertainty about real human/AI probabilities. Do not claim multiplicity-controlled statistical discoveries.

Report exact loss differences, their simulation estimates and intervals; success, catastrophe, human-use, safe-stop and ordinary-failure probabilities; elapsed time; resource consumption; retry efficiency; conditional time to success; exact accumulated oracle-action advantage; upper 5% empirical mean loss (CVaR-style descriptive tail metric); and selected-action Brier score. Brier scores use each policy's Bayesian assessment probabilities even for the robust policy, not its worst-case value. They are on-policy selected-action metrics, not proof of global calibration.

An 'excess handoff' is a human action whose oracle conditional cost exceeds a feasible nonhuman alternative. It is a model-dependent cost comparison, not proof the particular person was unnecessary. We do not estimate real-world avoidable-failure causality. Report policy failure-probability differences separately without relabeling them causal effects.

Exact recursion already integrates all latent outcomes in this finite model. Monte Carlo intervals validate the executable simulator and describe finite-sample variability; they are not needed to pretend that a computed finite-model expected value is unknown. Every conclusion must still distinguish model correctness from reality.

## EP-06. Verification and reporting

Check probability normalization, terminal-outcome partition, oracle dominance at exact expectation, the performance-difference identity, and robust bounds against each supported fixed model. Report any assertion failure instead of suppressing a scenario. Publish all scenarios, including ties, failures and negative comparisons. No policy is removed because it loses.

Measure cold root-decision runtime on a fresh policy/guard and cached recommendation overhead separately. Record Python/NumPy/SciPy versions, OS, CPU information, process memory and actual wall time. The execution host is Linux; no Windows execution or claimed speedup on the user's laptop follows from these timings.

There is no real LLM, paid API, human participant, real-agent trace dataset, randomized workplace intervention, learned probability estimator or external safety certification in this experiment.
