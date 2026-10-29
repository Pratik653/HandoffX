"""HandoffX controlled agent demonstration: order-delay investigation on SQLite.

A small, deterministic, rule-based agent investigates delayed orders in a local
SQLite database. Each task has two milestones: (1) look up the order and its
shipment, (2) obtain the carrier status. The carrier tool is unreliable in
controlled, labelled ways (transient timeouts, a persistent outage, a permission
restriction). Before every step the agent asks HandoffX whether to continue,
retry, request human assistance or stop, and logs each finished task so the
advisor recalibrates across tasks.

Everything is SIMULATED: the "human" is a seeded random helper with a fixed
success rate, not a person, and the tool failures are injected. This shows the
integration pattern and the decision logic; it is not evidence about real
operators, real LLM agents or real carriers. No network access, no paid APIs.

    python demo/runnable_examples/order_agent_demo.py [--tasks 30] [--seed 7] [--quiet]
"""
from __future__ import annotations
import argparse, random, sqlite3
from handoffx import Advisor, Costs

SCHEMA = """
CREATE TABLE orders(id INTEGER PRIMARY KEY, customer TEXT, promised_day INTEGER);
CREATE TABLE shipments(order_id INTEGER, carrier TEXT, tracking TEXT);
CREATE TABLE carrier_events(tracking TEXT, day INTEGER, status TEXT);
"""


class ToolError(Exception):
    def __init__(self, kind: str, message: str):
        super().__init__(message); self.kind = kind  # 'soft' = no diagnosis, 'hard' = explicit error signal


def build_db(rng: random.Random, n: int) -> sqlite3.Connection:
    db = sqlite3.connect(':memory:'); db.executescript(SCHEMA)
    for i in range(1, n + 1):
        carrier = rng.choice(['NorthFreight', 'BlueParcel', 'RapidRoute'])
        db.execute('INSERT INTO orders VALUES (?,?,?)', (i, f'customer-{i:03d}', rng.randint(3, 9)))
        if rng.random() > .1:  # 10% of orders have missing shipment data
            db.execute('INSERT INTO shipments VALUES (?,?,?)', (i, carrier, f'TRK{i:05d}'))
            db.execute('INSERT INTO carrier_events VALUES (?,?,?)', (f'TRK{i:05d}', rng.randint(1, 12),
                                                                     rng.choice(['in_transit', 'held_at_depot', 'delivered'])))
    return db


class Environment:
    """Injected tool behaviour for one task (hidden from the agent)."""

    def __init__(self, rng: random.Random, db: sqlite3.Connection, order_id: int):
        self.rng, self.db, self.order_id = rng, db, order_id
        r = rng.random()
        self.condition = 'outage' if r < .15 else 'permission' if r < .22 else 'normal'

    def lookup(self):
        if self.rng.random() < .08:
            raise ToolError('soft', 'database busy (timeout)')
        row = self.db.execute('SELECT o.id, s.carrier, s.tracking FROM orders o LEFT JOIN shipments s '
                              'ON s.order_id = o.id WHERE o.id = ?', (self.order_id,)).fetchone()
        if row[2] is None:
            raise ToolError('hard', 'shipment record missing')
        return row

    def carrier_status(self, tracking: str):
        if self.condition == 'outage' and self.rng.random() < .9:
            raise ToolError('hard', 'carrier API 503 service unavailable')
        if self.condition == 'permission':
            raise ToolError('hard', 'carrier API 403 forbidden for this account')
        if self.rng.random() < .15:
            raise ToolError('soft', 'carrier API timeout')
        return self.db.execute('SELECT status, day FROM carrier_events WHERE tracking = ?', (tracking,)).fetchone()

    def simulated_human(self) -> bool:
        # SIMULATED helper: resolves 85% of escalations, independent of the failure type.
        return self.rng.random() < .85


class Heuristic:
    """Baseline agents with the same interface as Advisor.recommend().action."""

    def __init__(self, kind: str, spec):
        self.kind, self.spec = kind, spec

    def recommend(self, history):
        failed = bool(history) and history[-1][1] != 'success'
        if self.kind == 'always_continue':
            return 'continue'
        consecutive = 0
        for _, o in reversed(history):
            if o == 'success': break
            consecutive += 1
        if not failed:
            return 'continue'
        return 'retry' if consecutive < 2 else 'human'  # retry-twice-then-escalate

    def record_episode(self, steps):
        pass


def task_loss(spec, steps, result):
    cost = {'continue': spec.action_cost[0], 'retry': spec.action_cost[1], 'human': spec.action_cost[2]}
    loss = sum(cost[a] + spec.time_price for a, _ in steps if a in cost)
    if result.startswith('stopped'):
        loss += spec.stop_loss
    elif result.startswith(('escalated', 'deadline')):
        loss += spec.failure_loss
    return loss


