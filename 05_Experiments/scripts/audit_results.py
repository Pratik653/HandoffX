"""Recheck stored results, reproduce scalar trajectories, audit robust objectives."""
from pathlib import Path
from functools import lru_cache
import csv,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'04_Python_Library/src'))
from handoffx import Action,State
from handoffx.scenarios import scenario_from_dict,policies
from handoffx.evaluation import ExactEvaluator,common_randomness,simulate

P=ROOT/'05_Experiments/results/main'
def rows(path):
    with path.open(newline='',encoding='utf-8') as f:return list(csv.DictReader(f))
def write_csv(path,values):
    with path.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(values[0]));w.writeheader();w.writerows(values)

def scalar_loss(spec,truth,policy,random):
    """Independent scalar trajectory loop; does not call vectorized simulate."""
    result=[];k=truth.kernels.reshape(-1,3,4);cdf=np.cumsum(truth.prior.ravel());cdf[-1]=1
    for i,u in enumerate(random['latent_u']):
        hidden=int(np.searchsorted(cdf,u,side='right'));state=State();loss=0.
        while True:
            term=spec.terminal_loss(state)
            if term is not None:loss+=term;break
            a=policy.action(state)
            if a==Action.STOP:loss+=spec.stop_loss;break
            loss+=spec.cost(a);p=k[hidden,int(a)];ocdf=np.cumsum(p);ocdf[-1]=1
            outcome=int(np.searchsorted(ocdf,random['outcome_u'][i,state.time,int(a)],side='right'))
            if outcome==1:loss+=spec.catastrophe_loss;break
            if a==Action.HUMAN:
                if outcome!=0:loss+=spec.failure_loss
                break
            counts=list(state.counts);counts[int(a)*3+{0:0,2:1,3:2}[outcome]]+=1
            state=State(tuple(counts),outcome!=0)
        result.append(loss)
    return np.asarray(result)

def rectangular_policy_value(spec,models,policy):
    @lru_cache(None)
    def value(s):
        terminal=spec.terminal_loss(s)
        if terminal is not None:return terminal
        a=policy.action(s)
        if a==Action.STOP:return spec.stop_loss
        p=models.conditionals(s)[:,int(a),:]
        q=np.full(len(p),spec.cost(a))+p[:,1]*spec.catastrophe_loss
        if a==Action.HUMAN:q+=(p[:,2]+p[:,3])*spec.failure_loss
        else:
            for o in (0,2,3):
                if p[:,o].max()>0:q+=p[:,o]*value(s.next(a,o))
        return float(q.max())
    return value(State())

def main():
    summary=rows(P/'summary.csv');raw_checks=0
    for row in summary:
        d=np.load(P/'raw'/(row['scenario']+'__'+row['policy']+'.npz'))
        assert abs(d['loss'].mean()-float(row['loss_mean']))<1e-10
        assert np.all(d['success']+d['severe']+d['stop']+d['ordinary_failure']==1)
        raw_checks+=len(d['loss'])
    old=rows(ROOT/'05_Experiments/logs/pre_validation_hardening_summary.csv')
    exclude={'cold_root_seconds','cached_call_seconds'}
    assert len(summary)==len(old)
    for x,y in zip(summary,old):
        for key in x:
            if key not in exclude:assert x[key]==y[key],(key,x[key],y[key])
    chosen=('ai_calibrated__human_under','low_hazard__ai_calibrated__human_calibrated','human_available_late','shift_unrecalibrated')
    scalar_checks=0
    metadata=json.loads((P/'run_metadata.json').read_text())
    robust_rows=[]
    names=json.loads((ROOT/'05_Experiments/configs/study.json').read_text())['scenario_names']
    for name in names:
        s=scenario_from_dict(json.loads((ROOT/'05_Experiments/configs'/(name+'.json')).read_text()))
        pp=policies(s,metadata['threshold'],metadata['retry_limit'])
        if name in chosen:
            random=common_randomness([78101,99118],500,s['spec'].horizon)
            for pn in ('handoffx_bayes','nominal_dp','robust_dp','retry_first'):
                scalar=scalar_loss(s['spec'],s['truth'],pp[pn],random)
                group=simulate(s['spec'],s['truth'],pp[pn],random)['loss']
                np.testing.assert_allclose(scalar,group,rtol=0,atol=1e-12);scalar_checks+=len(group)
        for pn,p in pp.items():
            fixed=max(ExactEvaluator(s['spec'],s['models'].one_model(m),p).as_dict()['loss'] for m in range(len(s['models'].names)))
            rectangle=rectangular_policy_value(s['spec'],s['models'],p)
            assert fixed<=rectangle+1e-8
            assert pp['robust_dp'].value()<=rectangle+1e-8
            robust_rows.append({'scenario':name,'policy':pn,'worst_supported_fixed_loss':fixed,
                'history_rectangular_loss':rectangle,'robust_optimal_envelope':pp['robust_dp'].value(),
                'rectangular_regret':rectangle-pp['robust_dp'].value()})
    write_csv(P/'robust_objective_evaluation.csv',robust_rows)
    report={'status':'all assertions passed','stored_episode_checks':raw_checks,
        'full_main_rerun_numerical_rows_identical':len(summary),'scalar_trajectory_matches':scalar_checks,
        'robust_objective_policy_scenario_checks':len(robust_rows),
        'scope':'automated self-audit with separate scalar and evaluation recursions; not external replication',
        'posthoc_disclosure':'Robust-objective comparisons added after the main run to distinguish expected-loss and minimax objectives; no policies or environments retuned.'}
    (ROOT/'05_Experiments/results/reproduction_audit.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
if __name__=='__main__':main()
