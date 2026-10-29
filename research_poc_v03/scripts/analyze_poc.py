"""Paired, kind-stratified analysis of pilot / confirmation results (protocol: EXPERIMENT_PROTOCOL.md)."""
from __future__ import annotations
from pathlib import Path
import csv, json, sys
import numpy as np

ROOT = Path(__file__).resolve().parents[2]; RES = ROOT / 'research_poc_v03/results'
B = 10_000


def strat_boot(values_by_kind, rng):
    """Percentile CI for the equally-weighted mean over kinds, resampling within kind."""
    kinds = list(values_by_kind)
    means = np.zeros(B)
    for k in kinds:
        v = values_by_kind[k]; means += v[rng.integers(0, len(v), (B, len(v)))].mean(1)
    means /= len(kinds)
    return [float(np.quantile(means, .025)), float(np.quantile(means, .975))]


def analyse(split):
    rows = list(csv.DictReader((RES / split / 'summary.csv').open(encoding='utf-8')))
    by = {(r['seed'], r['policy']): r for r in rows}
    seeds = list(dict.fromkeys(r['seed'] for r in rows)); kind = {r['seed']: r['kind'] for r in rows}
    kinds = list(dict.fromkeys(kind[s] for s in seeds)); policies = list(dict.fromkeys(r['policy'] for r in rows))
    f = lambda s, p, k='mean_exact_loss': float(by[(s, p)][k])
    out = {'split': split, 'n': len(seeds), 'per_kind_n': {k: sum(kind[s] == k for s in seeds) for k in kinds}, 'policies': {}}
    for p in policies:
        res = {}
        for ref in ('bayes_recal', 'nominal', 'handoffx_v2'):
            rel = {k: np.array([f(s, p) / f(s, ref) - 1 for s in seeds if kind[s] == k]) for k in kinds}
            rng = np.random.default_rng(11)
            res[f'vs_{ref}'] = {'pooled': float(np.mean([v.mean() for v in rel.values()])), 'pooled_ci95': strat_boot(rel, rng),
                                'per_kind': {k: float(v.mean()) for k, v in rel.items()},
                                'per_kind_ci95': {k: [float(np.quantile(v[np.random.default_rng(11).integers(0, len(v), (B, len(v)))].mean(1), q)) for q in (.025, .975)] for k, v in rel.items()},
                                'wins_ties_losses_1pct': [int(sum((v < -.01).sum() for v in rel.values())), int(sum((abs(v) <= .01).sum() for v in rel.values())), int(sum((v > .01).sum() for v in rel.values()))],
                                'worst': float(max(v.max() for v in rel.values()))}
        regret = np.mean([f(s, p) - f(s, 'oracle') for s in seeds])
        res['mean_regret_vs_oracle'] = float(regret)
        res['last20_regret_vs_oracle'] = float(np.mean([f(s, p, 'last20_exact_loss') - f(s, 'oracle', 'last20_exact_loss') for s in seeds]))
        for k in ('exact_severe', 'exact_success', 'exact_human', 'exact_retries', 'cal_err_ai', 'cal_err_human', 'prev_tv_error', 'human_observations', 'guarded_episodes', 'seconds'):
            res[k] = float(np.mean([f(s, p, k) for s in seeds]))
        out['policies'][p] = res
    (RES / split / 'analysis.json').write_text(json.dumps(out, indent=1) + '\n', encoding='utf-8')
    return out


def table(o):
    kinds = list(o['per_kind_n'])
    s = f"### {o['split']} (n = {o['n']}; {', '.join(f'{k} {v}' for k, v in o['per_kind_n'].items())})\n\n"
    s += '| Policy | vs bayes_recal pooled [95% CI] | ' + ' | '.join(kinds) + ' | vs nominal | vs v0.2 | W/T/L 1% vs bayes_recal | last-20 regret | severe p | human rate | retries/ep | s/stream |\n'
    s += '|---' * (11 + len(kinds)) + '|\n'
    for p, r in o['policies'].items():
        b = r['vs_bayes_recal']
        s += (f"| {p} | {100*b['pooled']:+.2f}% [{100*b['pooled_ci95'][0]:+.2f}, {100*b['pooled_ci95'][1]:+.2f}] | "
              + ' | '.join(f"{100*b['per_kind'][k]:+.2f}%" for k in kinds)
              + f" | {100*r['vs_nominal']['pooled']:+.2f}% | {100*r['vs_handoffx_v2']['pooled']:+.2f}% | {'/'.join(map(str, b['wins_ties_losses_1pct']))} | "
              f"{r['last20_regret_vs_oracle']:.3f} | {r['exact_severe']:.4f} | {r['exact_human']:.3f} | {r['exact_retries']:.3f} | {r['seconds']:.2f} |\n")
    s += '\nPredictive diagnostics (end of stream): '
    s += '; '.join(f"{p}: AI cal {r['cal_err_ai']:.3f}, human cal {r['cal_err_human']:.3f}, prevalence TV {r['prev_tv_error']:.3f}, human obs {r['human_observations']:.1f}, guarded eps {r['guarded_episodes']:.1f}"
                   for p, r in o['policies'].items() if p not in ('oracle',)) + '\n'
    return s


if __name__ == '__main__':
    md = ''.join(table(analyse(s)) + '\n' for s in sys.argv[1:])
    (RES / 'TABLES.md').write_text(md, encoding='utf-8'); print(md)
