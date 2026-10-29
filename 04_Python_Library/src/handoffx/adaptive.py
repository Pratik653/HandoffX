"""Cross-episode calibration and conservative adaptive policy selection (v0.2).

Within one episode the v0.1 planner cannot correct a biased supplied estimate:
its prior is centred on that estimate, an episode yields at most ``horizon``
observations, and human effectiveness is observed only after the terminal
handoff. This module pools evidence ACROSS episodes.

* :class:`EpisodeBelief` keeps a posterior over the fixed model index ``m`` of a
  :class:`~handoffx.models.ModelSet`. Each completed episode contributes the
  marginal likelihood ``sum_z prior[z|m] prod_t k[m,z,a_t,o_t]``. Because actions
  depend only on previously observed data (and, for Thompson sampling, on
  independent randomisation), the action-selection mechanism is ignorable and
  unobserved counterfactual outcomes need no imputation (Rubin, 1976). Outcomes
  of actions that were never taken carry no information; the belief over them
  stays at the prior, and :meth:`EpisodeBelief.effective_counts` exposes this.
* :class:`AdaptiveController` keeps an incumbent (nominal) policy and switches to
  a candidate only when the posterior expected loss reduction is positive and
  the posterior probability of a degradation larger than ``tolerance`` is at
  most ``alpha``. This is a Bayesian credible-set rule in the spirit of safe
  policy improvement (Thomas et al., 2015; Laroche et al., 2019); it is not a
  frequentist guarantee and it is only as good as the supplied model set.

Nothing here converts an uncalibrated confidence score into a probability.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable, Mapping, Sequence
import numpy as np
from numpy.typing import NDArray
from .models import Action, ModelError, ModelSet, State, TaskSpec
from .policies import ActionGuard, Planner, Policy
from .evaluation import ExactEvaluator

Step = tuple[Action, int]


def _outcome_columns(trajectory: Sequence[Step]) -> list[tuple[int, int]]:
    cols = []
    for a, o in trajectory:
        a = Action(a)
        if a == Action.STOP:
            raise ModelError('stop produces no outcome; omit it from the trajectory')
        if o not in (0, 1, 2, 3):
            raise ModelError('outcome must be 0 (success), 1 (severe), 2 (soft) or 3 (hard)')
        cols.append((int(a), int(o)))
    return cols


def episode_log_likelihood(models: ModelSet, trajectory: Sequence[Step]) -> NDArray[np.float64]:
    """Log marginal likelihood of one episode under each model index ``m``.

    The latent mode is integrated out with the model's own conditional mode
    prior because it is redrawn for each episode while ``m`` is shared.
    """
    cols = _outcome_columns(trajectory)
    masses = models.prior.sum(axis=1)
    with np.errstate(divide='ignore'):
        logw = np.log(models.prior / masses[:, None])
        for a, o in cols:
            logw = logw + np.log(models.kernels[:, :, a, o])
    mx = logw.max(axis=1)
    out = np.full(len(masses), -np.inf)
    ok = np.isfinite(mx)
    out[ok] = mx[ok] + np.log(np.exp(logw[ok] - mx[ok, None]).sum(axis=1))
    return out


@dataclass
class EpisodeBelief:
    """Posterior over the fixed model index, updated from completed episodes."""
    models: ModelSet
    log_weights: NDArray[np.float64] = field(init=False)
    episodes: int = field(init=False, default=0)
    action_counts: NDArray[np.int64] = field(init=False)

    def __post_init__(self) -> None:
        with np.errstate(divide='ignore'):
            self.log_weights = np.log(self.models.prior.sum(axis=1))
        self.action_counts = np.zeros(3, dtype=np.int64)

    def update(self, trajectory: Sequence[Step]) -> None:
        ll = episode_log_likelihood(self.models, trajectory)
        new = self.log_weights + ll
        if not np.isfinite(new.max()):
            raise ModelError('episode has zero likelihood under every supplied model; the model set is misspecified')
        self.log_weights = new - new.max()
        self.episodes += 1
        for a, _ in _outcome_columns(trajectory):
            self.action_counts[a] += 1

    @property
    def weights(self) -> NDArray[np.float64]:
        w = np.exp(self.log_weights - self.log_weights.max())
        return w / w.sum()

    def effective_counts(self) -> dict[str, int]:
        """Observed attempts per action; zero means that action is still prior-only."""
        return {Action(i).name.lower(): int(n) for i, n in enumerate(self.action_counts)}

    def posterior_models(self) -> ModelSet:
        """The supplied ModelSet with its model prior replaced by the posterior.

        Models with zero likelihood (log weight -inf) are ruled out and omitted.
        """
        alive = np.flatnonzero(np.isfinite(self.log_weights))
        # A finite weight that underflows to exactly 0 after decisive evidence is floored at the
        # smallest normal float, so every retained model keeps the positive mass ModelSet requires.
        # The perturbation is below 1e-307 per model; weights that did not underflow are unchanged.
        w = np.maximum(self.weights[alive], np.finfo(np.float64).tiny)
        p = self.models.prior[alive]
        prior = w[:, None] * p / p.sum(axis=1)[:, None]
        prior = prior / prior.sum()
        return ModelSet(self.models.kernels[alive], prior, tuple(self.models.names[i] for i in alive),
                        self.models.evidence_status, int(np.argmax(w)))

    def map_model(self) -> ModelSet:
        return self.models.one_model(int(np.argmax(self.weights)))

    def sample(self, rng: np.random.Generator) -> int:
        return int(rng.choice(len(self.weights), p=self.weights))

    def credible_set(self, mass: float = .9) -> NDArray[np.int64]:
        if not 0 < mass <= 1:
            raise ModelError('credible mass must be in (0, 1]')
        order = np.argsort(-self.weights, kind='stable')
        cum = np.cumsum(self.weights[order])
        return np.sort(order[:int(np.searchsorted(cum, mass - 1e-12) + 1)])


@dataclass(frozen=True)
class Selection:
    """Auditable outcome of one conservative selection."""
    chosen: str
    incumbent: str
    expected_loss: Mapping[str, float]
    expected_advantage: Mapping[str, float]
    degradation_probability: Mapping[str, float]
    worst_credible_degradation: Mapping[str, float]
    admissible: tuple[str, ...]
    reason: str


def model_losses(spec: TaskSpec, models: ModelSet, policy: Policy) -> NDArray[np.float64]:
    """Exact expected cumulative loss of ``policy`` under each fixed model index."""
    return np.array([ExactEvaluator(spec, models.one_model(i), policy).as_dict()['loss']
                     for i in range(len(models.names))])


class AdaptiveController:
    """Retain an incumbent policy unless posterior evidence supports a switch.

    ``candidates`` maps names to factories ``f(posterior_models) -> policy``. Each
    candidate is evaluated exactly under every model index; the controller
    chooses the admissible candidate with the largest posterior expected
    advantage, where admissible means

        E_w[Delta] > margin   and   P_w(Delta < -tolerance) <= alpha,
        Delta_m = L_m(incumbent) - L_m(candidate).

    With ``relative=True`` both ``tolerance`` and ``margin`` are fractions of the
    incumbent's posterior expected loss. With ``alpha = 1`` and ``margin = -inf``
    the rule reduces to posterior-risk minimisation over the candidate set.
    """

    def __init__(self, spec: TaskSpec, models: ModelSet, incumbent: Policy,
                 candidates: Mapping[str, Callable[[ModelSet], Policy]],
                 alpha: float = .1, tolerance: float = 0., margin: float = 0.,
                 credible_mass: float = .9, incumbent_name: str = 'nominal',
                 relative: bool = False):
        if not 0 <= alpha <= 1 or tolerance < 0:
            raise ModelError('alpha must be in [0,1] and tolerance nonnegative')
        if incumbent_name in candidates:
            raise ModelError('candidate names must differ from the incumbent name')
        self.spec = spec; self.belief = EpisodeBelief(models)
        self.incumbent = incumbent; self.incumbent_name = incumbent_name
        self.candidates = dict(candidates)
        self.alpha = alpha; self.tolerance = tolerance; self.margin = margin
        self.credible_mass = credible_mass; self.relative = relative
        self._incumbent_losses = model_losses(spec, models, incumbent)

    def select(self) -> tuple[Policy, Selection]:
        w = self.belief.weights; post = self.belief.posterior_models()
        cred = self.belief.credible_set(self.credible_mass)
        inc = self._incumbent_losses
        exp_loss = {self.incumbent_name: float(w @ inc)}
        scale = exp_loss[self.incumbent_name] if self.relative else 1.
        tol, margin = self.tolerance * scale, self.margin * scale
        adv, pdeg, worst, built, ok = {}, {}, {}, {}, []
        for name, factory in self.candidates.items():
            pol = factory(post); built[name] = pol
            lm = model_losses(self.spec, self.belief.models, pol)
            delta = inc - lm
            exp_loss[name] = float(w @ lm); adv[name] = float(w @ delta)
            pdeg[name] = float(w[delta < -tol].sum())
            worst[name] = float(max(0., -delta[cred].min()))
            if adv[name] > margin and pdeg[name] <= self.alpha + 1e-12:
                ok.append(name)
        if ok:
            chosen = max(ok, key=lambda n: (adv[n], n))
            reason = (f'{chosen} lowers posterior expected loss by {adv[chosen]:.4g}; posterior '
                      f'probability of degrading by more than {tol:.4g} is {pdeg[chosen]:.3f} <= {self.alpha:g}.')
            policy = built[chosen]
        else:
            chosen = self.incumbent_name; policy = self.incumbent
            reason = 'No candidate met the posterior improvement and degradation-probability criteria; incumbent retained.'
        return policy, Selection(chosen, self.incumbent_name, exp_loss, adv, pdeg, worst, tuple(ok), reason)

    def update(self, trajectory: Sequence[Step]) -> None:
        self.belief.update(trajectory)


def bayes_factory(spec: TaskSpec, guard: ActionGuard | None = None) -> Callable[[ModelSet], Planner]:
    return lambda post: Planner(spec, post, 'bayes', guard, 'bayes_posterior')


def run_episode(spec: TaskSpec, truth: ModelSet, policy: Policy, latent_u: float,
                outcome_u: NDArray[np.float64]) -> tuple[list[Step], float, dict[str, float]]:
    """Scalar episode simulation with supplied uniforms (common random numbers).

    ``outcome_u`` has shape ``(horizon,)``; the hidden (model, mode) pair is
    drawn once from ``truth.prior`` and never shown to the policy.
    """
    flat = truth.prior.reshape(-1); cdf = np.cumsum(flat); cdf[-1] = 1.
    hidden = int(np.searchsorted(cdf, latent_u, side='right'))
    k = truth.kernels.reshape(-1, 3, 4)[hidden]
    state = State(); traj: list[Step] = []; loss = 0.
    info = {'success': 0., 'severe': 0., 'human': 0., 'stop': 0., 'ordinary_failure': 0.}
    for t in range(spec.horizon + 1):
        term = spec.terminal_loss(state)
        if term is not None:
            loss += term; info['success' if term == 0 else 'ordinary_failure'] = 1.; break
        a = policy.action(state)
        if a == Action.STOP:
            loss += spec.stop_loss; info['stop'] = 1.; break
        loss += spec.cost(a)
        c = np.cumsum(k[int(a)]); c[-1] = 1.
        o = int(np.sum(outcome_u[t] >= c)); traj.append((a, o))
        if a == Action.HUMAN:
            info['human'] = 1.
        if o == 1:
            loss += spec.catastrophe_loss; info['severe'] = 1.; break
        if a == Action.HUMAN:
            if o == 0: info['success'] = 1.
            else: loss += spec.failure_loss; info['ordinary_failure'] = 1.
            break
        state = state.next(a, o)
    return traj, loss, info
