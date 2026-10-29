# Literature review and mathematical equivalence audit

**Review type:** targeted, source-grounded continuation of the supplied Phase 1 scoping audit; not a database-exhaustive systematic review. Search and verification date: October 28, 2026. The filename is retained to match the requested deliverable, not to imply a PRISMA-complete review. The original seven-file audit is preserved unchanged in `phase1_original/`.

## LIT-01. Decision after re-verification

The prior Category C decision survives: the defensible contribution is an auditable comparative benchmark and bounded reference implementation. Adding continue, retry, human and stop labels to a sequential decision model does not establish new mathematics. In particular, the additional verification of Bayes-adaptive POMDP literature strengthens, rather than weakens, the equivalence finding. HandoffX's joint belief over model parameters and task modes is a small finite-support specialization of established Bayesian sequential decision-making, not an original general solution.

## LIT-02. Closest evidence and implications

### KAE98: Kaelbling et al., 1998

Belief-state control in partially observable stochastic environments. The finite count-state solver is a restricted POMDP specialization. Access: metadata/abstract; Publisher metadata verified; author-hosted PDF timed out.

### ROSS11: Ross et al., 2011

Bayes-adaptive POMDPs jointly track state and uncertain model parameters. Joint hidden-state/parameter beliefs and information-sensitive planning are established. Access: selected original full text; JMLR PDF sections 2-3; selected equations inspected; p. 1736 screenshot inspected.

### MOZ20: Mozannar & Sontag, 2020

Cost-sensitive reduction and consistent surrogate learning; Bayes decisions compare machine and expert conditional correctness. HandoffX reuses the decision principle, not the trained surrogate or its sample guarantees. Access: selected original full text; Original PDF pp. 2-4, displayed Bayes rules and loss; equation pages visually inspected.

### IYE05: Iyengar, 2005

Robust dynamic programming uses structured uncertainty sets to support dynamic recursion. Rectangularity is consequential; HandoffX claims an envelope, not fixed-parameter minimax equivalence. Access: metadata/abstract; Publisher record/abstract; full original proof not independently rechecked.

### NIL05: Nilim & El Ghaoui, 2005

Robust MDP control handles uncertain transition matrices. Uncertain action transitions and worst-case cost optimization are established. Access: metadata/abstract; Publisher record/abstract; exact assumptions not re-proved from original paper.

### SUI20: Suilen et al., 2020

Uncertain-POMDP policy synthesis via convex optimization. Partial observation plus transition uncertainty is prior art. Access: metadata/abstract; Official IJCAI abstract/metadata; not an implemented algorithm comparison.

### CUB21: Cubuktepe et al., 2021

Robust finite-state controllers for uncertain POMDPs and specified objectives. HandoffX does not reproduce this controller-synthesis algorithm or inherit all guarantees. Access: metadata/abstract; Official AAAI metadata/abstract; CDN PDF access failed.

### SIN23: Singi et al., 2023

HULA queries an expert using estimated return variance with a limited call budget. Original method assumes consistently high-quality advice; this prototype permits weak helpers. Access: selected original full text; HTML section III and evaluation overview; robotic expert returns an action, not terminal rescue.

### SHA26: Shaikh, 2026

Bayesian intra-generation stopping, learned competence posterior and stronger-model escalation. Timing/calibration are prior art; reported real-model validation does not execute the optimal stopping DP. Access: selected original full text; arXiv v1 HTML sections 3-5, 8, 10; internal Version 1.1 is not arXiv v2.

### HIL26: Trinh et al., 2026

Progressive blockers and asking behavior in coding/SQL, evaluated with Ask-F1 and task outcomes. Sequential help-seeking benchmarks already exist; HandoffX instead isolates a costed synthetic decision model. Access: selected original full text; Version 4 HTML design/limitations; corrected author list and order.

### ALV25: Alves et al., 2025

Learning-to-defer benchmark includes synthetic expert behavior and capacity constraints. Benchmarking fallible humans is established; its tabular allocation task differs from repeated recoveries. Access: selected original full text; PMC full text methods/limitations; synthetic experts are not real participants.

### ROS11: Rosenthal et al., 2011

Robot assistance decisions model human accuracy and availability. Imperfect or unavailable people are established, not a new HandoffX concept. Access: metadata/abstract; Official AAAI abstract and metadata.

### BAL23: Balazadeh et al., 2023

Two-layer MDP switches control among agents, with confidence bounds and reported sublinear regret. Switching and shared environment information are prior art; no new online-regret claim is made. Access: metadata/abstract; arXiv v3 record; final TMLR record blocked, so cite this version.

### VER22: Verma & Nalisnick, 2022

