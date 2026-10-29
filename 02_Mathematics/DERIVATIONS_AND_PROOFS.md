# Derivations and proofs

**Attribution and status.** P1-P9 below are explicitly derived specializations, elementary consequences, or adaptations of established decision/probability theory. They are not claimed as original HandoffX theorems. Complete arguments are given so that the implementation is auditable. Numerical checks supplement these arguments and do not constitute proofs. No independent external mathematical peer review has occurred.

## P1. Static human-intervention boundary

**Assumptions.** A single task; two mutually terminal actions $A,H$; success losses zero; identical failure loss $L>0$; deterministic action costs $c_A,c_H$; correct conditional success probabilities $p_A,p_H$; no additional constraints or catastrophic-outcome category.

**Result.** Human assistance weakly minimizes expected loss exactly when $p_H\ge p_A+(c_H-c_A)/L$. At equality both actions are optimal. If a stop action or other alternative is present, this is only the pairwise human/AI comparison, not a sufficient condition for global optimality.

**Proof.** Subtract the two losses:

$$Q_H-Q_A=(c_H-c_A)-L(p_H-p_A). \tag{P1.1}$$

Therefore $Q_H\le Q_A$ is equivalent to the stated inequality. This exhausts both directions. Differentiating the threshold with respect to $c_H$ gives $1/L>0$, and with respect to $c_A$ gives $-1/L$. If $c_H\ge c_A$, increasing $L$ weakly lowers the extra probability advantage required from the human; if $c_H<c_A$, the sign of that loss sensitivity reverses. With $L=0$ the comparison reduces to costs, not a probability threshold. Thresholds outside $[0,1]$ indicate always/never feasibility rather than a need to clip the algebra. QED.

**Interpretation.** A more accurate helper can still be too expensive, and a less accurate but sufficiently cheaper helper can still minimize expected cost. The static decision is an established cost-sensitive deferral rule (Mozannar & Sontag, 2020).

## P2. Stability and regret under action-value errors

**Assumptions.** A finite feasible action set is identical under the estimated and true models. For every action, $|Q_a-\widehat Q_a|\le\epsilon_a$. The estimate selects $\hat a\in\arg\min\widehat Q_a$.

**Result.** If $\widehat Q_b-\widehat Q_{\hat a}>\epsilon_b+\epsilon_{\hat a}$ for every $b\ne\hat a$, then $\hat a$ is the unique true minimizer. Without that gap, true regret is at most $\epsilon_{\hat a}+\epsilon_{a^*}$, where $a^*$ minimizes true loss; hence it is at most $2\epsilon$ if all errors are at most $\epsilon$.

**Proof.** For each alternative,

$$Q_b-Q_{\hat a}\ge\widehat Q_b-\widehat Q_{\hat a}-\epsilon_b-\epsilon_{\hat a}>0.$$

For regret,

$$Q_{\hat a}-Q_{a^*}\le\widehat Q_{\hat a}+\epsilon_{\hat a}-\widehat Q_{a^*}+\epsilon_{a^*}\le\epsilon_{\hat a}+\epsilon_{a^*}. \tag{P2.1}$$

The last inequality follows from estimated optimality. QED.

For P1's static losses with exact costs, probability error at most $\eta_a$ yields $\epsilon_a=L\eta_a$. With cost errors at most $\rho_a$, take $\epsilon_a=\rho_a+L\eta_a$. This is a deterministic perturbation bound, not a statistical statement that an uncalibrated model attains those errors. It also does not transfer unchanged to sequential policy regret without controlling continuation-value error.

## P3. Correlation alone cannot change a one-step Bayesian linear-loss rule

**Assumptions.** Before observing any new signal, choose one terminal action. Its loss is $c_a+(1-P_a)L$; $P_a$ is uncertain. Two joint priors have the same marginal means $\mathbb E P_a$ for every action.

**Result.** Both priors produce identical expected action losses and identical sets of Bayes-optimal actions, irrespective of their cross-action correlations.

**Proof.** Linearity gives $\mathbb E[c_a+(1-P_a)L]=c_a+[1-\mathbb E P_a]L$. The right-hand side contains no cross-moment or covariance. Since it is equal action by action under the two priors, the minimizing sets agree. QED.

**Important limit.** The result does not apply to nonlinear objectives, multi-action contingent policies, or posterior means after an informative observation. For example, let $(P_A,P_H)$ be $(.2,.2)$ or $(.8,.8)$ with equal prior weights. A failed AI attempt yields $\mathbb E[P_H\mid A\text{ fails}]=.32$. For the opposite coupling $(.2,.8)$ or $(.8,.2)$, the same observed failure yields .68. Both initial human means were .5. With $c_H=.2,c_A=0,L=1$ and posterior AI success .32, the human action has loss .88 versus AI .68 under positive coupling, but human .52 under negative coupling. The human decision flips. This is the specific mechanism tested by the joint-prior ablation; vague claims that 'correlation always matters' are rejected.

