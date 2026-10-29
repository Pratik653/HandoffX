"""Shared v2 benchmark components: environment distribution and deployment streams.

An *environment* is a task specification, a supplied (possibly biased) estimate,
a finite model set built around that estimate, and a hidden true kernel. A
*stream* is a sequence of episodes in that environment; learning policies may
pool evidence across episodes, static policies may not. Every policy sees the
same supplied information and the same common random numbers.
"""
from __future__ import annotations
from dataclasses import replace, asdict
from pathlib import Path
import hashlib, json, sys, time
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / '04_Python_Library/src'))
from handoffx import Action, ModelSet, Planner, State, TaskSpec, ActionGuard  # noqa: E402
from handoffx.scenarios import BASE_P, BASE_Q, BASE_Z, BASE_D, kernels  # noqa: E402
from handoffx.evaluation import ExactEvaluator  # noqa: E402
from handoffx.adaptive import AdaptiveController, EpisodeBelief, bayes_factory, run_episode, model_losses  # noqa: E402

GRID = (-.2, -.1, 0., .1, .2)
GRID_PRIOR = np.array([.1, .2, .4, .2, .1])
CENTER = len(GRID) ** 2 // 2

# Distribution families. 'iid' is used for development, validation and the
# primary held-out test; 'shift' is a second held-out family whose biases may
# fall outside the model support and whose hazards/persistence are worse.
FAMILIES = {
    'iid': dict(bias=.2, p_calibrated=.25, hazard_shift=1., z_shift=0.),
    'shift': dict(bias=.3, p_calibrated=.10, hazard_shift=1.5, z_shift=.15),
}


def model_set(est_p, est_q, est_z, d):
    ks, names, prior = [], [], []
    for i, da in enumerate(GRID):
        for j, dh in enumerate(GRID):
            pp = est_p.copy(); pp[:2] += da; pp[2] += dh
            ks.append(kernels(pp, est_q, d)); names.append(f'ai={da:+.2f};human={dh:+.2f}')
            prior.append(GRID_PRIOR[i] * GRID_PRIOR[j] * est_z)
    prior = np.array(prior); prior /= prior.sum()
    return ModelSet(np.array(ks), prior, tuple(names), 'synthetic', CENTER)


def draw_environment(seed: int, family: str = 'iid') -> dict:
    f = FAMILIES[family]
    rng = np.random.Generator(np.random.PCG64(seed))
    est_p = np.clip(BASE_P + rng.uniform(-.04, .04, size=(3, 3)), .05, .97)
    est_q = BASE_Q * float(np.exp(rng.uniform(np.log(.2), np.log(1.5))))
    est_z = rng.dirichlet(20 * BASE_Z)
    calibrated = rng.random() < f['p_calibrated']
    b_ai, b_h = (0., 0.) if calibrated else tuple(rng.uniform(-f['bias'], f['bias'], 2))
    true_p = est_p.copy(); true_p[:2] += b_ai; true_p[2] += b_h
    true_q = est_q * f['hazard_shift']
    true_z = rng.dirichlet(30 * est_z)
    if f['z_shift']:
        true_z = (1 - f['z_shift']) * true_z + f['z_shift'] * np.array([0., 0., 1.])
    horizon = int(rng.choice([4, 5, 6]))
    human_cost = float(rng.uniform(1., 8.)); failure = float(rng.uniform(10., 30.))
    late = rng.random() < .2
    avail = tuple([not (late and t < 2) for t in range(horizon + 1)])
    spec = TaskSpec(horizon=horizon, milestones=2, budget=7, resource_cost=(1, 2, 3),
                    action_cost=(.6, float(rng.uniform(.8, 2.)), human_cost),
                    duration=(1, 1, int(rng.choice([1, 2, 3], p=[.3, .5, .2]))),
                    time_price=.15, failure_loss=failure,
                    stop_loss=float(rng.uniform(.4, .8)) * failure,
                    catastrophe_loss=float(rng.uniform(40., 180.)),
                    human_available=avail, human_budget=int(rng.random() > .1))
    models = model_set(est_p, est_q, est_z, BASE_D)
    truth = ModelSet(kernels(true_p, true_q, BASE_D)[None], true_z[None], ('true',), 'synthetic')
    return {'seed': seed, 'family': family, 'spec': spec, 'models': models, 'truth': truth,
            'bias_ai': float(b_ai), 'bias_human': float(b_h), 'calibrated': bool(calibrated),
            'in_support': bool(abs(b_ai) <= .2 and abs(b_h) <= .2)}


def env_record(env: dict) -> dict:
    return {'seed': env['seed'], 'family': env['family'], 'spec': asdict(env['spec']),
            'truth': env['truth'].to_dict(), 'models': env['models'].to_dict(),
            'bias_ai': env['bias_ai'], 'bias_human': env['bias_human'],
            'calibrated': env['calibrated'], 'in_support': env['in_support']}


