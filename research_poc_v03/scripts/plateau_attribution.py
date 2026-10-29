"""Stage C evidence (dev): attribute the bayes_recal plateau (episodes 201-400, prevalence matched)
to environments by human-bias sign and number of human observations."""
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
import json, sys
import numpy as np
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'benchmarks_v2/scripts'))
from common import draw_environment, Stream, ModelSet  # noqa: E402


def job(seed):
    e = draw_environment(seed); t = e['truth']; c = e['models'].one_model(e['models'].center)
    e['truth'] = ModelSet(t.kernels, c.prior, ('true',), 'synthetic')
    rb, mb = Stream(e, 'bayes_recal', 400, 5, seed * 7 + 1).run()
    ro, _ = Stream(e, 'oracle', 400, 5, seed * 7 + 1).run()
    reg = np.array([a['exact_loss'] - b['exact_loss'] for a, b in zip(rb, ro)])[200:].mean()
    return {'seed': seed, 'bias_ai': e['bias_ai'], 'bias_human': e['bias_human'], 'plateau_regret': float(reg),
            'human_obs': mb['human_observations'], 'oracle_human_rate': float(np.mean([b['exact_human'] for b in ro])),
            'learner_human_rate_late': float(np.mean([a['exact_human'] for a in rb[200:]]))}


if __name__ == '__main__':
    with ProcessPoolExecutor(16) as ex:
        res = list(ex.map(job, range(100000, 100032)))
    tot = sum(r['plateau_regret'] for r in res)
    under = [r for r in res if r['learner_human_rate_late'] < r['oracle_human_rate'] - .05]
    over = [r for r in res if r['learner_human_rate_late'] > r['oracle_human_rate'] + .05]
    s = {'total_plateau_regret': tot,
         'share_in_under_escalating_envs': sum(r['plateau_regret'] for r in under) / tot, 'n_under': len(under),
         'share_in_over_escalating_envs': sum(r['plateau_regret'] for r in over) / tot, 'n_over': len(over),
         'under_escalating_mean_human_obs': float(np.mean([r['human_obs'] for r in under])) if under else None}
    (ROOT / 'research_poc_v03/results/plateau_attribution.json').write_text(json.dumps({'summary': s, 'rows': res}, indent=1) + '\n', encoding='utf-8')
    print(json.dumps(s, indent=1))
    for r in sorted(res, key=lambda r: -r['plateau_regret'])[:6]:
        print({k: (round(v, 3) if isinstance(v, float) else v) for k, v in r.items()})
