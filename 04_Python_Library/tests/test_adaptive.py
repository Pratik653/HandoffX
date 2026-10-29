import numpy as np
import pytest
from handoffx import Action, ModelError, Planner, State
from handoffx.scenarios import make_scenario
from handoffx.evaluation import ExactEvaluator
from handoffx.adaptive import (AdaptiveController, EpisodeBelief, bayes_factory, episode_log_likelihood,
                               model_losses, run_episode)


@pytest.fixture
def base():
    return make_scenario('adaptive')


def test_episode_likelihood_matches_direct_sum(base):
    m = base['models']; traj = [(Action.CONTINUE, 3), (Action.RETRY, 0), (Action.HUMAN, 2)]
    zc = m.prior / m.prior.sum(axis=1, keepdims=True)
    direct = (zc * m.kernels[:, :, 0, 3] * m.kernels[:, :, 1, 0] * m.kernels[:, :, 2, 2]).sum(axis=1)
    np.testing.assert_allclose(np.exp(episode_log_likelihood(m, traj)), direct, rtol=1e-12)


def test_empty_episode_is_uninformative(base):
    b = EpisodeBelief(base['models']); w0 = b.weights.copy(); b.update([])
    np.testing.assert_allclose(b.weights, w0, atol=1e-15)
    assert b.episodes == 1 and b.effective_counts() == {'continue': 0, 'retry': 0, 'human': 0}


def test_stop_and_bad_outcomes_rejected(base):
    with pytest.raises(ModelError):
        episode_log_likelihood(base['models'], [(Action.STOP, 0)])
    with pytest.raises(ModelError):
        episode_log_likelihood(base['models'], [(Action.CONTINUE, 7)])


def test_belief_concentrates_on_generating_model(base):
    m = base['models']; truth = m.one_model(2); rng = np.random.default_rng(0)
    pol = Planner(base['spec'], truth, 'bayes'); b = EpisodeBelief(m)
    for _ in range(400):
        traj, _, _ = run_episode(base['spec'], truth, pol, rng.random(), rng.random(base['spec'].horizon + 1))
        b.update(traj)
    # This policy always hands off, so only the human offset is identifiable:
    # mass concentrates on the human=+0.18 column (models 2, 5, 8) while the
    # AI offset keeps its prior ratios. Unobserved actions stay prior-only.
    assert b.weights[[2, 5, 8]].sum() > .999
    assert b.effective_counts()['continue'] == 0
    prior = m.prior.sum(axis=1)
    np.testing.assert_allclose(b.weights[[2, 5, 8]] / b.weights[[2, 5, 8]].sum(),
                               prior[[2, 5, 8]] / prior[[2, 5, 8]].sum(), atol=1e-3)


def test_posterior_models_is_valid_and_reduces_to_prior(base):
    m = base['models']; b = EpisodeBelief(m)
    np.testing.assert_allclose(b.posterior_models().prior, m.prior, atol=1e-14)


def test_credible_set_mass(base):
    b = EpisodeBelief(base['models']); cs = b.credible_set(.9)
    assert b.weights[cs].sum() >= .9 - 1e-12
    assert len(b.credible_set(1.)) == len(base['models'].names)
    with pytest.raises(ModelError):
        b.credible_set(0.)


def test_model_losses_match_exact_evaluator(base):
    spec, m = base['spec'], base['models']; pol = Planner(spec, m.one_model(4), 'bayes')
    lm = model_losses(spec, m, pol)
    assert np.isclose(lm[3], ExactEvaluator(spec, m.one_model(3), pol).as_dict()['loss'])


def test_gate_never_increases_posterior_expected_loss(base):
    spec, m = base['spec'], base['models']
    nominal = Planner(spec, m.one_model(m.center), 'bayes')
    for alpha in (0., .1, 1.):
        c = AdaptiveController(spec, m, nominal, {'bayes': bayes_factory(spec)}, alpha=alpha)
        _, sel = c.select()
        assert sel.expected_loss[sel.chosen] <= sel.expected_loss['nominal'] + 1e-12


def test_gate_alpha_zero_requires_no_degradation(base):
    spec, m = base['spec'], base['models']
    nominal = Planner(spec, m.one_model(m.center), 'bayes')
    _, sel = AdaptiveController(spec, m, nominal, {'bayes': bayes_factory(spec)}, alpha=0.).select()
    if sel.chosen == 'bayes':
        assert sel.degradation_probability['bayes'] == 0.


def test_gate_alpha_one_equals_posterior_risk_minimiser(base):
    spec, m = base['spec'], base['models']
    nominal = Planner(spec, m.one_model(m.center), 'bayes')
    _, sel = AdaptiveController(spec, m, nominal, {'bayes': bayes_factory(spec)}, alpha=1., margin=-np.inf).select()
    assert np.isclose(sel.expected_loss[sel.chosen], min(sel.expected_loss.values()), atol=1e-12)


def test_controller_rejects_bad_settings(base):
    spec, m = base['spec'], base['models']; nominal = Planner(spec, m.one_model(m.center), 'bayes')
    with pytest.raises(ModelError):
        AdaptiveController(spec, m, nominal, {}, alpha=2.)
    with pytest.raises(ModelError):
        AdaptiveController(spec, m, nominal, {'nominal': bayes_factory(spec)})


def test_run_episode_matches_exact_expectation(base):
    spec, truth = base['spec'], base['truth']; pol = Planner(spec, base['models'], 'bayes')
    rng = np.random.default_rng(3); n = 20000
    losses = [run_episode(spec, truth, pol, rng.random(), rng.random(spec.horizon + 1))[1] for _ in range(n)]
    exact = ExactEvaluator(spec, truth, pol).as_dict()['loss']
    se = np.std(losses) / np.sqrt(n)
    assert abs(np.mean(losses) - exact) < 4 * se