## P4. Persistent mixtures make iid retry calculations optimistic

**Assumptions.** A fixed but unobserved $P\in[0,1]$ is drawn once per task. Repeated identical attempts are conditionally iid Bernoulli successes given $P$. Failed attempts do not repair or otherwise change $P$. Let $S_k=\mathbb E[(1-P)^k]$ and $p_k=\mathbb E[P\mid k\text{ failures}]$ whenever $S_k>0$.

**Results.** For integer $k\ge1$, $S_k\ge(1-\mathbb EP)^k$. Whenever $p_k<1$, the posterior success probability satisfies

$$p_k-p_{k+1}=\frac{\operatorname{Var}(P\mid k\text{ failures})}{1-p_k}\ge0. \tag{P4.1}$$

**Proof.** For $k=1$ the first statement is equality. For $k\ge2$, $(1-p)^k$ is convex on $[0,1]$, so Jensen's inequality gives the bound. For the second statement, take expectations under the posterior after $k$ failures, denoted $\mathbb E_k$:

$$p_{k+1}=\frac{\mathbb E_k[P(1-P)]}{\mathbb E_k[1-P]}=\frac{p_k-\mathbb E_k[P^2]}{1-p_k}.$$

Subtract this from $p_k$ to obtain $(\mathbb E_k[P^2]-p_k^2)/(1-p_k)$. This proves the identity and sign. If $p_k=1$, another failure has probability zero and the conditional posterior is undefined, rather than a counterexample. QED.

**Example.** $P=.8$ with probability .6 and $.05$ with probability .4 gives mean .5. Three iid attempts at .5 would promise success .875. The persistent mixture instead gives $1-[.6(.2)^3+.4(.95)^3]=.65225$. Dependence changes the prospective decision without introducing a new optimal-stopping theory. The result need not hold after a genuine repair action changes the latent mode; that process lies outside these assumptions.

## P5. Exactness of the finite-horizon Bayesian recursion

**Assumptions.** Finite latent model/mode and action/outcome sets; a correct prior and stationary conditional kernels; nonnegative bounded costs; observable feasibility restrictions; every nonterminal executable action consumes at least one time tick; the sufficient state and terminal losses are as defined in FM-01 through FM-06.

**Result.** Equations (4)-(6) return the minimum prior-predictive expected cumulative loss over all history-measurable admissible policies. A minimizing action at each sufficient state defines an optimal policy for that model.

**Proof.** At a success or unfinished deadline, the specified terminal value is the entire remaining loss, so the assertion holds. Induct on remaining time. At an earlier state, any admissible policy selects a first action using only history. Conditioning on the next outcome decomposes its loss into the action cost, any terminal loss, and continuation loss. The posterior in (3) is Bayes' rule; therefore it yields the correct predictive outcome probabilities. Conditional independence and stationary likelihoods make the count state sufficient, while $f$ retains the information needed for retry feasibility. By the induction hypothesis, each nonterminal continuation costs at least $V(s')$, with equality attained by the recursively minimizing policy. Minimizing the resulting first-action expectations gives (4)-(6) and an attaining policy. Every recursion reduces remaining time, so the induction terminates. QED.

This is a specialization of established POMDP dynamic programming (Kaelbling et al., 1998), not a guarantee under model misspecification or an assertion that the solver scales to arbitrary state spaces.

## P6. What the robust envelope actually guarantees

**Assumptions.** For each retained fixed model $m$, its conditional outcome kernel after each possible observable history is $K^m(s,a)$. The action set and costs are shared. The history-rectangular uncertainty set permits nature to choose any retained conditional kernel independently at each history/action. A fixed-model environment is included in this larger set. Priors over latent modes conditional on each model and observation likelihoods are correctly specified for the included environment.

**Result.** For any admissible policy $\pi$,

$$\max_m J_m(\pi)\le J_{\rm envelope}(\pi). \tag{P6.1}$$

The minimax recursion (8) computes the optimal envelope value. For its selected policy $\pi_R$, $\max_mJ_m(\pi_R)\le W_R(s_0)$. In general neither $W_R(s_0)=\min_\pi\max_mJ_m(\pi)$ nor universal improvement over a nominal policy follows.

**Proof.** Every distribution generated by keeping one model $m$ fixed is a permitted history-tree selection in the envelope: choose that model's conditional kernel at every history. The supremum over a set that contains each such distribution is at least its largest fixed-model expectation, giving (P6.1). The independent per-history choices make nature's continuation subproblems separable. Backward induction, with maximum over nature's kernel before minimization over the chosen action at that history, gives (8). Applying (P6.1) to its minimizing policy yields the bound. QED.

The guarantee is conditional on coverage of the true history kernels. Changing hazard rates, latent prevalence or diagnostic likelihoods can invalidate it even when a success-probability interval looks wide. Rectangularity and robust dynamic programming are established (Iyengar, 2005; Nilim & El Ghaoui, 2005). Counterexample CE5 shows why the larger uncertainty set cannot be silently equated with fixed-parameter uncertainty.

