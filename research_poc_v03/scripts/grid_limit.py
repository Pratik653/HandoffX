"""Stage C evidence (dev environments only): asymptotic limit of grid learning.

best_grid = loss of the best single model in the v0.2 5x5 grid when used as a nominal plan
(the most a perfectly converged plug-in learner could achieve); best_fine = same for a 9x9 grid.
"""
from pathlib import Path
import json, sys
import numpy as np
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'benchmarks_v2/scripts'))
import common  # noqa: E402
from common import draw_environment, Planner  # noqa: E402
from handoffx.evaluation import ExactEvaluator  # noqa: E402

res = []
for i in range(30):
    e = draw_environment(100000 + i); s, t = e['spec'], e['truth']
    L = lambda ms: ExactEvaluator(s, t, Planner(s, ms, 'bayes')).as_dict()['loss']
    nom, orc = L(e['models'].one_model(e['models'].center)), L(t)
    g5 = min(L(e['models'].one_model(k)) for k in range(25))
    common.GRID = tuple(np.linspace(-.2, .2, 9)); common.GRID_PRIOR = np.ones(9) / 9
    e9 = draw_environment(100000 + i); g9 = min(L(e9['models'].one_model(k)) for k in range(81))
    common.GRID = (-.2, -.1, 0., .1, .2); common.GRID_PRIOR = np.array([.1, .2, .4, .2, .1])
    res.append((nom, orc, g5, g9, e['calibrated']))
r = np.array([x[:4] for x in res]); rel = (r - r[:, :1]) / r[:, :1]
print('mean rel vs nominal: oracle %.2f%%  best 5x5 grid model %.2f%%  best 9x9 grid model %.2f%%' % tuple(100 * rel[:, 1:].mean(0)))
json.dump({'n': len(res), 'oracle': rel[:, 1].mean(), 'best_grid_5x5': rel[:, 2].mean(), 'best_grid_9x9': rel[:, 3].mean()},
          open(ROOT / 'research_poc_v03/results/grid_limit.json', 'w'), indent=1)
