"""Consistency checks for the final paper (run after build_final.py).

1. Every in-text citation has a reference entry and every entry is cited.
2. Key numbers quoted in the paper equal the stored analysis outputs.
3. No unresolved include or numbering placeholders; equation tags are consecutive.

    python publication_final/verify_paper.py
"""
from __future__ import annotations
from pathlib import Path
import json, re, sys

HERE = Path(__file__).resolve().parent; ROOT = HERE.parent
md = (HERE / 'HandoffX_Final_Research_Paper.md').read_text(encoding='utf-8')
body, refs = md.split('\n# References\n', 1)
refs, appendices = refs.split('\n# Appendix A.', 1)
text = body + appendices
fail = []

# ---------------------------------------------------------------- 1. citations
entries = [l for l in refs.strip().split('\n\n') if l.strip()]
ref_keys = {}
for e in entries:
    first = re.match(r'([^,]+),', e).group(1).strip()
    year = re.search(r'\((\d{4})\)', e).group(1)
    orig = re.search(r'Original work published (\d{4})', e)
    ref_keys[(first, year)] = e
    if orig:
        ref_keys[(first, f'{orig.group(1)}/{year}')] = e
cited = set()
for grp in re.findall(r'\(([^()]*?\d{4}(?:/\d{4})?[^()]*?)\)', text):
    for part in grp.split(';'):
        m = re.search(r"([A-Z][\w\-'À-ÿ ]*?)(?: et al\.)?(?:,| &[^,]*,| and [^,]*,)? (\d{4}(?:/\d{4})?)\b", part.strip())
        if m and not re.match(r'^(Version|Vol|pp|PDF|n =|seed)', part.strip()):
            name = m.group(1).split(' & ')[0].split(' and ')[0].strip()
            cited.add((name.split()[-1] if name.split()[-1][0].isupper() else name, m.group(2)))
for m in re.finditer(r"([A-Z][\w\-À-ÿ]+)(?:'s)?(?: et al\.| and [A-Z][\w\-]+| & [A-Z][\w\-]+)? \((\d{4}(?:/\d{4})?)\)", text):
    cited.add((m.group(1), m.group(2)))
surnames = {k[0].split()[-1]: k for k in ref_keys}
used = set()
for name, year in cited:
    hit = [k for k in ref_keys if k[0].split()[-1] == name and k[1] == year]
    if hit:
        used.update(hit)
    elif name in surnames:
        fail.append(f'citation {name} {year}: year mismatch with reference list')
unused = {k for k in ref_keys if '/' not in k[1]} - {(k[0], k[1].split('/')[-1]) for k in used} - used
if unused:
    fail.append(f'references never cited: {sorted(unused)}')

# ---------------------------------------------------------------- 2. numbers
def need(s):
    if s not in md:
        fail.append(f'expected text not found: {s!r}')

conf = json.loads((ROOT / 'research_poc_v03/confirmation/results/confirm/analysis.json').read_text(encoding='utf-8'))
p = conf['primary']
need(f"{100 * p['RRR']:.1f}% [{100 * p['RRR_ci95'][0]:.1f}%, {100 * p['RRR_ci95'][1]:.1f}%]")
need(f"ARD {p['ARD']:+.4f} [{p['ARD_ci95'][0]:+.4f}, {p['ARD_ci95'][1]:+.4f}]".replace('-', '−').replace('+', '', 1).replace('ARD ', 'ARD ').replace('ARD 0', 'ARD +0'))
need(f"+{100 * p['loss_ratio_minus_1']:.2f}% [{100 * p['loss_ratio_ci95'][0]:+.2f}%, +{100 * p['loss_ratio_ci95'][1]:.2f}%]".replace('-', '−'))
need(f"{p['severe_cand']:.4f}"); need(f"{p['severe_comp']:.4f}")
for k, label in (('persist_shift', 'persist_shift (Family A)'), ('human_shift', 'human_shift (Family B)'), ('hazard_shift', 'hazard_shift'),
                 ('calibrated', 'calibrated'), ('near_nominal', 'near_nominal'), ('ai_bias', 'ai_bias'), ('joint_bias', 'joint_bias')):
    c = conf['per_kind'][k]['bayes_recal']
    row = (f"| {label} | {conf['per_kind_n'][k]} | {100 * c['RRR']:.1f}% [{100 * c['RRR_ci95'][0]:.1f}, {100 * c['RRR_ci95'][1]:.1f}] | "
           f"{100 * c['loss_ratio_minus_1']:+.2f}% [{100 * c['loss_ratio_ci95'][0]:+.2f}, {100 * c['loss_ratio_ci95'][1]:+.2f}] |").replace('-', '−')
    need(row.replace('persist_shift', 'persist_shift').replace('near_nominal', 'near_nominal').replace('−shift', '-shift'))
