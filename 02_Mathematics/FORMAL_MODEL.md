# Formal model and notation

**Status:** specified and implemented for the bounded latent-mode subclass below. General MDP/POMDP notation explains the relationship to prior art; it does not imply that the prototype solves arbitrary POMDPs. All probabilities in the experiments are synthetic design choices, not observations of LLMs or human workers.

## FM-01. Decision environment and units

An episode is a task with $J$ ordered, otherwise homogeneous milestones, deadline $T$ integer time ticks, resource budget $B$ integer quota units, and at most one terminal human intervention. The controller minimizes expected cumulative operational loss. A loss unit is an artificial common utility unit. A time tick is a synthetic latency unit, not a measured second. Resource units are distinct from loss units and enforce a hard quota. Conversion of money, time and failure consequences into a common utility is an application owner's responsibility.

The broad finite-horizon formulation has hidden state $x_t$, observable history $h_t=(o_0,a_0,o_1,\ldots,o_t)$, available action set $\mathcal A(h_t)$, action-dependent transition kernel $P_\theta(x'\mid x,a)$, observation kernel $O_\theta(o\mid x',a)$, nonnegative cost $c_t(x,a)$, duration $d(a)$, and terminal loss $g(x)$. A history-measurable policy $\pi$ maps the observable history to an admissible action. A belief $b_t(x,\theta)$ is a conditional distribution, not a neural confidence score. These are established POMDP constructions (Kaelbling et al., 1998).

The implemented environment specializes this structure: $Z\in\{0,1,2\}$ is a fixed hidden task mode (healthy, recoverable, persistent), and $\Theta\in\{1,\ldots,M\}$ is a fixed episode-level model index. Neither is observed by any evaluated policy. The observed state contains completed progress, elapsed time, spent resources, unresolved-failure flag, and sufficient outcome counts. There are no hidden-state transitions except absorbing task termination. 'Recoverable' means a higher retry success probability, not a separately modeled repair of $Z$. Shared persistent $Z$ induces dependence among action outcomes even though they are conditionally independent given $(\Theta,Z)$.

## FM-02. Actions, outcomes and terminal semantics

The executable actions are $C$ (continue), $R$ (retry the currently failed milestone), and $H$ (human rescue of the entire remaining task); $S$ is authorized safe stop.

| Action | Admissibility | Successful outcome | Failure outcome | Duration | Quota |
|---|---|---|---|---:|---:|
| Continue $C$ | Time/quota/authorization sufficient | Advance one milestone | Remain at milestone; receive soft/hard diagnostic | 1 | 1 |
| Retry $R$ | Previous milestone attempt unresolved, plus constraints | Advance the failed milestone | Remain unresolved; receive diagnostic | 1 | 2 |
| Human $H$ | Ticket, known availability, time/quota sufficient | Complete the entire task | Terminal ordinary failure or catastrophe | 2 by default | 3 |
| Stop $S$ | Always externally authorized in this model | Not task success | Terminal safe abandonment | 0 | 0 |

Human rescue is deliberately not a perfect oracle. Continue and retry are not interchangeable: retry is unavailable initially, has different probability and cost parameters, and consumes twice the quota. Human assistance terminates the episode and consumes a different duration. A nonterminal outcome on the last time tick becomes ordinary deadline failure; it does not acquire a free last-moment safe-stop option. Task completion exactly at the deadline is success. Quota exhaustion before the deadline leaves the authorized safe-stop action available.

For $a\in\{C,R,H\}$ and $(m,z)$, let $p_{mza}$ be probability of progress/success and $q_{mza}$ probability of catastrophe. They are unconditional competing-outcome probabilities, so $0\le p_{mza}+q_{mza}\le1$. The remaining probability is ordinary failure. For $C,R$, a failure carries diagnostic $D\in\{0,1\}$ with $P(D=1\mid\text{failure},m,z,a)=d_z$. The prototype uses known diagnostic likelihoods, not learned ones. The four categorical probabilities are

$$K_{mza}=\left(p_{mza},q_{mza},(1-p_{mza}-q_{mza})(1-d_z),(1-p_{mza}-q_{mza})d_z\right). \tag{1}$$

For human rescue, $K_{mzH}=(p_{mzH},q_{mzH},1-p_{mzH}-q_{mzH},0)$. Its ordinary failure is terminal; it does not emit a diagnostic that can influence another decision. Outcomes are mutually exclusive and exhaustive.

## FM-03. Costs, restrictions and objective

Let $c_a$ be executable-action operating cost and $\lambda$ be loss per time tick. The immediate cost is $\kappa_a=c_a+\lambda d(a)$. Success has terminal loss zero, ordinary terminal failure/deadline has loss $L$, catastrophe has loss $F$, and authorized safe abandonment has loss $S$. All are nonnegative. Stopping does not count as task success and is reported separately from ordinary and severe failures.

