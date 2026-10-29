"""Regenerate result summaries and six plots from preserved numerical records."""
from pathlib import Path
import csv,json,sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'05_Experiments/results/main'; F=ROOT/'05_Experiments/figures';F.mkdir(exist_ok=True)
def rows(name):
    with (P/name).open(newline='',encoding='utf-8') as f:return list(csv.DictReader(f))
s=rows('summary.csv');e=rows('paired_effects.csv');b=rows('robust_bound_checks.csv');r=rows('robust_objective_evaluation.csv')
lookup={(x['scenario'],x['policy']):x for x in s}
def number(row,key):return float(row[key])
def save(fig,name):
    fig.tight_layout();fig.savefig(F/(name+'.png'),dpi=180,bbox_inches='tight');fig.savefig(F/(name+'.svg'),bbox_inches='tight');plt.close(fig)
# One axes per chart; default matplotlib colors only.
f=plt.figure(figsize=(8,6.5));ax=f.add_subplot(111)
q=[x for x in e if x['comparator']=='nominal_dp' and abs(number(x,'loss_difference_exact'))>1e-9]
labels=[x['scenario'].replace('low_hazard__','low hazard: ').replace('__',' / ').replace('_',' ') for x in q]
y=np.arange(len(q));mean=np.array([number(x,'paired_difference_mean') for x in q]);lo=np.array([number(x,'paired_ci_low') for x in q]);hi=np.array([number(x,'paired_ci_high') for x in q])
ax.errorbar(mean,y,xerr=np.array([mean-lo,hi-mean]),fmt='o',capsize=3,label='Paired simulation mean and 95% interval')
ax.plot([number(x,'loss_difference_exact') for x in q],y,'x',label='Exact expectation');ax.axvline(0,linestyle='--');ax.set_yticks(y,labels,fontsize=10);ax.invert_yaxis();ax.set_xlabel('HandoffX Bayes loss minus nominal-DP loss');ax.legend(fontsize=10,loc='lower left');save(f,'figure_01_paired_effects')
f=plt.figure(figsize=(8,5));ax=f.add_subplot(111)
policies=sorted(set(x['policy'] for x in s),key=lambda p:np.mean([number(x,'loss_exact') for x in s if x['policy']==p]))
means=[np.mean([number(x,'loss_exact') for x in s if x['policy']==p]) for p in policies]
ax.barh(policies,means);ax.invert_yaxis();ax.set_xlabel('Unweighted mean exact loss across 38 designed scenarios');save(f,'figure_02_design_means')
f=plt.figure(figsize=(7.5,4.5));ax=f.add_subplot(111)
for pn in ('handoffx_bayes','nominal_dp','robust_dp','bayes_independent','oracle'):
    vals=[number(lookup[('low_hazard__ai_calibrated__human_'+tag,pn)],'loss_exact') for tag in ('under','calibrated','over')]
    ax.plot([-.18,0,.18],vals,marker='o',label=pn)
