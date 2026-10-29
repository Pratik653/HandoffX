"""Reproducible numerical/symbolic supplements to the written proofs."""
from pathlib import Path
import sys,json
import numpy as np
import sympy as sp
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'04_Python_Library/src'))
from handoffx import State,Action,TaskSpec
from handoffx.scenarios import make_scenario,policies
from handoffx.evaluation import ExactEvaluator
from dataclasses import replace

def main():
    rng=np.random.default_rng(70128); checks={}
    ca,ch,pa,ph,L=sp.symbols('c_A c_H p_A p_H L',real=True)
    expression=sp.simplify(ch+(1-ph)*L-(ca+(1-pa)*L)-(ch-ca-L*(ph-pa)))
    checks['P1_symbolic_difference_zero']=bool(expression==0)
    stable=0
    for _ in range(5000):
        p=rng.random(4);phat=np.clip(p+rng.uniform(-.05,.05,4),0,1);cost=rng.uniform(0,3,4)
        q=cost+20*(1-p);qh=cost+20*(1-phat);a=qh.argmin()
        assert q[a]-q.min()<=2.+1e-12
        gap=np.sort(qh)[1]-qh[a]
        if gap>2:
            assert a==q.argmin();stable+=1
    checks['P2_random_trials']=5000;checks['P2_stable_gap_cases']=stable
    posterior_low=.8
    checks['P3_human_after_failure_positive']=posterior_low*.2+(1-posterior_low)*.8
    checks['P3_human_after_failure_negative']=posterior_low*.8+(1-posterior_low)*.2
    assert abs(checks['P3_human_after_failure_positive']-.32)<1e-12
    for _ in range(5000):
        p=rng.random(5);w=rng.dirichlet(np.ones(5));k=int(rng.integers(1,8))
        assert np.sum(w*(1-p)**k)>=(1-np.dot(w,p))**k-1e-12
        wk=w*(1-p)**k;wk/=wk.sum();m=wk@p;v=wk@((p-m)**2)
        wn=wk*(1-p);wn/=wn.sum();mnext=wn@p
        assert abs((m-mnext)-v/(1-m))<1e-10
    checks['P4_random_mixtures']=5000
    p=np.array([.8,.05]);w=np.array([.6,.4]);survival=w@((1-p)**3)
    checks['P4_three_retry_true_success']=float(1-survival)
    checks['P4_three_retry_iid_success']=float(1-(1-w@p)**3)
    checks['P4_recovery_after_three_failures']=float((w*p*(1-p)**3).sum()/survival)
    s=make_scenario('validation');pol=policies(s)
    exact=ExactEvaluator(s['spec'],s['truth'],pol['oracle']).as_dict()['loss']
    checks['P5_oracle_recursion_error']=float(abs(exact-pol['oracle'].value()))
    vals=[ExactEvaluator(s['spec'],s['models'].one_model(i),pol['robust_dp']).as_dict()['loss'] for i in range(9)]
    checks['P6_worst_fixed_model_loss']=float(max(vals));checks['P6_envelope_value']=pol['robust_dp'].value()
    assert max(vals)<=pol['robust_dp'].value()+1e-10
    rs=make_scenario('risk',spec=replace(TaskSpec(),severe_risk_budget=.05));rp=policies(rs)
    risks=[ExactEvaluator(rs['spec'],rs['models'].one_model(i),p).as_dict()['severe']
           for p in rp.values() for i in range(9)]
    checks['P7_policy_model_pairs']=len(risks);checks['P7_maximum_exact_severe_risk']=float(max(risks))
    assert max(risks)<=.05+1e-12
    # Enumerate the entire admissible count-state tree, not just one policy's paths.
    seen=set();stack=[State()];guard=pol['oracle'].guard
    while stack:
        st=stack.pop()
        if st in seen:continue
        seen.add(st)
        for a in guard.allowed(st):
            if a in (Action.CONTINUE,Action.RETRY):
                stack.extend(st.next(a,o) for o in (0,2,3))
    true=s['truth'];shift=s['models'].one_model(8)
    eps=max(float(np.abs(true.predict(st)-shift.predict(st)).sum(axis=1).max()/2)
            for st in seen if s['spec'].terminal_loss(st) is None)
    T=s['spec'].horizon;G=max(s['spec'].catastrophe_loss,s['spec'].failure_loss,s['spec'].stop_loss)
    cm=max(s['spec'].cost(a) for a in (Action.CONTINUE,Action.RETRY,Action.HUMAN))
    bound=2*eps*(T*G+T*(T-1)*cm/2)
    from handoffx import Planner
    shifted_policy=Planner(s['spec'],shift,guard=guard)
    regret=ExactEvaluator(s['spec'],true,shifted_policy).as_dict()['loss']-exact
    assert regret<=bound+1e-10
    checks['P8_enumerated_states']=len(seen);checks['P8_uniform_history_TV']=eps
    checks['P8_actual_regret']=float(regret);checks['P8_conservative_regret_bound']=float(bound)
    checks['P9_prior_loss']=5.;checks['P9_perfect_information_loss']=1.
    checks['P9_noisy_information_loss']=10*(1-(.8*.9+.2*.1))
    counterexamples={
      'CE1':{'AI_loss':.3,'good_human_loss':.15,'poor_human_loss':.7},
      'CE2':{'one_tick_AI':.1+.4,'human':.4,'two_tick_AI_then_human':.1+.4*.4},
      'CE3':{'iid_success':.875,'persistent_success':float(1-survival)},
      'CE4':{'true_AI_loss':.05,'robust_selected_human_true_loss':.25},
      'CE5':{'fixed_worst':max(sum(x) for x in [(0,1),(1,0)]),'rectangular_worst':2},
      'CE6':{'observed_AI_loss':.5,'unobserved_human_world_1':.15,'unobserved_human_world_2':1.05},
      'CE7':{'group_blind_loss':.45,'conditional_loss':(.1+.45)/2},
      'CE8':{'AI_expected_loss':.01*100,'human_expected_loss':2,'AI_severe_probability':.01}}
    assert counterexamples['CE2']['two_tick_AI_then_human']<.4<counterexamples['CE2']['one_tick_AI']
    assert counterexamples['CE4']['true_AI_loss']<counterexamples['CE4']['robust_selected_human_true_loss']
    out={'status':'all assertions passed','seed':70128,'checks':checks,'counterexamples':counterexamples,
         'proof_status':'Numerical checks supplement the complete written proofs; no external peer review.'}
    p=ROOT/'05_Experiments/results/mathematical_checks.json';p.write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')
    print(json.dumps(out,indent=2))
if __name__=='__main__':main()
