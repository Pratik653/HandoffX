# Publication-readiness assessment

**Status: reproducible research-stage technical report and working reference prototype; not a completed production validation, externally peer-reviewed publication, or finalized public release.**

| Requested phase | Completed evidence | Remaining boundary |
|---|---|---|
| 2A: mathematical specification | States, costs, outcomes, observations, budget, uncertainty semantics and terminal rules implemented | Bounded persistent-mode subclass, not all autonomous agents |
| 2B: mathematical validation | Nine conditional propositions, eight counterexamples, executable checks | No external proof review or theoretical novelty priority |
| 3: simulator and baselines | Typed library, 11 policies, deterministic tests, examples and wheel | Learned probability estimators and live adapters absent |
| 4: experiments | 38 scenarios, 418 exact cells, 5,016,000 stored executions, paired intervals, raw data and rerun | Synthetic evidence only; no prospective human or LLM study |
| 5: library prototype | Documented static, Bayesian and rectangular-robust APIs, guards, simulation and export | Not production-hardened; Windows execution unverified |
| 6: academic publication artifacts | 58-page DOCX/PDF/Markdown, two-page summary, full AI knowledge file, verified source register | Not 120-150 pages; author, licensing and external review pending |

## Integrity gates met within the stated scope

The novelty statement is bounded to empirical/software work. The decisive foundational equivalences are acknowledged. No conjecture is used as a guarantee. Numerical claims correspond to executable records. Complete rerun equality, separate scalar simulation and objective-aligned robust checks are preserved. Negative results and the out-of-set robustness failure are explicit. Rendering and navigation were inspected. The release manifest and checksums are independently testable using standard tools.

## Unfinished requirements and nonclaims

No exhaustive systematic literature review, real-agent trace evaluation, human-participant experiment, learned calibration subsystem, realistic queue or variable-delay model, external integration, Intel/Windows run, external replication or peer review was completed. Source-code ownership, author identity, funding/conflict statements and licenses require owner review. No DOI was reserved; nothing was uploaded to Zenodo, PyPI or GitHub. The prototype cannot estimate unknown probabilities or turn unsupported uncertainty sets into reliable safety guarantees. A general fixed-model minimax POMDP solver is not implemented.

## Release decision

The package can support review and further research now. Public deposition should follow owner confirmation of authorship and rights, final editorial review, and prominent retention of these limitations. A DOI would identify a deposited artifact; it would not validate the science or certify deployment safety.
