# Source verification, search execution log and screening register

**Execution date:** 2026-10-28 (Europe/Berlin). **Search interface actually used:** live web search (fast and slow discovery), followed by original publisher/proceedings/arXiv HTML inspection. **Database scopes not comprehensively queried:** full Google Scholar, IEEE Xplore, ACM DL subscriptions, Web of Science/Scopus, citation-graph APIs and all publisher full-text libraries. **No claimed PRISMA flow.** No count of search result totals, deduplicated all-world records, or total eligible papers is inferred from limited returned search rankings.

## 1. Executed query log (representative exact strings; discovery queries run on this date)

The following are **searches actually issued** during this audit, not just proposed templates. The tool returned ranked results and not comprehensive database hit counts; therefore any PRISMA screening tally would be misleading.

| Batch | Search | Purpose / discovery |
|---|---|---|
| F01 | `learning to defer to an expert Mozannar Sontag 2020 PMLR equations human error cost` | Mozannar & Sontag |
| F01 | `learning to defer under uncertainty expert competence sequential decisions human AI 2023 2024 2025` | Hemmer; recent benchmarks |
| F01 | `robust POMDP human robot intervention delegation recovery retry uncertainty` | uPOMDP |
| F01 | `learning to defer multiple experts cost-sensitive Madras Pitassi Zemel 2018` | Madras |
| F01 | `optimal stopping sequential human AI delegation intervention LLM agents 2024 2025 2026` | stopping-family scan |
| F01 | `Suilen robust finite state controllers uncertain POMDP 2020 arxiv` | Cubuktepe/Suilen |
| F02 | `Madras Pitassi Zemel predicting with an expert learning to defer NeurIPS 2018` | NeurIPS original |
| F02 | `Raghu Blumer Corrado Kleinberg Obermeyer Mullainathan algorithmic automation human AI complementarity 2019` | Raghu preprint |
| F02 | `Charusaie Mozannar Sontag Samadi sample efficient learning to defer multiple experts NeurIPS 2022` | Charusaie PMLR |
| F02 | `Verma Barrejón Nalisnick learning to defer distribution shift human expert uncertainty` | Verma PMLR |
| F02 | `dynamic learning to defer sequential decisions human experts 2024 2025` | dynamic literature |
| F02 | `Kamar Horvitz collaborative planning human machine crowdsourcing POMDP decision handoff mixed initiative` | mixed-initiative scan |
| F02 | `Iyengar robust dynamic programming 2005 Nilim El Ghaoui robust control Markov decision processes` | foundational |
| F03 | `site:proceedings.mlr.press "learning to defer" "sequential" expert` | sequential PMLR |
| F03 | `site:proceedings.mlr.press "learning to defer" "uncertainty" experts costs` | calibration |
| F03 | `site:papers.neurips.cc "human" "sequential" "defer" decision` | original NeurIPS |
| F03 | `human in loop reinforcement learning ask for help POMDP uncertain human assistance policy` | Singi / robots |
| F03 | `LLM agent when to ask human help retry stop escalation policy benchmark` | agent studies |
| F03 | `retries dependent failure correlated reliability optimal retry strategy Markov model` | failure model scan |
| F03 | `off policy evaluation human ai deferral selective labels missing counterfactuals learning to defer` | confounding |
| F03 | `2026 learning to defer autonomous agents human intervention agentic workflows` | recent search |
| F04 | `site:proceedings.mlr.press "learning to defer" "uncertainty" experts costs` | repeats from targeted scan (not independent evidence) |
| F04 | `human in loop reinforcement learning ask for help POMDP uncertain human assistance policy` | help seeking |
| F04 | `LLM agent when to ask human help retry stop escalation policy benchmark` | Shaikh; HiL |
| F05 | `"Learning to Switch Between Machines and Humans" NeurIPS 2020` | two-layer MDP lineage |
| F05 | `"When Does Confidence-Based Cascade Deferral Suffice" 2023 PMLR` | cascade prior art |
| F05 | `"Modeling Distinct Human Interaction in Web Agents" 2026 paper` | ACL final record |
| F05 | `"Learning to Defer" "distribution shift" robustness` | shifting policies |
| F05 | `"Conformal Risk Control" Bates Angelopoulos 2024` | risk calibration |
| F06 | `"Learning to Switch Among Agents in a Team via 2-Layer Markov Decision Processes" TMLR 2022` | TMLR confirmation |
| F06 | `"Reinforcement Learning Under Algorithmic Triage" paper proceedings` | related triage |
| F06 | `"Compensating for Sensing Failures via Delegation in Human–AI Hybrid Systems" authors 2023` | Fuchs full text |
| F06 | `"HiL-Bench" arxiv 2604.09408` | recent benchmark |
| F06 | `"Learning to Defer: A Survey" 2025 2026 arxiv` | 2025 survey warning |
| S01 | `"Learning to Switch Between Machines and Humans" Meresht De Singla Gomez Rodriguez` | original TMLR PDF |
| S02 | `site:proceedings.mlr.press "cost-sensitive" "deferral" "expert" workload 2024` | newer methods |
| S03 | `human AI delegation uncertainty both human machine competence Bayesian intervention 2025 2026` | joint uncertainty |