POLICIES = ('nominal', 'bayes_static', 'robust_static', 'plugin_recal', 'bayes_recal',
            'ts_recal', 'handoffx_v2', 'gate_static', 'v2_iid', 'oracle')
LEARNING = ('plugin_recal', 'bayes_recal', 'ts_recal', 'handoffx_v2', 'v2_iid')


def calibration_error(belief_models, truth):
    """Mean absolute error of root success probabilities for continue and human."""
    pr, tr = belief_models.predict(State()), truth.predict(State())
    return float(abs(pr[0, 0] - tr[0, 0])), float(abs(pr[2, 0] - tr[2, 0]))


class Stream:
    """Runs one policy for ``episodes`` episodes with recalibration every ``cadence``."""

    def __init__(self, env, policy, episodes, cadence, rng_seed, gate=None):
        self.env = env; self.policy = policy; self.T = episodes; self.cadence = cadence
        self.gate = dict(gate or {'alpha': .1, 'tolerance': 0., 'margin': 0.})
        self.gate.setdefault('relative', True)
        self.rng_seed = rng_seed

    def run(self):
        env = self.env; spec, models, truth = env['spec'], env['models'], env['truth']
        if self.policy == 'v2_iid':
            models = models.iid_modes()
        guard = ActionGuard(spec, env['models'])
        r = np.random.Generator(np.random.PCG64(self.rng_seed))
        latent = r.random(self.T); outcomes = r.random((self.T, spec.horizon + 1))
        ts_rng = np.random.Generator(np.random.PCG64(self.rng_seed + 7919))
        nominal = Planner(spec, models.one_model(models.center), 'bayes', guard, 'nominal')
        belief = EpisodeBelief(models)
        exact_cache = {}

        def exact(key, pol):
            if key not in exact_cache:
                exact_cache[key] = ExactEvaluator(spec, truth, pol).as_dict()
            return exact_cache[key]

        controller = None
        if self.policy in ('handoffx_v2', 'gate_static', 'v2_iid'):
            controller = AdaptiveController(spec, models, nominal, {'bayes_posterior': bayes_factory(spec, guard)},
                                            **self.gate)
            belief = controller.belief
        ts_planners = {}
        cal0 = calibration_error(belief.posterior_models(), truth)
        current = None; key = None; switched = 0; rows = []
        for t in range(self.T):
            refresh = t % self.cadence == 0
            p = self.policy
            if p == 'nominal':
                current, key = nominal, 'nominal'
            elif p == 'bayes_static' and current is None:
                current, key = Planner(spec, models, 'bayes', guard, 'bayes_static'), 'bs'
            elif p == 'robust_static' and current is None:
                current, key = Planner(spec, models, 'robust', guard, 'robust_static'), 'rs'
            elif p == 'oracle' and current is None:
                current, key = Planner(spec, truth, 'bayes', guard, 'oracle'), 'or'
            elif p == 'plugin_recal' and refresh:
                m = int(np.argmax(belief.weights))
                current, key = Planner(spec, models.one_model(m), 'bayes', guard, 'plugin'), ('m', m)
            elif p == 'bayes_recal' and refresh:
                current, key = Planner(spec, belief.posterior_models(), 'bayes', guard, 'bayes_recal'), ('b', t)
            elif p == 'ts_recal':
                m = belief.sample(ts_rng)
                if m not in ts_planners:
                    ts_planners[m] = Planner(spec, models.one_model(m), 'bayes', guard, 'ts')
                current, key = ts_planners[m], ('m', m)
            elif (p in ('handoffx_v2', 'v2_iid') and refresh) or (p == 'gate_static' and current is None):
                current, sel = controller.select()
                key = ('n',) if sel.chosen == 'nominal' else ('g', t)
            if p in ('handoffx_v2', 'gate_static', 'v2_iid'):
                switched += key != ('n',)
            ex = exact(key if key != ('n',) else 'nominal', current)
            traj, loss, info = run_episode(spec, truth, current, latent[t], outcomes[t])
            if p in LEARNING:
                belief.update(traj)
            rows.append({'t': t, 'exact_loss': ex['loss'], 'exact_severe': ex['severe'],
                         'exact_success': ex['success'], 'exact_human': ex['human'],
                         'realized_loss': loss, **{f'realized_{k}': v for k, v in info.items()}})
        cal1 = calibration_error(belief.posterior_models(), truth)
        return rows, {'switched_episodes': switched,
                      'cal_err_ai_start': cal0[0], 'cal_err_human_start': cal0[1],
                      'cal_err_ai_end': cal1[0], 'cal_err_human_end': cal1[1],
                      'final_map': int(np.argmax(belief.weights)),
                      'final_map_weight': float(belief.weights.max()),
                      'human_observations': int(belief.action_counts[2])}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()
