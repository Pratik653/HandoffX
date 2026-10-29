# Source verification and search continuation

Date: 2026-10-28. **22 active primary-source metadata records** are included in the manuscript bibliography; **six** had selected original full-text methods inspected in this continuation. The remaining 16 support only the appropriately bounded claims recorded below. A full-text access label does not mean every theorem or experiment was independently verified. The original 29-record audit remains separately archived, with its own historical search log and uncorrected metadata visible for provenance.

## Executed continuation queries

The exact discovery expressions below were issued through live web search. Direct URL opens and citation chaining to official pages supplemented them. They are not database-wide export queries, and no total hit count or PRISMA flow is asserted.

| Search interface | Exact expression |
|---|---|
| system1 | `"Learning to Defer to an Expert" "Mozannar"` |
| system1 | `"robust" "POMDP" "Cubuktepe" 2021` |
| system1 | `"Shaikh" "Bayesian" "escalation" 2026` |
| system1 | `"Learning to Switch Among Agents" "Team"` |
| system2 | `Kaelbling Littman Cassandra 1998 Planning and acting in partially observable stochastic domains` |
| system2 | `A benchmarking framework and dataset learning defer human AI decision making Alves 2025 PMC` |
| system2 | `When to act and when to ask policy learning deferral hidden confounding 2024 Ghoummaid Shalit` |
| system2 | `Bayes adaptive POMDPs Ross Pineau Chaib draa 2008 UAI` |
| system2 | `Knowing when to ask for help Bayesian self-escalation hierarchical LLM agents 2026 Shaikh` |

## Inclusion, exclusion and version decisions

Included active records directly support the model equivalence, calibration, human uncertainty, sequential assistance, robust-control or benchmark interpretation used in the manuscript. Official publisher/proceedings/arXiv records were preferred. Secondary indexed duplicates were used only for discovery, not authoritative claims. The Ross (2011) journal formulation was retained instead of separately counting the 2007 conference and 2008 related presentations. The Balazadeh arXiv v3 record replaces, rather than duplicates, the blocked final-publication record. Other original-audit records remain as provenance but were not silently promoted to verified active references.

No native Scholar, Scopus, Web of Science, IEEE Xplore or ACM subscription search/export was executed. No independent second screener, exhaustive citation-graph expansion, or complete equivalent-formulation search was completed. No papers were excluded because their results contradicted HandoffX. The latest verifiable studies encountered are retained with their preprint status; discovery is not a claim that these are every latest study.

## Corrections to the supplied audit

1. **HEM23:** official AAAI author list identifies **Lukas Thede**, not Lars Thede. Preserve the original file and use the corrected active record.
2. **HIL26:** use arXiv version 4 (May 4, 2026), with Trinh first, then Elfeki, Luo and Luu; correct Hernandez, Carabedo and Castillo spellings and Yannis Yiming He. The current author list differs materially from the supplied record.
3. **SHA26:** the accessible arXiv record is version 1, while the manuscript labels itself Version 1.1. The attempted arXiv v2 HTML returned 404. These version systems must not be conflated.
4. **BAL23:** the accessible record is arXiv version 3, revised June 30, 2023, original submission 2020. The OpenReview final-publication page returned a browser challenge and its API attempt failed. Do not silently mix the preprint title/year with a claimed independently inspected TMLR edition.
5. **Additional missed foundation:** Ross et al. (2011) explicitly covers joint model uncertainty and hidden-state beliefs. Its inclusion further limits theoretical novelty.

## Failed or restricted access

The Cubuktepe CDN PDF timed out; the AAAI official abstract/metadata remained accessible. The Kaelbling author-hosted PDF timed out; publisher metadata remained available. The Nature landing page for Alves failed via redirect, while the primary full text in PMC was accessible. MDPI returned HTTP 429 for the Fuchs paper in this continuation; that source was not added to the active bibliography. An attempted AAAI URL ending 25736 returned an unrelated concept-bottleneck paper; it was excluded and the correct Hemmer URL ending 25742 was then inspected. One JMLR page-3 screenshot failed with cache miss; page 7 rendered successfully. These are access limits, not evidence against the underlying studies.

## Active verification register

### ALV25: Alves et al., 2025

- Primary record: https://pmc.ncbi.nlm.nih.gov/articles/PMC12019285/
- Access: selected original full text. PMC full text methods/limitations; synthetic experts are not real participants.
- Permitted claim: Learning-to-defer benchmark includes synthetic expert behavior and capacity constraints.
- Interpretation boundary: Benchmarking fallible humans is established; its tabular allocation task differs from repeated recoveries.

### ANG24: Angelopoulos et al., 2024

