from dataclasses import replace
import json
import numpy as np
import pytest
from handoffx import Action,State,TaskSpec,ModelSet,ModelError,TerminalStateError,Planner,ActionGuard,recommend_or_stop
from handoffx.scenarios import make_scenario,policies,scenarios,scenario_to_dict,scenario_from_dict,COUPLED
from handoffx.evaluation import ExactEvaluator,common_randomness,simulate
from handoffx.static import expected_losses,human_threshold

@pytest.fixture
def base():return make_scenario('test')

@pytest.mark.parametrize('counts',[(0,0),(0,0,0,0,0,-1),(0.,0,0,0,0,0),[0,0,0,0,0,0]])
def test_reject_bad_counts(counts):
    with pytest.raises(ModelError):State(counts)

def test_retry_only_after_failure():
    with pytest.raises(ModelError):State().next(Action.RETRY,0)
    assert State().next(Action.CONTINUE,3).next(Action.RETRY,0).progress==1

@pytest.mark.parametrize('field,value',[('horizon',0),('horizon',13),('budget',-1),('stop_loss',-1.),('duration',(2,1,2)),('human_available',(True,)),('severe_risk_budget',1.1)])
def test_reject_bad_spec(field,value):
    with pytest.raises(ModelError):replace(TaskSpec(),**{field:value})

@pytest.mark.parametrize('kind',['nan','negative','row_sum','prior_sum','uncalibrated'])
def test_reject_bad_model(base,kind):
    m=base['models'];k=m.kernels.copy();p=m.prior.copy();e='synthetic'
    if kind=='nan':k[0,0,0,0]=np.nan
    if kind=='negative':k[0,0,0,0]=-.1
    if kind=='row_sum':k[0,0,0,0]=.1
    if kind=='prior_sum':p*=2
    if kind=='uncalibrated':e='uncalibrated'
    with pytest.raises(ModelError):ModelSet(k,p,m.names,e,m.center)

def test_immutable_inputs(base):
    with pytest.raises(ValueError):base['models'].kernels[0,0,0,0]=0

def test_posterior_normalized_and_failure_learns(base):
    m=base['models'].one_model(4);n=State().next(Action.CONTINUE,3)
    assert np.isclose(m.posterior(n).sum(),1.)
    assert m.posterior(n)[0,2]>m.prior[0,2]

def test_posterior_matches_direct_likelihood(base):
    m=base['models'];s=State().next(Action.CONTINUE,3).next(Action.RETRY,2)
    direct=m.prior*m.kernels[:,:,0,3]*m.kernels[:,:,1,2];direct/=direct.sum()
    np.testing.assert_allclose(m.posterior(s),direct,atol=1e-14)

def test_iid_preserves_marginal(base):
    np.testing.assert_allclose(base['models'].predict(State()),base['models'].iid_modes().predict(State()))

def test_terminal_success_precedes_deadline():
    spec=replace(TaskSpec(),horizon=1,milestones=1,human_available=(True,True))
    assert spec.terminal_loss(State().next(Action.CONTINUE,0))==0
    assert spec.terminal_loss(State().next(Action.CONTINUE,2))==spec.failure_loss

def test_missing_evidence_abstains():
    d=recommend_or_stop(None);assert d.action=='stop' and d.values=={} and d.evidence_status=='missing'

def test_json_api(base):
    p=policies(base)['handoffx_bayes'];d=json.loads(p.recommend().to_json())
    assert d['action'] in d['admissible_actions'] and d['evidence_status']=='synthetic'

def test_scores_readonly(base):
    with pytest.raises(TypeError):policies(base)['handoffx_bayes'].scores(State())[Action.STOP]=0.

def test_serialization_round_trip(base):
    b=scenario_from_dict(json.loads(json.dumps(scenario_to_dict(base))))
    assert b['spec']==base['spec']
    np.testing.assert_array_equal(b['models'].kernels,base['models'].kernels)

def test_nominal_equals_oracle_when_calibrated(base):
    p=policies(base)
    assert p['nominal_dp'].value()==pytest.approx(p['oracle'].value(),abs=1e-12)
    assert p['nominal_dp'].action()==p['oracle'].action()

def test_exact_oracle_value_matches_evaluator(base):
    p=policies(base);e=ExactEvaluator(base['spec'],base['truth'],p['oracle'],p['oracle']).as_dict()
    assert e['loss']==pytest.approx(p['oracle'].value(),abs=1e-10)
    assert e['decision_regret']==pytest.approx(0.,abs=1e-10)
    assert sum(e[x] for x in ('success','severe','stop','ordinary_failure'))==pytest.approx(1.)

@pytest.mark.parametrize('policy_name',['always_continue','always_human','retry_first','confidence','static_loss','nominal_dp','robust_dp','handoffx_bayes','bayes_independent','bayes_iid'])
def test_oracle_dominates_and_performance_difference(base,policy_name):
    p=policies(base);e=ExactEvaluator(base['spec'],base['truth'],p[policy_name],p['oracle']).as_dict()
    diff=e['loss']-p['oracle'].value()
    assert diff>=-1e-10
    assert e['decision_regret']==pytest.approx(diff,abs=1e-9)

def test_robust_upper_bounds_every_fixed_model(base):
    p=policies(base);r=p['robust_dp'];bound=r.value()
    for i in range(len(base['models'].names)):
        v=ExactEvaluator(base['spec'],base['models'].one_model(i),r).as_dict()['loss']
        assert v<=bound+1e-10

