"""Run: python examples/basic_usage.py (after installing handoffx)."""
import json
from handoffx import State, Action
from handoffx.scenarios import make_scenario,policies

def main():
    scenario=make_scenario('documented_synthetic_example')
    policy=policies(scenario)['handoffx_bayes']
    print(policy.recommend(State()).to_json())
    # An adapter records only observable actions/outcomes, never the hidden mode.
    observed=State().next(Action.CONTINUE,3)
    print(policy.recommend(observed).to_json())
    assert json.loads(policy.recommend(observed).to_json())['evidence_status']=='synthetic'

if __name__=='__main__':main()
