"""Run the pre-registered confirmation (PRE_REGISTERED_PROTOCOL.md) once.

    python research_poc_v03/confirmation/scripts/run_confirmation.py smoke      # 2 envs per kind, seeds 990000+; checks only
    python research_poc_v03/confirmation/scripts/run_confirmation.py confirm    # frozen design, seeds 800000 + 1000k + i
"""
from __future__ import annotations
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
import argparse, csv, hashlib, json, platform, subprocess, sys, time
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from confirm_lib import KINDS, confirm_environment, run_stream, true_prevalence_models, check_equivalence  # noqa: E402

CONF = Path(__file__).resolve().parents[1]
CFG = json.loads((CONF / 'configs/confirmation.json').read_text(encoding='utf-8'))
POLICIES = {'nominal': dict(policy='nominal'), 'handoffx_v2': dict(policy='handoffx_v2'),
            'bayes_recal': dict(policy='bayes_recal'), 'oracle': dict(policy='oracle'),
            'A_prev': dict(policy='candidate', prev=True),
            # mechanism diagnostics, not decision-eligible
            'A_static_diag': dict(policy='candidate', prev=True, learn=False),
            'recal_trueprev_diag': dict(policy='bayes_recal', trueprev=True)}


def job(args):
    seed, kind = args
    env = confirm_environment(seed, kind); out = []
    for name, kw in POLICIES.items():
        kw = dict(kw); trueprev = kw.pop('trueprev', False)
        t0 = time.perf_counter()
        rows, meta = run_stream(env, seed=seed * 7 + 1, T=CFG['episodes_per_stream'], cadence=CFG['cadence'],
                                models_override=true_prevalence_models(env) if trueprev else None, **kw)
        out.append((name, rows, meta, time.perf_counter() - t0))
    return seed, kind, env['subtype'], env['params'], out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('split', choices=('smoke', 'confirm')); ap.add_argument('--workers', type=int, default=16)
    a = ap.parse_args()
    if a.split == 'smoke':
        jobs = [(990000 + 1000 * k + i, kind) for k, kind in enumerate(KINDS) for i in range(2)]
        env = confirm_environment(jobs[0][0], KINDS[0])
        print('equivalence vs frozen poc_lib runner, max |diff| =', check_equivalence(env, jobs[0][0] * 7 + 1))
    else:
        jobs = [(CFG['seed_base'] + 1000 * k + i, kind) for k, kind in enumerate(KINDS) for i in range(CFG['n_per_kind'][kind])]
    out = CONF / 'results' / a.split; (out / 'raw').mkdir(parents=True, exist_ok=True)
    tic = time.perf_counter(); summary = []; raw = {}
    with ProcessPoolExecutor(a.workers) as ex:
        for seed, kind, sub, par, res in ex.map(job, jobs):
            for p, rows, meta, secs in res:
                el = np.array([r['exact_loss'] for r in rows])
                rec = {'seed': seed, 'kind': kind, 'subtype': sub, 'policy': p,
                       'cum_exact_loss': float(el.sum()), 'mean_exact_loss': float(el.mean()),
                       **{k: float(np.mean([r[k] for r in rows])) for k in rows[0] if k != 'exact_loss'},
                       'last20_exact_severe': float(np.mean([r['exact_severe'] for r in rows[-20:]])),
                       **meta, 'seconds': secs, 'params': json.dumps(par)}
                summary.append(rec); raw[f'{seed}__{p}'] = np.array([[r['exact_loss'], r['exact_severe']] for r in rows])
    with (out / 'summary.csv').open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(summary[0])); w.writeheader(); w.writerows(summary)
    np.savez_compressed(out / 'raw' / 'episodes.npz', **raw)
    rev = subprocess.run(['git', 'rev-parse', 'HEAD'], capture_output=True, text=True, cwd=CONF).stdout.strip()
    hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((CONF / 'scripts').glob('*.py'))}
    meta = {'split': a.split, 'git_revision_at_run': rev, 'environments': len(jobs), 'policies': list(POLICIES),
            'config': CFG, 'script_sha256': hashes, 'wall_seconds': time.perf_counter() - tic, 'workers': a.workers,
            'python': sys.version, 'platform': platform.platform(), 'numpy': np.__version__}
    (out / 'run_metadata.json').write_text(json.dumps(meta, indent=2) + '\n', encoding='utf-8')
    print('COMPLETE', a.split, f"{meta['wall_seconds']:.1f}s")


if __name__ == '__main__':
    main()