## P7. Conditional per-action catastrophe guard

**Assumptions.** At most $T$ executable actions occur per episode. For every history reached by a guarded policy, its next-action catastrophe probability under the true environment is at most $\delta/T$. Stop has zero catastrophe probability. The chosen ambiguity set contains the true conditional next-outcome law whenever a worst-model cap is used.

**Result.** Episode catastrophe probability is at most $\delta$ for every policy that obeys the guard, even with dependent failures and adaptive decisions.

**Proof.** Let $I_t$ indicate catastrophe on the $t$th executable action, assigning zero after termination. By conditional expectation, $\mathbb E I_t\le\delta/T$. Since $\mathbf1\{\text{any catastrophe}\}\le\sum_{t=1}^T I_t$, taking expectations yields $P(\text{any catastrophe})\le\sum_t\mathbb EI_t\le\delta$. Independence is not needed. QED.

This is a conservative union-bound specialization, not a new safety theorem. Its premise is stronger than average calibration, and checking an estimated cap does not establish its premise. The filter may force safe abandonment. Task success and feasibility costs must therefore be reported alongside catastrophe frequency.

## P8. A bounded-horizon transfer/approximation inequality

**Assumptions.** Two processes share the same finite history/action tree, feasible actions and terminal-loss function. There are at most $T$ decisions. Nonterminal action costs lie in $[0,c_{\max}]$ and differ between models by at most $\epsilon_c$ at every history/action. Terminal losses lie in $[0,G]$. The total variation distance of the next-outcome laws is at most $\epsilon_p$ uniformly over all those histories/actions, including terminal outcomes. Total variation is $\frac12\sum_o|P(o)-P'(o)|$.

**Result.** For a fixed policy,

$$|J_P(\pi)-J_{P'}(\pi)|\le D_T:=T\epsilon_c+\epsilon_p\left[TG+\tfrac12T(T-1)c_{\max}\right]. \tag{P8.1}$$

If $\pi'$ is optimal under $P'$, its regret under $P$ is at most $2D_T$.

**Proof.** Let $\Delta_h$ bound the fixed-policy value difference with $h$ decisions remaining. At the next action, the immediate-cost difference is at most $\epsilon_c$. Add and subtract the expectation of the same reference continuation under the other next-outcome law. The difference caused by continuation values is at most $\Delta_{h-1}$. The reference continuation, including a terminal branch's loss, lies between zero and $(h-1)c_{\max}+G$, so the total-variation inequality bounds the distributional difference by $\epsilon_p[(h-1)c_{\max}+G]$. Thus $\Delta_h\le\epsilon_c+\Delta_{h-1}+\epsilon_p[(h-1)c_{\max}+G]$, with $\Delta_0=0$ because the terminal-loss functions agree. Summing proves (P8.1). For regret add and subtract the two $P'$ policy values; their difference is nonpositive by optimality, leaving at most two fixed-policy discrepancies. QED.

The bound can be numerically loose. Importantly, it requires uniform error in history-conditioned outcome laws, not just small raw parameter error or aggregate calibration. The formula is an elementary finite-horizon simulation-lemma-style adaptation, not a newly claimed online-learning regret rate.

## P9. Free information cannot increase optimal Bayes loss

**Assumptions.** An optional signal is observed before a terminal decision. It does not change the environment, feasible actions, costs or deadline, and has no acquisition cost. The posterior model is correct and the controller may ignore the signal.

**Result.** The optimal expected loss with the signal is no greater than without it. If a signal costs $k$, its use is beneficial exactly when the reduction in optimal expected terminal loss exceeds $k$, subject to the stated unchanged-environment assumptions.

**Proof.** Any fixed action available before the signal can be used after every signal realization, so the signal-contingent policy class contains every signal-ignoring policy. Minimization over a superset cannot increase the optimum. Equivalently, $\mathbb E[\min_a\mathbb E(\ell_a\mid Y)]\le\min_a\mathbb E\ell_a$. Adding a deterministic cost $k$ gives the second statement. QED.

**Example.** Two equally likely task types favor opposite actions with success probabilities .9 and .1; failure loss is 10 and action costs are zero. Before information either action has loss 5. Perfect type information gives loss 1, so its value is 4. An 80%-accurate symmetric signal gives selected-action success .74 and loss 2.6, a value of 2.4. Waiting in the HandoffX simulator is not a free exogenous signal: it consumes time, may incur risk, and can alter human availability. This proposition cannot justify unqualified recommendations to delay intervention.

## Mathematical claim ceiling

The complete arguments above establish properties of the specified mathematical objects. They do not prove probability-estimator consistency, universal threshold monotonicity, robust dominance, unconditional transfer, human superiority, real-world intervention benefit, or novel mathematical priority. There are no unresolved theorems presented as results and no unproved conjectures used by the implementation.
