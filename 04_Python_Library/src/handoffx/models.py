"""Validated, immutable inputs for a deliberately bounded research model.

Outcomes: 0 = progress/success, 1 = catastrophe, 2 = soft failure,
3 = hard-signal failure. Human assistance is terminal. The hidden mode and
model index remain fixed within an episode. This is not a general POMDP solver.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import IntEnum
from typing import Any
import numpy as np
from numpy.typing import NDArray

class Action(IntEnum):
    CONTINUE = 0
    RETRY = 1
    HUMAN = 2
    STOP = 3

class ModelError(ValueError):
    """Invalid probabilities, unsupported evidence, or inconsistent state."""

class TerminalStateError(ValueError):
    """Recommendations cannot be requested for completed or timed-out tasks."""

@dataclass(frozen=True)
class State:
    """Sufficient counts: C-progress/C-soft/C-hard/R-progress/R-soft/R-hard.

    The last-failure flag controls retry eligibility. Counts, not hidden modes,
    are exposed to policies. Count compression is valid only for stationary
    conditionally independent outcomes given the fixed latent model/mode.
    """
    counts: tuple[int, ...] = (0, 0, 0, 0, 0, 0)
    failed: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.counts,tuple) or len(self.counts) != 6 or any(type(n) is not int or n < 0 for n in self.counts):
            raise ModelError("counts must contain six nonnegative Python integers")
        if type(self.failed) is not bool:
            raise ModelError("failed must be a bool")
        if self.failed and sum(self.counts[i] for i in (1, 2, 4, 5)) == 0:
            raise ModelError("failed=True requires an observed failure")

    @property
    def time(self) -> int:
        return sum(self.counts)

    @property
    def progress(self) -> int:
        return self.counts[0] + self.counts[3]

    @property
    def retries(self) -> int:
        return sum(self.counts[3:])

    def next(self, action: Action, outcome: int) -> State:
        if action not in (Action.CONTINUE, Action.RETRY) or outcome not in (0, 2, 3):
            raise ModelError("only nonterminal continue/retry outcomes have a next state")
        if action == Action.RETRY and not self.failed:
            raise ModelError("retry requires a preceding unresolved failure")
        i = int(action) * 3 + {0: 0, 2: 1, 3: 2}[outcome]
        n = list(self.counts); n[i] += 1
        return State(tuple(n), outcome != 0)

@dataclass(frozen=True)
class TaskSpec:
    horizon: int = 6
    milestones: int = 2
    budget: int = 7
    resource_cost: tuple[int, int, int] = (1, 2, 3)
    action_cost: tuple[float, float, float] = (0.6, 1.4, 4.0)
    duration: tuple[int, int, int] = (1, 1, 2)
    time_price: float = 0.15
    failure_loss: float = 18.0
    stop_loss: float = 12.0
    catastrophe_loss: float = 90.0
    human_available: tuple[bool, ...] = (True,) * 7
    human_budget: int = 1
    forbid_continue_after_failure: bool = False
    forbidden_actions: tuple[Action, ...] = ()
    severe_risk_budget: float | None = None

    def __post_init__(self) -> None:
        for name in ("resource_cost", "action_cost", "duration", "human_available", "forbidden_actions"):
            if not isinstance(getattr(self, name), tuple):
                raise ModelError(f"{name} must be an immutable tuple")
        if type(self.forbid_continue_after_failure) is not bool:
            raise ModelError("forbid_continue_after_failure must be a bool")
        if any(type(x) is not int for x in (self.horizon, self.milestones, self.budget, self.human_budget)):
            raise ModelError("integer resources are required")
        if not 1 <= self.horizon <= 12 or self.milestones < 1 or self.budget < 0 or self.human_budget < 0:
            raise ModelError("invalid horizon (supported 1..12), milestones, or budget")
        if len(self.human_available) != self.horizon + 1 or any(type(x) is not bool for x in self.human_available):
            raise ModelError("availability must contain horizon+1 booleans")
        if len(self.action_cost) != 3 or len(self.duration) != 3 or len(self.resource_cost) != 3:
            raise ModelError("exactly three executable action specifications are required")
        if self.duration[:2] != (1, 1):
            raise ModelError("count-state implementation requires one-tick C and R actions")
        if any(type(x) is not int or x < 1 for x in (*self.duration, *self.resource_cost)):
            raise ModelError("durations and resource costs must be positive integers")
        vals=(*self.action_cost,self.time_price,self.failure_loss,self.stop_loss,self.catastrophe_loss)
        if any(not np.isfinite(x) or x < 0 for x in vals):
            raise ModelError("costs and losses must be finite and nonnegative")
        if Action.STOP in self.forbidden_actions:
            raise ModelError("this model requires an authorized safe-stop option")
        if any(not isinstance(x,Action) for x in self.forbidden_actions):
            raise ModelError("forbidden_actions must contain Action values")
        if self.severe_risk_budget is not None and not (0 <= self.severe_risk_budget <= 1):
            raise ModelError("severe_risk_budget must be in [0,1]")

    def cost(self, action: Action) -> float:
        if action == Action.STOP:
            return self.stop_loss
        return self.action_cost[int(action)] + self.time_price*self.duration[int(action)]

    def spent(self, state: State) -> int:
        return sum(state.counts[:3])*self.resource_cost[0] + sum(state.counts[3:])*self.resource_cost[1]

    def terminal_loss(self, state: State) -> float | None:
        if state.progress > self.milestones or self.spent(state) > self.budget:
            raise ModelError("state exceeds task progress or resource limits")
        if state.progress == self.milestones:
            return 0.0
        if state.time >= self.horizon:
            return self.failure_loss
        return None

@dataclass(frozen=True, eq=False)
class ModelSet:
    """Finite joint model/mode distribution and categorical action kernels.

    kernels[m,z,a,o], prior[m,z]. Rows must sum to one; they are never silently
    normalized. 'synthetic' and 'assumed' are not empirical calibration claims.
    """
    kernels: NDArray[np.float64]
    prior: NDArray[np.float64]
    names: tuple[str, ...]
    evidence_status: str = "assumed"
    center: int = 0
    _log_likelihood: NDArray[np.float64] = field(init=False, repr=False)
    _log_prior: NDArray[np.float64] = field(init=False, repr=False)

    def __post_init__(self) -> None:
        k=np.array(self.kernels,dtype=float,copy=True); p=np.array(self.prior,dtype=float,copy=True)
        if k.ndim != 4 or k.shape[2:] != (3,4) or p.shape != k.shape[:2]:
            raise ModelError("expected kernels (models,modes,3,4) and prior (models,modes)")
        if not np.isfinite(k).all() or not np.isfinite(p).all() or (k<0).any() or (p<0).any():
            raise ModelError("probabilities must be finite and nonnegative")
        if not np.allclose(k.sum(-1),1,atol=1e-12,rtol=0) or not np.isclose(p.sum(),1,atol=1e-12,rtol=0):
            raise ModelError("probabilities must sum to one without implicit normalization")
        if len(self.names)!=k.shape[0] or not 0<=self.center<k.shape[0]:
            raise ModelError("invalid model names or center")
        if (p.sum(axis=1)<=0).any():
            raise ModelError("every retained model needs positive prior mass")
        if self.evidence_status not in ("synthetic","assumed","calibrated"):
            raise ModelError("uncalibrated scores are not valid probability evidence")
        lik=np.stack([k[:,:,a,o] for a in (0,1) for o in (0,2,3)],axis=-1)
        with np.errstate(divide='ignore'):
            ll=np.log(lik); lp=np.log(p)
        for arr in (k,p,ll,lp): arr.setflags(write=False)
        object.__setattr__(self,'names',tuple(self.names))
        object.__setattr__(self,'kernels',k); object.__setattr__(self,'prior',p)
        object.__setattr__(self,'_log_likelihood',ll); object.__setattr__(self,'_log_prior',lp)

    def posterior(self, state: State) -> NDArray[np.float64]:
        logw=self._log_prior.copy()
        for i,n in enumerate(state.counts):
            if n: logw += n*self._log_likelihood[:,:,i]
        mx=np.max(logw)
        if not np.isfinite(mx):
            raise ModelError("observed history has zero likelihood in every supplied model")
        w=np.exp(logw-mx); return w/w.sum()

    def predict(self, state: State) -> NDArray[np.float64]:
        return np.einsum('mz,mzao->ao', self.posterior(state),self.kernels)

    def conditionals(self, state: State) -> NDArray[np.float64]:
        """Outcome distributions conditional on each still-possible fixed model."""
        post=self.posterior(state); masses=post.sum(axis=1)
        keep=masses>0
        return np.einsum('mz,mzao->mao',post[keep]/masses[keep,None],self.kernels[keep])

    def one_model(self, index: int) -> ModelSet:
        if not 0 <= index < len(self.names): raise IndexError(index)
        p=self.prior[index:index+1]; p=p/p.sum()
        return ModelSet(self.kernels[index:index+1],p,(self.names[index],),self.evidence_status,0)

    def iid_modes(self) -> ModelSet:
        """Ablation: resample hidden modes each action, retaining one-step marginals."""
        masses=self.prior.sum(axis=1)
        cond=self.prior/masses[:,None]
        k=np.einsum('mz,mzao->mao',cond,self.kernels)[:,None,:,:]
        return ModelSet(k,masses[:,None],self.names,self.evidence_status,self.center)

    def to_dict(self) -> dict[str,Any]:
        return {'kernels':self.kernels.tolist(),'prior':self.prior.tolist(),
                'names':list(self.names),'evidence_status':self.evidence_status,'center':self.center}

    @classmethod
    def from_dict(cls, d: dict[str,Any]) -> ModelSet:
        return cls(np.asarray(d['kernels']),np.asarray(d['prior']),tuple(d['names']),
                   str(d['evidence_status']),int(d.get('center',0)))
