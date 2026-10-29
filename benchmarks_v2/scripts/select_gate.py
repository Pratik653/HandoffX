"""Apply the pre-registered dev selection rule and write configs/frozen_gate.json."""
from __future__ import annotations
from pathlib import Path
import csv, json
import numpy as np

ROOT = Path(__file__).resolve().parents[2]


def main():
    study = json.loads((ROOT / 'benchmarks_v2/configs/study_v2.json').read_text())
    rows = list(csv.DictReader((ROOT / 'benchmarks_v2/results/dev/summary.csv').open(encoding='utf-8')))
    nominal = {r['environment']: float(r['mean_exact_loss']) for r in rows if r['policy'] == 'nominal'}
    table = []
    for a in study['dev_grid']['alpha']:
        for t in study['dev_grid']['tolerance']:
            name = f'handoffx_v2[a={a},tol={t}]'
            rel = np.array([(float(r['mean_exact_loss']) - nominal[r['environment']]) / nominal[r['environment']]
                            for r in rows if r['policy'] == name])
            table.append({'alpha': a, 'tolerance': t, 'n': len(rel), 'mean_relative_difference': float(rel.mean()),
                          'share_degraded_gt_1pct': float((rel > .01).mean()), 'worst_relative': float(rel.max())})
    ok = [r for r in table if r['share_degraded_gt_1pct'] <= .10]
    if ok:
        best = min(ok, key=lambda r: (r['mean_relative_difference'], r['alpha'], r['tolerance'])); rule = 'primary'
    else:
        best = min(table, key=lambda r: (r['share_degraded_gt_1pct'], r['alpha'], r['tolerance'])); rule = 'fallback'
    out = {'gate': {'alpha': best['alpha'], 'tolerance': best['tolerance'], 'margin': 0., 'relative': True},
           'selection_rule_branch': rule, 'selected_row': best, 'grid': table,
           'source': 'benchmarks_v2/results/dev/summary.csv'}
    (ROOT / 'benchmarks_v2/configs/frozen_gate.json').write_text(json.dumps(out, indent=2) + '\n')
    for r in table:
        print(f"a={r['alpha']:<5} tol={r['tolerance']:<5} mean_rel={100*r['mean_relative_difference']:+.3f}% "
              f"degraded>1%={100*r['share_degraded_gt_1pct']:.1f}% worst={100*r['worst_relative']:+.2f}%")
    print('SELECTED', out['gate'], rule)


if __name__ == '__main__':
    main()
