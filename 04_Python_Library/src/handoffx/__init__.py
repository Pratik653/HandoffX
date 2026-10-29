"""HandoffX: auditable continue/retry/human/stop decision support for autonomous agents.

Research-stage software. It recommends; it never executes actions or overrides
external authorization. No real-world safety certification is claimed.
"""
from .models import Action, State, TaskSpec, ModelSet, ModelError, TerminalStateError
from .policies import Planner, Baseline, ActionGuard, Decision, recommend_or_stop
from .adaptive import AdaptiveController, EpisodeBelief, Selection, episode_log_likelihood
from .advisor import Advisor, Costs, Recommendation, history_to_state
__version__ = '0.2.0'
__all__ = ['Action', 'State', 'TaskSpec', 'ModelSet', 'ModelError', 'TerminalStateError',
           'Planner', 'Baseline', 'ActionGuard', 'Decision', 'recommend_or_stop',
           'AdaptiveController', 'EpisodeBelief', 'Selection', 'episode_log_likelihood',
           'Advisor', 'Costs', 'Recommendation', 'history_to_state', '__version__']