$$J_P(\pi)=\mathbb E_P^\pi\left[\sum_{t:\,a_t\ne S}\kappa_{a_t}+g_{\rm terminal}\right],\quad g_{\rm terminal}\in\{0,L,F,S\}. \tag{2}$$

The expected-loss objective is not a tail-risk or catastrophic-failure guarantee. Severe-failure probability and empirical upper-tail loss are distinct secondary measures. One optional action guard imposes a per-decision worst-model catastrophe-probability cap $\delta/T$; Proposition P7 states exactly what this ensures. There is no implemented general constrained-POMDP or CVaR optimizer.

The admissible set excludes actions without enough quota or time, unavailable human assistance, unauthorized actions, retry before a failure, and (in one scenario) continued execution after failure in an irreversible workflow. A known schedule $u_t\in\{0,1\}$ represents human availability. The prototype does not learn availability, model a human queue, or coordinate capacity across simultaneous tasks. A human ticket is a per-task constraint. No passive 'wait' action exists; delaying help means taking a permitted task action. If no such action is authorized, safe stop remains.

## FM-04. Sufficient state and belief update

Let $n=(n_{C+},n_{C0},n_{C1},n_{R+},n_{R0},n_{R1})$ count observed nonterminal progress and soft/hard failures. Let $f\in\{0,1\}$ record whether the last milestone attempt remains unresolved. Elapsed time is $t=\sum_i n_i$, progress is $j=n_{C+}+n_{R+}$, and quota used is $b=\sum_{i=1}^3 n_i+2\sum_{i=4}^6 n_i$. Human actions never enter these counts because they terminate the task. Thus the implemented state is $s=(n,f)$ with the immutable task specification supplied separately.

Write $\mu_{mz}=P(\Theta=m,Z=z)$ for the initial joint distribution. Because the hidden pair is fixed and likelihoods commute, counts are sufficient for inference in this subclass:

$$b_{mz}(n)=\frac{\mu_{mz}\prod_{a\in\{C,R\}}\prod_{o\in\{+,0,1\}}K_{mza,o}^{n_{ao}}}{\sum_{m',z'}\mu_{m'z'}\prod_{a,o}K_{m'z'a,o}^{n_{ao}}}. \tag{3}$$

The code computes this expression in log space. Zero-likelihood observations under every supplied model raise an explicit error; they are not silently renormalized into an arbitrary posterior. Counts do not suffice under time-varying probabilities, fatigue, learning human operators, history-sensitive repairs, or action-order-dependent outcomes. Such applications need a richer adapter and a different solver.

The Bayesian predictive outcome law is $\bar K_{a,o}(s)=\sum_{m,z}b_{mz}(s)K_{mza,o}$. For robustness, $K^m_{a,o}(s)=\sum_z b(z\mid m,s)K_{mza,o}$ is the model-conditional predictive law. A single nominal-model planner keeps $m$ fixed at the central supplied model and updates only $Z$.

## FM-05. Models A and B: static action loss

For a single binary task and mutually terminal alternatives, $Q_a=c_a+(1-p_a)L$, with $Q_S=S$. Catastrophe can be included as $Q_a=\kappa_a+q_aF+(1-p_a-q_a)L$. Minimize over feasible actions. Human rescue is preferred to AI exactly when $p_H-p_A\ge(c_H-c_A)/L$ under the symmetric-loss, no-separate-catastrophe assumptions and $L>0$. This is an adaptation of established Bayes deferral, not new mathematics (Mozannar & Sontag, 2020).

Example: $p_A=.65$, $p_H=.90$, $c_A=1$, $c_H=4$, $L=20$ gives losses 8 and 6, so human rescue is preferred; the human-success threshold is .80. A .05 probability error changes the corresponding action loss by one loss unit. With $S=5$, stopping dominates both. With $L=0$, only action costs matter and division by $L$ is invalid. A computed threshold above 1 means human rescue cannot satisfy that inequality; it is not clipped to manufacture feasibility.

The implemented `static_loss` benchmark uses static committed completion plans because $C,R$ only finish a milestone while $H$ finishes a task. Its $C$ plan attempts all remaining milestones without post-failure recovery; its $R$ plan retries the present milestone then continues. It values failure as terminal but replans after an actually observed nonterminal failure. The fully sequential nominal planner is the principal strong comparator, so conclusions do not depend on this deliberately myopic comparator.

## FM-06. Models C and D: sequential partial-observation control

Let $s^{a,o}$ be the updated count state for $a=C,R$ and a noncatastrophic outcome. The value at completed progress is zero. The value at an unfinished deadline is $L$. Otherwise,

