# Verified counterexamples and rejected generalizations

All values below are constructed mathematical examples, not empirical observations. The validation script checks their arithmetic.

## CE1. AI confidence alone does not determine handoff

Set $p_A=.7,c_A=0,c_H=.1,L=1$. AI loss is .3. If $p_H=.95$, human loss is .15 and handoff is preferable; if $p_H=.4$, human loss is .7 and continuation is preferable. The same AI probability yields opposite decisions. A universal threshold on AI confidence alone therefore requires additional fixed assumptions about human effectiveness and costs.

## CE2. An identical confidence can imply different decisions at different horizons

Let $p_A=.6,c_A=.1,p_H=1,c_H=.4,L=1$, with both actions completing the task upon success and human action taking one tick. With one tick left, AI loss is $.1+.4(1)=.5$ and human loss .4. With two ticks left and human available after AI failure, continuing then using human assistance costs $.1+.4(.4)=.26$. The preferred action switches solely because recovery opportunities change. No claim of a state-independent confidence threshold is warranted.

## CE3. iid retries overestimate recovery under a persistent mixture

For the two-mode mixture in P4, one-attempt success is .5. Three iid attempts predict success .875, while the persistent mixture yields .65225. The error is .22275 in absolute success probability. These values concern repeated identical attempts without catastrophic outcomes or state repair; the main simulator is more detailed.

## CE4. Robustness need not improve true expected loss

True autonomous success is .95, autonomous cost zero, human success .8, human cost .05, failure loss one. The nominal optimal action has true loss .05. An ambiguity set that permits autonomous success as low as .1 but fixes human success at .8 makes the robust rule choose human assistance, with true loss .25. The robust action is worse by .20 in the true favorable environment, despite being optimal for its stated ambiguity set.

## CE5. Rectangularization can double worst-case cost

There are two fixed environment models and two compulsory stages. Their deterministic stage-loss vectors are $(0,1)$ and $(1,0)$. Every fixed model has total loss 1. Allowing nature to switch models after each stage yields a rectangular worst case of $1+1=2$. Thus $\max_m\sum_t\ell_{mt}$ is not generally equal to $\sum_t\max_m\ell_{mt}$. This abstract example can also be represented by stage-specific deterministic transitions to unit-cost outcomes. It rejects the interpretation of a per-stage adversary as one fixed unknown parameter.

## CE6. No human-outcome overlap prevents identification

Suppose every logged task is assigned to AI with observed success probability .5 and cost zero. Two data-generating worlds agree on every observed record but have human success .95 versus .05. With human cost .1 and failure loss one, the human loss is .15 in the first world and 1.05 in the second, compared with AI .5 in both. Opposite optimal choices are observationally indistinguishable. More AI-only logs do not identify human outcomes. Logging action propensities does not repair zero probability of assigning the human action. This is an identifiability limitation, not proof that all selective-label problems are unsolvable under additional assumptions.

## CE7. Aggregate calibration is insufficient for conditional decision quality

Two equally common observable groups have actual AI success .9 and .1. A constant prediction .5 is perfectly calibrated in aggregate. Human success is .6 at cost .05 and failure loss is one. A group-blind expected-loss policy selects human assistance with loss .45. A group-aware policy selects AI in the high-success group (loss .1) and human in the other group (loss .45), averaging .275. Aggregate calibration alone does not establish the history-conditioned error premise of P8.

## CE8. Expected-loss optimality is not a severe-risk constraint

An autonomous action succeeds with probability .99 and catastrophically fails with probability .01, has cost zero, and catastrophe loss 100. A human action is perfectly safe but costs 2. Expected-loss minimization chooses AI (loss 1 versus 2), while an episode catastrophe constraint below .01 forbids it. The objectives are different; neither metric may be relabeled as the other.

## Additional limits checked in the text

P3 proves that correlation of uncertain probabilities cannot by itself change a one-step linear Bayes decision with unchanged marginal means. A claimed universal correlation advantage is therefore rejected even before simulation. The fixed-mode model cannot describe genuine fault repair that changes subsequent probabilities; future work must not reuse the P4 inequality after violating that assumption.