def test_bayes_equals_oracle_for_prior_predictive():
    s=make_scenario('predictive',truth_prior='coupled');p=policies(s)
    assert p['handoffx_bayes'].value()==pytest.approx(p['oracle'].value(),abs=1e-11)

def test_same_marginals_different_coupling(base):
    p=policies(base)
    a=p['handoffx_bayes'].models;b=p['bayes_independent'].models
    np.testing.assert_allclose(a.predict(State()),b.predict(State()),atol=1e-12)
    np.testing.assert_allclose(a.prior.reshape(3,3,-1).sum((1,2)),b.prior.reshape(3,3,-1).sum((1,2)))

def test_guard_never_overridden():
    s=make_scenario('guard',spec=replace(TaskSpec(),forbidden_actions=(Action.CONTINUE,Action.HUMAN)))
    for p in policies(s).values():assert p.action(State())==Action.STOP

def test_irreversible_after_failure():
    s=make_scenario('guard',spec=replace(TaskSpec(),forbid_continue_after_failure=True))
    st=State().next(Action.CONTINUE,2)
    for p in policies(s).values():assert p.action(st)!=Action.CONTINUE

def test_human_no_time_no_budget_no_ticket():
    for spec in [replace(TaskSpec(),budget=2),replace(TaskSpec(),human_budget=0),
                 replace(TaskSpec(),horizon=1,human_available=(True,)*2)]:
        s=make_scenario('g',spec=spec)
        assert Action.HUMAN not in ActionGuard(spec,s['models']).allowed(State())

def test_union_risk_bound_all_policies():
    s=make_scenario('risk',spec=replace(TaskSpec(),severe_risk_budget=.05))
    for p in policies(s).values():
        assert ExactEvaluator(s['spec'],s['truth'],p).as_dict()['severe']<=.05+1e-12

def test_reproducible_simulation(base):
    p=policies(base);r=common_randomness([11,22],200,base['spec'].horizon)
    a=simulate(base['spec'],base['truth'],p['handoffx_bayes'],r,p['oracle'])
    b=simulate(base['spec'],base['truth'],p['handoffx_bayes'],r,p['oracle'])
    for k in a:np.testing.assert_array_equal(a[k],b[k])

def test_mc_agrees_with_exact(base):
    p=policies(base);r=common_randomness([301,302,303,304],4000,base['spec'].horizon)
    a=simulate(base['spec'],base['truth'],p['retry_first'],r,p['oracle'])
    e=ExactEvaluator(base['spec'],base['truth'],p['retry_first']).as_dict()
    se=np.std(a['loss'],ddof=1)/np.sqrt(len(a['loss']))
    assert abs(a['loss'].mean()-e['loss'])<5*se+.01

def test_static_algebra():
    x=expected_losses({'continue':.65,'human':.90},{'continue':1.,'human':4.},20.)
    assert x['continue']==pytest.approx(8.) and x['human']==pytest.approx(6.)
    assert human_threshold(.65,1.,4.,20.)==pytest.approx(.8)

@pytest.mark.parametrize('x',[-.1,1.1,float('nan')])
def test_static_invalid_probabilities(x):
    with pytest.raises(ValueError):expected_losses({'continue':x},{'continue':1.},20.)

def test_raw_history_exhaustive_reference():
    """Independent no-count-cache history recursion for a small Bayes problem."""
    spec=replace(TaskSpec(),horizon=3,milestones=1,human_available=(True,)*4)
    s=make_scenario('small',spec=spec);m=s['models'];k=m.kernels
    def recurse(w,t,b,remaining,failed):
        if remaining==0:return 0.
        if t>=spec.horizon:return spec.failure_loss
        vals=[spec.stop_loss]
        for a in (0,1,2):
            if a==1 and not failed:continue
            if b<spec.resource_cost[a] or t+spec.duration[a]>spec.horizon:continue
            pred=np.einsum('mz,mzo->o',w,k[:,:,a,:])
            q=spec.action_cost[a]+spec.time_price*spec.duration[a]+pred[1]*spec.catastrophe_loss
            if a==2:q+=(pred[2]+pred[3])*spec.failure_loss
            else:
                for o in (0,2,3):
                    if pred[o]:
                        neww=w*k[:,:,a,o]/pred[o]
                        q+=pred[o]*recurse(neww,t+1,b-spec.resource_cost[a],remaining-(o==0),o!=0)
            vals.append(q)
        return min(vals)
    reference=recurse(m.prior,0,spec.budget,1,False)
    assert policies(s)['handoffx_bayes'].value()==pytest.approx(reference,abs=1e-10)

def test_all_scenario_models_valid():
    for s in scenarios():
        for m in (s['models'],s['truth']):
            np.testing.assert_allclose(m.kernels.sum(-1),1.,atol=1e-12)
            assert np.isclose(m.prior.sum(),1.)


@pytest.mark.parametrize('field,value',[
    ('action_cost',[.6,1.4,4.]),('duration',[1,1,2]),
    ('resource_cost',[1,2,3]),('human_available',[True]*7),
    ('forbidden_actions',[]),('forbid_continue_after_failure','False'),
    ('severe_risk_budget',float('nan'))])
def test_mutable_or_ambiguous_spec_rejected(field,value):
    with pytest.raises(ModelError):replace(TaskSpec(),**{field:value})
