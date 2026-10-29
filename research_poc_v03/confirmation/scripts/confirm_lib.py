"""Independent confirmation of candidate A: environments, streams and exact breakdowns.

Reuses the frozen v0.3 PoC components unchanged:
- `poc_lib.prevalence_augmented` (candidate A's model set: LEVELS, LEVEL_PRIOR),
- the v0.2 environment draw (`benchmarks_v2/scripts/common.py::draw_environment`)
  for task specifications and supplied estimates,
- the v0.2 library (`Planner`, `EpisodeBelief`, `AdaptiveController`, `run_episode`).

`run_stream` mirrors `poc_lib.run_stream` for the policies used here and adds
outcome breakdowns; `check_equivalence` verifies bit-identical losses against
`poc_lib.run_stream`. Policies see only the supplied model set and logged
trajectories; `env['truth']` is used by the simulator and the exact evaluator only.
"""
from __future__ import annotations
from pathlib import Path
import sys
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / 'scripts'))
from poc_lib import (draw_environment, Planner, ModelSet, ActionGuard, State, Action, kernels, BASE_D,  # noqa: E402
                     ExactEvaluator, AdaptiveController, EpisodeBelief, bayes_factory, run_episode,
                     prevalence_augmented, FROZEN_V2_GATE, _p_q)
import poc_lib  # noqa: E402

KINDS = ('persist_shift', 'human_shift', 'hazard_shift', 'calibrated', 'near_nominal', 'ai_bias', 'joint_bias')
PRIMARY = ('persist_shift', 'human_shift')
SUBTYPES = {'persist_shift': ('prevalence', 'dependence', 'both'),
            'human_shift': ('uniform', 'mode_flat', 'persistent_only')}


# ------------------------------------------------------------------ environments
def _sign_mag(rng, lo, hi):
    return float(rng.choice([-1, 1]) * rng.uniform(lo, hi))


def confirm_environment(seed: int, kind: str) -> dict:
    """Task spec and supplied estimate from the v0.2 i.i.d. draw; hidden truth set per kind."""
    env = draw_environment(seed, 'iid'); env['kind'] = kind; env['subtype'] = ''
    rng = np.random.Generator(np.random.PCG64(seed + 31))
    c = env['models'].one_model(env['models'].center)
    p, q = _p_q(c.kernels[0]); z = c.prior[0].copy()          # supplied estimate (p[a, mode], q[a, mode], prevalence)
    p0 = p.copy(); par = {}
    if kind == 'near_nominal':
        p[:2] += rng.uniform(-.03, .03); p[2] += rng.uniform(-.03, .03); z = rng.dirichlet(200 * z + 1e-9)
    elif kind == 'ai_bias':
        par['b_ai'] = _sign_mag(rng, .10, .25); p[:2] += par['b_ai']
    elif kind == 'joint_bias':
        par['b_ai'] = _sign_mag(rng, .10, .25); par['b_h'] = _sign_mag(rng, .10, .25)
        p[:2] += par['b_ai']; p[2] += par['b_h']
    elif kind == 'persist_shift':
        # Family A: how common persistent faults are (prevalence) and/or how persistent
        # they are (AI success inside the non-transient modes); human and hazards unchanged.
        sub = SUBTYPES[kind][int(rng.integers(3))]; env['subtype'] = sub
        if sub in ('prevalence', 'both'):
            s = rng.uniform(.10, .40); vertex = np.eye(3)[2 if rng.random() < .5 else 0]
            z = rng.dirichlet(50 * ((1 - s) * z + s * vertex) + 1e-9); par['prev_shift'] = float(s)
        if sub in ('dependence', 'both'):
            r = float(np.exp(rng.uniform(np.log(.4), np.log(1.6)))); p[:2, 1:] *= r; par['dependence_scale'] = r
    elif kind == 'human_shift':
        # Family B: human effectiveness changes; prevalence exact; AI nearly exact.
        sub = SUBTYPES[kind][int(rng.integers(3))]; env['subtype'] = sub
        b = _sign_mag(rng, .10, .30); par['b_h'] = b; p[:2] += rng.uniform(-.02, .02)
        if sub == 'uniform':
            p[2] += b
        elif sub == 'mode_flat':                      # human success no longer depends on the fault mode
            p[2] = float(p0[2] @ z) + b
        else:                                         # only the persistent-fault mode changes
            p[2, 2] += b
    elif kind == 'hazard_shift':
        par['hazard_scale'] = float(np.exp(rng.uniform(np.log(1.3), np.log(2.5)))); q = q * par['hazard_scale']
    elif kind != 'calibrated':
        raise ValueError(kind)
    q = np.minimum(q, .9)
    env['truth'] = ModelSet(kernels(p, q, BASE_D)[None], z[None], ('true',), 'synthetic')
    env['params'] = par
    env['true_prevalence'] = z
    return env


def true_prevalence_models(env: dict) -> ModelSet:
    """Diagnostic only (privileged): the supplied grid with its mode prior replaced by the true prevalence."""
    m = env['models']; w = m.prior.sum(axis=1)
    return ModelSet(m.kernels, w[:, None] * env['true_prevalence'][None], m.names, m.evidence_status, m.center)


