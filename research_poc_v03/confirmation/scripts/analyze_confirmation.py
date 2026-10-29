"""Pre-registered analysis of the candidate-A confirmation (PRE_REGISTERED_PROTOCOL.md sections 5-7).

    python research_poc_v03/confirmation/scripts/analyze_confirmation.py confirm
"""
from __future__ import annotations
from pathlib import Path
import csv, json, sys
import numpy as np

CONF = Path(__file__).resolve().parents[1]
CFG = json.loads((CONF / 'configs/confirmation.json').read_text(encoding='utf-8'))
B = CFG['bootstrap']['resamples']; PRIMARY = tuple(CFG['primary']['target_distribution']); MARGIN = CFG['loss_noninferiority']['margin']
CAND, COMP = 'A_prev', 'bayes_recal'


def load(split):
    rows = list(csv.DictReader((CONF / 'results' / split / 'summary.csv').open(encoding='utf-8')))
    by = {(int(r['seed']), r['policy']): r for r in rows}
    seeds = sorted({int(r['seed']) for r in rows}); kind = {int(r['seed']): r['kind'] for r in rows}
    sub = {int(r['seed']): r['subtype'] for r in rows}
    return rows, by, seeds, kind, sub


class Boot:
    """Paired bootstrap over environments, stratified by kind; kinds weighted equally."""

    def __init__(self, groups, seed):
        rng = np.random.default_rng(seed)
        self.groups = groups; self.idx = {g: rng.integers(0, len(s), (B, len(s))) for g, s in groups.items()}

    def mean(self, val):          # val: seed -> float ; returns (point, resamples)
        pts, res = [], np.zeros(B)
        for g, s in self.groups.items():
            v = np.array([val(x) for x in s]); pts.append(v.mean()); res += v[self.idx[g]].mean(1)
        return float(np.mean(pts)), res / len(self.groups)


def ci(res):
    return [float(np.quantile(res, .025)), float(np.quantile(res, .975))]


def compare(by, groups, cand, comp, boot_seed):
    bt = Boot(groups, boot_seed)
    g = lambda p, k: (lambda s: float(by[(s, p)][k]))
    sA, rA = bt.mean(g(cand, 'exact_severe')); sR, rR = bt.mean(g(comp, 'exact_severe'))
    lA, qA = bt.mean(g(cand, 'cum_exact_loss')); lR, qR = bt.mean(g(comp, 'cum_exact_loss'))
    rel, rrel = bt.mean(lambda s: float(by[(s, cand)]['cum_exact_loss']) / float(by[(s, comp)]['cum_exact_loss']) - 1)
    n = sum(len(v) for v in groups.values())
    return {'n_env': n, 'severe_cand': sA, 'severe_comp': sR,
            'ARD': sA - sR, 'ARD_ci95': ci(rA - rR), 'RRR': 1 - sA / sR, 'RRR_ci95': ci(1 - rA / rR),
            'loss_ratio_minus_1': lA / lR - 1, 'loss_ratio_ci95': ci(qA / qR - 1),
            'loss_mean_rel_diff': rel, 'loss_mean_rel_diff_ci95': ci(rrel),
            'expected_severe_events_cand': sA * n * CFG['episodes_per_stream'], 'expected_severe_events_comp': sR * n * CFG['episodes_per_stream']}