ax.set_xlabel('Supplied human-success probability bias');ax.set_ylabel('Exact cumulative loss');ax.set_xticks([-.18,0,.18]);ax.legend(fontsize=10);save(f,'figure_03_human_miscalibration')
f=plt.figure(figsize=(7.5,4.5));ax=f.add_subplot(111)
ks=np.arange(7);p=np.array([.8,.05]);w=np.array([.6,.4]);post=np.array([np.sum(w*(1-p)**k*p)/np.sum(w*(1-p)**k) for k in ks])
ax.plot(ks,post,marker='o',label='Persistent-mode posterior recovery probability');ax.plot(ks,np.full(7,.5),linestyle='--',label='Independently resampled mean');ax.set_xlabel('Consecutive failed attempts');ax.set_ylabel('Next-attempt success probability');ax.legend(fontsize=10);save(f,'figure_04_retry_dependence')
f=plt.figure(figsize=(8,4.8));ax=f.add_subplot(111)
sel=['ai_calibrated__human_calibrated','low_hazard__ai_calibrated__human_calibrated','shift_unrecalibrated','shift_perfect_recalibration']
bs={x['scenario']:x for x in b};ys=np.arange(len(sel));width=.25
ax.barh(ys-width,[number(bs[x],'root_envelope_value') for x in sel],height=width,label='Reported envelope')
ax.barh(ys,[number(bs[x],'worst_supported_fixed_model_loss') for x in sel],height=width,label='Worst supported fixed model')
ax.barh(ys+width,[number(bs[x],'true_environment_loss') for x in sel],height=width,label='True generating environment')
ax.set_yticks(ys,['Calibrated base','Calibrated low hazard','Shift, stale parameters','Shift, exact refresh']);ax.set_xlabel('Robust-policy expected loss / bound');ax.invert_yaxis();ax.legend(fontsize=10);save(f,'figure_05_robust_coverage')
f=plt.figure(figsize=(8,4.8));ax=f.add_subplot(111)
pns=['static_loss','nominal_dp','handoffx_bayes','robust_dp']
ax.boxplot([[number(x,'cold_root_seconds')*1000 for x in s if x['policy']==p] for p in pns],tick_labels=pns,showfliers=True)
ax.set_ylabel('Cold root-decision time (milliseconds)');ax.set_xlabel('Measured Linux host; distributions across 38 scenarios');save(f,'figure_06_runtime')
counts={}
for comp in sorted(set(x['comparator'] for x in e)):
    d=np.array([number(x,'loss_difference_exact') for x in e if x['comparator']==comp])
    counts[comp]={'lower':int((d< -1e-9).sum()),'equal':int((abs(d)<=1e-9).sum()),'higher':int((d>1e-9).sum()),'mean_difference':float(d.mean()),'minimum_difference':float(d.min()),'maximum_difference':float(d.max())}
# Compare objective-aligned criteria, separately from expected-loss comparisons.
rlookup={(x['scenario'],x['policy']):x for x in r};worse_fixed=0;better_fixed=0;equal_fixed=0
for name in sorted(set(x['scenario'] for x in s)):
    d=number(rlookup[(name,'robust_dp')],'worst_supported_fixed_loss')-number(rlookup[(name,'handoffx_bayes')],'worst_supported_fixed_loss')
    worse_fixed+=d>1e-9;better_fixed+=d< -1e-9;equal_fixed+=abs(d)<=1e-9
stats={'comparisons':counts,'design_means':dict(zip(policies,means)),'raw_episode_count':sum(int(x['episodes']) for x in s),
       'mean_interval_contains_exact':sum(number(x,'loss_ci_low')-1e-10<=number(x,'loss_exact')<=number(x,'loss_ci_high')+1e-10 for x in s),
       'rectangular_robust_vs_bayes_worst_fixed':{'lower':int(better_fixed),'equal':int(equal_fixed),'higher':int(worse_fixed)},
       'largest_rectangularization_gap':max(number(x,'rectangularization_gap') for x in b),
       'model_coverage_bound_failures':[x['scenario'] for x in b if x['true_loss_within_bound']=='False'],
       'candidate_cold_median_ms':float(np.median([number(x,'cold_root_seconds')*1000 for x in s if x['policy']=='handoffx_bayes'])),
       'candidate_cached_median_us':float(np.median([number(x,'cached_call_seconds')*1e6 for x in s if x['policy']=='handoffx_bayes']))}
(ROOT/'05_Experiments/results/analysis_summary.json').write_text(json.dumps(stats,indent=2)+'\n')
# Full transparent per-scenario comparison, no row selection by significance.
md='# Complete exact-loss table\n\nValues are artificial loss units. Every row is a deliberately chosen synthetic environment; rows are not a sample of real deployments.\n\n'
md+='| Scenario | Bayes | Nominal | Robust | Oracle |\n|---|---:|---:|---:|---:|\n'
for name in json.loads((ROOT/'05_Experiments/configs/study.json').read_text())['scenario_names']:
    md+='| '+name+' | '+' | '.join(f"{number(lookup[(name,p)],'loss_exact'):.6f}" for p in ('handoffx_bayes','nominal_dp','robust_dp','oracle'))+' |\n'
(ROOT/'05_Experiments/results/ALL_SCENARIOS.md').write_text(md)
print(json.dumps(stats,indent=2))
if __name__=='__main__':pass
