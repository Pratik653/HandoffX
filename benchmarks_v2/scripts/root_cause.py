"""Phase B root-cause analysis of the original nominal-vs-joint-Bayes comparison.

Reads the frozen v0.1 scenario configs (never modified) and decomposes each
non-tied exact loss difference with the performance-difference identity

    L(pi_B) - L(pi_N) = sum_s d_B(s) [Q_N(s, pi_B(s)) - Q_N(s, pi_N(s))],

where d_B is the true state-visit probability under the Bayes policy and Q_N is
the true action value of acting once and then following the nominal policy.
"""
from __future__ import annotations
from pathlib import Path
import csv, json, sys
import numpy as np
from handoffx import Action, State
from handoffx.scenarios import policies, scenario_from_dict
from handoffx.evaluation import ExactEvaluator

ROOT = Path(__file__).resolve().parents[2]
CONF = ROOT / '05_Experiments/configs'
OUT = ROOT / 'benchmarks_v2/results/root_cause'
TOL = 1e-9


def true_q(spec, truth, follow_value, state, action):
    if action == Action.STOP:
        return spec.stop_loss
    p = truth.predict(state)[int(action)]
    q = spec.cost(action) + p[1] * spec.catastrophe_loss
    if action == Action.HUMAN:
        return q + (p[2] + p[3]) * spec.failure_loss
    for o in (0, 2, 3):
        if p[o] > 0:
            q += p[o] * follow_value(state.next(action, o))
    return q


def visit_distribution(spec, truth, policy):
    """Forward pass: probability that the true process reaches each nonterminal state."""
    frontier = {State(): 1.0}; visits = {}
    while frontier:
        nxt = {}
        for s, w in frontier.items():
            if spec.terminal_loss(s) is not None:
                continue
            visits[s] = visits.get(s, 0.0) + w
            a = policy.action(s)
            if a in (Action.STOP, Action.HUMAN):
                continue
            p = truth.predict(s)[int(a)]
            for o in (0, 2, 3):
                if p[o] > 0:
                    t = s.next(a, o); nxt[t] = nxt.get(t, 0.0) + w * p[o]
        frontier = nxt
    return visits


def analyse(name):
    s = scenario_from_dict(json.loads((CONF / f'{name}.json').read_text()))
    spec, truth, models = s['spec'], s['truth'], s['models']
    pp = policies(s, .5, 2)
    bayes, nominal, oracle = pp['handoffx_bayes'], pp['nominal_dp'], pp['oracle']
    ev_n = ExactEvaluator(spec, truth, nominal)
    follow = lambda st: float(ev_n.metrics(st)[0])
    lb = ExactEvaluator(spec, truth, bayes).as_dict()['loss']; ln = follow(State())
    visits = visit_distribution(spec, truth, bayes)
    contributions = []
    for st, w in visits.items():
        ab, an = bayes.action(st), nominal.action(st)
        if ab != an:
            gap = true_q(spec, truth, follow, st, ab) - true_q(spec, truth, follow, st, an)
            contributions.append({'state': list(st.counts) + [int(st.failed)], 'visit_prob': w,
                                  'bayes_action': ab.name.lower(), 'nominal_action': an.name.lower(),
                                  'true_q_gap': gap, 'contribution': w * gap})
    total = sum(c['contribution'] for c in contributions)
    if abs(total - (lb - ln)) > 1e-8:
        raise AssertionError(f'performance-difference identity failed for {name}')
    root_pred = {k: m.predict(State()) for k, m in (('truth', truth), ('nominal', nominal.models), ('bayes', models))}
    return {
        'scenario': name, 'category': s['category'], 'loss_bayes': lb, 'loss_nominal': ln,
        'loss_oracle': oracle.value(), 'difference': lb - ln,
        'relative_difference': (lb - ln) / ln,
        'nominal_gap_to_oracle': ln - oracle.value(),
        'nominal_is_oracle_equivalent': abs(ln - oracle.value()) < TOL,
        'truth_in_model_support': bool(any(np.allclose(truth.kernels[0], models.kernels[i]) for i in range(len(models.names)))) if truth.kernels.shape[0] == 1 else 'mixture',
        'n_divergent_states': len(contributions),
        'p_ai_success_root': {k: float(v[0, 0]) for k, v in root_pred.items()},
        'p_human_success_root': {k: float(v[2, 0]) for k, v in root_pred.items()},
        'divergences': sorted(contributions, key=lambda c: -abs(c['contribution']))[:6],
    }


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    names = json.loads((CONF / 'study.json').read_text())['scenario_names']
    rows = [analyse(n) for n in names]
    (OUT / 'root_cause.json').write_text(json.dumps(rows, indent=2) + '\n')
    flat = [{k: v for k, v in r.items() if not isinstance(v, (dict, list))} for r in rows]
    with (OUT / 'root_cause_summary.csv').open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(flat[0])); w.writeheader(); w.writerows(flat)
    d = np.array([r['difference'] for r in rows])
    print('better/equal/worse (tol 1e-9):', int((d < -TOL).sum()), int((abs(d) <= TOL).sum()), int((d > TOL).sum()))
    for tol in (1e-3, 1e-2, .05):
        print(f'better/equal/worse (tol {tol}):', int((d < -tol).sum()), int((abs(d) <= tol).sum()), int((d > tol).sum()))
    print('sum of losses', d[d > TOL].sum(), 'sum of wins', d[d < -TOL].sum(), 'max relative loss', max(r['relative_difference'] for r in rows))
    print('nominal oracle-equivalent in', sum(r['nominal_is_oracle_equivalent'] for r in rows), 'of', len(rows))
    for r in sorted(rows, key=lambda r: -r['difference']):
        if abs(r['difference']) > TOL:
            dv = r['divergences'][0] if r['divergences'] else {}
            print(f"{r['scenario']:44s} d={r['difference']:+.4f} ({100*r['relative_difference']:+.2f}%) nomOracle={r['nominal_is_oracle_equivalent']!s:5s} "
                  f"pAI t/n/b={r['p_ai_success_root']['truth']:.3f}/{r['p_ai_success_root']['nominal']:.3f}/{r['p_ai_success_root']['bayes']:.3f} "
                  f"pH t/n/b={r['p_human_success_root']['truth']:.3f}/{r['p_human_success_root']['nominal']:.3f}/{r['p_human_success_root']['bayes']:.3f} "
                  f"div={r['n_divergent_states']} top={dv.get('state')} {dv.get('bayes_action')}vs{dv.get('nominal_action')} w={dv.get('visit_prob',0):.3f} gap={dv.get('true_q_gap',0):+.3f}")


if __name__ == '__main__':
    main()
