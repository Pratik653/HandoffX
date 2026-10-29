"""Execute the fixed CPU-only study; --quick writes separate smoke-test results."""
from pathlib import Path
import argparse,csv,datetime,gc,hashlib,importlib.metadata,json,os,platform,sys,time,tracemalloc
import numpy as np
from scipy.stats import t as student_t
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'04_Python_Library/src'))
from handoffx import State,TaskSpec
from handoffx.scenarios import make_scenario,policies,scenario_from_dict,scenario_to_dict,BASE_Q,BASE_P
from handoffx.evaluation import ExactEvaluator,common_randomness,simulate,METRICS
from dataclasses import replace

def csv_write(path,rows):
    path.parent.mkdir(parents=True,exist_ok=True)
    if not rows:raise ValueError('refusing empty result table')
    with path.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def ci(values):
    a=np.asarray(values,float);mean=float(a.mean());se=float(a.std(ddof=1)/np.sqrt(len(a)))
    half=float(student_t.ppf(.975,len(a)-1)*se)
    return mean,mean-half,mean+half,se

def develop(out):
    spec=replace(TaskSpec(),horizon=5,human_available=(True,)*6)
    dev=[make_scenario('dev_standard',spec=spec,true_z=np.array([.55,.30,.15])),
         make_scenario('dev_low_hazard',spec=spec,true_z=np.array([.55,.30,.15]),true_q=BASE_Q*.35),
         make_scenario('dev_high_human_cost',spec=replace(spec,action_cost=(.6,1.4,6.)),true_z=np.array([.40,.35,.25])),
         make_scenario('dev_moderate_human',spec=spec,true_p=np.array([BASE_P[0],BASE_P[1],[.80,.65,.35]]),true_z=np.array([.55,.30,.15]))]
    (out/'development_configs').mkdir(exist_ok=True)
    for s in dev:(out/'development_configs'/(s['name']+'.json')).write_text(json.dumps(scenario_to_dict(s),indent=2)+'\n')
    rows=[]
    for threshold in (.20,.35,.50,.65,.80):
        vals=[ExactEvaluator(s['spec'],s['truth'],policies(s,threshold=threshold)['confidence']).as_dict()['loss'] for s in dev]
        rows.append({'policy':'confidence','setting':threshold,'mean_development_loss':float(np.mean(vals))})
    for limit in (1,2,3):
        vals=[ExactEvaluator(s['spec'],s['truth'],policies(s,retry_limit=limit)['retry_first']).as_dict()['loss'] for s in dev]
        rows.append({'policy':'retry_first','setting':limit,'mean_development_loss':float(np.mean(vals))})
    csv_write(out/'tuning.csv',rows)
    threshold=min((r for r in rows if r['policy']=='confidence'),key=lambda r:(r['mean_development_loss'],r['setting']))['setting']
    retry=int(min((r for r in rows if r['policy']=='retry_first'),key=lambda r:(r['mean_development_loss'],r['setting']))['setting'])
    return threshold,retry

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--quick',action='store_true');args=ap.parse_args()
    started=datetime.datetime.now(datetime.timezone.utc).isoformat();tic=time.perf_counter()
    study=json.loads((ROOT/'05_Experiments/configs/study.json').read_text())
    out=ROOT/'05_Experiments/results'/('quick' if args.quick else 'main');out.mkdir(parents=True,exist_ok=True)
    rawdir=out/'raw';rawdir.mkdir(exist_ok=True);threshold,retry_limit=develop(out)
    seeds=study['seeds'][:2] if args.quick else study['seeds'];episodes=50 if args.quick else study['episodes_per_seed']
    names=study['scenario_names'][:2] if args.quick else study['scenario_names']
    config_hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'05_Experiments/configs').glob('*.json'))}
    source_hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'04_Python_Library/src').rglob('*.py'))}
    metadata={'started_utc':started,'quick':args.quick,'seed_batches':len(seeds),'episodes_per_batch':episodes,
        'scenario_count':len(names),'policy_count':11,'episode_executions':len(names)*11*len(seeds)*episodes,
        'threshold':threshold,'retry_limit':retry_limit,'python':sys.version,'platform':platform.platform(),
        'logical_cpu_count':os.cpu_count(),'cpu_only':True,'config_sha256':config_hashes,'source_sha256':source_hashes,
        'dependencies':{m:importlib.metadata.version(m) for m in ('numpy','scipy','pytest')},
        'thread_limits':{k:os.environ.get(k) for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS')}}
    try:metadata['cpu_model']=next(x.split(':',1)[1].strip() for x in Path('/proc/cpuinfo').read_text().splitlines() if x.startswith('model name'))
    except (OSError,StopIteration):metadata['cpu_model']=platform.processor()
    (out/'run_metadata.json').write_text(json.dumps(metadata,indent=2)+'\n')
    summaries=[];batches=[];effects=[];bounds=[];timings=[];terminal_checks=0
    for si,name in enumerate(names):
        s=scenario_from_dict(json.loads((ROOT/'05_Experiments/configs'/(name+'.json')).read_text()))
        pp=policies(s,threshold,retry_limit);oracle=pp['oracle'];random=common_randomness(seeds,episodes,s['spec'].horizon)
        raw={};exact={};batch_loss={}
        for pname,policy in pp.items():
            fresh=policies(s,threshold,retry_limit)[pname];start=time.perf_counter();fresh.action(State());cold=time.perf_counter()-start
            t0=time.perf_counter()
            if hasattr(fresh,'recommend'):
                for _ in range(1000):fresh.recommend(State())
                api='recommend'
            else:
                for _ in range(1000):fresh.action(State())
                api='action'
            cached=(time.perf_counter()-t0)/1000
            timings.append({'scenario':name,'policy':pname,'cold_root_seconds':cold,'cached_call_seconds':cached,'cached_api':api})
            exact[pname]=ExactEvaluator(s['spec'],s['truth'],policy,oracle).as_dict()
            if exact[pname]['loss']<oracle.value()-1e-8:raise AssertionError('policy beats exact oracle')
            if abs(exact[pname]['decision_regret']-(exact[pname]['loss']-oracle.value()))>1e-7:raise AssertionError('performance difference identity failed')
            data=simulate(s['spec'],s['truth'],policy,random,oracle);raw[pname]=data;terminal_checks+=len(data['loss'])
            storage={k:v.astype(np.float64 if k=='loss' else (np.int16 if k=='batch' else np.float32)) for k,v in data.items()}
            np.savez_compressed(rawdir/f'{name}__{pname}.npz',**storage)
            all_batch=[]
            for bi,seed in enumerate(seeds):
                sl=slice(bi*episodes,(bi+1)*episodes);row={'scenario':name,'policy':pname,'batch':bi,'seed':seed,'episodes':episodes}
                row.update({m:float(data[m][sl].mean()) for m in METRICS})
                row['selected_action_brier']=float(data['brier_sum'][sl].sum()/max(1,data['executed_actions'][sl].sum()))
                batches.append(row);all_batch.append(row['loss'])
            batch_loss[pname]=np.array(all_batch);mean,lo,hi,se=ci(all_batch)
            row={'scenario':name,'category':s['category'],'policy':pname,'episodes':len(data['loss']),
                 'root_action':policy.action(State()).name.lower(),'loss_mean':mean,'loss_ci_low':lo,'loss_ci_high':hi,
                 'loss_se':se,'loss_exact':exact[pname]['loss'],'oracle_excess_loss_exact':exact[pname]['loss']-oracle.value()}
            for m in METRICS[1:]:row[m+'_mean']=float(data[m].mean());row[m+'_exact']=exact[pname][m]
            row['loss_cvar95_empirical']=float(np.sort(data['loss'])[-max(1,int(np.ceil(.05*len(data['loss'])))):].mean())
            row['loss_quantile95_empirical']=float(np.quantile(data['loss'],.95))
            row['selected_action_brier']=float(data['brier_sum'].sum()/max(1,data['executed_actions'].sum()))
            row['time_to_success']=float(data['success_time'].sum()/max(1,data['success'].sum()))
            row['retry_efficiency']=float(data['retry_success'].sum()/max(1,data['retries'].sum()))
            row['cold_root_seconds']=cold;row['cached_call_seconds']=cached;summaries.append(row)
        for comparator in ('nominal_dp','robust_dp','static_loss','bayes_independent','bayes_iid','oracle'):
            mean,lo,hi,se=ci(batch_loss['handoffx_bayes']-batch_loss[comparator])
            effects.append({'scenario':name,'category':s['category'],'candidate':'handoffx_bayes','comparator':comparator,
                'loss_difference_exact':exact['handoffx_bayes']['loss']-exact[comparator]['loss'],
                'paired_difference_mean':mean,'paired_ci_low':lo,'paired_ci_high':hi,'paired_se':se,
                'n_seed_batches':len(seeds),'episodes_per_policy':len(seeds)*episodes})
        robust=pp['robust_dp'];fixed=[ExactEvaluator(s['spec'],s['models'].one_model(i),robust).as_dict()['loss'] for i in range(len(s['models'].names))]
        if max(fixed)>robust.value()+1e-8:raise AssertionError('robust envelope bound failed')
        bounds.append({'scenario':name,'root_envelope_value':robust.value(),'worst_supported_fixed_model_loss':max(fixed),
                       'rectangularization_gap':robust.value()-max(fixed),'true_environment_loss':exact['robust_dp']['loss'],
                       'true_loss_within_bound':bool(exact['robust_dp']['loss']<=robust.value()+1e-8)})
        print(f'{si+1:02d}/{len(names)} {name}: Bayes={exact["handoffx_bayes"]["loss"]:.6f}, nominal={exact["nominal_dp"]["loss"]:.6f}, robust={exact["robust_dp"]["loss"]:.6f}, oracle={oracle.value():.6f}',flush=True)
        csv_write(out/'summary.csv',summaries);csv_write(out/'paired_effects.csv',effects)
        del raw,pp,random;gc.collect()
    csv_write(out/'batch_results.csv',batches);csv_write(out/'robust_bound_checks.csv',bounds);csv_write(out/'timing.csv',timings)
    tracemalloc.start();ms=make_scenario('memory');mp=policies(ms)['handoffx_bayes'];mp.value()
    current,peak=tracemalloc.get_traced_memory();tracemalloc.stop()
    metadata.update({'finished_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'wall_seconds':time.perf_counter()-tic,
        'terminal_partition_checks':terminal_checks,'candidate_python_peak_bytes':peak,'candidate_python_current_bytes':current,
        'all_exact_oracle_checks_passed':True,'all_performance_difference_checks_passed':True,'all_supported_fixed_model_robust_bounds_passed':True})
    try:
        import resource
        metadata['process_max_rss_kib_linux']=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    except ImportError:pass
    (out/'run_metadata.json').write_text(json.dumps(metadata,indent=2)+'\n')
    print('COMPLETE',json.dumps({k:metadata[k] for k in ('episode_executions','wall_seconds','threshold','retry_limit','candidate_python_peak_bytes')}),flush=True)
if __name__=='__main__':main()
