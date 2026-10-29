"""Exact finite-horizon policies on a sufficient-count belief state.

Bayes uses a fixed latent model. Robust uses a HISTORY-RECTANGULAR envelope
of fixed-model conditional kernels. It is not fixed-parameter minimax control.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from functools import lru_cache
from typing import Protocol, Any
import json
from types import MappingProxyType
import numpy as np
from .models import Action, ModelSet, TaskSpec, State, TerminalStateError, ModelError

class Policy(Protocol):
    name: str
    spec: TaskSpec
    def action(self,state:State)->Action: ...

@dataclass(frozen=True)
class Decision:
    action: str
    values: dict[str,float]
    value_semantics: str
    reason: str
    evidence_status: str
    assumptions: tuple[str,...]
    admissible_actions: tuple[str,...]
    def to_json(self)->str:
        return json.dumps(asdict(self),sort_keys=True,allow_nan=False,indent=2)

class ActionGuard:
    """External feasibility and optional conditional-risk filter, shared by policies."""
    def __init__(self,spec:TaskSpec,uncertainty:ModelSet):
        self.spec=spec; self.uncertainty=uncertainty
        self.allowed=lru_cache(maxsize=32768)(self.allowed)

    def allowed(self,state:State)->tuple[Action,...]:
        s=self.spec
        if s.terminal_loss(state) is not None: return ()
        actions=[Action.STOP]
        risk=None
        if s.severe_risk_budget is not None:
            risk=self.uncertainty.conditionals(state)[:,:,1].max(axis=0)
        for a in (Action.CONTINUE,Action.RETRY,Action.HUMAN):
            if a in s.forbidden_actions: continue
            i=int(a)
            if s.spent(state)+s.resource_cost[i]>s.budget or state.time+s.duration[i]>s.horizon: continue
            if a==Action.RETRY and not state.failed: continue
            if a==Action.CONTINUE and s.forbid_continue_after_failure and state.failed: continue
            if a==Action.HUMAN and (s.human_budget<1 or not s.human_available[state.time]): continue
            if risk is not None and risk[i]>s.severe_risk_budget/s.horizon+1e-12: continue
            actions.append(a)
        return tuple(actions)

class Planner:
    def __init__(self,spec:TaskSpec,models:ModelSet,mode:str='bayes',
                 guard:ActionGuard|None=None,name:str|None=None):
        if mode not in ('bayes','robust'): raise ValueError('mode must be bayes or robust')
        self.spec=spec; self.models=models; self.mode=mode
        self.guard=guard or ActionGuard(spec,models)
        if self.guard.spec != spec: raise ModelError('guard and planner task specifications differ')
        self.name=name or mode
        self.scores=lru_cache(maxsize=32768)(self.scores)
        self.value=lru_cache(maxsize=32768)(self.value)
        self.action=lru_cache(maxsize=32768)(self.action)

    def scores(self,state:State)->dict[Action,float]:
        s=self.spec
        if s.terminal_loss(state) is not None: return MappingProxyType({})
        ks=self.models.conditionals(state) if self.mode=='robust' else self.models.predict(state)[None,:,:]
        result={Action.STOP:s.stop_loss}
        for a in self.guard.allowed(state):
            if a==Action.STOP: continue
            p=ks[:,int(a),:]
            q=np.full(p.shape[0],s.cost(a)) + p[:,1]*s.catastrophe_loss
            if a==Action.HUMAN:
                q+=(p[:,2]+p[:,3])*s.failure_loss
            else:
                for o in (0,2,3):
                    if p[:,o].max()>0:
                        nxt=state.next(a,o)
                        q+=p[:,o]*self.value(nxt)
            result[a]=float(q.max() if self.mode=='robust' else q[0])
        return MappingProxyType(result)

    def value(self,state:State=State())->float:
        terminal=self.spec.terminal_loss(state)
        if terminal is not None: return terminal
        return min(self.scores(state).values())

    def action(self,state:State=State())->Action:
        scores=self.scores(state)
        if not scores: raise TerminalStateError('no action for a terminal state')
        # Conservative deterministic tie order: stop, human, retry, continue.
        return min(scores,key=lambda a:(round(scores[a],12),-int(a)))

    def recommend(self,state:State=State())->Decision:
        a=self.action(state); scores=self.scores(state)
        semantics=('history-rectangular worst-case cumulative loss' if self.mode=='robust'
                   else 'posterior expected cumulative loss')
        return Decision(a.name.lower(),{k.name.lower():v for k,v in scores.items()},semantics,
            f'{a.name.lower()} minimizes {semantics} among externally admissible actions.',
            self.models.evidence_status,
            ('finite horizon; stationary fixed hidden mode within an episode',
             'model probabilities supplied, not predicted or calibrated by this library',
             'safe stop must be authorized by the integrating system',
             'guarantees require the stated model/ambiguity assumptions'),
            tuple(x.name.lower() for x in self.guard.allowed(state)))

class Baseline:
    def __init__(self,spec:TaskSpec,models:ModelSet,kind:str,guard:ActionGuard|None=None,
                 threshold:float=0.65,retry_limit:int=2):
        kinds=('always_continue','always_human','retry_first','confidence','static_loss')
        if kind not in kinds: raise ValueError(kind)
        if not 0<=threshold<=1 or retry_limit<0: raise ValueError('invalid heuristic settings')
        self.spec=spec; self.models=models; self.kind=kind; self.name=kind
        self.guard=guard or ActionGuard(spec,models)
        self.threshold=threshold; self.retry_limit=retry_limit
        self.macro_cost=lru_cache(maxsize=32768)(self.macro_cost)
        self.action=lru_cache(maxsize=32768)(self.action)

    def macro_cost(self,state:State,action:Action)->float:
        """Static loss of a committed completion plan; a failure ends the plan.

        C: continue through remaining milestones. R: retry the current milestone,
        then continue. H: terminal human rescue. Policy replans after actual
        nonterminal failures, but this static scoring function does not value
        future recovery choices. Future authorization filters still apply.
        """
        s=self.spec; term=s.terminal_loss(state)
        if term is not None: return term
        if action not in self.guard.allowed(state) or action==Action.STOP: return s.stop_loss
        p=self.models.predict(state)[int(action)]
        q=s.cost(action)+p[1]*s.catastrophe_loss+(p[2]+p[3])*s.failure_loss
        if action!=Action.HUMAN:
            q+=p[0]*self.macro_cost(state.next(action,0),Action.CONTINUE)
        return float(q)

    def action(self,state:State=State())->Action:
        allowed=self.guard.allowed(state)
        if not allowed: raise TerminalStateError('no action for a terminal state')
        if self.kind=='static_loss':
            return min(allowed,key=lambda a:(round(self.macro_cost(state,a),12),-int(a)))
        if self.kind=='always_continue': order=(Action.CONTINUE,Action.STOP)
        elif self.kind=='always_human': order=(Action.HUMAN,Action.CONTINUE,Action.STOP)
        elif self.kind=='retry_first':
            if not state.failed: order=(Action.CONTINUE,Action.HUMAN,Action.STOP)
            elif state.retries<self.retry_limit: order=(Action.RETRY,Action.HUMAN,Action.CONTINUE,Action.STOP)
            else: order=(Action.HUMAN,Action.STOP)
        else:
            remaining=self.spec.milestones-state.progress
            p=float(np.sum(self.models.posterior(state)*self.models.kernels[:,:,0,0]**remaining))
            order=((Action.CONTINUE,Action.RETRY,Action.HUMAN,Action.STOP) if p>=self.threshold
                   else (Action.HUMAN,Action.RETRY,Action.CONTINUE,Action.STOP))
        return next(a for a in order if a in allowed)


def recommend_or_stop(planner:Planner|None,state:State=State())->Decision:
    """Explicit unscored abstention; no confidence-to-probability conversion."""
    if planner is None:
        return Decision('stop',{},'not scored','Missing validated probability inputs; request model review.',
                        'missing',('safe stop requires external authorization',),('stop',))
    try:
        return planner.recommend(state)
    except ModelError as exc:
        return Decision('stop',{},'not scored',str(exc),'invalid',
                        ('no quantitative performance guarantee',),('stop',))
