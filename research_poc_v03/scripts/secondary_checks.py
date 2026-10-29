"""Paired CIs for A_prev vs bayes_recal on two secondary signals seen in every round:
severe-failure probability (all kinds) and loss in the shift kind. Reported per independent round, not pooled."""
from pathlib import Path
import csv, json
import numpy as np
ROOT = Path(__file__).resolve().parents[2]; RES = ROOT / 'research_poc_v03/results'
out = {}
for split in ('pilot', 'confirm', 'replicate'):
    rows = list(csv.DictReader((RES / split / 'summary.csv').open(encoding='utf-8')))
    by = {(r['seed'], r['policy']): r for r in rows}; seeds = sorted({r['seed'] for r in rows}); kind = {r['seed']: r['kind'] for r in rows}
    rng = np.random.default_rng(11)
    def ci(x):
        m = x[rng.integers(0, len(x), (10000, len(x)))].mean(1); return [float(x.mean()), float(np.quantile(m, .025)), float(np.quantile(m, .975))]
    sev = np.array([float(by[(s, 'A_prev')]['exact_severe']) - float(by[(s, 'bayes_recal')]['exact_severe']) for s in seeds])
    base_sev = np.mean([float(by[(s, 'bayes_recal')]['exact_severe']) for s in seeds])
    sh = np.array([float(by[(s, 'A_prev')]['mean_exact_loss']) / float(by[(s, 'bayes_recal')]['mean_exact_loss']) - 1 for s in seeds if kind[s] == 'shift'])
    out[split] = {'severe_abs_diff_ci': ci(sev), 'bayes_recal_severe': float(base_sev), 'shift_relative_loss_ci': ci(sh)}
(RES / 'secondary_checks.json').write_text(json.dumps(out, indent=1) + '\n', encoding='utf-8')
for k, v in out.items():
    s = v['severe_abs_diff_ci']; h = v['shift_relative_loss_ci']
    print(f"{k:9s} severe diff {s[0]:+.4f} [{s[1]:+.4f}, {s[2]:+.4f}] (base {v['bayes_recal_severe']:.4f}) | shift loss {100*h[0]:+.2f}% [{100*h[1]:+.2f}, {100*h[2]:+.2f}]")
