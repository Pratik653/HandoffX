"""Minimal v0.3 feasibility candidates on top of the unchanged v0.2 code.

Policies only ever see logged trajectories; `truth` is used by the simulator and
the exact evaluator alone.
"""
from __future__ import annotations
from pathlib import Path
import sys
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'benchmarks_v2/scripts'))
from common import draw_environment, Planner, ModelSet, ActionGuard, State, Action  # noqa: E402
from handoffx.scenarios import kernels, BASE_D  # noqa: E402
from handoffx.evaluation import ExactEvaluator  # noqa: E402
from handoffx.adaptive import AdaptiveController, EpisodeBelief, bayes_factory, episode_log_likelihood, run_episode  # noqa: E402

KINDS = ('calibrated', 'success_bias', 'prevalence_misspec', 'human_bias', 'mixed', 'shift')
LEVELS = (-.25, 0., .25)
LEVEL_PRIOR = np.array([.25, .5, .25])
NGRID = 5
FROZEN_V2_GATE = {'alpha': .35, 'tolerance': .03, 'margin': 0., 'relative': True}


# ------------------------------------------------------------------ environments
def _p_q(kernel):
    """Recover success p[a, z] and severe q[a, z] from a (modes, 3, 4) kernel."""
    return kernel[:, :, 0].T.copy(), kernel[:, :, 1].T.copy()


def poc_environment(seed: int, kind: str) -> dict:
    if kind == 'shift':
        env = draw_environment(seed, 'shift')
    else:
        env = draw_environment(seed, 'iid')
    env['kind'] = kind
    if kind in ('mixed', 'shift'):
        return env
    rng = np.random.Generator(np.random.PCG64(seed + 17))
    m = env['models']; c = m.one_model(m.center)
    p, q = _p_q(c.kernels[0]); z = c.prior[0].copy(); b_ai = b_h = 0.
    if kind == 'success_bias':
        b_ai, b_h = rng.uniform(-.2, .2, 2)
    elif kind == 'human_bias':
        b_h = rng.choice([-1, 1]) * rng.uniform(.1, .25); b_ai = rng.uniform(-.05, .05)
    elif kind == 'prevalence_misspec':
        s = rng.uniform(.1, .35); vertex = np.eye(3)[2 if rng.random() < .5 else 0]
        z = rng.dirichlet(30 * ((1 - s) * z + s * vertex) + 1e-9)
    p[:2] += b_ai; p[2] += b_h
    env['truth'] = ModelSet(kernels(p, q, BASE_D)[None], z[None], ('true',), 'synthetic')
    env['bias_ai'], env['bias_human'] = float(b_ai), float(b_h)
    env['calibrated'] = kind == 'calibrated'
    return env


# ------------------------------------------------------------------ candidate A
def prevalence_augmented(models: ModelSet) -> ModelSet:
    """Each base model x three prevalence levels along the transient-persistent line."""
    ks, pr, names = [], [], []
    for i in range(len(models.names)):
        w = models.prior[i].sum(); zc = models.prior[i] / w
        for lam, lp in zip(LEVELS, LEVEL_PRIOR):
            v = np.eye(3)[2 if lam > 0 else 0]
            z = (1 - abs(lam)) * zc + abs(lam) * v
            ks.append(models.kernels[i]); pr.append(w * lp * z); names.append(f'{models.names[i]};prev={lam:+.2f}')
    pr = np.array(pr); pr /= pr.sum()
    return ModelSet(np.array(ks), pr, tuple(names), models.evidence_status, models.center * 3 + 1)


def human_index(idx: int, augmented: bool) -> int:
    base = idx // 3 if augmented else idx
    return base % NGRID


