"""Stage C evidence (dev environments): does bayes_recal regret plateau, and is the plateau caused by
prevalence mismatch? 400-episode streams; 'matched' replaces the true mode prevalence by the supplied one."""
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
import json, sys
import numpy as np
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'benchmarks_v2/scripts'))
from common import draw_environment, Stream, ModelSet  # noqa: E402


def job(seed):
    out = {}
    for variant in ('as_drawn', 'matched'):
        e = draw_environment(seed)
        if variant == 'matched':
            t = e['truth']; c = e['models'].one_model(e['models'].center)
            e['truth'] = ModelSet(t.kernels, c.prior, ('true',), 'synthetic')
        r = {p: np.array([x['exact_loss'] for x in Stream(e, p, 400, 5, seed * 7 + 1).run()[0]])
             for p in ('nominal', 'bayes_recal', 'oracle')}
        reg = r['bayes_recal'] - r['oracle']
        out[variant] = {'nominal_regret': float((r['nominal'] - r['oracle']).mean()),
                        'regret_by_100': [float(reg[k:k + 100].mean()) for k in range(0, 400, 100)]}
    return out


if __name__ == '__main__':
    with ProcessPoolExecutor(16) as ex:
        res = list(ex.map(job, range(100000, 100032)))
    summ = {v: {'nominal_regret': float(np.mean([r[v]['nominal_regret'] for r in res])),
                'bayes_recal_regret_by_100_episodes': np.mean([r[v]['regret_by_100'] for r in res], axis=0).tolist()} for v in ('as_drawn', 'matched')}
    (ROOT / 'research_poc_v03/results/learning_limit.json').write_text(json.dumps(summ, indent=1) + '\n', encoding='utf-8')
    print(json.dumps(summ, indent=1))
