"""Forest plot: pooled relative loss vs bayes_recal by round, and A_prev per kind by round."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT = Path(__file__).resolve().parents[2]; RES = ROOT / 'research_poc_v03/results'
rounds = ('pilot', 'confirm', 'replicate')
A = {r: json.loads((RES / r / 'analysis.json').read_text())['policies'] for r in rounds}
fig, axes = plt.subplots(1, 2, figsize=(12, 5))
ax = axes[0]; y = 0; ticks = []
for p in ('handoffx_v2', 'A_prev', 'B_humants', 'C_bfguard', 'AC', 'ABC'):
    for i, r in enumerate(rounds):
        if p in A[r]:
            v = A[r][p]['vs_bayes_recal']; m, lo, hi = (100 * x for x in (v['pooled'], *v['pooled_ci95']))
            ax.errorbar(m, y, xerr=[[m - lo], [hi - m]], fmt='os^'[i], color=f'C{i}', capsize=3, label=r if p == 'A_prev' else None)
            ticks.append((y, f'{p} ({r})')); y += 1
    y += .6
ax.axvline(0, ls='--', lw=1); ax.axvline(-.5, ls=':', lw=1, color='gray')
ax.set_yticks([t[0] for t in ticks], [t[1] for t in ticks], fontsize=8); ax.invert_yaxis()
ax.set_xlabel('Relative loss vs ungated bayes_recal (%), pooled over kinds, 95% CI'); ax.legend(fontsize=8)
ax.set_title('Pooled effect by round (dotted: GO threshold -0.5%)', fontsize=10)
ax = axes[1]; kinds = list(A['confirm']['A_prev']['vs_bayes_recal']['per_kind'])
for i, r in enumerate(rounds):
    v = A[r]['A_prev']['vs_bayes_recal']
    ax.plot([100 * v['per_kind'][k] for k in kinds], range(len(kinds)), 'os^'[i], color=f'C{i}', label=r)
ax.axvline(0, ls='--', lw=1); ax.set_yticks(range(len(kinds)), kinds); ax.invert_yaxis()
ax.set_xlabel('A_prev relative loss vs bayes_recal (%), per kind'); ax.legend(fontsize=8)
ax.set_title('Candidate A by environment kind', fontsize=10)
fig.tight_layout(); fig.savefig(ROOT / 'research_poc_v03/figures/effects_by_round.png', dpi=150)
