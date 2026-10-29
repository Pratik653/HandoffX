# 15. Cross-study synthesis

## 15.1. What the five studies establish together

**Table {T:synthesis}.** *Principal findings, by kind of evidence*

| Finding | Studies | Evidence |
|---|---|---|
| Exact planning on a correct model is optimal for its objective; Bayes, robust and gate statements hold only under their stated premises | P1–P9, A1–A4 | Theoretical (model-relative) |
| Modelling persistent failure modes is the most valuable single ingredient: removing it raised loss by about 5.8% in Study II and lost 15 of 38 comparisons in Study I | I, II | Exact calculation; held-out |
| Joint-Bayesian planning with a static prior is not uniformly better than nominal planning (6 better / 23 equal / 9 worse) | I | Exact calculation (designed scenarios) |
| Cross-episode calibration yields a small held-out average-loss improvement over nominal planning, with an interval that includes zero (−0.46% [−1.07, +0.09] gated; −0.63% [−1.28, −0.05] ungated) | II | Pre-registered, held-out |
| The conservative gate adds no measurable average benefit and can be confidently wrong under misspecification | II (CE9) | Held-out; counterexample |
| The nominal-to-oracle gap is small on these distributions (about 2–3.5%) | II, III | Exact calculation |
| The remaining headroom is limited by learning, not by model resolution: selective observation, a self-confirming escalation trap and nuisance misspecification | III | Diagnostics (development data) |
| No average-loss improvement over ungated recalibration replicated across independent samples | III | Screening with replication |
| Prevalence-flexible learning reduces severe-failure probability by 17.8% [12.0, 24.0] (about 3.2 per 1,000 episodes) under two independent shift families | IV | **Confirmatory** |
| Its loss non-inferiority within 0.5% is not demonstrated (+0.28%, upper bound +0.82%); it costs about 3.3 pp task completion and adds loss under human misestimation | IV | Pre-registered |
| The reduction arises mainly from more cautious decisions, not better prevalence estimation; simple catastrophe weighting reproduces comparable reductions along a risk–loss frontier | V | Exploratory |
| None of the above has been shown for real agents, real operators or real costs | All | Not established |

## 15.2. How interpretations developed

- **Study I to Study II.** The 6/23/9 result was first read as "joint uncertainty is not uniformly helpful". Study II preserved that reading and explained it: most losses were tiny and occurred where nominal planning was already optimal, and the root cause was within-episode non-identifiability.
- **Study II to Study III.** Study II proposed model sets that include prevalence, and posterior predictive checks, as remedies for CE9. Study III tested both ideas (candidates A and C). Neither produced a replicated average-loss gain.
- **Study III to Study IV.** Study III treated A's severe-failure reduction as a promising secondary signal. Study IV made it the primary endpoint and confirmed it.
- **Study IV to Study V.** The working hypothesis "A helps by learning failure prevalence" was **not supported**. The refined interpretation is "A helps by evidence-triggered caution". The study-level feasibility decision called this a CONDITIONAL GO for a risk-sensitive controller. Study V adds that explicit, tunable risk weighting may deliver the same benefit more transparently, but this has not been tested prospectively.

No earlier numerical result has been changed. Statements that were later refined are identified above and in Section 11.6.

## 15.3. Answers to the research questions

<<v01|# 13. Answers to the research questions|# 14. Conclusions and future research>>

The answers to RQ1–RQ8 above are the original Study I answers. Later studies add the following:
- **RQ3** is refined by Study II. The direction of estimate bias matters most; over-estimated human effectiveness benefited most from calibration (−2.25%).
- **RQ9.** Cross-episode calibration gives a small held-out improvement over nominal planning that is not statistically clear in relative terms. The conservative gate is not shown to help.
- **RQ10.** Learning, not model resolution, limits further improvement: selective observation, the escalation trap and nuisance misspecification. Three targeted remedies did not produce replicated average-loss gains.
- **RQ11.** Yes for severe failures in the tested model families: a confirmed 17.8% relative reduction. The loss constraint is unresolved, and the cost is fewer completed tasks. The mechanism is caution rather than better estimation.

# 16. Practical implications

The following implications are conditional on the modelled assumptions. They are not deployment guidance validated on real systems.

1. **Model persistence before sophistication.** Distinguishing transient from persistent failures had the largest and most consistent effect. Retry logic that assumes independent attempts is systematically optimistic (P4, CE3).
2. **Prefer exact nominal planning when estimates are believed calibrated.** Every adaptive or uncertainty-aware method lost a little in calibrated environments.
3. **Learn from logs, but escalate enough to learn.** Cross-episode calibration is valid under adaptive logging (A1). Human effectiveness is learned only from actual escalations (A2); a system that stops escalating can lock in a wrong belief.
4. **Choose the risk posture explicitly.** Reducing severe failures was possible, but it cost task completion and, in some conditions, average loss. The evidence favours making that trade-off an explicit, documented setting rather than a side effect of a learning method. Examples are a catastrophe weight or a severe-risk budget; the library already provides a per-action severe-risk guard (P7).
5. **Do not treat posterior confidence as safety.** Under misspecification the posterior and the gate became confidently wrong (CE9).

