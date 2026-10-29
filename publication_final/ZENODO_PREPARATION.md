# Zenodo deposit preparation (not deposited)

Nothing has been deposited. A deposit requires the owner's separate, explicit approval. A Zenodo DOI identifies an archived version; it is not evidence of peer review.

## Option 1: software release archive (GitHub integration)

- When the Zenodo–GitHub integration is enabled for `Pratik653/HandoffX`, Zenodo archives **every published GitHub release** automatically, using the root `.zenodo.json`.
- The integration is **not** enabled as of 29 October 2026: the repository has no webhooks.
- If it is enabled later, the next GitHub release will create a deposit. Enable it only when a deposit is intended.

## Option 2: separate deposit of the paper (upload type "publication / preprint")

| Field | Proposed value | Verified |
|---|---|---|
| Title | HandoffX: A reproducible decision-theoretic framework for continue, retry, human-assistance and stop decisions under uncertainty: five studies of planning, adaptive calibration and risk reduction | from the paper |
| Creators | Pratik653 | **owner to confirm full name, affiliation, ORCID** |
| Description | Paper abstract (first section of `HandoffX_Final_Research_Paper.md`) | yes |
| Keywords | human–AI collaboration; learning to defer; Bayesian sequential decision-making; POMDP; robust control; model misspecification; risk-sensitive decision-making; reproducible research | yes |
| Version | Final consolidated paper 1.0 (software 0.2.1) | yes |
| Licence | CC BY 4.0 (text, figures, data); the software is MIT and is linked, not included | yes |
| Related identifiers | isSupplementedBy https://github.com/Pratik653/HandoffX; the software DOI if Option 1 is used | URL yes |
| Files | `HandoffX_Final_Research_Paper.pdf`, `.docx`, `.md`, `HandoffX_Final_References.bib` | built 29 October 2026 |
| Reproducibility | Appendix F of the paper; per-study protocols and stored results in the repository | yes |
| Peer review | none | stated in the paper |

## Owner decisions before deposit

1. Author metadata: full name, affiliation, ORCID.
2. Whether to keep the paper's AI-assistance disclosure as drafted (Declarations) or edit it to the target venue's policy.
3. Funding and competing-interest statements.
4. Whether to deposit the software (Option 1), the paper (Option 2) or both.