- Primary record: https://proceedings.iclr.cc/paper_files/paper/2024/hash/f3549ef9b5ff520a7e41ff3cc306ab2b-Abstract-Conference.html
- Access: metadata/abstract. Official ICLR abstract; no conformal implementation or guarantee claimed.
- Permitted claim: Conformal risk control bounds expected monotone losses under its calibration assumptions.
- Interpretation boundary: The implemented guard is a union bound, not conformal risk control or distribution-free certification.

### BAL23: Balazadeh et al., 2023

- Primary record: https://arxiv.org/abs/2002.04258v3
- Access: metadata/abstract. arXiv v3 record; final TMLR record blocked, so cite this version.
- Permitted claim: Two-layer MDP switches control among agents, with confidence bounds and reported sublinear regret.
- Interpretation boundary: Switching and shared environment information are prior art; no new online-regret claim is made.

### CHA22: Charusaie et al., 2022

- Primary record: https://proceedings.mlr.press/v162/charusaie22a.html
- Access: metadata/abstract. Official PMLR abstract and metadata.
- Permitted claim: Sample-efficient learning of predictors that complement human decisions.
- Interpretation boundary: Human complementarity and data acquisition require their own learning evaluation.

### CUB21: Cubuktepe et al., 2021

- Primary record: https://ojs.aaai.org/index.php/AAAI/article/view/17401
- Access: metadata/abstract. Official AAAI metadata/abstract; CDN PDF access failed.
- Permitted claim: Robust finite-state controllers for uncertain POMDPs and specified objectives.
- Interpretation boundary: HandoffX does not reproduce this controller-synthesis algorithm or inherit all guarantees.

### GHO24: Ghoummaid & Shalit, 2024

- Primary record: https://papers.nips.cc/paper_files/paper/2024/hash/660cf2a1eabe448920a3ab6754555adb-Abstract-Conference.html
- Access: metadata/abstract. Official NeurIPS abstract; no causal estimator is implemented here.
- Permitted claim: Policy learning with deferral accounts for hidden confounding.
- Interpretation boundary: Observed outcomes do not identify missing human/AI counterfactuals without assumptions.

### HEM23: Hemmer et al., 2023

- Primary record: https://ojs.aaai.org/index.php/AAAI/article/view/25742
- Access: metadata/abstract. Official AAAI authors/abstract; real and synthetic expert evaluations reported.
- Permitted claim: Expertise prediction supplies missing expert predictions from limited labeled examples.
- Interpretation boundary: Limited human labels are established research; correction: Lukas Thede, not Lars.

### HIL26: Trinh et al., 2026

- Primary record: https://arxiv.org/abs/2604.09408v4
- Access: selected original full text. Version 4 HTML design/limitations; corrected author list and order.
- Permitted claim: Progressive blockers and asking behavior in coding/SQL, evaluated with Ask-F1 and task outcomes.
- Interpretation boundary: Sequential help-seeking benchmarks already exist; HandoffX instead isolates a costed synthetic decision model.

### IYE05: Iyengar, 2005

- Primary record: https://pubsonline.informs.org/doi/10.1287/moor.1040.0129
- Access: metadata/abstract. Publisher record/abstract; full original proof not independently rechecked.
- Permitted claim: Robust dynamic programming uses structured uncertainty sets to support dynamic recursion.
- Interpretation boundary: Rectangularity is consequential; HandoffX claims an envelope, not fixed-parameter minimax equivalence.

### JIT23: Jitkrittum et al., 2023

- Primary record: https://papers.neurips.cc/paper_files/paper/2023/hash/1f09e1ee5035a4c3fe38a5681cae5815-Abstract-Conference.html
- Access: metadata/abstract. Official NeurIPS abstract; experiments reported by authors, not rerun.
- Permitted claim: Characterizes when confidence-only cascade deferral fails, including specialist downstream models and shift.
- Interpretation boundary: A scalar AI-confidence threshold need not be sufficient.

### KAE98: Kaelbling et al., 1998

- Primary record: https://www.sciencedirect.com/science/article/pii/S000437029800023X
- Access: metadata/abstract. Publisher metadata verified; author-hosted PDF timed out.
- Permitted claim: Belief-state control in partially observable stochastic environments.
- Interpretation boundary: The finite count-state solver is a restricted POMDP specialization.

### MAD18: Madras et al., 2018

- Primary record: https://papers.neurips.cc/paper_files/paper/2018/hash/09d37c08f7b129e96277388757530c72-Abstract.html
- Access: metadata/abstract. Instance features; prediction or deferral; reported classification evaluation.
- Permitted claim: Predict/defer learning with a fallible downstream decision maker and fairness-sensitive loss.
- Interpretation boundary: Human-versus-AI expected loss is prior art; no retry benchmark is replicated here.

