"""Synthetic specifications. These numbers are experimental choices, not data."""
from __future__ import annotations
from dataclasses import replace, asdict
from typing import Any
import numpy as np
from .models import TaskSpec, ModelSet, Action
from .policies import Planner, Baseline, ActionGuard

BASE_P=np.array([[.88,.40,.07],[.90,.78,.12],[.94,.85,.55]])
BASE_Q=np.array([[.005,.030,.100],[.002,.008,.025],[.001,.003,.010]])
BASE_Z=np.array([.50,.30,.20])
BASE_D=np.array([.10,.45,.85])
COUPLED=np.array([[.20,.025,.05],[.025,.40,.025],[.05,.025,.20]])
OFFSETS=(-.18,0.,.18)

def kernels(p:np.ndarray,q:np.ndarray,d:np.ndarray)->np.ndarray:
    p=np.asarray(p,float);q=np.asarray(q,float);d=np.asarray(d,float)
    if p.shape!=(3,3) or q.shape!=(3,3) or d.shape!=(3,): raise ValueError('expected three actions and three latent modes')
    if (q<0).any() or (q>=.98).any() or (d<0).any() or (d>1).any(): raise ValueError('invalid synthetic settings')
    # Clipping is part of the declared perturbation generator, NOT model validation.
    p=np.clip(p,.01,1-q-.01)
    k=np.zeros((3,3,4))
    for a in range(3):
        k[:,a,0]=p[a];k[:,a,1]=q[a]
        f=1-p[a]-q[a]
        if a==2: k[:,a,2]=f
        else: k[:,a,2]=f*(1-d);k[:,a,3]=f*d
    return k

def make_scenario(name:str,ai_bias:float=0.,human_bias:float=0.,
                  true_p:np.ndarray|None=None,true_q:np.ndarray|None=None,
                  true_z:np.ndarray|None=None,estimated_p:np.ndarray|None=None,
                  estimated_q:np.ndarray|None=None,estimated_z:np.ndarray|None=None,
                  diagnostic:np.ndarray|None=None,spec:TaskSpec|None=None,
                  independent:bool=False,truth_prior:str|None=None,
                  category:str='stress',description:str='')->dict[str,Any]:
    p=BASE_P.copy() if true_p is None else np.array(true_p,float)
    q=BASE_Q.copy() if true_q is None else np.array(true_q,float)
    z=BASE_Z.copy() if true_z is None else np.array(true_z,float)
    ep=p.copy() if estimated_p is None else np.array(estimated_p,float)
    eq=q.copy() if estimated_q is None else np.array(estimated_q,float)
    ez=z.copy() if estimated_z is None else np.array(estimated_z,float)
    d=BASE_D.copy() if diagnostic is None else np.array(diagnostic,float)
    ep[:2]+=ai_bias;ep[2]+=human_bias
    all_k=[];names=[]
    for i,da in enumerate(OFFSETS):
        for j,dh in enumerate(OFFSETS):
            pp=ep.copy();pp[:2]+=da;pp[2]+=dh
            all_k.append(kernels(pp,eq,d));names.append(f'ai={da:+.2f};human={dh:+.2f}')
    models=ModelSet(np.array(all_k),COUPLED.reshape(-1,1)*ez[None,:],tuple(names),'synthetic',4)
    truth=ModelSet(kernels(p,q,d)[None,:,:,:],z[None,:],('true',),'synthetic')
    if truth_prior is not None:
        weights=COUPLED if truth_prior=='coupled' else np.fliplr(COUPLED)
        truth=ModelSet(models.kernels,weights.reshape(-1,1)*ez[None,:],models.names,'synthetic',4)
    if independent: models=models.iid_modes();truth=truth.iid_modes()
    return {'name':name,'spec':spec or TaskSpec(),'models':models,'truth':truth,
            'category':category,'description':description,'ai_bias':ai_bias,'human_bias':human_bias}