**Search result handling:** retained directly relevant primary sources and a single survey; removed duplicate records/preprint-versus-proceedings duplicates where a definitive publication exists. No paper was excluded for disagreeing with HandoffX. To finish a systematic search, preserve native-database syntax, exported result counts, complete title/abstract screens, full-text decisions, duplicate hashes, forward/backward citation chains and independent screening adjudications.

## 2. Scope and inclusion / exclusion rules applied

- **Included:** primary mathematical/empirical works with relevant actions or uncertainty, 2017–2026, plus foundational 2005/2011; official benchmark descriptions; one clearly labeled survey.
- **Retained older work:** Iyengar (2005), Nilim & El Ghaoui (2005), Rosenthal et al. (2011), because excluding them would falsely inflate novelty.
- **Deduplicated:** arXiv/prior versions of Mozannar 2020; Cubuktepe 2020/AAAI 2021; τ-bench 2024/ICLR 2025; Huq preprint/ACL 2026; Fuchs preprint/Sensors 2023. These are version matches, not counted as new studies.
- **Not advanced into authoritative evidence corpus:** general business blogs, vendor white papers or GitHub practices with no mathematical/experimental validation; user-facing explanation articles; scraped duplicates; unrelated media; preprint claims without a traceable source.
- **Unresolved and not silently excluded:** broad human-robot assistance-game literature, all historical retry/repair operations-research papers, dense multi-agent RL and nonrectangular robust POMDP literature; a future exhaustive search could reveal exact conjunctions.

## 3. Original access and verification levels

| Level | Meaning | Sources |
|---|---|---|
| L3 | Original full text (HTML or PDF) examined for method/critical results | Mozannar & Sontag 2020 (PDF with rendered equation page); Shaikh 2026 (full HTML); Alves et al. 2025 (full HTML); Fuchs et al. 2023 (full HTML); HiL-Bench 2026 (original arXiv HTML) |
| L2 | Official publisher abstract, bibliographic record and DOI/URL, sometimes introduction/PDF snippet | Most other primary records; details in matrix |
| L1 | Official metadata/abstract or preprint only, full text not comprehensively reviewed | Balazadeh Meresht 2022 (original PDF abstract; OpenReview challenge); τ²-bench 2026 (publisher indexed abstract, occasional fetch error); Strong et al. 2025 (Zenodo summary, 429 full-view access issue) |

**Critical interpretation:** "bibliographically verified" ≠ "all original equations, assumptions and proofs independently verified". Any paper-specific claim beyond inspected sections is explicitly attributed as the authors' report. `HANDOFFX_VERIFIED_REFERENCES.bib` contains only records supported by primary venue and/or original preprint metadata, with the below caveats.

## 4. Version and metadata caveats

1. **Huq et al. (2026):** the final ACL Anthology publication (`2026.findings-emnlp.2029`) differs numerically from arXiv (`2602.17588`) abstract snippets and the April blog. For publication cite **final ACL claims** (user-rated usefulness +36.8%); do not treat +26.5% preprint as same version. Final source: https://aclanthology.org/2026.findings-emnlp.2029/.
2. **HiL-Bench (2026):** arXiv HTML author spelling/order differs across discovery mirrors. The BibTeX follows the **original arXiv HTML retrieved for this audit**, not third-party scraped records. Re-verify immediately before formal release. https://arxiv.org/abs/2604.09408.
3. **Shaikh (2026):** arXiv contains a revised version 1.1 adding one model-cascade validation. It **does not** empirically test the full optimal-stopping DP. Treat its mathematical results as preprint claims, not independently certified.
4. **Balazadeh Meresht et al. (2022):** accepted PDF calls it a two-layer MDP; the accessible announcement abbreviates its title as *Learning to Switch Among Agents in a Team*. Final citation/title normalization against TMLR is a **bibliographic review item**; entry preserves PDF title. OpenReview HTML currently presents a verification challenge.
5. **Strong et al. (2025) survey:** Zenodo metadata can be found, but the page returned rate limit on a follow-up fetch. Survey is context only, not primary proof.
6. **BIB file structure:** author/title/year/venue/URL and verified DOIs where available; `howpublished` is deliberately conservative. A final publication bibliography should run DOI/venue cross-validation and convert entries to BibLaTeX-standard type-specific fields. Do not claim DOI validation for items with empty DOI.

## 5. Reproducibility and limitations

29 retained entries in the corpus; one is a secondary survey. Retention does *not* mean 29 full papers were reviewed. Online search was live on the audit date, but ranked search responses and partial publisher access prevent claiming database completeness or independent double review. No citation count, PRISMA flow, literature prevalence, total unique search hits or formal systematic-review completion can be asserted. No HandoffX numerical experiments or real human interventions were run.

**Independent source checking remaining before journal submission:** search ACM/IEEE/Scopus/Web of Science/Google Scholar as accessible, all current 2026 literature, formal forward/backward citation chaining, check all bibliographic fields and retractions, second-reviewer screening, then read closest 15–20 full papers and check every theorem's assumptions. These are *uncompleted quality gates*, not accomplishments.
