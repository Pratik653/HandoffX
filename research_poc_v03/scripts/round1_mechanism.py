"""Round 1: sanity and mechanism checks for candidates A, B, C (seeds 450000+ and v0.2 dev seeds for reproduction)."""
from pathlib import Path
import json, sys
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from poc_lib import (ROOT, poc_environment, prevalence_augmented, run_stream, human_index, LEVELS, Planner, ModelSet,
                     ActionGuard, State, Action, EpisodeBelief, episode_log_likelihood, run_episode, draw_environment, NGRID)
sys.path.insert(0, str(ROOT / 'benchmarks_v2/scripts'))
from common import Stream  # noqa: E402

out = {}
# 1. The in-loop baselines reproduce the v0.2 runner exactly (same seeds, same uniforms).
dev = []
for seed in (100000, 100001, 100002):
    e = draw_environment(seed)
    for p in ('nominal', 'bayes_recal', 'ts_recal', 'handoffx_v2', 'oracle'):
        a = np.array([x['exact_loss'] for x in Stream(e, p, 40, 5, seed * 7 + 1, {'alpha': .35, 'tolerance': .03, 'margin': 0.}).run()[0]])
        b = np.array([x['exact_loss'] for x in run_stream(e, p, 40, 5, seed * 7 + 1)[0]])
        dev.append(float(abs(a - b).max()))
out['reproduces_v02_runner_max_abs_diff'] = max(dev)

# 2. Candidate A: prevalence level identifiable from AI attempts (data from the nominal policy).
ident = {}
for lam_true in LEVELS:
    e = poc_environment(450000, 'calibrated'); base = e['models']; aug = prevalence_augmented(base)
    li = aug.center - 1 + LEVELS.index(lam_true)  # same success offsets as the centre, chosen prevalence level
    truth = aug.one_model(li); spec = e['spec']
    pol = Planner(spec, base.one_model(base.center), 'bayes'); b = EpisodeBelief(aug); rng = np.random.default_rng(1)
    for _ in range(300):
        b.update(run_episode(spec, truth, pol, rng.random(), rng.random(spec.horizon + 1))[0])
    lev = b.weights.reshape(-1, 3).sum(axis=0)
    ident[f'{lam_true:+.2f}'] = [round(float(x), 3) for x in lev]
out['A_level_posterior_after_300_nominal_episodes'] = ident

# 3. Candidate B: a point-mass human posterior gives the same decisions as full posterior planning.
e = poc_environment(450001, 'human_bias'); spec, m = e['spec'], e['models']; b = EpisodeBelief(m)
b.log_weights = np.array([0. if human_index(i, False) == 3 else -60. for i in range(len(m.names))])
post = b.posterior_models(); idx = [i for i in range(len(m.names)) if human_index(i, False) == 3]
full = Planner(spec, post, 'bayes'); restricted = Planner(spec, ModelSet(post.kernels[idx], post.prior[idx] / post.prior[idx].sum(), tuple(m.names[i] for i in idx), 'synthetic', 0), 'bayes')
states = [State(), State().next(Action.CONTINUE, 3), State().next(Action.CONTINUE, 2).next(Action.RETRY, 3), State().next(Action.CONTINUE, 0)]
out['B_point_mass_equivalence'] = all(full.action(s) == restricted.action(s) and abs(full.value(s) - restricted.value(s)) < 1e-8 for s in states if spec.terminal_loss(s) is None)

# 4. Candidate C: Bayes factor against the centre model over a stream (bayes_recal data).
bf = {}
for kind, seed in (('calibrated', 450002), ('success_bias', 450003), ('prevalence_misspec', 450004)):
    e = poc_environment(seed, kind); m = e['models']; spec = e['spec']
    lw0 = np.log(m.prior.sum(1)); ll = np.zeros(len(m.names)); pol = Planner(spec, m.one_model(m.center), 'bayes'); rng = np.random.default_rng(2); trace = []
    for t in range(100):
        tr = run_episode(spec, e['truth'], pol, rng.random(), rng.random(spec.horizon + 1))[0]; ll += episode_log_likelihood(m, tr)
        trace.append(float(np.logaddexp.reduce(lw0 + ll) - ll[m.center]))
    bf[kind] = {'logBF_at_0_25_50_100': [0.0, round(trace[24], 2), round(trace[49], 2), round(trace[99], 2)], 'threshold': round(float(np.log(3)), 3)}
out['C_log_bayes_factor'] = bf

# 5. Candidate streams run and use no truth at decision time (structural: planners are built from supplied models and logged data only).
e = poc_environment(450005, 'success_bias')
for name, kw in (('A', dict(prev=True)), ('B', dict(humants=True)), ('C', dict(guard=True))):
    rows, meta = run_stream(e, 'candidate', 30, 5, 99, **kw)
    out[f'{name}_smoke_mean_loss_30ep'] = round(float(np.mean([r['exact_loss'] for r in rows])), 4)
(ROOT / 'research_poc_v03/results/round1_mechanism.json').write_text(json.dumps(out, indent=1) + '\n', encoding='utf-8')
print(json.dumps(out, indent=1))