# ------------------------------------------------------------------ exact breakdown
def severe_breakdown(spec, truth, policy, oracle) -> dict:
    """Exact probabilities: severe by action, severe at states where the oracle acts differently,
    and stopping where the oracle would not stop."""
    memo = {}

    def f(state):
        if state in memo:
            return memo[state]
        out = np.zeros(6)          # sev_continue, sev_retry, sev_human, sev_off_oracle, stop_off_oracle, human_off_oracle
        if spec.terminal_loss(state) is None:
            a = policy.action(state); oa = oracle.action(state)
            if a == Action.STOP:
                out[4] = float(oa != Action.STOP)
            else:
                pr = truth.predict(state)[int(a)]
                out[int(a)] += pr[1]
                if a != oa:
                    out[3] += pr[1]
                if a == Action.HUMAN:
                    out[5] = float(oa != Action.HUMAN)
                else:
                    for o in (0, 2, 3):
                        if pr[o] > 0:
                            out += pr[o] * f(state.next(a, o))
        memo[state] = out
        return out
    v = f(State())
    return dict(zip(('sev_continue', 'sev_retry', 'sev_human', 'sev_off_oracle', 'stop_off_oracle', 'human_off_oracle'), map(float, v)))


# ------------------------------------------------------------------ stream
def run_stream(env: dict, policy: str, T: int = 100, cadence: int = 5, seed: int = 0,
               prev: bool = False, learn: bool = True, models_override: ModelSet | None = None):
    """policy in {'nominal','oracle','bayes_recal','handoffx_v2','candidate'}; 'candidate' = A flags only."""
    spec, base, truth = env['spec'], env['models'], env['truth']
    shared_guard = ActionGuard(spec, base)
    r = np.random.Generator(np.random.PCG64(seed))
    latent = r.random(T); outcomes = r.random((T, spec.horizon + 1))
    learn_base = models_override if models_override is not None else base
    models = prevalence_augmented(learn_base) if prev else learn_base
    nominal = Planner(spec, base.one_model(base.center), 'bayes', shared_guard, 'nominal')
    oracle = Planner(spec, truth, 'bayes', shared_guard, 'oracle')
    belief = EpisodeBelief(models)
    controller = None
    if policy == 'handoffx_v2':
        controller = AdaptiveController(spec, base, nominal, {'bayes_posterior': bayes_factory(spec, shared_guard)}, **FROZEN_V2_GATE)
        belief = controller.belief
    cache: dict[int, tuple] = {}
    rows = []; current = None
    for t in range(T):
        refresh = t % cadence == 0
        if policy == 'nominal':
            current = nominal
        elif policy == 'oracle':
            current = oracle
        elif policy in ('bayes_recal', 'candidate') and refresh:
            current = Planner(spec, belief.posterior_models(), 'bayes', shared_guard, policy)
        elif policy == 'handoffx_v2' and refresh:
            current, _ = controller.select()
        key = id(current)
        if key not in cache:
            ex = ExactEvaluator(spec, truth, current, oracle=oracle).as_dict()
            cache[key] = (current, ex, severe_breakdown(spec, truth, current, oracle))
        _, ex, br = cache[key]
        traj, loss, info = run_episode(spec, truth, current, latent[t], outcomes[t])
        if policy in ('bayes_recal', 'handoffx_v2') or (policy == 'candidate' and learn):
            belief.update(traj)
        rows.append({'exact_loss': ex['loss'], 'exact_severe': ex['severe'], 'exact_success': ex['success'],
                     'exact_human': ex['human'], 'exact_stop': ex['stop'], 'exact_retries': ex['retries'],
                     'exact_excess_handoff': ex['excess_handoff'], 'exact_decision_regret': ex['decision_regret'],
                     **br, 'realized_loss': loss, 'realized_severe': info['severe']})
    pm = belief.posterior_models() if policy not in ('nominal', 'oracle') else base.one_model(base.center)
    zt = env['true_prevalence']; zhat = pm.prior.sum(axis=0) / pm.prior.sum()
    zsup = base.prior.sum(axis=0) / base.prior.sum()
    pr, tr = pm.predict(State()), truth.predict(State())
    meta = {'prev_tv_error': float(abs(zhat - zt).sum() / 2), 'prev_tv_error_supplied': float(abs(zsup - zt).sum() / 2),
            'persistent_share_est': float(zhat[2]), 'persistent_share_true': float(zt[2]),
            'cal_err_ai': float(abs(pr[0, 0] - tr[0, 0])), 'cal_err_human': float(abs(pr[2, 0] - tr[2, 0])),
            'ai_root_bias_signed': float(pr[0, 0] - tr[0, 0]), 'human_root_bias_signed': float(pr[2, 0] - tr[2, 0])}
    return rows, meta


def check_equivalence(env: dict, seed: int) -> float:
    """Max |exact loss difference| between this runner and the frozen poc_lib runner (should be 0)."""
    worst = 0.
    for pol, kw in (('nominal', {}), ('bayes_recal', {}), ('handoffx_v2', {}), ('candidate', {'prev': True})):
        a, _ = run_stream(env, pol, seed=seed, **kw)
        b, _ = poc_lib.run_stream(env, pol, seed=seed, **kw)
        worst = max(worst, max(abs(x['exact_loss'] - y['exact_loss']) for x, y in zip(a, b)))
    return worst
