import json
import numpy as np
import pytest
from handoffx import Advisor, Costs, ModelError, history_to_state


@pytest.fixture
def adv():
    return Advisor.from_estimates(continue_success=.8, retry_success=.6, human_success=.9, uncertainty=.15)


def test_recommend_returns_admissible_action_with_explanation(adv):
    r = adv.recommend()
    assert r.action in r.admissible_actions and r.action in r.expected_loss
    assert 'Recommended' in r.explain() and json.loads(r.to_json())['action'] == r.action
    assert any('prior-only' in w for w in r.warnings)


def test_history_validation():
    with pytest.raises(ModelError):
        history_to_state([('human', 'success')])
    with pytest.raises(ModelError):
        history_to_state([('retry', 'success')])  # retry needs a preceding failure
    assert history_to_state([('continue', 'hard_failure'), ('retry', 'success')]).progress == 1


@pytest.mark.parametrize('kw', [dict(continue_success=1.), dict(human_success=-.1), dict(uncertainty=.9),
                                dict(severe=(.1, .1)), dict(persistent_failure_rate=1.5)])
def test_invalid_estimates_rejected(kw):
    base = dict(continue_success=.8, retry_success=.6, human_success=.9)
    with pytest.raises(ModelError):
        Advisor.from_estimates(**(base | kw))


def test_unavailable_human_and_forbidden_actions_respected(adv):
    r = adv.recommend([('continue', 'hard_failure')], human_available=False, forbidden=['continue'])
    assert 'human' not in r.admissible_actions and 'continue' not in r.admissible_actions
    with pytest.raises(ModelError):
        adv.recommend(forbidden=['stop'])


def test_repeated_hard_failures_shift_toward_handoff(adv):
    first = adv.recommend()
    later = adv.recommend([('continue', 'hard_failure'), ('retry', 'hard_failure')])
    assert later.expected_loss['continue'] - later.expected_loss.get('human', np.inf) > \
        first.expected_loss['continue'] - first.expected_loss.get('human', np.inf)


def test_recording_episodes_recalibrates_human_estimate():
    # Supplied human estimate 0.9 but logged handoffs mostly fail.
    adv = Advisor.from_estimates(continue_success=.8, retry_success=.6, human_success=.9, uncertainty=.15)
    before = adv.calibrated_estimates()['human_success']
    for i in range(40):
        adv.record_episode([('human', 'success' if i % 3 == 0 else 'soft_failure')])
    after = adv.calibrated_estimates()['human_success']
    assert after < before - .1
    assert adv.recommend().warnings == ('AI success rates have not been observed yet; they are prior-only',)


def test_finished_episode_rejected(adv):
    with pytest.raises(ModelError):
        adv.recommend([('continue', 'success'), ('continue', 'success')])


def test_costs_flow_into_spec():
    a = Advisor.from_estimates(.8, .6, .9, costs=Costs(human=9.))
    assert a.spec.action_cost[2] == 9.
