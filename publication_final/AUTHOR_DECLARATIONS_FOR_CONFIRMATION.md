# Author and declaration fields: for the author's confirmation

None of the bracketed values has been invented. Fill in or confirm each one. The same fields then need updating in the files listed in the last column.

| Field | Current value | Your confirmation | Where it appears |
|---|---|---|---|
| Author display name | `Pratik653` (GitHub handle) | | paper title page and Declarations; `CITATION.cff`; `.zenodo.json`; `pyproject.toml` `authors` |
| Full name | not set | | paper, `CITATION.cff` (`given-names`, `family-names`), `.zenodo.json` (`creators.name`) |
| Affiliation | not set | | paper, `CITATION.cff`, `.zenodo.json` |
| ORCID | not set | | paper, `CITATION.cff` (`orcid`), `.zenodo.json` (`creators.orcid`) |
| Contact address | not set (no e-mail is published anywhere) | | paper (optional) |
| Author contributions | not set | | paper Declarations |
| Use of AI tools | "AI-based writing and coding assistance was used in preparing software, analyses and text. The author reviewed the material and is responsible for its content." Names no tool and gives no credit | keep / edit / remove per venue policy | paper Declarations |
| Funding | not set | | paper Declarations |
| Competing interests | not set | | paper Declarations |

After you confirm, edit `publication_final/src/07_synthesis_end.md` (Declarations) and the front matter in `src/01_front_intro.md`, then rebuild:

```bash
python publication_final/build_final.py --word-refresh
python publication_final/verify_paper.py
```

The archived v0.1 and v0.2 manuscripts are not changed.
