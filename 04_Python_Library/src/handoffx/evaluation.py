"""Exact policy evaluation and common-random-number simulation.

No future random outcomes or realized hidden modes are passed to policies.
The simulator alone receives the true sampled hidden model/mode.
"""
from __future__ import annotations
from functools import lru_cache
from typing import Any
import numpy as np
from numpy.typing import NDArray
from .models import State,Action,TaskSpec,ModelSet
from .policies import Policy,Planner

METRICS=('loss','success','severe','human','stop','ordinary_failure','elapsed',
         'resource','retries','retry_success','decisions','excess_handoff','decision_regret','success_time')
INDEX={k:i for i,k in enumerate(METRICS)}

class ExactEvaluator:
    def __init__(self,spec:TaskSpec,truth:ModelSet,policy:Policy,oracle:Planner|None=None):
        self.spec=spec;self.truth=truth;self.policy=policy;self.oracle=oracle
        self.metrics=lru_cache(maxsize=32768)(self.metrics)

    def metrics(self,state:State=State())->NDArray[np.float64]:
        s=self.spec;out=np.zeros(len(METRICS));term=s.terminal_loss(state)
        if term is not None:
            out[0]=term
            if state.progress==s.milestones:
                out[1]=1.;out[13]=state.time
            else:out[5]=1.
            out.setflags(write=False);return out
        a=self.policy.action(state);out[10]=1.
        if self.oracle is not None:
            oq=self.oracle.scores(state)
            out[12]=max(0.,oq[a]-self.oracle.value(state))
            if a==Action.HUMAN:
                alternatives=[v for aa,v in oq.items() if aa!=Action.HUMAN]
                out[11]=float(bool(alternatives) and oq[a]>min(alternatives)+1e-10)
        if a==Action.STOP:
            out[0]=s.stop_loss;out[4]=1.;out.setflags(write=False);return out
        i=int(a);p=self.truth.predict(state)[i]
        out[0]=s.cost(a)+p[1]*s.catastrophe_loss
        out[2]=p[1];out[6]=s.duration[i];out[7]=s.resource_cost[i]
        if a==Action.HUMAN:
            out[0]+=(p[2]+p[3])*s.failure_loss
            out[1]=p[0];out[3]=1.;out[5]=p[2]+p[3]
            out[13]=p[0]*(state.time+s.duration[i])
        else:
            if a==Action.RETRY:out[8]=1.;out[9]=p[0]
            for o in (0,2,3):
                if p[o]>0:out+=p[o]*self.metrics(state.next(a,o))
        out.setflags(write=False);return out

    def as_dict(self,state:State=State())->dict[str,float]:
        return dict(zip(METRICS,map(float,self.metrics(state))))


def common_randomness(seeds:list[int],episodes_per_seed:int,horizon:int)->dict[str,NDArray]:
    if episodes_per_seed<1 or not seeds or len(set(seeds))!=len(seeds):
        raise ValueError('positive sample size and distinct seeds required')
    z=[];outcomes=[];batch=[]
    for i,seed in enumerate(seeds):
        rng=np.random.Generator(np.random.PCG64(seed))
        z.append(rng.random(episodes_per_seed))
        outcomes.append(rng.random((episodes_per_seed,horizon,3)))
        batch.append(np.full(episodes_per_seed,i,dtype=np.int16))
    return {'latent_u':np.concatenate(z),'outcome_u':np.concatenate(outcomes),'batch':np.concatenate(batch)}


def simulate(spec:TaskSpec,truth:ModelSet,policy:Policy,randomness:dict[str,NDArray],
             oracle:Planner|None=None)->dict[str,NDArray]:
    u=randomness['outcome_u'];n=len(randomness['latent_u'])
    if u.shape!=(n,spec.horizon,3):raise ValueError('random schedule has wrong shape')
    flat=truth.prior.reshape(-1);cdf=np.cumsum(flat);cdf[-1]=1.
    hidden=np.searchsorted(cdf,randomness['latent_u'],side='right')
    k=truth.kernels.reshape(-1,3,4)
    counts=np.zeros((n,6),dtype=np.int16);failed=np.zeros(n,dtype=bool)
    active=np.ones(n,dtype=bool)
    data={m:np.zeros(n,dtype=np.float64) for m in METRICS}
    data['brier_sum']=np.zeros(n);data['executed_actions']=np.zeros(n)
    data['batch']=randomness['batch'].copy()
    for t in range(spec.horizon):
        ids=np.flatnonzero(active)
        if not len(ids):break
        # All nonterminal executable actions take one tick in this prototype.
        rows=np.column_stack((counts[ids],failed[ids].astype(np.int16)))
        states,inverse=np.unique(rows,axis=0,return_inverse=True)
        for group,row in enumerate(states):
            ii=ids[inverse==group]
            state=State(tuple(int(x) for x in row[:6]),bool(row[6]))
            a=policy.action(state);data['decisions'][ii]+=1
            if oracle is not None:
                oq=oracle.scores(state)
                data['decision_regret'][ii]+=max(0.,oq[a]-oracle.value(state))
                if a==Action.HUMAN:
                    other=[v for aa,v in oq.items() if aa!=Action.HUMAN]
                    if other and oq[a]>min(other)+1e-10:data['excess_handoff'][ii]+=1
            if a==Action.STOP:
                data['loss'][ii]+=spec.stop_loss;data['stop'][ii]=1;active[ii]=False;continue
            ai=int(a);data['loss'][ii]+=spec.cost(a)
            data['elapsed'][ii]+=spec.duration[ai];data['resource'][ii]+=spec.resource_cost[ai]
            data['executed_actions'][ii]+=1
            if a==Action.HUMAN:data['human'][ii]+=1
            if a==Action.RETRY:data['retries'][ii]+=1
            probs=k[hidden[ii],ai,:]
            cdf_o=np.cumsum(probs,axis=1);cdf_o[:,-1]=1.
            outcome=np.sum(u[ii,t,ai,None]>=cdf_o,axis=1)
            prediction=float(policy.models.predict(state)[ai,0])
            data['brier_sum'][ii]+=(prediction-(outcome==0))**2
            severe=ii[outcome==1]
            data['loss'][severe]+=spec.catastrophe_loss;data['severe'][severe]=1;active[severe]=False
            if a==Action.HUMAN:
                success=ii[outcome==0];failure=ii[(outcome==2)|(outcome==3)]
                data['success'][success]=1;data['success_time'][success]=t+spec.duration[ai]
                data['ordinary_failure'][failure]=1;data['loss'][failure]+=spec.failure_loss
                active[ii]=False
            else:
                for o,col in ((0,0),(2,1),(3,2)):
                    jj=ii[outcome==o]
                    counts[jj,ai*3+col]+=1;failed[jj]=(o!=0)
                    if o==0 and a==Action.RETRY:data['retry_success'][jj]+=1
                    done=jj[(counts[jj,0]+counts[jj,3])==spec.milestones]
                    if len(done):
                        data['success'][done]=1;data['success_time'][done]=t+1;active[done]=False
        if t==spec.horizon-1:
            timed=np.flatnonzero(active)
            data['loss'][timed]+=spec.failure_loss;data['ordinary_failure'][timed]=1;active[timed]=False
    if active.any():raise RuntimeError('simulation left active episodes')
    total=data['success']+data['severe']+data['ordinary_failure']+data['stop']
    if not np.all(total==1):raise RuntimeError('terminal outcomes not exclusive/exhaustive')
    return data