def run_task(adv, env: Environment, verbose: bool) -> tuple[list, str]:
    steps, history, found = [], [], None
    milestone = 0
    for _ in range(adv.spec.horizon):
        if isinstance(adv, Heuristic):
            from types import SimpleNamespace
            rec = SimpleNamespace(action=adv.recommend(history))
        else:
            rec = adv.recommend(history)
        if verbose:
            print(f'    advisor -> {rec.action:8s} (policy {rec.policy}; '
                  + ', '.join(f'{a}={v:.2f}' for a, v in sorted(rec.expected_loss.items(), key=lambda kv: kv[1])) + ')')
        if rec.action == 'stop':
            steps.append(('stop', 'success')); return steps, 'stopped safely'
        if rec.action == 'retry' and not history:
            rec.action = 'continue'
        if rec.action == 'human':
            ok = env.simulated_human(); steps.append(('human', 'success' if ok else 'soft_failure'))
            return steps, 'resolved by (simulated) human' if ok else 'escalated, unresolved'
        try:
            if milestone == 0:
                found = env.lookup()
            else:
                status = env.carrier_status(found[2])
            outcome = 'success'
        except ToolError as e:
            outcome = 'hard_failure' if e.kind == 'hard' else 'soft_failure'
            if verbose:
                print(f'      tool error: {e}')
        steps.append((rec.action, outcome)); history.append((rec.action, outcome))
        if outcome == 'success':
            milestone += 1
            if milestone == adv.spec.milestones:
                return steps, f'completed autonomously: {status[0]} (day {status[1]})'
    return steps, 'deadline reached'


def main(argv=None):
    ap = argparse.ArgumentParser(); ap.add_argument('--tasks', type=int, default=30)
    ap.add_argument('--seed', type=int, default=7); ap.add_argument('--quiet', action='store_true')
    ap.add_argument('--compare', action='store_true', help='also run heuristic agents on the same seeded tasks')
    a = ap.parse_args(argv)
    if a.compare:
        return compare(a.tasks, a.seed)
    rng = random.Random(a.seed); db = build_db(rng, a.tasks)
    adv = make_advisor()
    tally = {}
    print('HandoffX order-agent demo (simulated tools and simulated human; see module docstring)\n')
    for t in range(1, a.tasks + 1):
        env = Environment(rng, db, t)
        if not a.quiet:
            print(f'Task {t:02d}: investigate order {t} [hidden condition: {env.condition}]')
        steps, result = run_task(adv, env, not a.quiet)
        adv.record_episode(steps)
        key = (env.condition, result.split(':')[0]); tally[key] = tally.get(key, 0) + 1
        if not a.quiet:
            print(f'    result: {result}\n')
    print('Summary by hidden condition and outcome:')
    for (cond, res), n in sorted(tally.items()):
        print(f'  {cond:10s} {res:34s} {n}')
    est = adv.calibrated_estimates()
    print(f"\nRecalibrated first-attempt success estimates after {a.tasks} tasks: "
          f"continue {est['continue_success']:.2f} (supplied .85), human {est['human_success']:.2f} (supplied .80)")
    print('Current policy:', adv.selection.chosen, '-', adv.selection.reason)


def make_advisor():
    # Supplied estimates are deliberately optimistic about the carrier tool.
    return Advisor.from_estimates(continue_success=.85, retry_success=.7, human_success=.8, uncertainty=.15,
                                  persistent_failure_rate=.1, costs=Costs(human=3., failure=15., stop=8.),
                                  horizon=5, human_delay=1)


def compare(tasks: int, seed: int):
    print('Illustrative comparison on identical seeded task conditions (simulated tools and human).')
    print('Tool outcomes are drawn per call, so agents that call tools differently see different draws;')
    print('this is a demonstration, not the benchmark (see benchmarks_v2/).')
    print()
    for name in ('handoffx', 'retry_twice_then_escalate', 'always_continue'):
        agent = make_advisor() if name == 'handoffx' else Heuristic(
            'always_continue' if name == 'always_continue' else 'retry', make_advisor().spec)
        db = build_db(random.Random(seed), tasks); losses, done, human = [], 0, 0
        for t in range(1, tasks + 1):
            env = Environment(random.Random(seed * 100003 + t), db, t)
            steps, result = run_task(agent, env, False); agent.record_episode(steps)
            losses.append(task_loss(agent.spec, steps, result))
            done += result.startswith(('completed', 'resolved')); human += any(a == 'human' for a, _ in steps)
        print(f'  {name:28s} mean loss {sum(losses)/tasks:6.2f}   resolved {done}/{tasks}   escalations {human}')


if __name__ == '__main__':
    main()
