"""Figures for the v2 benchmark, regenerated from stored results only."""
from pathlib import Path
import csv, json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
RES = ROOT / 'benchmarks_v2/results'; FIG = ROOT / 'benchmarks_v2/figures'; FIG.mkdir(exist_ok=True)
SHOW = ('nominal', 'bayes_static', 'plugin_recal', 'bayes_recal', 'ts_recal', 'handoffx_v2', 'gate_static')


def save(fig, name):
    fig.tight_layout(); fig.savefig(FIG / f'{name}.png', dpi=170, bbox_inches='tight')
    fig.savefig(FIG / f'{name}.svg', bbox_inches='tight'); plt.close(fig)


for split in ('test', 'shift'):
    c = json.loads((RES / split / 'learning_curves.json').read_text())
    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    k = 10
    for p in SHOW:
        x = np.convolve(np.array(c[p]), np.ones(k) / k, mode='valid')
        ax.plot(np.arange(k, len(c[p]) + 1), x, label=p)
    ax.set_xlabel('Episode in deployment stream (10-episode moving average)')
    ax.set_ylabel('Mean exact loss minus oracle')
    ax.set_title(f'Learning curves, held-out {split} split')
    ax.legend(fontsize=8, ncol=2); save(fig, f'v2_learning_curves_{split}')

rows = list(csv.DictReader((RES / 'test' / 'summary.csv').open(encoding='utf-8')))
by = {(r['environment'], r['policy']): float(r['mean_exact_loss']) for r in rows}
envs = sorted({r['environment'] for r in rows})
fig, ax = plt.subplots(figsize=(7.5, 4.5))
data = [[100 * (by[(e, p)] / by[(e, 'nominal')] - 1) for e in envs] for p in SHOW[1:] + ('robust_static', 'v2_iid', 'oracle')]
ax.boxplot(data, tick_labels=list(SHOW[1:]) + ['robust_static', 'v2_iid', 'oracle'], showfliers=True)
ax.axhline(0, linestyle='--', linewidth=1)
ax.set_ylabel('Relative loss vs nominal (%)'); ax.set_title('Per-environment relative loss, held-out test (n=200)')
plt.setp(ax.get_xticklabels(), rotation=30, ha='right'); save(fig, 'v2_relative_loss_test')

g = json.loads((ROOT / 'benchmarks_v2/configs/frozen_gate.json').read_text())['grid']
fig, ax = plt.subplots(figsize=(6.5, 4.5))
for tol in sorted({r['tolerance'] for r in g}):
    s = [r for r in g if r['tolerance'] == tol]
    ax.plot([100 * r['share_degraded_gt_1pct'] for r in s], [100 * r['mean_relative_difference'] for r in s],
            marker='o', label=f'tolerance {tol}')
    for r in s:
        ax.annotate(f"a={r['alpha']}", (100 * r['share_degraded_gt_1pct'], 100 * r['mean_relative_difference']), fontsize=7)
ax.axvline(10, linestyle='--', linewidth=1)
ax.set_xlabel('Dev environments degraded by >1% (%)'); ax.set_ylabel('Mean relative loss vs nominal (%)')
ax.set_title('Gate trade-off on the development split'); ax.legend(fontsize=8); save(fig, 'v2_gate_tradeoff_dev')
print('figures written to', FIG)
