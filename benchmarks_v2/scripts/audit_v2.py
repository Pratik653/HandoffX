"""Verify v2 derived summaries against raw per-episode arrays and check split disjointness."""
from pathlib import Path
import csv, json
import numpy as np

ROOT = Path(__file__).resolve().parents[2]; RES = ROOT / 'benchmarks_v2/results'
report = {}
seeds = {}
for split in ('dev', 'validation', 'test', 'shift', 'original'):
    rows = list(csv.DictReader((RES / split / 'summary.csv').open(encoding='utf-8')))
    raw = np.load(RES / split / 'raw' / 'episodes.npz')
    err = 0.
    for r in rows:
        k = f"{r['environment']}__{r['policy']}"
        e, z = raw[k + '__exact'], raw[k + '__realized']
        err = max(err, abs(e.mean() - float(r['mean_exact_loss'])), abs(e[:20].mean() - float(r['first20_exact_loss'])),
                  abs(e[-20:].mean() - float(r['last20_exact_loss'])), abs(z.mean() - float(r['mean_realized_loss'])))
    oracle_violation = sum(float(r['mean_exact_loss']) < float(next(x for x in rows if x['environment'] == r['environment']
                                                                     and x['policy'] == 'oracle')['mean_exact_loss']) - 1e-9 for r in rows)
    seeds[split] = {r['environment'] for r in rows}
    report[split] = {'rows': len(rows), 'max_abs_summary_vs_raw': err, 'policies_below_oracle': oracle_violation}
named = [s for s in seeds if s != 'original']
report['seed_overlap_between_splits'] = sum(len(seeds[a] & seeds[b]) for i, a in enumerate(named) for b in named[i + 1:])
report['all_passed'] = all(v['max_abs_summary_vs_raw'] < 1e-9 and v['policies_below_oracle'] == 0 for k, v in report.items()
                           if isinstance(v, dict)) and report['seed_overlap_between_splits'] == 0
(RES / 'audit_v2.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
print(json.dumps(report, indent=2))
