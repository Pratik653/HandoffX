---
title: "HandoffX"
subtitle: "A reproducible decision-theoretic framework for continue, retry, human-assistance and stop decisions under uncertainty: five studies of planning, adaptive calibration and risk reduction"
author: "Pratik653"
date: "October 29, 2026"
version: "Final consolidated paper, version 1.0 (reference software HandoffX 0.2.1)"
lang: en-US
---

# Abstract

Autonomous agents repeatedly decide whether to continue, retry a failed step, request human assistance or stop. HandoffX formulates this choice as a finite-horizon, partially observed decision problem with:
- latent persistent failure modes;
- uncertain AI and human effectiveness;
- fallible terminal human rescue;
- costs, deadlines, resources and external action restrictions.

It provides exact nominal, Bayesian and history-rectangular robust planners in a small open-source Python library. This paper consolidates five studies conducted with that framework.

- **Study I** compared 11 policies in 38 designed scenarios using exact expectations and 5,016,000 paired simulated executions. Joint-Bayesian planning had lower exact loss than nominal planning in 6 scenarios, equal loss in 23 and higher loss in 9. Removing failure persistence was costly, and a robust bound failed outside its uncertainty set.
- **Study II** diagnosed that result as within-episode non-identifiability and added cross-episode Bayesian calibration with a conservative switching gate. On 200 pre-registered held-out environments, the gated controller changed mean exact loss relative to nominal planning by −0.46% (95% bootstrap interval −1.07% to +0.09%). Ungated posterior recalibration did at least as well (−0.63%), so the gate was not shown to add value. Under misspecification, the posterior concentrated on a wrong model.
- **Study III** screened three extensions against ungated recalibration in three independent rounds. No candidate's average-loss improvement replicated. One candidate, which adds uncertainty about the prevalence of persistent failures, consistently reduced severe failures.
- **Study IV**, a pre-registered confirmation on 500 fresh environments, confirmed that reduction. Severe-failure probability fell by 17.8% in relative terms (95% CI 12.0% to 24.0%), an absolute reduction of 3.2 per 1,000 episodes, in both prespecified shift families. Average-loss non-inferiority within a 0.5% margin was not demonstrated: +0.28%, with an upper bound of +0.82%. The candidate completed 3.3 percentage points fewer tasks and stopped more often.
- **Study V**, exploratory, attributes the reduction mainly to more cautious decisions rather than more accurate estimation of failure prevalence. Simpler catastrophe-weighted planning reaches comparable or larger reductions along a risk–loss trade-off.

Overall:
- HandoffX does not demonstrate universal superiority over nominal planning.
- Its supported contributions are a unified, reproducible framework and benchmark, and a precise account of when adaptation helps or fails.
- The work also identifies learning failures caused by selective observation and misspecification, and characterizes the trade-off between severe-failure reduction, expected loss and task completion.

All evidence is synthetic.

**Keywords:** human–AI collaboration; learning to defer; Bayesian sequential decision-making; partially observable Markov decision processes; robust control; model misspecification; risk-sensitive decision-making; reproducible research.

**Research status.** This paper reports theory, exact finite-model calculations and synthetic simulations. It reports no real agents, real operators or deployments, and it has not been peer reviewed. The reference software is MIT-licensed; the text is CC BY 4.0.

# How to read this paper

The five studies were carried out in sequence, and each was designed in response to the previous one.

**Table {T:overview}.** *Overview of the five studies*

