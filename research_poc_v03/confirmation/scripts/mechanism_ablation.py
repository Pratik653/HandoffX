"""EXPLORATORY (post hoc) mechanism ablations, on fresh seeds 850000 + 1000k + i.

Written after the confirmation results were seen; it plays no role in the decision.
Questions:
1. Is A's severe reduction a *prior mean* effect? A's 3-level prior raises the expected
   persistent-fault share from z2 to 0.875 z2 + 0.0625 (prior mean of the augmented set).
   `pess_prior_recal` = bayes_recal on the 25 supplied models whose mode prior is fixed at
   that mean (no prevalence flexibility).
2. Does A beat plain cost-based risk aversion? `riskcost_c` = bayes_recal that plans with
   catastrophe_loss x c (evaluation always uses the true costs).
"""
from __future__ import annotations
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace
from pathlib import Path
import csv, json, sys, time
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from confirm_lib import (KINDS, confirm_environment, run_stream, severe_breakdown, ModelSet, Planner, ActionGuard,  # noqa: E402
                         ExactEvaluator, EpisodeBelief, run_episode)
from poc_lib import LEVELS, LEVEL_PRIOR  # noqa: E402


CONF = Path(__file__).resolve().parents[1]
N = {'persist_shift': 60, 'human_shift': 60, 'hazard_shift': 20, 'calibrated': 20, 'near_nominal': 20, 'ai_bias': 20, 'joint_bias': 20}
COSTS = (1.25, 1.5, 2., 3.)


def a_prior_mean_models(models: ModelSet) -> ModelSet:
    """Supplied grid with each model's mode prior replaced by A's prior-mean prevalence."""
    w = models.prior.sum(axis=1); z = models.prior / w[:, None]
    zbar = np.zeros_like(z)
    for lam, lp in zip(LEVELS, LEVEL_PRIOR):
        v = np.eye(3)[2 if lam > 0 else 0]; zbar += lp * ((1 - abs(lam)) * z + abs(lam) * v)
    return ModelSet(models.kernels, w[:, None] * zbar, models.names, models.evidence_status, models.center)


def recal_stream(env, seed, plan_spec, T=100, cadence=5):
    """bayes_recal path of confirm_lib.run_stream, planning with `plan_spec`."""
    spec, base, truth = env['spec'], env['models'], env['truth']
    guard = ActionGuard(spec, base); plan_guard = ActionGuard(plan_spec, base); r = np.random.Generator(np.random.PCG64(seed))
    latent = r.random(T); outcomes = r.random((T, spec.horizon + 1))
    oracle = Planner(spec, truth, 'bayes', guard, 'oracle'); belief = EpisodeBelief(base)
    rows = []; current = None; cache = {}
    for t in range(T):
        if t % cadence == 0:
            current = Planner(plan_spec, belief.posterior_models(), 'bayes', plan_guard, 'riskcost')
        if id(current) not in cache:
            cache[id(current)] = (current, ExactEvaluator(spec, truth, current, oracle=oracle).as_dict(), severe_breakdown(spec, truth, current, oracle))
        _, ex, br = cache[id(current)]
        traj, loss, info = run_episode(spec, truth, current, latent[t], outcomes[t]); belief.update(traj)
        rows.append({'exact_loss': ex['loss'], 'exact_severe': ex['severe'], 'exact_success': ex['success'],
                     'exact_human': ex['human'], 'exact_stop': ex['stop'], 'exact_retries': ex['retries'], **br})
    return rows


def job(args):
    seed, kind = args; env = confirm_environment(seed, kind); s = seed * 7 + 1; out = {}
    out['nominal'] = run_stream(env, 'nominal', seed=s)[0]
    out['oracle'] = run_stream(env, 'oracle', seed=s)[0]
    out['bayes_recal'] = run_stream(env, 'bayes_recal', seed=s)[0]
    out['A_prev'] = run_stream(env, 'candidate', seed=s, prev=True)[0]
    out['pess_prior_recal'] = run_stream(env, 'bayes_recal', seed=s, models_override=a_prior_mean_models(env['models']))[0]
    chk = recal_stream(env, s, env['spec'])
    eq = max(abs(a['exact_loss'] - b['exact_loss']) for a, b in zip(chk, out['bayes_recal']))
    for c in COSTS:
        out[f'riskcost_{c:g}'] = recal_stream(env, s, replace(env['spec'], catastrophe_loss=env['spec'].catastrophe_loss * c))
    return seed, kind, env['subtype'], eq, {p: {k: float(np.mean([r[k] for r in rows])) for k in rows[0]} | {'cum_exact_loss': float(sum(r['exact_loss'] for r in rows))}
                                            for p, rows in out.items()}


