# 4. Problem formulation

**Status.** Specified and implemented for the bounded latent-mode subclass below. General MDP/POMDP notation explains the relationship to prior art; it does not imply that the software solves arbitrary POMDPs. All probabilities in the experiments are synthetic design choices, not observations of language models or human workers.

**Table {T:notation}.** *Notation and abbreviations*

| Symbol or term | Meaning and units |
|---|---|
| C, R, H, S | Continue, retry, terminal human rescue, authorized safe stop |
| T, t | Deadline and elapsed time, in artificial time ticks |
| j, J | Completed and required milestones |
| B, b | Resource quota and amount spent, in resource units |
| Z | Fixed hidden task (failure) mode within an episode: healthy/transient, recoverable/intermediate, persistent |
| Θ, m | Fixed latent capability-model index; $M$ is the finite model set |
| μ, b(s) | Prior and posterior distributions over model and mode |
| K, k | Conditional categorical outcome kernel |
| κ(a) | Operating plus time cost of action a, in common artificial loss units |
| L, F, S | Ordinary-failure, catastrophe (severe-failure) and safe-abandonment losses |
| V, Q | Bayesian value and action-value functions |
| W_R | History-rectangular robust value, not a mean-loss estimate |
| δ | Episode severe-risk budget, conditional on model coverage |
| J_P(π) | Expected cumulative loss of policy π in environment P |
| e, τ_e, w_E | Episode index, logged trajectory of episode e, posterior over the model index after E episodes |
| π(z∣m) | Prevalence of latent mode z under model m |
| λ | Prevalence level of candidate A (Study III–V) |
| ARD, RRR | Absolute risk difference; relative risk reduction (ratio of means) |
| pp | Percentage points (difference of two percentages) |
| MDP / POMDP | Markov / partially observable Markov decision process |
| DP | Dynamic programming |
| CRN | Common random numbers for paired simulation |

## 4.1. Decision environment and units (FM-01)

<<v01|## FM-01.|## FM-02.>>

## 4.2. Actions, outcomes and terminal semantics (FM-02)

<<v01|## FM-02.|## FM-03.>>

## 4.3. Costs, restrictions and objective (FM-03)

<<v01|## FM-03.|## FM-04.>>

## 4.4. Deployment streams (Studies II–V)

Studies II–V embed the within-episode model in a deployment, without changing the within-episode model:
- A deployment is a sequence of episodes $e=1,2,\ldots$ that share a fixed model index $m^*$ from a finite set $M$.
- Each episode draws a latent failure mode $z_e\sim\pi(\cdot\mid m^*)$, which stays fixed within the episode.
- Episode $e$ yields a trajectory $\tau_e$ of action–outcome pairs; the stop action produces no outcome.
- Actions may depend on earlier trajectories, the current history and independent randomization, but never on $m^*$ or $z_e$.

The objective of a deployment policy is the mean per-episode expected loss over a stream of fixed length; in Studies II–V the length is 100 episodes. The severe-failure probability of an episode is the exact probability, under the hidden true kernel, that the policy in force for that episode ends in catastrophe (outcome index 1). It is a separate endpoint, not a component that expected loss controls.

## 4.5. Transfer and reliability boundary (FM-10)

<<v01|## FM-10.|# 5. Worked examples>>

# 5. Mathematical framework

## 5.1. Sufficient state and belief update (FM-04)

<<v01|## FM-04.|## FM-05.>>

## 5.2. Static action loss (FM-05)

<<v01|## FM-05.|## FM-06.>>

## 5.3. Sequential partial-observation control (FM-06)

<<v01|## FM-06.|## FM-07.>>

## 5.4. Joint fixed-model uncertainty (FM-07)

<<v01|## FM-07.|## FM-08.>>

## 5.5. Dependent failure and the iid ablation (FM-08)

<<v01|## FM-08.|## FM-09.>>

## 5.6. History-rectangular robustness (FM-09)

<<v01|## FM-09.|## FM-10.>>

## 5.7. Cross-episode posterior

Under the deployment structure of Section 4.4, the posterior over the model index after $E$ completed episodes is