def scenarios()->list[dict[str,Any]]:
    s=[]
    tags={-.18:'under',0.:'calibrated',.18:'over'}
    for a in OFFSETS:
        for h in OFFSETS:
            s.append(make_scenario(f'ai_{tags[a]}__human_{tags[h]}',a,h,category='bias_factorial',
                description='Controlled supplied success-probability errors; positive is overconfidence.'))
    # Pre-specified second hazard regime prevents the factorial from being only
    # a high-risk, immediate-human-routing exercise. No final outcomes were used.
    for a in OFFSETS:
        for h in OFFSETS:
            s.append(make_scenario(f'low_hazard__ai_{tags[a]}__human_{tags[h]}',a,h,
                true_q=BASE_Q*.2,category='bias_factorial_low_hazard',
                description='Same 3x3 estimation-error factorial with one-fifth catastrophe probabilities.'))
    s.extend([
        make_scenario('persistent_low',true_z=np.array([.70,.25,.05]),description='Calibrated low persistent-mode prevalence.'),
        make_scenario('persistent_high',true_z=np.array([.25,.30,.45]),description='Calibrated high persistent-mode prevalence.'),
        make_scenario('independent_modes',independent=True,description='Modes independently resampled each action; one-step marginals preserved.'),
        make_scenario('human_delay_3',spec=replace(TaskSpec(),duration=(1,1,3)),description='Human response consumes three time ticks.'),
        make_scenario('human_available_late',spec=replace(TaskSpec(),human_available=(False,False,True,True,True,True,True)),description='Human available from tick two, known schedule.'),
        make_scenario('human_unavailable',spec=replace(TaskSpec(),human_budget=0),description='No human ticket; no hidden free fallback.'),
        make_scenario('high_consequence',spec=replace(TaskSpec(),catastrophe_loss=180.),description='Severe failure loss doubles; other losses unchanged.'),
        make_scenario('low_consequence',spec=replace(TaskSpec(),catastrophe_loss=30.,failure_loss=6.,stop_loss=4.),description='All failure consequences reduced.'),
        make_scenario('limited_budget',spec=replace(TaskSpec(),budget=3),description='Three resource units for the episode.'),
        make_scenario('short_deadline',spec=replace(TaskSpec(),horizon=3,human_available=(True,)*4),description='Three-tick horizon.'),
        make_scenario('uninformative_diagnostic',diagnostic=np.array([.5,.5,.5]),description='Failure alarm carries no additional mode information.'),
        make_scenario('weak_human',true_p=np.array([BASE_P[0],BASE_P[1],[.45,.30,.15]]),description='Calibrated fallible helper, often dominated.'),
        make_scenario('expensive_human',spec=replace(TaskSpec(),action_cost=(.6,1.4,8.)),description='Human execution cost doubles.'),
        make_scenario('cheap_human',spec=replace(TaskSpec(),action_cost=(.6,1.4,1.)),description='Low human execution cost.'),
        make_scenario('shift_unrecalibrated',true_p=BASE_P-np.array([[.12],[.12],[.20]]),
                      true_q=BASE_Q*1.4,true_z=np.array([.25,.30,.45]),
                      estimated_p=BASE_P,estimated_q=BASE_Q,estimated_z=BASE_Z,
                      description='Joint success, hazard and mode-prevalence shift; training estimates retained.'),
        make_scenario('shift_perfect_recalibration',true_p=BASE_P-np.array([[.12],[.12],[.20]]),
                      true_q=BASE_Q*1.4,true_z=np.array([.25,.30,.45]),
                      description='Same shifted environment with exact updated parameters: calibration upper bound, not a fitted estimator.'),
        make_scenario('irreversible_guard',spec=replace(TaskSpec(),forbid_continue_after_failure=True),description='External authorization forbids continue after failure.'),
        make_scenario('conditional_risk_guard',spec=replace(TaskSpec(),severe_risk_budget=.05),description='Shared worst-model per-action severe-risk cap 0.05/6.'),
        make_scenario('joint_prior_predictive',truth_prior='coupled',category='prior_check',description='Fixed model sampled from declared coupled prior each episode.'),
        make_scenario('opposite_coupling',truth_prior='opposite',category='prior_check',description='Same marginal model probabilities but opposite AI-human coupling.'),
    ])
    return s

def policies(s:dict[str,Any],threshold:float=.65,retry_limit:int=2):
    spec=s['spec']; models=s['models']; guard=ActionGuard(spec,models)
    nominal=models.one_model(models.center)
    out={kind:Baseline(spec,nominal,kind,guard,threshold,retry_limit) for kind in
         ('always_continue','always_human','retry_first','confidence','static_loss')}
    out['nominal_dp']=Planner(spec,nominal,'bayes',guard,'nominal_dp')
    out['robust_dp']=Planner(spec,models,'robust',guard,'robust_dp')
    out['handoffx_bayes']=Planner(spec,models,'bayes',guard,'handoffx_bayes')
    margins=COUPLED.sum(axis=1); indep=np.outer(margins,margins).reshape(-1)
    zcond=models.prior/models.prior.sum(axis=1)[:,None]
    independent=ModelSet(models.kernels,indep[:,None]*zcond,models.names,'synthetic',models.center)
    out['bayes_independent']=Planner(spec,independent,'bayes',guard,'bayes_independent')
    out['bayes_iid']=Planner(spec,models.iid_modes(),'bayes',guard,'bayes_iid')
    out['oracle']=Planner(spec,s['truth'],'bayes',guard,'oracle')
    return out

def scenario_to_dict(s:dict[str,Any])->dict[str,Any]:
    d={k:v for k,v in s.items() if k not in ('spec','models','truth')}
    d['spec']=asdict(s['spec']);d['models']=s['models'].to_dict();d['truth']=s['truth'].to_dict()
    return d

def scenario_from_dict(d:dict[str,Any])->dict[str,Any]:
    out=dict(d); sd=dict(d['spec'])
    for k in ('resource_cost','action_cost','duration','human_available'):sd[k]=tuple(sd[k])
    sd['forbidden_actions']=tuple(Action(x) for x in sd['forbidden_actions'])
    out['spec']=TaskSpec(**sd);out['models']=ModelSet.from_dict(d['models']);out['truth']=ModelSet.from_dict(d['truth'])
    return out
