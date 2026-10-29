"""Simple integration API: supply estimates, ask for a recommendation, log outcomes.

    from handoffx import Advisor, Costs
    adv = Advisor.from_estimates(continue_success=.8, retry_success=.6, human_success=.9,
                                 uncertainty=.15, costs=Costs(human=4.0))
    rec = adv.recommend([("continue", "hard_failure")])
    print(rec.action, rec.explain())
    adv.record_episode([("continue", "hard_failure"), ("human", "success")])

The advisor only recommends. It never executes actions and never overrides an
external authorization decision. Probabilities you supply are treated as
estimates with the stated uncertainty, not as calibrated facts; logged episodes
recalibrate them across episodes (see :mod:`handoffx.adaptive`).
"""
from __future__ import annotations
from dataclasses import dataclass, field, replace
from typing import Iterable, Sequence
import json
import numpy as np
from .models import Action, ModelError, ModelSet, State, TaskSpec
from .policies import ActionGuard, Planner
from .adaptive import AdaptiveController, Selection, bayes_factory

OUTCOMES = {'success': 0, 'severe_failure': 1, 'soft_failure': 2, 'hard_failure': 3}
ACTIONS = {'continue': Action.CONTINUE, 'retry': Action.RETRY, 'human': Action.HUMAN, 'stop': Action.STOP}
_GRID = (-1., -.5, 0., .5, 1.)
_GRID_PRIOR = np.array([.1, .2, .4, .2, .1])


@dataclass(frozen=True)
class Costs:
    """Losses in one consistent unit (e.g. minutes or currency)."""
    continue_: float = .6
    retry: float = 1.4
    human: float = 4.0
    time_price: float = .15
    failure: float = 18.0
    stop: float = 12.0
    severe: float = 90.0


@dataclass(frozen=True)
class Recommendation:
    action: str
    expected_loss: dict[str, float]
    admissible_actions: tuple[str, ...]
    policy: str
    rationale: str
    reliability: str
    warnings: tuple[str, ...]
    selection: dict = field(default_factory=dict)

    def explain(self) -> str:
        alts = ', '.join(f'{a}={v:.3f}' for a, v in sorted(self.expected_loss.items(), key=lambda kv: kv[1]))
        lines = [f'Recommended: {self.action} (policy: {self.policy})',
                 f'Expected cumulative loss by first action: {alts}',
                 f'Admissible: {", ".join(self.admissible_actions)}',
                 f'Why: {self.rationale}', f'Reliability: {self.reliability}']
        lines += [f'Warning: {w}' for w in self.warnings]
        return '\n'.join(lines)

    def to_json(self) -> str:
        return json.dumps(self.__dict__, indent=2, sort_keys=True, allow_nan=False, default=list)


def _check_p(name: str, p: float) -> float:
    if not isinstance(p, (int, float)) or not np.isfinite(p) or not 0 < p < 1:
        raise ModelError(f'{name} must be a probability strictly between 0 and 1')
    return float(p)


def _kernel(succ, severe, persistent_success, persistent_rate, diag):
    """Two latent modes: 0 = no persistent fault, 1 = persistent fault.

    Supplied AI success probabilities are marginal over the mode prior, so the
    no-fault success is solved from p = (1 - r) p0 + r min(p0, ps).
    """
    k = np.zeros((2, 3, 4))
    for z in range(2):
        for a in range(3):
            ps = min(persistent_success, succ[a])
            p0 = succ[a] if (a == 2 or persistent_rate == 0) else (succ[a] - persistent_rate * ps) / (1 - persistent_rate)
            p = p0 if (z == 0 or a == 2) else ps
            q = severe[a]; p = float(np.clip(p, .005, 1 - q - .005)); f = 1 - p - q
            k[z, a, 0] = p; k[z, a, 1] = q
            if a == 2:
                k[z, a, 2] = f
            else:
                k[z, a, 2] = f * (1 - diag[z]); k[z, a, 3] = f * diag[z]
    return k


def history_to_state(history: Iterable[tuple[str, str]]) -> State:
    s = State()
    for a, o in history:
        if a not in ('continue', 'retry') or o not in ('success', 'soft_failure', 'hard_failure'):
            raise ModelError('in-episode history may contain only continue/retry with success/soft_failure/hard_failure')
        s = s.next(ACTIONS[a], OUTCOMES[o])
    return s


def _trajectory(steps: Sequence[tuple[str, str]]):
    out = []
    for a, o in steps:
        if a not in ACTIONS or o not in OUTCOMES:
            raise ModelError(f'unknown action/outcome {a!r}/{o!r}')
        if a != 'stop':
            out.append((ACTIONS[a], OUTCOMES[o]))
    return out


