"""Run one split of the v2 deployment-stream benchmark.

    python benchmarks_v2/scripts/run_v2.py dev          # gate-hyperparameter grid
    python benchmarks_v2/scripts/run_v2.py validation   # frozen gate + all policies
    python benchmarks_v2/scripts/run_v2.py test         # held-out i.i.d. family
    python benchmarks_v2/scripts/run_v2.py shift        # held-out shifted family
    python benchmarks_v2/scripts/run_v2.py original     # v0.1 scenarios, diagnostic only

Seeds, sizes and the frozen gate live in benchmarks_v2/configs/. Each split
writes summary.csv (one row per environment x policy), episodes.npz (every
episode, git-ignored as raw), environments.json and run_metadata.json.
"""
from __future__ import annotations
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
import argparse, csv, datetime, json, os, platform, sys, time, zlib
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (ROOT, POLICIES, Stream, draw_environment, env_record, sha256)  # noqa: E402

CONF = ROOT / 'benchmarks_v2/configs'
RES = ROOT / 'benchmarks_v2/results'


def gate_grid(study):
    return [{'alpha': a, 'tolerance': t, 'margin': 0.} for a in study['dev_grid']['alpha']
            for t in study['dev_grid']['tolerance']]


def gate_name(g):
    return f"handoffx_v2[a={g['alpha']},tol={g['tolerance']}]"


def original_environment(name):
    from handoffx.scenarios import scenario_from_dict
    from handoffx.models import ModelSet
    s = scenario_from_dict(json.loads((ROOT / '05_Experiments/configs' / f'{name}.json').read_text()))
    models = s['models']
    return {'seed': None, 'name': name, 'family': 'original_v01', 'spec': s['spec'], 'models': models,
            'truth': s['truth'], 'bias_ai': s['ai_bias'], 'bias_human': s['human_bias'],
            'calibrated': s['ai_bias'] == 0 and s['human_bias'] == 0, 'in_support': None}


def job(args):
    env_key, split, policies, gates, T, cadence, frozen = args
    env = original_environment(env_key) if split == 'original' else draw_environment(env_key[0], env_key[1])
    stream_seed = (env['seed'] if env['seed'] is not None else zlib.crc32(env_key.encode()) % 10**6) * 7 + 1
    out = []
    runs = [(p, frozen) for p in policies] + [(gate_name(g), g) for g in gates]
    for name, gate in runs:
        policy = 'handoffx_v2' if name.startswith('handoffx_v2[') else name
        t0 = time.perf_counter()
        rows, meta = Stream(env, policy, T, cadence, stream_seed, gate).run()
        out.append((name, rows, meta, time.perf_counter() - t0))
    return env_key, env_record(env) | ({'name': env['name']} if 'name' in env else {}), out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('split', choices=('dev', 'validation', 'test', 'shift', 'original'))
    ap.add_argument('--workers', type=int, default=max(1, (os.cpu_count() or 2) - 1))
    ap.add_argument('--limit', type=int, default=None, help='smoke test: first N environments only')
    args = ap.parse_args()
    study = json.loads((CONF / 'study_v2.json').read_text())
    T, cadence = study['episodes_per_stream'], study['recalibration_cadence']
    frozen_path = CONF / 'frozen_gate.json'
    if args.split == 'dev':
        policies, gates, frozen = ['nominal', 'oracle'], gate_grid(study), None
    else:
        if not frozen_path.exists():
            raise SystemExit('frozen_gate.json missing: run and freeze the dev split first')
        frozen = json.loads(frozen_path.read_text())['gate']; policies, gates = list(POLICIES), []
    if args.split == 'original':
        keys = json.loads((ROOT / '05_Experiments/configs/study.json').read_text())['scenario_names']
    else:
        sp = study['splits'][args.split]
        keys = [(sp['seed_start'] + i, sp['family']) for i in range(sp['n_environments'])]
    if args.limit:
        keys = keys[:args.limit]
    out = RES / (args.split if not args.limit else f'{args.split}_smoke'); out.mkdir(parents=True, exist_ok=True)
    started = datetime.datetime.now(datetime.timezone.utc).isoformat(); tic = time.perf_counter()
    summary, envs, episodes = [], [], {}
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        for i, (key, rec, results) in enumerate(ex.map(job, [(k, args.split, policies, gates, T, cadence, frozen) for k in keys])):
            envs.append(rec); eid = rec.get('name') or rec['seed']
            for name, rows, meta, secs in results:
                el = np.array([r['exact_loss'] for r in rows]); rl = np.array([r['realized_loss'] for r in rows])
                summary.append({'environment': eid, 'family': rec['family'], 'policy': name,
                                'bias_ai': rec['bias_ai'], 'bias_human': rec['bias_human'],
                                'calibrated': rec['calibrated'], 'in_support': rec['in_support'],
                                'mean_exact_loss': float(el.mean()), 'first20_exact_loss': float(el[:20].mean()),
                                'last20_exact_loss': float(el[-20:].mean()),
                                'mean_exact_severe': float(np.mean([r['exact_severe'] for r in rows])),
                                'mean_exact_success': float(np.mean([r['exact_success'] for r in rows])),
                                'mean_exact_human': float(np.mean([r['exact_human'] for r in rows])),
                                'mean_realized_loss': float(rl.mean()),
                                'realized_severe_rate': float(np.mean([r['realized_severe'] for r in rows])),
                                'realized_human_rate': float(np.mean([r['realized_human'] for r in rows])),
                                'realized_success_rate': float(np.mean([r['realized_success'] for r in rows])),
                                'seconds': secs, **meta})
                episodes[f'{eid}__{name}__exact'] = el.astype(np.float64)
                episodes[f'{eid}__{name}__realized'] = rl.astype(np.float64)
            print(f'{i+1:03d}/{len(keys)} env {eid} done', flush=True)
    with (out / 'summary.csv').open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(summary[0])); w.writeheader(); w.writerows(summary)
    (out / 'raw').mkdir(exist_ok=True)
    np.savez_compressed(out / 'raw' / 'episodes.npz', **episodes)
    (out / 'environments.json').write_text(json.dumps(envs, indent=1) + '\n')
    hashes = {str(p.relative_to(ROOT)).replace('\\', '/'): sha256(p) for p in
              sorted([*(ROOT / 'benchmarks_v2/scripts').glob('*.py'), *CONF.glob('*.json'),
                      *(ROOT / '04_Python_Library/src/handoffx').glob('*.py')])}
    import numpy, scipy  # noqa: E401
    meta = {'split': args.split, 'started_utc': started, 'wall_seconds': time.perf_counter() - tic,
            'environments': len(keys), 'episodes_per_stream': T, 'recalibration_cadence': cadence,
            'policies': policies + [gate_name(g) for g in gates], 'frozen_gate': frozen,
            'python': sys.version, 'platform': platform.platform(), 'processor': platform.processor(),
            'logical_cpus': os.cpu_count(), 'workers': args.workers, 'numpy': numpy.__version__,
            'scipy': scipy.__version__, 'sha256': hashes}
    (out / 'run_metadata.json').write_text(json.dumps(meta, indent=2) + '\n')
    print('COMPLETE', args.split, f"{meta['wall_seconds']:.1f}s")


if __name__ == '__main__':
    main()
