# Contributing to HandoffX

Thanks for your interest. HandoffX is research software; correctness and honest reporting matter more than features.

## Development setup

```bash
python -m venv .venv
. .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -e ".[research]"
pytest
```

## Guidelines

- Keep the runtime dependency set minimal (NumPy only).
- Validate inputs explicitly; never silently normalise probabilities or fall back on invalid input.
- Add focused tests for every behavioural change; mathematical changes need a numerical check.
- Do not edit stored benchmark results or the v0.1 research artifacts. New experiments go in new result directories with their configuration committed before the run.
- Report negative results. Claims in documentation must be backed by a committed result file.
- Use conventional commit messages (`feat:`, `fix:`, `docs:`, `test:`, `exp:`, `chore:`).

## Reporting issues

Open a GitHub issue with a minimal reproducible example, your Python and NumPy versions and the observed vs. expected behaviour.
