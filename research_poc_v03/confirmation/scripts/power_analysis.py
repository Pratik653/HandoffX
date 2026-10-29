"""Pre-execution precision estimate from the earlier PoC rounds (confirm, replicate) only.

Uses the closest earlier kinds as proxies (persist_shift ~ prevalence_misspec, human_shift ~ human_bias)
for the per-environment SD of the paired severe and loss differences, then normal-approximation power
for the frozen sample sizes. No confirmation data are used.
"""
from __future__ import annotations
from pathlib import Path
import csv, json
import numpy as np
from math import erf, sqrt

ROOT = Path(__file__).resolve().parents[3]; CONF = ROOT / 'research_poc_v03/confirmation'
PROXY = {'persist_shift': 'prevalence_misspec', 'human_shift': 'human_bias'}
Phi = lambda x: .5 * (1 + erf(x / sqrt(2)))


def proxy_stats():
    d = {k: [] for k in PROXY.values()}
    for split in ('confirm', 'replicate'):
        rows = list(csv.DictReader((ROOT / f'research_poc_v03/results/{split}/summary.csv').open(encoding='utf-8')))
        by = {(r['seed'], r['policy']): r for r in rows}
        for r in rows:
            if r['policy'] == 'A_prev' and r['kind'] in d:
                c = by[(r['seed'], 'bayes_recal')]
                d[r['kind']].append((float(r['exact_severe']) - float(c['exact_severe']), float(c['exact_severe']),
                                     float(r['mean_exact_loss']) - float(c['mean_exact_loss']), float(c['mean_exact_loss'])))
    out = {}
    for fam, k in PROXY.items():
        v = np.array(d[k])
        out[fam] = {'proxy_kind': k, 'n_earlier': len(v), 'ARD': v[:, 0].mean(), 'sd_dS': v[:, 0].std(ddof=1), 'base_severe': v[:, 1].mean(),
                    'loss_rel': v[:, 2].mean() / v[:, 3].mean(), 'sd_dL_rel': v[:, 2].std(ddof=1) / v[:, 3].mean()}
    return out


def main():
    cfg = json.loads((CONF / 'configs/confirmation.json').read_text(encoding='utf-8'))
    st = proxy_stats(); res = {'proxies': st, 'design_n': cfg['n_per_kind']}
    n = {f: cfg['n_per_kind'][f] for f in st}
    # Planning effect: an RRR of 10% (the practical threshold) at each family's earlier baseline severe level.
    for f, s in st.items():
        se = s['sd_dS'] / np.sqrt(n[f]); eff = .10 * s['base_severe']
        res[f] = {'se_ARD': se, 'power_RRR10pct': Phi(eff / se - 1.96), 'power_at_earlier_effect': Phi(-s['ARD'] / se - 1.96),
                  'minimum_detectable_RRR_80pct': (1.96 + .8416) * se / s['base_severe']}
    # Pooled target (equal weights).
    se = np.sqrt(sum((st[f]['sd_dS'] / 2) ** 2 / n[f] for f in st)); base = np.mean([st[f]['base_severe'] for f in st])
    earlier = np.mean([st[f]['ARD'] for f in st])
    res['pooled'] = {'se_ARD': se, 'power_RRR10pct': Phi(.10 * base / se - 1.96), 'power_at_earlier_effect': Phi(-earlier / se - 1.96),
                     'minimum_detectable_RRR_80pct': (1.96 + .8416) * se / base}
    sel = np.sqrt(sum((st[f]['sd_dL_rel'] / 2) ** 2 / n[f] for f in st))
    res['noninferiority'] = {'se_loss_rel_approx': sel,
                             **{f'power_if_true_diff_{d:+.1%}': Phi((.005 - d) / sel - 1.96) for d in (0., -.002, -.005, .002)}}
    (CONF / 'results/power_analysis.json').write_text(json.dumps(res, indent=1, default=float) + '\n', encoding='utf-8')
    print(json.dumps(res, indent=1, default=float))


if __name__ == '__main__':
    main()
