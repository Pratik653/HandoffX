# Final publication report

Status as of 29 October 2026.

## Deliverables

All deliverables are in `publication_final/`.

| File | Status |
|---|---|
| `HandoffX_Final_Research_Paper.md` | Generated from `src/` by `build_final.py`; 19 numbered sections, declarations, 35 references and appendices A–F |
| `HandoffX_Final_Research_Paper.pdf` | 83 pages, A4. Title page, linked contents, equations (1)–(14), 33 numbered tables, 12 numbered figures, page numbers |
| `HandoffX_Final_Research_Paper.docx` | Native Word equations (306 math objects), 33 tables, 12 images, 177 headings, TOC field |
| `HandoffX_Final_References.bib` | 35 BibTeX records |

## How the paper was consolidated

**Preservation.**
- The original mathematics and results are included **verbatim** from the archived manuscripts through include directives: FM-01–FM-10, P1–P9 with proofs, CE1–CE8, the Study I methods, results and appendices, and the Study II root-cause text.
- The only changes are heading renumbering, table and figure renumbering, and one updated sentence about publication status.
- The archived manuscripts themselves are unchanged.

**Integration.** The text follows a single journal-style structure, organized as five sequential studies, with:
- explicit evidence labels (theoretical, exact calculation, held-out, confirmatory, exploratory);
- a cross-study synthesis;
- a section (15.2) stating how each interpretation was refined.

**Numbers.** Every Study III–V number was read from the stored analysis JSON. `verify_paper.py` checks 40 key quoted values against those files, including:
- the Study IV primary table and kind table;
- the realized event counts;
- the behaviour table;
- the Study V frontier;
- the Study III pooled effects;
- the Study II headline results.

It also checks that every in-text citation has a reference entry and every reference is cited (35/35), and that equations are numbered consecutively (1–14). All checks pass.

**References.**
- 30 existing records are retained.
- Five were added and verified against Crossref on 29 October 2026: Chow (1970), Howard & Matheson (1972), Altman (1999/2021), Kass & Raftery (1995) and Harrison et al. (2012).
- APA 7 style throughout.
- No DOIs, pages or quotations were invented.

## Claims audit

- **Not claimed:**
  - universal optimality or superiority;
  - real-world safety;
  - reduced failures in deployed agents;
  - novelty of Bayesian or decision-theoretic principles;
  - more accurate prevalence estimation by candidate A.
- Loss non-inferiority is stated as **not demonstrated**.
- ARD and RRR are reported separately, and percentage points are distinguished from percent.
- The Study V matched-risk comparison is labelled exploratory and approximate. The proposed pre-registered matched-risk experiment is identified as **not performed**.

## Formatting verification

- **PDF:** rendered page images were inspected for the title page, contents, equation-heavy pages, table pages, figure pages, references and the final appendix. A table-overflow problem that shrank the whole document was found and fixed.
- **DOCX:** validated structurally only. Microsoft Word automation hung on this machine, so the document was **not opened in Word**. Its pagination and the populated table of contents (a field that Word refreshes on opening) are unverified.

## Items for the author

1. **Authorship metadata.** The paper, `CITATION.cff`, `.zenodo.json` and `pyproject.toml` use the GitHub handle `Pratik653`. Add your full name, affiliation and ORCID before formal submission; none was invented.
2. **AI-assistance disclosure.**
   - The Declarations section contains a neutral statement that AI-based writing and coding assistance was used and that the author is responsible for the content. It names no assistant and gives no credit.
   - Most journals require such a disclosure. Keep, edit or remove it according to the target venue's policy.
   - The archived v0.1 and v0.2 manuscripts contain a similar sentence and were left unchanged.
3. **Funding and competing interests.** Marked "to be completed by the author".
4. **Zenodo.** Prepared (`publication_final/ZENODO_PREPARATION.md`, `.zenodo.json`) but not deposited. The Zenodo–GitHub integration is not enabled (the repository has no webhooks), so a GitHub release does not create a deposit.
5. **Peer review.** None. A DOI would not imply peer review.
