"""Round 2 pilot / Round 3 confirmation runner.

    python research_poc_v03/scripts/run_poc.py pilot      # 12 envs per kind, seeds 500000 + 1000k + i
    python research_poc_v03/scripts/run_poc.py confirm    # 50 envs per kind, seeds 600000 + 1000k + i, policies from configs/frozen_confirm.json
"""
from __future__ import annotations
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
import argparse, csv, json, os, platform, subprocess, sys, time
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from poc_lib import ROOT, KINDS, poc_environment, run_stream  # noqa: E402

CANDIDATES = {'A_prev': dict(prev=True), 'B_humants': dict(humants=True), 'C_bfguard': dict(guard=True),
              'AB': dict(prev=True, humants=True), 'AC': dict(prev=True, guard=True), 'BC': dict(humants=True, guard=True),
              'ABC': dict(prev=True, humants=True, guard=True),
              # post-pilot mechanism diagnostic (not eligible for GO): A's augmented prior without cross-episode learning
              'A_static_diag': dict(prev=True, learn=False)}
BASELINES = ('nominal', 'handoffx_v2', 'bayes_recal', 'ts_recal', 'oracle')
SPLITS = {'pilot': (500000, 12), 'confirm': (600000, 50), 'replicate': (700000, 50)}


def job(args):
    seed, kind, policies = args
    env = poc_environment(seed, kind); out = []
    for p in policies:
        t0 = time.perf_counter()
        rows, meta = (run_stream(env, 'candidate', seed=seed * 7 + 1, **CANDIDATES[p]) if p in CANDIDATES
                      else run_stream(env, p, seed=seed * 7 + 1))
        out.append((p, rows, meta, time.perf_counter() - t0))
    return seed, kind, out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('split', choices=SPLITS); ap.add_argument('--workers', type=int, default=16)
    a = ap.parse_args(); start, n = SPLITS[a.split]
    if a.split == 'pilot':
        policies = list(BASELINES) + ['A_prev', 'B_humants', 'C_bfguard']
    elif a.split == 'confirm':
        policies = list(BASELINES) + json.loads((ROOT / 'research_poc_v03/configs/frozen_confirm.json').read_text())['candidates']
    else:
        policies = ['nominal', 'handoffx_v2', 'bayes_recal', 'oracle', 'A_prev', 'AC', 'ABC']
    jobs = [(start + 1000 * k + i, kind, policies) for k, kind in enumerate(KINDS) for i in range(n)]
    out = ROOT / 'research_poc_v03/results' / a.split; (out / 'raw').mkdir(parents=True, exist_ok=True)
    tic = time.perf_counter(); summary = []; raw = {}
    with ProcessPoolExecutor(a.workers) as ex:
        for seed, kind, res in ex.map(job, jobs):
            for p, rows, meta, secs in res:
                el = np.array([r['exact_loss'] for r in rows])
                summary.append({'seed': seed, 'kind': kind, 'policy': p, 'mean_exact_loss': float(el.mean()),
                                'last20_exact_loss': float(el[-20:].mean()),
                                **{k: float(np.mean([r[k] for r in rows])) for k in ('exact_severe', 'exact_success', 'exact_human', 'exact_retries', 'realized_loss')},
                                **meta, 'seconds': secs})
                raw[f'{seed}__{p}'] = el
    with (out / 'summary.csv').open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(summary[0])); w.writeheader(); w.writerows(summary)
    np.savez_compressed(out / 'raw' / 'episodes.npz', **raw)
    rev = subprocess.run(['git', 'rev-parse', 'HEAD'], capture_output=True, text=True, cwd=ROOT).stdout.strip()
    meta = {'split': a.split, 'git_revision_at_run': rev, 'environments': len(jobs), 'policies': policies,
            'episodes_per_stream': 100, 'cadence': 5, 'wall_seconds': time.perf_counter() - tic, 'workers': a.workers,
            'python': sys.version, 'platform': platform.platform(), 'numpy': np.__version__}
    (out / 'run_metadata.json').write_text(json.dumps(meta, indent=2) + '\n', encoding='utf-8')
    print('COMPLETE', a.split, f"{meta['wall_seconds']:.1f}s")


if __name__ == '__main__':
    main()