### MOZ20: Mozannar & Sontag, 2020

- Primary record: https://proceedings.mlr.press/v119/mozannar20b.html
- Access: selected original full text. Original PDF pp. 2-4, displayed Bayes rules and loss; equation pages visually inspected.
- Permitted claim: Cost-sensitive reduction and consistent surrogate learning; Bayes decisions compare machine and expert conditional correctness.
- Interpretation boundary: HandoffX reuses the decision principle, not the trained surrogate or its sample guarantees.

### NIL05: Nilim & El Ghaoui, 2005

- Primary record: https://pubsonline.informs.org/doi/abs/10.1287/opre.1050.0216
- Access: metadata/abstract. Publisher record/abstract; exact assumptions not re-proved from original paper.
- Permitted claim: Robust MDP control handles uncertain transition matrices.
- Interpretation boundary: Uncertain action transitions and worst-case cost optimization are established.

### ROS11: Rosenthal et al., 2011

- Primary record: https://ojs.aaai.org/index.php/AAAI/article/view/7980
- Access: metadata/abstract. Official AAAI abstract and metadata.
- Permitted claim: Robot assistance decisions model human accuracy and availability.
- Interpretation boundary: Imperfect or unavailable people are established, not a new HandoffX concept.

### ROSS11: Ross et al., 2011

- Primary record: https://www.jmlr.org/papers/v12/ross11a.html
- Access: selected original full text. JMLR PDF sections 2-3; selected equations inspected; p. 1736 screenshot inspected.
- Permitted claim: Bayes-adaptive POMDPs jointly track state and uncertain model parameters.
- Interpretation boundary: Joint hidden-state/parameter beliefs and information-sensitive planning are established.

### SHA26: Shaikh, 2026

- Primary record: https://arxiv.org/abs/2608.24087v1
- Access: selected original full text. arXiv v1 HTML sections 3-5, 8, 10; internal Version 1.1 is not arXiv v2.
- Permitted claim: Bayesian intra-generation stopping, learned competence posterior and stronger-model escalation.
- Interpretation boundary: Timing/calibration are prior art; reported real-model validation does not execute the optimal stopping DP.

### SIN23: Singi et al., 2023

- Primary record: https://arxiv.org/abs/2303.06710v2
- Access: selected original full text. HTML section III and evaluation overview; robotic expert returns an action, not terminal rescue.
- Permitted claim: HULA queries an expert using estimated return variance with a limited call budget.
- Interpretation boundary: Original method assumes consistently high-quality advice; this prototype permits weak helpers.

### SUI20: Suilen et al., 2020

- Primary record: https://www.ijcai.org/proceedings/2020/569
- Access: metadata/abstract. Official IJCAI abstract/metadata; not an implemented algorithm comparison.
- Permitted claim: Uncertain-POMDP policy synthesis via convex optimization.
- Interpretation boundary: Partial observation plus transition uncertainty is prior art.

### VER22: Verma & Nalisnick, 2022

- Primary record: https://proceedings.mlr.press/v162/verma22c.html
- Access: metadata/abstract. Official PMLR abstract and complete metadata.
- Permitted claim: One-vs-all construction addresses calibration of expert correctness in learning to defer.
- Interpretation boundary: Numerically valid probabilities are not automatically calibrated; HandoffX does not fit an estimator.

### VER23: Verma et al., 2023

- Primary record: https://proceedings.mlr.press/v206/verma23a.html
- Access: metadata/abstract. Official PMLR abstract; no independent proof replication.
- Permitted claim: Multiple-expert deferral, calibrated surrogate scores and conformal expert ensembles.
- Interpretation boundary: Multiple candidate helpers or expert uncertainty are not inherently new.

### YAO25: Yao et al., 2025

- Primary record: https://proceedings.iclr.cc/paper_files/paper/2025/hash/1b126cc38b8638e07bef37e7b2bb72bf-Abstract-Conference.html
- Access: metadata/abstract. Official ICLR abstract and metadata.
- Permitted claim: Tool-agent-user benchmark evaluates interactions in operational domains.
- Interpretation boundary: Real agent interaction is broader than the toy simulator; no benchmark result is reproduced.

## Traceability and integrity

`ACTIVE_REFERENCE_RECORDS.json` links each stable key to metadata, APA entry, access level and source locator. `PRIOR_ART_MATRIX.csv` records explicit comparison boundaries; an unexamined feature is not encoded as proved absent. Manuscript author-date citations resolve to the active bibliography. The original supplied archive is not an independent scholarly source. External paper PDFs, copyrighted full texts and font files are not redistributed.