One-vs-all construction addresses calibration of expert correctness in learning to defer. Numerically valid probabilities are not automatically calibrated; HandoffX does not fit an estimator. Access: metadata/abstract; Official PMLR abstract and complete metadata.

### VER23: Verma et al., 2023

Multiple-expert deferral, calibrated surrogate scores and conformal expert ensembles. Multiple candidate helpers or expert uncertainty are not inherently new. Access: metadata/abstract; Official PMLR abstract; no independent proof replication.

### MAD18: Madras et al., 2018

Predict/defer learning with a fallible downstream decision maker and fairness-sensitive loss. Human-versus-AI expected loss is prior art; no retry benchmark is replicated here. Access: metadata/abstract; Instance features; prediction or deferral; reported classification evaluation.

### CHA22: Charusaie et al., 2022

Sample-efficient learning of predictors that complement human decisions. Human complementarity and data acquisition require their own learning evaluation. Access: metadata/abstract; Official PMLR abstract and metadata.

### HEM23: Hemmer et al., 2023

Expertise prediction supplies missing expert predictions from limited labeled examples. Limited human labels are established research; correction: Lukas Thede, not Lars. Access: metadata/abstract; Official AAAI authors/abstract; real and synthetic expert evaluations reported.

### JIT23: Jitkrittum et al., 2023

Characterizes when confidence-only cascade deferral fails, including specialist downstream models and shift. A scalar AI-confidence threshold need not be sufficient. Access: metadata/abstract; Official NeurIPS abstract; experiments reported by authors, not rerun.

### GHO24: Ghoummaid & Shalit, 2024

Policy learning with deferral accounts for hidden confounding. Observed outcomes do not identify missing human/AI counterfactuals without assumptions. Access: metadata/abstract; Official NeurIPS abstract; no causal estimator is implemented here.

### ANG24: Angelopoulos et al., 2024

Conformal risk control bounds expected monotone losses under its calibration assumptions. The implemented guard is a union bound, not conformal risk control or distribution-free certification. Access: metadata/abstract; Official ICLR abstract; no conformal implementation or guarantee claimed.

### YAO25: Yao et al., 2025

Tool-agent-user benchmark evaluates interactions in operational domains. Real agent interaction is broader than the toy simulator; no benchmark result is reproduced. Access: metadata/abstract; Official ICLR abstract and metadata.

## LIT-03. Explicit mapping, not title matching

Let an intervention environment have observable resources, a hidden task mode, action-dependent outcome probabilities and terminal losses. Encode continue and retry as nonterminal actions, human assistance as either a transition or a terminal rescue action, and stop as an absorbing abandonment outcome. The standard belief-state control formulation then contains the decision problem. A finite latent parameter index extends the hidden state to represent uncertainty in both AI and human effectiveness. History-dependent transition ambiguity yields a robust control formulation if its consistency and rectangularity assumptions are made explicit. None of these encodings requires access to neural weights.

This representational argument is not evidence that estimation is solved. One must still define what a successful step means, measure its conditional probability after relevant histories, estimate human outcomes, price delays and consequences, and validate the model. It is also not an efficient algorithm for every POMDP. The exact solver in this package exploits a short horizon and stationary conditional likelihoods.

A one-step learning-to-defer loss is recovered by letting each action terminate. A conventional stopping problem is recovered by retaining only continue and terminal handoff/stop. The four-action model can therefore contain those decision structures without creating a new universal theory. The fixed-parameter and rectangular models are different uncertainty semantics, not interchangeable implementations of the same minimax objective.

## LIT-04. What is solved, partially solved, and not established

**Established formulation:** cost-sensitive deferral; belief-state sequential optimization; joint Bayesian state/model uncertainty; robust control under appropriate ambiguity assumptions; effects of fallible experts; finite-budget assistance. These claims concern available mathematical tools, not validated success of every deployment.

**Partially addressed in existing and present work:** estimating usable conditional probabilities, learning from limited human labels, operating under shift, choosing informative help requests, and comparing policy families fairly. HandoffX does not supersede the cited specialist solutions.

**Not established by this study:** a universal intervention threshold; uniformly superior joint Bayesian or robust intervention; real human benefits; reliable performance transfer between named LLMs; safety under arbitrary misspecification; novelty of every benchmark feature conjunction; production readiness. The reviewed material did not establish an identical matched implementation with this exact finite simulator, but absence from this targeted search is not proof of originality.

## LIT-05. Contribution retained after experiments

The resulting artifact exposes the difference between parameter uncertainty and persistent task difficulty, retains negative policy comparisons, checks exact expectations against simulation, and reports an oracle without future-outcome leakage. These are useful engineering and experimental choices. The new empirical observations are conditional on the explicitly artificial environments. They are neither a new decision-theoretic foundation nor a demonstration that HandoffX outperforms established published learning systems.
