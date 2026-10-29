from .scenarios import make_scenario, policies
from .models import State

def main():
    scenario=make_scenario('demo')
    policy=policies(scenario)['handoffx_bayes']
    print(policy.recommend(State()).to_json())

if __name__=='__main__': main()
