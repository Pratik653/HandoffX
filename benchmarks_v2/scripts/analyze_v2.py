"""Paired, environment-level analysis of a v2 split (pre-registered in EXPERIMENTAL_PROTOCOL.md section 7).

    python benchmarks_v2/scripts/analyze_v2.py validation test shift original
"""
from __future__ import annotations
from pathlib import Path
import csv, json, sys
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
RES = ROOT / 'benchmarks_v2/results'
B = 10_000


def boot(x, rng):
    idx = rng.integers(0, len(x), size=(B, len(x)))
    m = x[idx].mean(axis=1)
    return float(np.quantile(m, .025)), float(np.quantile(m, .975))


def cvar95(x):
    s = np.sort(x); k = max(1, int(np.ceil(.05 * len(s))))
    return float(s[-k:].mean())


def analyse(split):
    rows = list(csv.DictReader((RES / split / 'summary.csv').open(encoding='utf-8')))
    raw = np.load(RES / split / 'raw' / 'episodes.npz')
    policies = list(dict.fromkeys(r['policy'] for r in rows))
    by = {(r['environment'], r['policy']): r for r in rows}
    envs = list(dict.fromkeys(r['environment'] for r in rows))
    f = lambda e, p, k: float(by[(e, p)][k])
    nom = np.array([f(e, 'nominal', 'mean_exact_loss') for e in envs])
    orc = np.array([f(e, 'oracle', 'mean_exact_loss') for e in envs])
    out = {'split': split, 'n_environments': len(envs), 'policies': {}}
    for p in policies:
        rng = np.random.default_rng(7)
        L = np.array([f(e, p, 'mean_exact_loss') for e in envs]); d = L - nom; rel = d / nom
        realized = np.concatenate([raw[f'{e}__{p}__realized'] for e in envs])
        sd = d.std(ddof=1)
        out['policies'][p] = {
            'mean_loss': float(L.mean()), 'mean_difference_vs_nominal': float(d.mean()),
            'difference_ci95': boot(d, rng), 'mean_relative_difference': float(rel.mean()),
            'relative_ci95': boot(rel, rng), 'effect_size_dz': float(d.mean() / sd) if sd > 0 else 0.,
            'wins_ties_losses_exact': [int((d < -1e-9).sum()), int((abs(d) <= 1e-9).sum()), int((d > 1e-9).sum())],
            'wins_ties_losses_1pct': [int((rel < -.01).sum()), int((abs(rel) <= .01).sum()), int((rel > .01).sum())],
            'worst_relative_degradation': float(rel.max()), 'best_relative_improvement': float(rel.min()),
            'mean_regret_vs_oracle': float((L - orc).mean()),
            'share_of_nominal_gap_closed': float((nom - L).sum() / (nom - orc).sum()) if (nom - orc).sum() > 0 else None,
            'first20_loss': float(np.mean([f(e, p, 'first20_exact_loss') for e in envs])),
            'last20_loss': float(np.mean([f(e, p, 'last20_exact_loss') for e in envs])),
            'severe_probability': float(np.mean([f(e, p, 'mean_exact_severe') for e in envs])),
            'success_probability': float(np.mean([f(e, p, 'mean_exact_success') for e in envs])),
            'human_rate': float(np.mean([f(e, p, 'mean_exact_human') for e in envs])),
            'realized_loss_cvar95': cvar95(realized),
            'calibration_error_ai_start_end': [float(np.mean([f(e, p, 'cal_err_ai_start') for e in envs])),
                                               float(np.mean([f(e, p, 'cal_err_ai_end') for e in envs]))],
            'calibration_error_human_start_end': [float(np.mean([f(e, p, 'cal_err_human_start') for e in envs])),
                                                  float(np.mean([f(e, p, 'cal_err_human_end') for e in envs]))],
            'mean_switched_episodes': float(np.mean([f(e, p, 'switched_episodes') for e in envs])),
            'mean_seconds_per_stream': float(np.mean([f(e, p, 'seconds') for e in envs])),
        }
    # Pre-specified subgroups for the primary comparison.
    groups = {}
    meta = {e: by[(e, 'nominal')] for e in envs}
    defs = {'calibrated': lambda m: m['calibrated'] == 'True',
            'biased': lambda m: m['calibrated'] != 'True',
            'in_support': lambda m: m['in_support'] == 'True',
            'out_of_support': lambda m: m['in_support'] == 'False',
            'human_underestimated': lambda m: float(m['bias_human']) > .05,
            'human_overestimated': lambda m: float(m['bias_human']) < -.05,
            'ai_underestimated': lambda m: float(m['bias_ai']) > .05,
            'ai_overestimated': lambda m: float(m['bias_ai']) < -.05}
    for g, fn in defs.items():
        sel = [i for i, e in enumerate(envs) if fn(meta[e])]
        if not sel:
            continue
        groups[g] = {'n': len(sel)}
        for p in ('handoffx_v2', 'bayes_recal', 'plugin_recal', 'ts_recal', 'robust_static'):
            if p not in policies:
                continue
            rel = np.array([(f(envs[i], p, 'mean_exact_loss') - nom[i]) / nom[i] for i in sel])
            groups[g][p] = {'mean_relative_difference': float(rel.mean()),
                            'share_degraded_gt_1pct': float((rel > .01).mean()),
                            'share_improved_gt_1pct': float((rel < -.01).mean())}
    out['subgroups'] = groups
    # Learning curves (mean exact loss by episode index, relative to oracle).
    curves = {p: np.mean([raw[f'{e}__{p}__exact'] - raw[f'{e}__oracle__exact'] for e in envs], axis=0).tolist()
              for p in policies}
    (RES / split / 'learning_curves.json').write_text(json.dumps(curves) + '\n')
    (RES / split / 'analysis.json').write_text(json.dumps(out, indent=2) + '\n')
    return out


def table(out):
    s = f"### Split `{out['split']}` ({out['n_environments']} environments)\n\n"
    s += ('| Policy | Mean loss | Δ vs nominal [95% CI] | Rel. Δ [95% CI] | d_z | W/T/L (1%) | Worst rel. | '
          'Gap closed | Severe p | Human rate | CVaR95 |\n|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|\n')
    for p, r in out['policies'].items():
        gc = '' if r['share_of_nominal_gap_closed'] is None else f"{100*r['share_of_nominal_gap_closed']:.1f}%"
        s += (f"| {p} | {r['mean_loss']:.3f} | {r['mean_difference_vs_nominal']:+.3f} [{r['difference_ci95'][0]:+.3f}, {r['difference_ci95'][1]:+.3f}] | "
              f"{100*r['mean_relative_difference']:+.2f}% [{100*r['relative_ci95'][0]:+.2f}, {100*r['relative_ci95'][1]:+.2f}] | "
              f"{r['effect_size_dz']:+.2f} | {'/'.join(map(str, r['wins_ties_losses_1pct']))} | {100*r['worst_relative_degradation']:+.2f}% | "
              f"{gc} | {r['severe_probability']:.4f} | {r['human_rate']:.3f} | {r['realized_loss_cvar95']:.1f} |\n")
    return s


if __name__ == '__main__':
    md = ''
    for split in sys.argv[1:]:
        md += table(analyse(split)) + '\n'
    (RES / 'TABLES.md').write_text(md, encoding='utf-8')
    print(md)