# ------------------------------------------------------------------ stream
def run_stream(env: dict, policy: str, T: int = 100, cadence: int = 5, seed: int = 0,
               prev: bool = False, humants: bool = False, guard: bool = False, learn: bool = True):
    """policy in {'nominal','oracle','bayes_recal','ts_recal','handoffx_v2','candidate'};
    'candidate' combines the A/B/C flags on top of ungated posterior planning."""
    spec, base, truth = env['spec'], env['models'], env['truth']
    shared_guard = ActionGuard(spec, base)
    r = np.random.Generator(np.random.PCG64(seed))
    latent = r.random(T); outcomes = r.random((T, spec.horizon + 1))
    samp = np.random.Generator(np.random.PCG64(seed + 7919))
    models = prevalence_augmented(base) if prev else base
    nominal = Planner(spec, base.one_model(base.center), 'bayes', shared_guard, 'nominal')
    belief = EpisodeBelief(models)
    controller = None
    if policy == 'handoffx_v2':
        controller = AdaptiveController(spec, base, nominal, {'bayes_posterior': bayes_factory(spec, shared_guard)}, **FROZEN_V2_GATE)
        belief = controller.belief
    log_w0 = np.log(models.prior.sum(axis=1)); cum_ll = np.zeros(len(models.names))
    exact_cache: dict[int, dict] = {}
    rows = []; current = None; post = None; guarded = 0; planners = {}
    for t in range(T):
        refresh = t % cadence == 0
        if policy == 'nominal':
            current = nominal
        elif policy == 'oracle':
            current = current or Planner(spec, truth, 'bayes', shared_guard, 'oracle')
        elif policy == 'bayes_recal' and refresh:
            current = Planner(spec, belief.posterior_models(), 'bayes', shared_guard, 'bayes_recal')
        elif policy == 'ts_recal':
            m = belief.sample(samp)
            current = planners.setdefault(m, Planner(spec, models.one_model(m), 'bayes', shared_guard, 'ts'))
        elif policy == 'handoffx_v2' and refresh:
            current, _ = controller.select()
        elif policy == 'candidate':
            if refresh:
                planners = {}
                post = belief.posterior_models()
                lbf = float(np.logaddexp.reduce(log_w0 + cum_ll) - cum_ll[models.center]) if guard else np.inf
                use_nominal = lbf <= np.log(3.)
            if use_nominal:
                current = nominal; guarded += 1
            elif humants:
                hw = np.zeros(NGRID)
                for i, w in enumerate(belief.weights):
                    hw[human_index(i, prev)] += w
                h = int(samp.choice(NGRID, p=hw / hw.sum()))
                if h not in planners:
                    idx = [i for i in range(len(models.names)) if human_index(i, prev) == h]
                    pr = post.prior[idx]; pr = pr / pr.sum()
                    planners[h] = Planner(spec, ModelSet(post.kernels[idx], pr, tuple(models.names[i] for i in idx), 'synthetic', 0),
                                          'bayes', shared_guard, f'humants{h}')
                current = planners[h]
            elif refresh:
                current = Planner(spec, post, 'bayes', shared_guard, 'candidate')
        key = id(current)
        if key not in exact_cache:
            exact_cache[key] = (current, ExactEvaluator(spec, truth, current).as_dict())
        ex = exact_cache[key][1]
        traj, loss, info = run_episode(spec, truth, current, latent[t], outcomes[t])
        if policy in ('bayes_recal', 'ts_recal', 'handoffx_v2') or (policy == 'candidate' and learn):
            belief.update(traj)
            cum_ll += episode_log_likelihood(models, traj)
        rows.append({'exact_loss': ex['loss'], 'exact_severe': ex['severe'], 'exact_success': ex['success'],
                     'exact_human': ex['human'], 'exact_retries': ex['retries'], 'realized_loss': loss,
                     'realized_human': info['human']})
    # predictive diagnostics at stream end
    pm = belief.posterior_models() if policy not in ('nominal', 'oracle') else base.one_model(base.center)
    zt = truth.prior[0] if truth.prior.shape[0] == 1 else truth.prior.sum(axis=0) / truth.prior.sum()
    zhat = (pm.prior.sum(axis=0) / pm.prior.sum())
    pr, tr = pm.predict(State()), truth.predict(State())
    meta = {'prev_tv_error': float(abs(zhat - zt).sum() / 2), 'cal_err_ai': float(abs(pr[0, 0] - tr[0, 0])),
            'cal_err_human': float(abs(pr[2, 0] - tr[2, 0])), 'human_observations': int(belief.action_counts[2]),
            'guarded_episodes': guarded}
    return rows, meta