<<v01|## 11.1. Enterprise data and SQL workflows|# 12. Discussion and threats to validity|0|keepstart|sec=11:16>>

# 17. Threats to validity

<<v01|## 12.1. Internal validity|# 13. Answers to the research questions|0|keepstart|sec=12:17>>

## 17.6. Threats specific to Studies II–V

- **Synthetic generators designed by the same researcher.** Study IV used two independently specified shift families and a third hazard family, but all were built within one simulator. Robustness "within the tested model families" is not robustness to real conditions.
- **Equal weighting of kinds.** Pooled results weight environment kinds equally, which has no real-world prevalence interpretation. Separate kind-level results are always reported.
- **Multiplicity.** Study III examined many contrasts. Only effects that replicated across independent samples, and the single pre-registered primary endpoint of Study IV, are treated as findings.
- **Secondary-to-primary promotion.** The severe-failure endpoint was chosen for Study IV *because* it looked promising in Study III. The fresh seeds, the new shift families and the frozen protocol address this, but the hypothesis was not chosen blind.
- **Post hoc mechanism analysis.** Study V is exploratory. Its catastrophe weights were not tuned, and its matched-risk comparison is approximate and unreplicated.
- **Exact versus realized severe failures.** The primary endpoint uses exact probabilities under the simulator's truth. Realized event counts (790 versus 973) agree in direction but are not independent evidence.

# 18. Limitations and future research

**Limitations.**
- All evidence is synthetic: there were no real agents, operators, costs or deployments.
- The model class has:
  - fixed latent modes within an episode;
  - terminal human rescue;
  - known availability;
  - small horizons;
  - stationary kernels.
- Human effectiveness is identifiable only from escalations, and is confounded with failure prevalence when human success varies by mode.
- Severe-failure reductions came with fewer completed tasks.
- Loss non-inferiority of the risk-reducing candidate was not established.
- The conservative gate showed no average benefit.
- The literature review is targeted rather than systematic.
- No result has been peer reviewed or independently replicated.

**Future research, in order of justification.**
1. **Pre-registered matched-risk comparison (proposed, not performed).** Compare candidate A against bayes_recal with a fixed catastrophe weight chosen on separate data, at matched severe-failure risk, with loss as the primary endpoint. Include a variant of A whose prevalence prior has the supplied mean, to remove the prior asymmetry, and report the human-effectiveness family separately. This would decide whether evidence-triggered caution adds anything beyond an explicit risk weight.
2. **Explicit risk control in the library.** If (1) is negative or inconclusive, risk sensitivity is better offered as an explicit setting than as an implicit learning effect, for example a catastrophe weight or a severe-risk budget.
3. **Real logs and real operators.** Collect agent execution logs with escalation outcomes, with consent and adequate overlap, to estimate the conditional probabilities the controller needs (CE6, A2).
4. **Exploration under selective observation.** Costed probe or diagnostic actions, and value-of-information methods, aimed at the escalation trap.
5. **Richer models.** Nonterminal assistance, changing failure modes, queues and multi-task human capacity, each requiring new state models and renewed validation.

# 19. Conclusion

HandoffX makes intervention decisions for autonomous agents explicit, computable and auditable within a bounded model. Across five studies, the evidence supports a modest and specific set of conclusions:
- Exact planning that models persistent failures captures most of the value available in this decision structure.
- Joint uncertainty and cross-episode learning help when supplied estimates are biased in a way the logs can reveal, and cost a little when estimates are right.
- A conservative gate added no measurable benefit.
- Average-loss improvements beyond ungated recalibration did not replicate.
- A prevalence-flexible learner reliably reduced severe failures, by 17.8% in a pre-registered confirmation. It did so by being more cautious, at a cost in completed tasks, and without demonstrated loss non-inferiority.

HandoffX does not show universal superiority, real-world safety or a better estimate of hidden failure prevalence. It offers a reproducible framework, a reference implementation and an honest map of where adaptive and risk-sensitive intervention helps, where it does not, and why. The natural next steps are explicit risk control and evaluation on real agent logs.

# Declarations

**Authorship.** Prepared by the repository owner, Pratik653. The author's full name, affiliation and ORCID will be added before formal submission.

**Use of AI tools.** AI-based writing and coding assistance was used in preparing software, analyses and text. The author reviewed the material and is responsible for its content. Disclosure requirements of the target venue should be checked before submission.

**Data and code availability.** All code, configurations, results and figures are in the public repository https://github.com/Pratik653/HandoffX. Raw episode arrays are reproducible from the stored configurations and seeds.

**Licences.** Software: MIT. Text, figures and data: CC BY 4.0.

**Funding and competing interests.** To be completed by the author.

**Peer review.** This paper has not been peer reviewed. A repository DOI, if assigned, identifies a deposited version and does not imply peer review.