$$w_E(m)\propto w_0(m)\prod_{e=1}^{E}\sum_{z}\pi(z\mid m)\prod_{(a,o)\in\tau_e}k(o\mid m,z,a). \tag{9}$$

Each episode contributes its marginal likelihood, in which the latent mode is summed out per episode, because modes are redrawn independently across episodes. Proposition A1 (Section 7.10) shows that the data-dependent choice of actions does not enter (9). Planning then uses the posterior-weighted model set as the prior of the within-episode recursion (4)–(6). Studies II–IV recompute this "posterior model set" every five episodes. The implementation (`handoffx.adaptive.EpisodeBelief`) works in log space. A history with zero likelihood under every model raises an error rather than being renormalized. From version 0.2.1, when the posterior model set is formed, models with exactly zero likelihood are omitted and finite posterior weights that underflow to zero are floored at the smallest normal floating-point number (Section 8.4).

# 6. Decision policies and algorithms

## 6.1. Study I policy suite

<<v01|## Implementation and baseline fairness|# 9. Experimental findings>>

## 6.2. Cross-episode learners (Study II)

All learners use the same supplied information as nominal planning:
- a model set built around the supplied estimate;
- the action guard;
- the costs;
- common random numbers.

They differ only in how they use logged episodes:

- **nominal**: exact DP on the supplied centre model; no learning.
- **bayes_static**, **robust_static**: the Study I Bayesian and robust planners on the prior model set; no learning.
- **plugin_recal**: plan on the maximum-a-posteriori model under (9).
- **bayes_recal**: plan by exact Bayes-adaptive DP with the posterior model set ("ungated posterior recalibration"). This is the strongest deployable learner of Study II and the comparator in Studies III–V.
- **ts_recal**: Thompson sampling of one model per episode (Thompson, 1933; Russo et al., 2018).
- **handoffx_v2**: the conservative gate below, choosing between nominal and bayes_recal.
- **gate_static**: the gate evaluated on the prior only.
- **v2_iid**: handoffx_v2 without persistent modes.
- **oracle**: exact DP on the true model. It knows the generating process, but not the realized mode or future outcomes.

**Conservative switching gate.** Let $\pi_0$ be nominal DP and $\pi_c$ the Bayes-adaptive DP with posterior prior $w$. For each model $m$, let $\Delta_m=L_m(\pi_0)-L_m(\pi_c)$, computed exactly. The gate deploys $\pi_c$ for the next five episodes if and only if

$$\mathbb E_w[\Delta]>\text{margin}\quad\text{and}\quad P_w(\Delta<-\tau)\le\alpha, \tag{10}$$

and otherwise keeps $\pi_0$. The tolerance $\tau$ is a fraction of the incumbent's posterior expected loss. The frozen Study II setting is $\alpha=0.35$, $\tau=3\%$ and margin $0$, selected on development data only. This follows the logic of high-confidence and safe policy improvement (Thomas et al., 2015; Laroche et al., 2019). It is a posterior statement inside a finite, possibly misspecified model set, not a frequentist guarantee.

## 6.3. Study III candidates

All three candidates sit on top of bayes_recal and add no new solver.

**Candidate A: prevalence-augmented posterior planning.** Each supplied model is crossed with three prevalence levels $\lambda\in\{-0.25,0,+0.25\}$ with prior $(0.25,0.5,0.25)$:

$$z(\lambda)=(1-|\lambda|)\,\hat z+|\lambda|\,e_{k(\lambda)},\qquad k(\lambda)=\begin{cases}\text{transient}&\lambda<0\\\text{persistent}&\lambda>0\end{cases}, \tag{11}$$

where $\hat z$ is the supplied prevalence and $e_k$ a vertex of the simplex. The posterior is exact over the resulting 75 models, with planning as in bayes_recal. Under this prior, the expected persistent-mode share is $0.875\,\hat z_{\text{persistent}}+0.0625$, which is higher than the supplied share whenever that share is below 0.5. This asymmetry matters in Study V.

