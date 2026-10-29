"""Figures for the candidate-A confirmation.

1. figures/confirmation_forest.png: severe-failure change and loss change of A vs bayes_recal, per kind (confirmatory).
2. figures/risk_loss_frontier.png: severe change vs loss change on the target families (exploratory set).
"""
from __future__ import annotations
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

CONF = Path(__file__).resolve().parents[1]
BLUE, ORANGE, INK, MUTED, GRID, SURF = '#2a78d6', '#eb6834', '#0b0b0b', '#52514e', '#e4e3df', '#fcfcfb'
plt.rcParams.update({'font.size': 9, 'axes.edgecolor': MUTED, 'axes.labelcolor': INK, 'xtick.color': MUTED, 'ytick.color': INK,
                     'axes.spines.top': False, 'axes.spines.right': False, 'figure.facecolor': SURF, 'axes.facecolor': SURF})


def forest():
    o = json.loads((CONF / 'results/confirm/analysis.json').read_text(encoding='utf-8'))
    rows = [('Primary target (persist + human)', o['primary'])]
    labels = {'persist_shift': 'Family A: persistent-failure shift', 'human_shift': 'Family B: human-effectiveness shift',
              'hazard_shift': 'Hazard shift (secondary)', 'calibrated': 'Control: calibrated', 'near_nominal': 'Control: near-nominal',
              'ai_bias': 'Control: AI recovery bias', 'joint_bias': 'Control: AI + human bias'}
    rows += [(f"{labels[k]} (n={o['per_kind_n'][k]})", o['per_kind'][k]['bayes_recal']) for k in labels]
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.2), sharey=True, gridspec_kw={'wspace': .08})
    ys = list(range(len(rows)))[::-1]
    for ax, key, cik, title, ref in ((axes[0], 'RRR', 'RRR_ci95', 'Severe-failure probability change (%)', None),
                                     (axes[1], 'loss_ratio_minus_1', 'loss_ratio_ci95', 'Cumulative loss change (%)', .5)):
        for y, (lab, c) in zip(ys, rows):
            sgn = -1 if key == 'RRR' else 1
            pt = sgn * 100 * c[key]; lo, hi = sorted(sgn * 100 * x for x in c[cik])
            col = BLUE if key == 'RRR' else ORANGE
            ax.plot([lo, hi], [y, y], color=col, lw=2, solid_capstyle='round')
            ax.plot(pt, y, 'o', ms=8 if y == ys[0] else 6, color=col, mec=SURF, mew=1.5)
        ax.axvline(0, color=MUTED, lw=1)
        if ref is not None:
            ax.axvline(ref, color=MUTED, lw=1, ls=(0, (4, 3))); ax.text(ref, ys[0] + .6, ' +0.5% NI margin', color=MUTED, fontsize=8, va='bottom')
        ax.axhline(ys[0] - .5, color=GRID, lw=1)
        ax.set_xlabel(title); ax.grid(axis='x', color=GRID, lw=.8); ax.set_axisbelow(True)
    axes[0].set_yticks(ys); axes[0].set_yticklabels([r[0] for r in rows])
    fig.suptitle('Candidate A vs ungated Bayesian recalibration: confirmation, 500 fresh environments (95% CIs)', x=.02, ha='left', color=INK)
    fig.savefig(CONF / 'figures/confirmation_forest.png', dpi=160, bbox_inches='tight'); plt.close(fig)


def frontier():
    o = json.loads((CONF / 'results/exploratory_mechanism/analysis.json').read_text(encoding='utf-8'))['TARGET']
    fig, ax = plt.subplots(figsize=(6.4, 4.4))
    rc = ['bayes_recal', 'riskcost_1.25', 'riskcost_1.5', 'riskcost_2', 'riskcost_3']
    xs = [100 * o[p]['loss_ratio_minus_1'] for p in rc]; ys = [-100 * o[p]['RRR'] for p in rc]
    ax.plot(xs, ys, '-o', color=MUTED, lw=2, ms=6, mec=SURF, mew=1.5)
    for p, x, y in zip(rc, xs, ys):
        ax.annotate('×1 (bayes_recal)' if p == 'bayes_recal' else '×' + p.split('_')[1], (x, y), xytext=(6, 2), textcoords='offset points', color=MUTED, fontsize=8)
    ax.text(xs[3] + .4, ys[3] + 8, 'bayes_recal planning with\ncatastrophe loss × c', color=MUTED, fontsize=8)
    for p, lab, col in (('A_prev', 'Candidate A', BLUE), ('pess_prior_recal', "A's prior mean only", ORANGE)):
        v = o[p]; x, y = 100 * v['loss_ratio_minus_1'], -100 * v['RRR']
        ax.errorbar(x, y, xerr=[[x - 100 * v['loss_ratio_ci95'][0]], [100 * v['loss_ratio_ci95'][1] - x]],
                    yerr=[[y + 100 * v['RRR_ci95'][1]], [-100 * v['RRR_ci95'][0] - y]], fmt='o', color=col, ms=8, mec=SURF, mew=1.5, elinewidth=1.5, capsize=0)
        ax.annotate(lab, (x, y), xytext=(8, -12), textcoords='offset points', color=INK, fontsize=9)
    ax.axhline(0, color=GRID, lw=1); ax.axvline(0, color=GRID, lw=1)
    ax.set_xlabel('Cumulative loss change vs bayes_recal (%)'); ax.set_ylabel('Severe-failure probability change (%)')
    ax.grid(color=GRID, lw=.8); ax.set_axisbelow(True)
    ax.set_title('Exploratory (fresh seeds 850000+): A vs explicit risk aversion\non the two target families (120 environments)', loc='left', color=INK, fontsize=9.5)
    fig.savefig(CONF / 'figures/risk_loss_frontier.png', dpi=160, bbox_inches='tight'); plt.close(fig)


if __name__ == '__main__':
    forest(); frontier(); print('figures written')
