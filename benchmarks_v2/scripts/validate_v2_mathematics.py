"""Numerical checks supplementing the written v0.2 propositions (ADAPTIVE_POLICY_MATHEMATICS.md)."""
from __future__ import annotations
import json
import numpy as np
from common import ROOT, draw_environment, Planner, State, Action, ActionGuard
from handoffx.adaptive import AdaptiveController, EpisodeBelief, bayes_factory, episode_log_likelihood, model_losses, run_episode
from handoffx.evaluation import ExactEvaluator

rng = np.random.default_rng(2026)
out = {}

# A1: sequential episode updates equal one batch likelihood (order invariance, ignorability of the policy).
env = draw_environment(900001); m = env['models']; spec = env['spec']
trajs = []
for pol in (Planner(spec, m.one_model(m.center), 'bayes'), Planner(spec, m.one_model(0), 'bayes')):
    for _ in range(25):
        trajs.append(run_episode(spec, env['truth'], pol, rng.random(), rng.random(spec.horizon + 1))[0])
b1 = EpisodeBelief(m); [b1.update(t) for t in trajs]
b2 = EpisodeBelief(m); [b2.update(t) for t in reversed(trajs)]
batch = np.log(m.prior.sum(1)) + sum(episode_log_likelihood(m, t) for t in trajs)
batch = np.exp(batch - batch.max()); batch /= batch.sum()
out['A1_max_abs_error_sequential_vs_batch'] = float(abs(b1.weights - batch).max())
out['A1_max_abs_error_order'] = float(abs(b1.weights - b2.weights).max())

# A2: models differing only in an untried action keep their prior ratio.
human_only_never = [t for t in trajs if all(a != Action.HUMAN for a, _ in t)]
b = EpisodeBelief(m); [b.update(t) for t in human_only_never]
pr = m.prior.sum(1); ratios = []
for i in range(5):  # AI offset fixed, human offset varies: identical AI kernels
    idx = [5 * i + j for j in range(5)]
    ratios.append(float(abs(b.weights[idx] / b.weights[idx].sum() - pr[idx] / pr[idx].sum()).max()))
out['A2_max_prior_ratio_deviation_untried_human'] = max(ratios)

# A3: Bayes-posterior candidate has nonnegative posterior advantage; the gate never raises posterior risk.
adv, risk = [], []
for k in range(30):
    e = draw_environment(910000 + k); sp, ms = e['spec'], e['models']
    nominal = Planner(sp, ms.one_model(ms.center), 'bayes')
    c = AdaptiveController(sp, ms, nominal, {'bayes': bayes_factory(sp)}, alpha=.35, tolerance=.03, relative=True)
    for _ in range(int(rng.integers(0, 30))):
        c.update(run_episode(sp, e['truth'], nominal, rng.random(), rng.random(sp.horizon + 1))[0])
    _, sel = c.select()
    adv.append(sel.expected_advantage['bayes'])
    risk.append(sel.expected_loss[sel.chosen] - sel.expected_loss['nominal'])
out['A3_min_posterior_advantage_of_bayes_candidate'] = float(min(adv))
out['A3_max_posterior_risk_increase_of_gate'] = float(max(risk))

# A4 boundary cases: alpha=0, tol=0 switches only under weak dominance on every supported model.
viol = 0
for k in range(30):
    e = draw_environment(920000 + k); sp, ms = e['spec'], e['models']
    nominal = Planner(sp, ms.one_model(ms.center), 'bayes')
    pol, sel = AdaptiveController(sp, ms, nominal, {'bayes': bayes_factory(sp)}, alpha=0.).select()
    if sel.chosen == 'bayes':
        d = model_losses(sp, ms, nominal) - model_losses(sp, ms, pol)
        viol += int((d < -1e-9).any())
out['A4_dominance_violations_alpha0'] = viol

# Performance-difference identity used in ROOT_CAUSE_ANALYSIS (re-checked on v2 environments).
errs = []
for k in range(10):
    e = draw_environment(930000 + k); sp, tr = e['spec'], e['truth']
    pa, pb = Planner(sp, e['models'], 'bayes'), Planner(sp, e['models'].one_model(e['models'].center), 'bayes')
    errs.append(abs(ExactEvaluator(sp, tr, pa).as_dict()['loss'] - ExactEvaluator(sp, tr, pb).as_dict()['loss']
                    - (ExactEvaluator(sp, tr, pa, Planner(sp, tr, 'bayes')).as_dict()['decision_regret']
                       - ExactEvaluator(sp, tr, pb, Planner(sp, tr, 'bayes')).as_dict()['decision_regret'])))
out['performance_difference_max_abs_error'] = float(max(errs))

out['all_passed'] = bool(out['A1_max_abs_error_sequential_vs_batch'] < 1e-10 and out['A1_max_abs_error_order'] < 1e-10
                         and out['A2_max_prior_ratio_deviation_untried_human'] < 1e-10
                         and out['A3_min_posterior_advantage_of_bayes_candidate'] >= -1e-10
                         and out['A3_max_posterior_risk_increase_of_gate'] <= 1e-10
                         and out['A4_dominance_violations_alpha0'] == 0 and out['performance_difference_max_abs_error'] < 1e-8)
(ROOT / 'benchmarks_v2/results/mathematical_checks_v2.json').write_text(json.dumps(out, indent=2) + '\n', encoding='utf-8')
print(json.dumps(out, indent=2))