$$V(s)=\min_{a\in\mathcal A(s)}Q(s,a), \tag{4}$$
$$Q(s,S)=S,\qquad Q(s,H)=\kappa_H+\bar K_{H,1}(s)F+[\bar K_{H,2}(s)+\bar K_{H,3}(s)]L, \tag{5}$$
$$Q(s,a)=\kappa_a+\bar K_{a,1}(s)F+\sum_{o\in\{0,2,3\}}\bar K_{a,o}(s)V(s^{a,o}),\quad a\in\{C,R\}. \tag{6}$$

Outcome index 0 means progress, index 1 catastrophe, and indices 2/3 diagnostic failures. The mathematical symbols $+,0,1$ in the counts denote progress and the two diagnostic values; they are distinct from these categorical array indices. All code documentation uses the four categorical indices to avoid an implicit mapping.

This is finite-horizon belief-state dynamic programming, specialized from established POMDP theory. Recursion terminates because every nonterminal action increases elapsed time. A cached exact computation is feasible for the small experiment horizons. No approximation grid or learned value function is used. The general problem can be expensive; the implementation accepts horizons 1 through 12, and the reported evidence is concentrated at 3 and 6 ticks.

## FM-07. Model E: joint fixed-model uncertainty

Each supplied model is an alternative joint account of AI and human effectiveness. The benchmark uses nine combinations of additive offsets $(-.18,0,.18)$ to AI success probabilities (both $C,R$) and human success probabilities. The perturbation generator explicitly clips to $[.01,1-q-.01]$ before constructing a valid model; the public model validator never silently fixes invalid probabilities.

The joint prior over these offsets is

$$W=\begin{pmatrix}.20&.025&.05\\.025&.40&.025\\.05&.025&.20\end{pmatrix}. \tag{7}$$

Its marginal probabilities are $(.275,.45,.275)$ on each axis. The independent-prior ablation uses the outer product of these marginals, retaining the same support and initial one-action predictions. The off-diagonal-reversed true-prior scenario preserves those marginals while changing the sign of association. In every case, the model index is fixed within an episode, rather than independently redrawn on every action.

The prior is elicited synthetic experimental structure. It is not a fitted posterior or a confidence region with empirical coverage. Bayesian optimality applies to its prior-predictive distribution, not automatically to each possible fixed model. Failure observations can update beliefs about human effectiveness through the assumed coupling; incorrect coupling can therefore mislead the policy.

## FM-08. Model F: dependent failure and iid ablation

Conditional independence given a persistent hidden mode does not imply marginal independence. If an action has latent success probability $P$, then survival through $k$ failed attempts has probability $\mathbb E[(1-P)^k]$, not generally $(1-\mathbb E P)^k$. The count posterior responds to repeated failures by shifting mass toward persistent modes. The iid-mode ablation averages the kernel over the initial mode distribution separately within each model, then resamples the implicit mode at each action. It preserves one-step marginals but removes within-model temporal dependence. It retains episode-level parameter uncertainty if multiple models remain.

## FM-09. Model G: history-rectangular robustness

At each observable history, form $\mathcal U(s,a)=\operatorname{conv}\{K^m_a(s):m\text{ remains possible}\}$. The robust policy solves an adversarial history-tree problem in which nature can select a different conditional kernel at each history and action. Its recursion replaces the Bayesian outcome expectation in (5)-(6) with a maximum over the model-conditional expectations, using a common robust continuation value $W_R$.

$$W_R(s)=\min_{a\in\mathcal A(s)}\max_m\left\{\kappa_a+\mathbb E_{K^m_a(s)}[\text{terminal loss or }W_R(s')]\right\}. \tag{8}$$

Stop has no uncertain transition. The row-selection envelope contains every fixed-model history distribution, but usually also distributions that cannot arise from any fixed model. This gives an upper bound on fixed-model worst-case loss, not equality with fixed-parameter minimax. This interpretation is essential to applying established rectangular robust dynamic programming (Iyengar, 2005; Nilim & El Ghaoui, 2005). The code does not reproduce the finite-state-controller algorithm of Cubuktepe et al. (2021); that paper establishes broader prior art.

## FM-10. Transfer and reliability boundary

Structural transfer means the same solver accepts a new adapter's correctly defined kernels, states, costs and restrictions. Parameter transfer means those conditional probabilities remain accurate. Performance transfer additionally requires the objective, feasibility rules and relevant conditional distributions to remain comparable. Only structural transfer is built into the API. The experiment's shifted environment changes success, hazards and mode prevalence; perfect recalibration is an oracle-like upper-bound control, not evidence that a real estimator can recover those values.

Reliability in this report means (i) correct optimization/evaluation within the specified finite model, (ii) reproducible empirical loss and catastrophic-failure rates, and (iii) explicitly conditional theoretical bounds. It does not mean safety certification, universal correctness, an autonomous-control authorization, or verified real-world human benefit.