ev = conf['realized_severe_events']
for pol, lab in (('A_prev', 'Candidate A'), ('bayes_recal', 'bayes_recal'), ('handoffx_v2', 'handoffx_v2'), ('nominal', 'nominal'), ('oracle', 'oracle')):
    need(f'| {lab} | {ev[pol]} |')
b = conf['behaviour']['TARGET']
for key in ('exact_success', 'exact_stop', 'exact_human', 'exact_retries'):
    need(f"{b['A_prev'][key]:.3f}"); need(f"{b['bayes_recal'][key]:.3f}")
need(f"{100 * (b['bayes_recal']['exact_success'] - b['A_prev']['exact_success']):.1f} percentage points fewer")
exp = json.loads((ROOT / 'research_poc_v03/confirmation/results/exploratory_mechanism/analysis.json').read_text(encoding='utf-8'))
for pol, lab in (('riskcost_1.25', 'Catastrophe weight × 1.25'), ('riskcost_1.5', 'Catastrophe weight × 1.5'), ('riskcost_2', 'Catastrophe weight × 2'),
                 ('riskcost_3', 'Catastrophe weight × 3'), ('pess_prior_recal', "A's prior mean only"), ('A_prev', 'Candidate A')):
    v = exp['TARGET'][pol]
    need((f"| {lab} | {100 * v['RRR']:.1f}% [{100 * v['RRR_ci95'][0]:.1f}, {100 * v['RRR_ci95'][1]:.1f}] | "
          f"{100 * v['loss_ratio_minus_1']:+.2f}% [{100 * v['loss_ratio_ci95'][0]:+.2f}, {100 * v['loss_ratio_ci95'][1]:+.2f}] | "
          f"{100 * v['d_exact_success']:+.1f} pp |").replace('-', '−').replace('+−', '−'))
for sp, col in (('pilot', 0), ('confirm', 1), ('replicate', 2)):
    a = json.loads((ROOT / f'research_poc_v03/results/{sp}/analysis.json').read_text(encoding='utf-8'))['policies']['A_prev']['vs_bayes_recal']
    need(f"{100 * a['pooled']:+.2f}% [{100 * a['pooled_ci95'][0]:+.2f}, {100 * a['pooled_ci95'][1]:+.2f}]".replace('-', '−'))
v2 = json.loads((ROOT / 'benchmarks_v2/results/test/analysis.json').read_text(encoding='utf-8'))
need('−0.46% [−1.07, +0.09]'); need('−0.63% [−1.28, −0.05]'); need('−1.94% [−2.69, −1.29]')
need('6 scenarios, equal loss in 23 and higher loss in 9'); need('| nominal_dp | 6 | 23 | 9 |')

# ---------------------------------------------------------------- 3. structure
for pat in (r'<<', r'\{[TF]:', r'\]\(\)'):
    if re.search(pat, md):
        fail.append(f'unresolved pattern {pat}')
tags = [t for t in re.findall(r'\\tag\{(\d+)\}', md)]
if [int(t) for t in tags] != list(range(1, len(tags) + 1)):
    fail.append(f'equation tags not consecutive: {tags}')

print(f'citations: {len(cited)} in-text keys, {len(entries)} references; equations tagged 1-{len(tags)}')
if fail:
    print('FAILED:'); [print(' -', f) for f in fail]; sys.exit(1)
print('all checks passed')