def main():
    jobs = [(850000 + 1000 * k + i, kind) for k, kind in enumerate(KINDS) for i in range(N[kind])]
    tic = time.perf_counter(); recs = []; worst = 0.
    with ProcessPoolExecutor(16) as ex:
        for seed, kind, sub, eq, res in ex.map(job, jobs):
            worst = max(worst, eq)
            for p, m in res.items():
                recs.append({'seed': seed, 'kind': kind, 'subtype': sub, 'policy': p, **m})
    out = CONF / 'results/exploratory_mechanism'; out.mkdir(parents=True, exist_ok=True)
    with (out / 'summary.csv').open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(recs[0])); w.writeheader(); w.writerows(recs)
    # paired summaries vs bayes_recal: target (persist+human, equal weight) and per kind
    by = {(r['seed'], r['policy']): r for r in recs}; pols = list(dict.fromkeys(r['policy'] for r in recs))
    rng = np.random.default_rng(17); groups = {k: [s for s, kk in jobs if kk == k] for k in KINDS}
    idx = {k: rng.integers(0, len(v), (10000, len(v))) for k, v in groups.items()}

    def stat(p, ks, ref='bayes_recal'):
        def m(pol, key):
            pt, rs = [], 0
            for k in ks:
                v = np.array([by[(s, pol)][key] for s in groups[k]]); pt.append(v.mean()); rs = rs + v[idx[k]].mean(1)
            return np.mean(pt), rs / len(ks)
        (sa, ra), (sr, rr) = m(p, 'exact_severe'), m(ref, 'exact_severe')
        (la, qa), (lr, qr) = m(p, 'cum_exact_loss'), m(ref, 'cum_exact_loss')
        d = {}
        for key in ('exact_success', 'exact_stop', 'exact_human', 'exact_retries'):
            d[f'd_{key}'] = float(m(p, key)[0] - m(ref, key)[0])
        return {'RRR': float(1 - sa / sr), 'RRR_ci95': [float(np.quantile(1 - ra / rr, q)) for q in (.025, .975)],
                'loss_ratio_minus_1': float(la / lr - 1), 'loss_ratio_ci95': [float(np.quantile(qa / qr - 1, q)) for q in (.025, .975)], **d}
    res = {'note': 'EXPLORATORY post hoc; seeds 850000+; not part of the confirmatory decision',
           'n_per_kind': N, 'equivalence_recal_stream_vs_confirm_lib': worst, 'wall_seconds': time.perf_counter() - tic,
           'TARGET': {p: stat(p, ('persist_shift', 'human_shift')) for p in pols},
           'A_vs_controls_TARGET': {c: stat('A_prev', ('persist_shift', 'human_shift'), c) for c in ('pess_prior_recal', 'riskcost_1.25', 'riskcost_1.5')},
           'per_kind': {k: {p: stat(p, (k,)) for p in pols} for k in KINDS}}
    (out / 'analysis.json').write_text(json.dumps(res, indent=1) + '\n', encoding='utf-8')
    for p, v in res['TARGET'].items():
        print(f"{p:18s} RRR {100*v['RRR']:+6.1f}% [{100*v['RRR_ci95'][0]:+.1f},{100*v['RRR_ci95'][1]:+.1f}]  loss {100*v['loss_ratio_minus_1']:+.2f}% "
              f"[{100*v['loss_ratio_ci95'][0]:+.2f},{100*v['loss_ratio_ci95'][1]:+.2f}]  dSucc {v['d_exact_success']:+.3f} dStop {v['d_exact_stop']:+.3f} dHum {v['d_exact_human']:+.3f} dRetry {v['d_exact_retries']:+.3f}")
    for c, v in res['A_vs_controls_TARGET'].items():
        print(f"A vs {c:16s} severe {-100*v['RRR']:+.1f}% [{-100*v['RRR_ci95'][1]:+.1f},{-100*v['RRR_ci95'][0]:+.1f}] loss {100*v['loss_ratio_minus_1']:+.2f}% [{100*v['loss_ratio_ci95'][0]:+.2f},{100*v['loss_ratio_ci95'][1]:+.2f}] dSucc {v['d_exact_success']:+.3f}")
    print('equivalence', worst, 'secs', res['wall_seconds'])


if __name__ == '__main__':
    main()