def main(split):
    rows, by, seeds, kind, sub = load(split)
    kinds = list(dict.fromkeys(kind[s] for s in seeds)); pols = list(dict.fromkeys(r['policy'] for r in rows))
    grp = lambda ks: {k: [s for s in seeds if kind[s] == k] for k in ks}
    seed0 = CFG['bootstrap']['seed']
    out = {'split': split, 'n_env': len(seeds), 'per_kind_n': {k: len(v) for k, v in grp(kinds).items()},
           'episodes_per_policy': len(seeds) * CFG['episodes_per_stream']}
    # ---- primary and non-inferiority (target distribution)
    prim = compare(by, grp(PRIMARY), CAND, COMP, seed0); out['primary'] = prim
    # ---- per kind / per subtype, A versus each comparator and diagnostics versus bayes_recal
    out['per_kind'] = {}
    for k in kinds:
        out['per_kind'][k] = {ref: compare(by, grp([k]), CAND, ref, seed0) for ref in ('bayes_recal', 'handoffx_v2', 'nominal')}
        out['per_kind'][k]['diagnostics_vs_bayes_recal'] = {d: compare(by, grp([k]), d, COMP, seed0) for d in ('A_static_diag', 'recal_trueprev_diag')}
    out['per_subtype'] = {}
    for k in PRIMARY:
        for st in sorted({sub[s] for s in seeds if kind[s] == k}):
            gs = {st: [s for s in seeds if kind[s] == k and sub[s] == st]}
            out['per_subtype'][f'{k}/{st}'] = {d: compare(by, gs, d, COMP, seed0) for d in (CAND, 'A_static_diag', 'recal_trueprev_diag')}
    out['target_vs_other'] = {ref: compare(by, grp(PRIMARY), CAND, ref, seed0) for ref in ('handoffx_v2', 'nominal', 'oracle')}
    out['target_diagnostics'] = {d: compare(by, grp(PRIMARY), d, COMP, seed0) for d in ('A_static_diag', 'recal_trueprev_diag')}
    # ---- behaviour, safeguards, mechanism metrics (means per kind and on target)
    keys = ('exact_severe', 'exact_success', 'exact_human', 'exact_stop', 'exact_retries', 'exact_excess_handoff', 'exact_decision_regret',
            'sev_continue', 'sev_retry', 'sev_human', 'sev_off_oracle', 'stop_off_oracle', 'human_off_oracle', 'realized_severe',
            'last20_exact_severe', 'prev_tv_error', 'prev_tv_error_supplied', 'persistent_share_est', 'persistent_share_true',
            'cal_err_ai', 'cal_err_human', 'ai_root_bias_signed', 'human_root_bias_signed', 'seconds', 'mean_exact_loss')
    def means(ss):
        return {p: {k: float(np.mean([float(by[(s, p)][k]) for s in ss])) for k in keys} for p in pols}
    out['behaviour'] = {k: means(v) for k, v in grp(kinds).items()}
    out['behaviour']['TARGET'] = means([s for s in seeds if kind[s] in PRIMARY])
    out['realized_severe_events'] = {p: int(round(sum(float(by[(s, p)]['realized_severe']) * CFG['episodes_per_stream'] for s in seeds))) for p in pols}
    # ---- mechanism: per-environment association of severe change with predictive changes (target)
    ts = [s for s in seeds if kind[s] in PRIMARY]
    d = lambda k: np.array([float(by[(s, CAND)][k]) - float(by[(s, COMP)][k]) for s in ts])
    def spearman(x, y):
        rx, ry = np.argsort(np.argsort(x)), np.argsort(np.argsort(y)); return float(np.corrcoef(rx, ry)[0, 1])
    dS = d('exact_severe')
    out['mechanism_association'] = {f'spearman(dSevere, d{k})': spearman(dS, d(k)) for k in
                                    ('prev_tv_error', 'cal_err_ai', 'cal_err_human', 'exact_human', 'exact_retries', 'exact_stop', 'sev_continue', 'sev_retry', 'sev_human')}
    out['severe_change_by_action_target'] = {k: float(d(k).mean()) for k in ('sev_continue', 'sev_retry', 'sev_human', 'sev_off_oracle')}
    # ---- frozen decision rule
    fam = {k: out['per_kind'][k]['bayes_recal'] for k in PRIMARY}
    primary_ok = prim['ARD_ci95'][1] < 0 and prim['RRR'] >= .10
    ni_ok = prim['loss_ratio_ci95'][1] < MARGIN
    ni_fail = prim['loss_ratio_ci95'][0] > MARGIN
    robust_ok = all(f['ARD'] < 0 and f['RRR'] >= .05 for f in fam.values()) and out['per_kind']['hazard_shift']['bayes_recal']['ARD_ci95'][0] <= 0
    one_family = any(f['ARD'] >= 0 for f in fam.values())
    sev_harm = [k for k in kinds if out['per_kind'][k]['bayes_recal']['ARD_ci95'][0] > 0]
    loss_harm = [k for k in kinds if out['per_kind'][k]['bayes_recal']['loss_ratio_ci95'][0] > .01]
    not_replicated = prim['ARD_ci95'][1] >= 0 and prim['RRR'] < .05
    if not_replicated or ni_fail or one_family or sev_harm:
        decision = 'NO-GO'
    elif primary_ok and ni_ok and robust_ok and not loss_harm:
        decision = 'GO'
    else:
        decision = 'CONDITIONAL GO'
    out['decision'] = {'decision': decision, 'primary_ok': primary_ok, 'noninferiority_ok': ni_ok, 'noninferiority_clearly_failed': ni_fail,
                       'robustness_ok': robust_ok, 'benefit_in_one_family_only': one_family, 'kinds_with_significant_severe_increase': sev_harm,
                       'kinds_with_loss_increase_lower_bound_above_1pct': loss_harm, 'not_replicated': not_replicated}
    (CONF / 'results' / split / 'analysis.json').write_text(json.dumps(out, indent=1) + '\n', encoding='utf-8')
    return out


if __name__ == '__main__':
    o = main(sys.argv[1] if len(sys.argv) > 1 else 'confirm')
    print(json.dumps(o['decision'], indent=1))