| Study | Question | Design | Evidence status |
|---|---|---|---|
| I. Original framework (v0.1) | How do nominal, Bayesian and robust planning compare on a fixed design? | 38 designed scenarios, 11 policies, exact expectations plus simulation | Locally recorded protocol; descriptive comparisons |
| II. Adaptive learning (v0.2) | Can cross-episode calibration beat nominal planning, and is a conservative gate useful? | Pre-registered development, validation, held-out test and shift splits | Pre-registered; held-out |
| III. Feasibility screening (v0.3) | Can any of three extensions improve average loss over the best v0.2 learner? | Pilot, confirmation and replication rounds | Frozen protocol per round; screening |
| IV. Risk-reduction confirmation | Does prevalence uncertainty reduce severe failures without unacceptable loss? | Pre-registered, 500 fresh environments | **Confirmatory** for the primary endpoint |
| V. Mechanism analysis | Why does the reduction occur; can explicit risk aversion reproduce it? | Post hoc ablations on separate fresh seeds | **Exploratory** |

Results from earlier studies are reported unchanged. Where a later study refines an earlier interpretation, the text says so explicitly; Section 15 summarizes these developments. The labels P1–P9, A1–A4 and CE1–CE9 identify propositions and counterexamples throughout. Equations are numbered consecutively, and tables and figures are numbered in order of appearance.

# 1. Introduction

An agent can fail for several reasons:
- its next step is difficult;
- a retry repeats the same underlying failure;
- a tool is unavailable;
- its belief about a person's ability to rescue the task is wrong.

These situations do not share a universal response. Repeating a low-cost recoverable step can be useful, while repeating a persistent failure can consume the entire budget. A skilled person may resolve the task, but an unavailable, costly or equally uninformed person may not improve the outcome. Stopping can be optimal when the remaining expected benefit is smaller than the operational and failure costs.

The decision problem must therefore separate an action's immediate cost from its effect on later options. It must also separate uncertainty in the true task state from uncertainty in the probabilities used to predict the future. Established belief-state and Bayes-adaptive formulations already supply the relevant mathematical language (Kaelbling et al., 1998; Ross et al., 2011), and HandoffX does not claim to invent it. Its purpose is to make a bounded version operationally explicit, and to test reproducibly what happens when nominal, Bayesian, adaptive, robust and risk-averse interpretations are applied to the same synthetic decision problem.

The central practical question is not whether a Bellman equation can contain an action called human assistance; it can. The questions are:
1. Can the required inputs be defined and supplied consistently?
2. Do the implemented decision rules respect the intended uncertainty semantics?
3. Does additional mathematical or statistical machinery produce a measurable advantage over simpler or established alternatives?
4. When an advantage appears, what does it actually consist of?

This paper answers these questions for a specified model class and a sequence of synthetic benchmarks. It does not claim to solve estimation from real execution logs.

## 1.1. Scope of model agnosticism

The controller does not inspect a neural network's weights, hidden activations, architecture or brand. It receives categorical outcome probabilities, observations, costs and restrictions. This is architectural independence within a specified decision-process class, and it implies none of the following:
- that one model's probabilities transfer to another model;
- that the same milestones have equivalent meanings across tasks;
- that performance transfers between organizations.

A model-independent equation can still be wrong for a particular workflow.

## 1.2. The research sequence in brief

- **Study I** found no uniform advantage for joint-Bayesian planning over nominal planning: 6 improvements, 23 ties and 9 degradations across 38 scenarios. Persistent-failure modelling was, however, consistently valuable.
- **Study II** showed why: within one episode, a prior centred on a biased estimate cannot be corrected, because human effectiveness is observed only after a terminal handoff. Pooling evidence across episodes produced a small held-out improvement whose interval included zero, and the conservative gate added nothing measurable.
- **Study III** asked whether the remaining headroom could be recovered:
  - the model grid was not the bottleneck;
  - learning stalled, partly through a self-confirming escalation trap and partly through misspecified failure prevalence;
  - none of the three tested remedies produced a replicated average-loss gain;
  - one of them repeatedly reduced severe failures.
- **Study IV** tested that reduction prospectively, and **Study V** examined its mechanism.

The resulting picture is consistent and modest. Exact planning with persistent-failure modelling captures most of the value available in this decision structure. The remaining choices are mainly about how much expected loss and task completion to trade for fewer severe failures.