**Candidate B: escalation-targeted posterior sampling.** Each episode, only the human-success offset $h$ is sampled from its posterior marginal; planning is exact Bayes over the models with that offset. Exploration is confined to the parameter that suffers from selective observation (Proposition A2).

**Candidate C: Bayes-factor reversion guard.** With cumulative episode log-likelihoods $\ell_m$, define

$$\log\mathrm{BF}=\log\sum_m w_0(m)\,e^{\ell_m}-\ell_{\text{centre}}. \tag{12}$$

C plans with the posterior only if $\log\mathrm{BF}>\log 3$ (Kass & Raftery, 1995), and otherwise acts nominally. The intent is to stay with the supplied estimate unless the data clearly contradict it.

## 6.4. Catastrophe-weighted planning (exploratory, Study V)

To ask whether explicit risk aversion reproduces candidate A's effect, Study V plans bayes_recal with an inflated catastrophe loss, $F'=cF$ with $c\in\{1.25,1.5,2,3\}$. It evaluates every policy with the true costs:

$$\pi_c=\arg\min_\pi \mathbb E_w\Big[\sum_t\kappa_{a_t}+g'_{\text{terminal}}\Big],\quad g'\in\{0,L,cF,S\};\qquad \text{evaluate }J_P(\pi_c)\text{ with }F. \tag{13}$$

This is a simple risk-sensitive heuristic, related in spirit to exponential-utility and constrained formulations (Howard & Matheson, 1972; Altman, 1999/2021). It is not an implementation of them, and $c$ was not tuned.

# 7. Theoretical properties and limitations

**Attribution and status.** P1–P9 and A1–A4 are derived specializations, elementary consequences or adaptations of established decision and probability theory. They are not claimed as original theorems. Complete arguments are given so that the implementation can be audited. Numerical checks supplement these arguments and do not constitute proofs. No external mathematical peer review has taken place. All guarantees are **model-relative**: they hold for the specified finite model and its assumptions, not for real agents or people.

<<v01|## P1. Static human-intervention boundary|## Mathematical claim ceiling|0|keepstart>>

## 7.10. Propositions for the cross-episode layer (A1–A4)

**Proposition A1 (ignorable sequential design; adaptation of Rubin, 1976).**

*Assumptions.* The deployment structure of Section 4.4: $m^*$ is fixed, modes are redrawn independently per episode and fixed within it, kernels are stationary, and actions depend only on logged data and independent randomization.

*Result.* The posterior over the model index after $E$ episodes is given by (9).

*Proof.* The joint probability of all actions and outcomes factorizes into two kinds of terms:
- action terms $P(a_t\mid\text{past data},\text{randomization})$, which do not involve $m$;
- outcome terms $k(o_t\mid m,z_e,a_t)$.

Integrating each $z_e$ independently gives the episode marginal in (9), and terms not involving $m$ cancel on normalization. The action terms are why the action-selection mechanism is ignorable: no reweighting for data-dependent action choice is required, and unobserved counterfactual outcomes need no imputation. QED.

*Checks.* Sequential and batch updates agree to $4.8\times10^{-15}$, and update order changes nothing ($1.9\times10^{-16}$). The result fails if escalation also depends on unlogged information, such as an operator's private judgement.

**Proposition A2 (no learning without the action).**

*Assumptions.* Models $m,m'$ have identical prevalences and identical kernels for every action except $a$, and $a$ was never taken in the data.

*Result.* $w_E(m)/w_E(m')=w_0(m)/w_0(m')$.

*Proof.* Every factor in (9) other than the prior is identical for $m$ and $m'$. QED.

*Consequences.*
- Within one episode, human effectiveness is never learned before handing off. This formalizes CE6 for the planner and explains Study I's inability to correct a biased human estimate (Section 11.1).
- Across episodes, a policy that stops escalating stops learning about the human. This exploration problem underlies the self-confirming trap of Section 7.13.

**Proposition A3 (posterior-risk monotonicity of the gate).**

*Result.* (a) If $\pi_c$ is the Bayes-adaptive DP policy for prior $w$, then $\mathbb E_w[\Delta]\ge0$. (b) For any margin $\ge0$, the policy deployed by (10) has posterior expected loss no larger than the incumbent's.

*Proof.* (a) Exact DP with prior $w$ minimizes $\mathbb E_w[L_m(\pi)]$ over all history-dependent admissible policies (P5), and $\pi_0$ is such a policy. (b) The gate switches only when $\mathbb E_w[\Delta]>\text{margin}\ge0$. QED.

*Checks.* Over 30 random environments and posteriors: minimum posterior advantage 0.0, and maximum posterior risk increase of the gate 0.0.

**Proposition A4 (credible degradation statement).**

*Result.* If the gate switches, then $P_w(L_m(\pi_c)>L_m(\pi_0)+\tau)\le\alpha$. In the boundary cases:
- with $\alpha=0$ and $\tau=0$, it switches only under weak dominance on every model with positive posterior weight;
- with $\alpha=1$ and margin $-\infty$, it reduces to posterior-risk minimization over $\{\pi_0,\pi_c\}$, which is bayes_recal.

*Proof.* Direct from (10). QED.

*What A4 does not say.* It is not a frequentist bound on the true environment. If the truth is not in $M$, the posterior concentrates on the models closest in Kullback–Leibler divergence (Berk, 1966), which need not be the models closest in decision loss. The gate can then become more confident precisely when it is wrong (CE9).

## 7.11. Mathematical claim ceiling

<<v01|## Mathematical claim ceiling|# 7. Counterexamples and limits>>

The cross-episode layer adds A1–A4 and CE9. Not established:
- any frequentist improvement guarantee;
- regret bounds for deployment streams;
- consistency under misspecification beyond Berk's (1966) KL-projection result;
- optimality of the gate, of candidate A or of catastrophe weighting outside the benchmark distributions.

## 7.12. Counterexamples (CE1–CE9)

<<v01|# 7. Counterexamples and limits|## Additional limits checked in the text|+1>>

### CE9. Under misspecification the posterior converges confidently to a wrong model

This counterexample was observed in Study II, held-out test environment 300120:
- The supplied success and hazard estimates were exactly correct, so nominal DP was optimal.
- The true persistent-mode prevalence was 0.45, against an estimated 0.31.
- Prevalence is not a free parameter of the Study II model grid, so the posterior accommodated the extra persistent failures by moving to a wrong human-success offset ($-0.10$).
- The gate's within-model degradation probability fell below $\alpha$, and it switched in 80 of 100 episodes.
- True loss rose 13.2% above nominal, which here equals the oracle.

A posterior predictive check (Box, 1980) or a richer model set are natural remedies. Study III tested the second (candidate A) and a marginal-likelihood guard (candidate C). Neither removed the underlying identifiability problem (Sections 12 and 14).

### Additional limits

<<v01|## Additional limits checked in the text|# 8. Computational methodology>>

## 7.13. Empirical learning traps (observations, not theorems)

Studies III–V documented three mechanisms that limit adaptive learning in this model class. They are reported here as empirical regularities with a clear mechanism; they are not theorems.

1. **Self-confirming escalation trap.** In 6 of 32 development environments, a learner that became pessimistic about the human almost stopped escalating. In one example the late human-escalation rate was 0.01 against the oracle's 1.0, with only 7 human observations in total. By A2 it then stopped learning that escalation would have helped. These environments held 91% of the residual learning plateau. This is an instance of incomplete learning in Bayesian sequential decisions (Harrison et al., 2012). Targeted exploration (candidate B) did not escape it within 100 episodes.
2. **Stop-at-first-step trap.** In some environments nominal planning stops at the first step, so no action is ever taken and no policy that starts from it collects data.
3. **Human/prevalence confounding.** In the supplied model, human success differs by latent mode and is highest relative to AI success in the persistent mode. Evidence that "the human fails more often than expected" can therefore be partly explained by "persistent faults are more common", and the two are not separately identifiable from these logs. Study IV confirmed the practical consequence: candidate A escalated *more* when the human was *worse* than supplied (Section 13.5).