class Advisor:
    """Conservative adaptive intervention advisor (HandoffX v0.2 controller).

    Defaults ``alpha=0.35`` and relative ``tolerance=0.03`` are the gate frozen on
    the v0.2 development split. On held-out benchmarks the gate helped when the
    supplied estimates were biased and slightly hurt when they were already
    calibrated; see research_v2/EXPERIMENTAL_RESULTS.md.
    """

    def __init__(self, spec: TaskSpec, models: ModelSet, alpha: float = .35, tolerance: float = .03,
                 cadence: int = 5):
        if type(cadence) is not int or cadence < 1:
            raise ModelError('cadence must be a positive integer')
        self.spec = spec; self.models = models; self.guard = ActionGuard(spec, models)
        self.nominal = Planner(spec, models.one_model(models.center), 'bayes', self.guard, 'nominal')
        self.controller = AdaptiveController(spec, models, self.nominal, {'adaptive': bayes_factory(spec, self.guard)},
                                             alpha=alpha, tolerance=tolerance, relative=True)
        self.cadence = cadence
        self._policy, self._selection = self.controller.select()

    @classmethod
    def from_estimates(cls, continue_success: float, retry_success: float, human_success: float,
                       uncertainty: float = .15, persistent_failure_rate: float = .2,
                       persistent_success: float = .1, severe: tuple[float, float, float] = (.005, .003, .001),
                       costs: Costs = Costs(), horizon: int = 6, milestones: int = 2,
                       human_delay: int = 2, human_available: bool = True, budget: int = 12,
                       severe_risk_budget: float | None = None, **gate) -> 'Advisor':
        succ = [_check_p(n, v) for n, v in (('continue_success', continue_success), ('retry_success', retry_success),
                                            ('human_success', human_success))]
        if not 0 <= uncertainty <= .4:
            raise ModelError('uncertainty must be in [0, 0.4] (absolute probability offset)')
        z = _check_p('persistent_failure_rate', persistent_failure_rate) if persistent_failure_rate else 0.
        if not 0 <= persistent_success < 1:
            raise ModelError('persistent_success must be in [0, 1)')
        if len(severe) != 3 or any(not 0 <= q < .5 for q in severe):
            raise ModelError('severe must be three probabilities in [0, 0.5)')
        spec = TaskSpec(horizon=horizon, milestones=milestones, budget=budget, resource_cost=(1, 1, 1),
                        action_cost=(costs.continue_, costs.retry, costs.human), duration=(1, 1, human_delay),
                        time_price=costs.time_price, failure_loss=costs.failure, stop_loss=costs.stop,
                        catastrophe_loss=costs.severe, human_available=(human_available,) * (horizon + 1),
                        human_budget=1 if human_available else 0, severe_risk_budget=severe_risk_budget)
        ks, prior, names = [], [], []
        for i, da in enumerate(_GRID):
            for j, dh in enumerate(_GRID):
                s = [succ[0] + da * uncertainty, succ[1] + da * uncertainty, succ[2] + dh * uncertainty]
                ks.append(_kernel(s, severe, persistent_success, z, (.15, .85)))
                prior.append(_GRID_PRIOR[i] * _GRID_PRIOR[j] * np.array([1 - z, z]))
                names.append(f'ai{da * uncertainty:+.3f};human{dh * uncertainty:+.3f}')
        prior = np.array(prior); prior /= prior.sum()
        models = ModelSet(np.array(ks), prior, tuple(names), 'assumed', len(_GRID) ** 2 // 2)
        return cls(spec, models, **gate)

    def recommend(self, history: Iterable[tuple[str, str]] = (), human_available: bool | None = None,
                  forbidden: Iterable[str] = ()) -> Recommendation:
        """Recommend the next action given this episode's observed history."""
        state = history_to_state(history)
        spec = self.spec
        forb = tuple(ACTIONS[a] for a in forbidden)
        if Action.STOP in forb:
            raise ModelError('stop must remain authorized')
        if human_available is not None or forb:
            avail = spec.human_available if human_available is None else (bool(human_available),) * (spec.horizon + 1)
            spec = replace(spec, human_available=avail, forbidden_actions=tuple(set(spec.forbidden_actions) | set(forb)))
            policy = Planner(spec, self._policy.models, 'bayes', ActionGuard(spec, self.models), self._selection.chosen)
        else:
            policy = self._policy
        term = spec.terminal_loss(state)
        if term is not None:
            raise ModelError('episode already finished (success or deadline); start a new episode')
        scores = policy.scores(state); a = policy.action(state)
        counts = self.controller.belief.effective_counts(); warns = []
        if counts['human'] == 0:
            warns.append('human effectiveness has not been observed yet; it is prior-only')
        if counts['continue'] + counts['retry'] == 0:
            warns.append('AI success rates have not been observed yet; they are prior-only')
        reliability = ('model-based under the supplied estimates and uncertainty; '
                       f"{self.controller.belief.episodes} logged episodes")
        sel = self._selection
        return Recommendation(a.name.lower(), {k.name.lower(): float(v) for k, v in scores.items()},
                              tuple(x.name.lower() for x in policy.guard.allowed(state)), sel.chosen,
                              f'{a.name.lower()} minimizes expected cumulative loss under the {sel.chosen} policy. {sel.reason}',
                              reliability, tuple(warns),
                              {'expected_advantage': dict(sel.expected_advantage),
                               'degradation_probability': dict(sel.degradation_probability)})

    def record_episode(self, steps: Sequence[tuple[str, str]]) -> None:
        """Log one completed episode (all actions taken and their outcomes)."""
        self.controller.update(_trajectory(steps))
        if self.controller.belief.episodes % self.cadence == 0:
            self._policy, self._selection = self.controller.select()

    @property
    def selection(self) -> Selection:
        return self._selection

    def calibrated_estimates(self) -> dict[str, float]:
        """Posterior predictive first-attempt success probabilities.

        Before any episode these can differ slightly from the supplied values
        because grid models near 0 or 1 are clipped to valid probabilities.
        """
        p = self.controller.belief.posterior_models().predict(State())
        return {'continue_success': float(p[0, 0]), 'human_success': float(p[2, 0])}
