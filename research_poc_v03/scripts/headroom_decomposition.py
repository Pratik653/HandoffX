"""Stage A/C evidence: decompose the nominal->oracle gap on v0.2 DEV environments only.

Planners with partial truth (diagnostic, not deployable):
  oracle_success:    true success/hazard kernels, supplied mode prevalence
  oracle_prevalence: supplied kernels, true mode prevalence
"""
from pathlib import Path
import json, sys
import numpy as np
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'benchmarks_v2/scripts'))
from common import draw_environment, Planner, ModelSet  # noqa: E402
from handoffx.evaluation import ExactEvaluator  # noqa: E402

rows = []
for family, start in (('iid', 100000), ('shift', 100000)):
    for i in range(60):
        e = draw_environment(start + i, family); s, m, t = e['spec'], e['models'], e['truth']
        c = m.one_model(m.center); est_z = c.prior[0]; true_z = t.prior[0]
        L = lambda models: ExactEvaluator(s, t, Planner(s, models, 'bayes')).as_dict()['loss']
        nom, orc = L(c), L(t)
        os_ = L(ModelSet(t.kernels, est_z[None], ('x',), 'synthetic'))
        op = L(ModelSet(c.kernels, true_z[None], ('x',), 'synthetic'))
        rows.append(dict(family=family, seed=start + i, calibrated=e['calibrated'], nominal=nom, oracle=orc,
                         oracle_success=os_, oracle_prevalence=op, z_tv=float(abs(true_z - est_z).sum() / 2)))
out = {}
for fam in ('iid', 'shift'):
    for sub, f in (('all', lambda r: True), ('calibrated', lambda r: r['calibrated']), ('biased', lambda r: not r['calibrated'])):
        R = [r for r in rows if r['family'] == fam and f(r)]
        if not R: continue
        rel = lambda k: float(np.mean([(r[k] - r['nominal']) / r['nominal'] for r in R]))
        out[f'{fam}/{sub}'] = {'n': len(R), 'oracle': rel('oracle'), 'oracle_success_only': rel('oracle_success'),
                               'oracle_prevalence_only': rel('oracle_prevalence'),
                               'mean_prevalence_tv_distance': float(np.mean([r['z_tv'] for r in R]))}
(ROOT / 'research_poc_v03/results/headroom_decomposition.json').write_text(json.dumps({'summary': out, 'rows': rows}, indent=1) + '\n', encoding='utf-8')
for k, v in out.items():
    print(f"{k:16s} n={v['n']:3d} oracle {100*v['oracle']:+.2f}%  success-only {100*v['oracle_success_only']:+.2f}%  prevalence-only {100*v['oracle_prevalence_only']:+.2f}%  TV(z) {v['mean_prevalence_tv_distance']:.3f}")
