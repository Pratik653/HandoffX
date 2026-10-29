# Worked examples across model families

All figures in this file are either explicitly illustrative arithmetic or values computed from `results/worked_examples.json`. Utility units are artificial and comparable within an example; they are not euros, dollars or a real organization's losses.

## WE-A. Static terminal decision

For autonomous success 0.65, human success 0.90, AI cost 1, human cost 4 and ordinary failure loss 20, expected losses are 8 and 6. The human threshold is 0.80. A stopping loss of 12 does not alter the handoff choice; lowering stopping loss to 5 makes abandonment optimal. With zero failure loss only action costs matter. A threshold outside [0,1] represents impossibility or inevitability of the inequality, not a probability to clip. This is ordinary expected-loss minimization, with constant-size arithmetic.

## WE-B. Four terminal alternatives

As an illustrative one-decision recovery comparison after a failure, add a retry with success 0.75 and cost 1.4. Its expected loss is 6.4, so human assistance at loss 6 remains best among AI continuation (8), retry (6.4), human (6) and stop (12). If human success is instead 0.50, its loss is 14 and retry wins. This terminal model is valid only if the alternatives have comparable success definitions; it cannot directly compare a single-milestone attempt with whole-task rescue. The implemented static comparator therefore scores committed completion plans.

## WE-C. Sequential intervention

In the base calibrated model, two milestones remain. Nominal dynamic scores at the initial state are continue 8.895722, human 7.514800 and stop 12; retry is infeasible. After one successful continuation, the remaining scores change to continue 2.761979, human 6.007805 and stop 12. Continuing now wins. The initial continue score already accounts for future contingent actions and terminal consequences; it is not its immediate cost alone. Cached finite-horizon recursion, rather than a single threshold, computes this comparison.

## WE-D. Partial observability

The base prior assigns persistent mode probability 0.20. After a hard continuation failure, the nominal posterior over healthy, recoverable and persistent modes is approximately (0.025693, 0.343834, 0.630474). The controller was never shown the true mode: it learned from the likelihood of the observed failure. The corresponding nominal future scores are continue 17.280532, retry 13.532213, human 10.892995 and stop 12. A recovery attempt is not necessarily worth taking simply because it is technically available. Observation likelihoods, not raw confidence labels, produce the update.

## WE-E. Joint uncertainty and value semantics

With the declared nine-model coupled prior, the base root Bayesian predicted human loss is 7.902880, while the central true environment yields 7.514800 when that action is taken. These are different quantities: the first averages assumed model uncertainty; the second evaluates a fixed generating environment. They must not be confused in a results table or UI. A hard failure changes both task-mode and model weights. With simultaneous downward 0.18 capability biases, nominal planning selects continue (predicted 10.683540 versus human 10.754800), whereas joint Bayes selects human (predicted 10.754800 versus continue 10.862543). Its actual benefit in that synthetic environment is reported separately in the empirical table.

## WE-F. Persistent recovery

Suppose a task's fixed success probability is 0.80 with probability 0.60 and 0.05 with probability 0.40. Both an iid approximation and the persistent model start with mean success 0.50. After three attempted retries, the iid model predicts success 0.875; the persistent model yields 0.65225. After three failures, the persistent model's next-attempt success probability is approximately 0.060352. The computation requires a two-component posterior, not a claim that failures are independent because the code draws independent uniforms conditional on a mode. The result changes if a real repair alters the mode.

## WE-G. Robust control and a risk guard

The base robust root scores are continue 11.191880, human 10.754800 and stop 12. At the hard-failure state they become continue 18.289857, retry 14.334406, human 14.437118 and stop 12: robust planning stops even though nominal planning requests human rescue. This is conservatism under the larger conditional-kernel envelope, not proof that either action is universally safer.

For a severe-risk budget 0.05 and horizon 6, the guard cap is 0.008333 per action. At the base root, continuation's predicted catastrophe probability is 0.0315, while human rescue's is 0.0034. The former is excluded, the latter allowed. The episode bound requires the true conditional hazards to be covered. In the distribution-shift experiment, the robust value 10.754800 does not bound true loss 13.194520 because the true model lies outside the assumed set. Robust optimization cannot repair an unsupported ambiguity specification.
