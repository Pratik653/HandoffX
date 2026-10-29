from pathlib import Path
import sys,json,hashlib,datetime
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'04_Python_Library/src'))
from handoffx.scenarios import scenarios,scenario_to_dict

def main():
    conf=ROOT/'05_Experiments/configs';ss=scenarios()
    seeds=[20261028+997*i for i in range(24)]
    study={'design':'18-cell bias/hazard factorial plus 20 sensitivity checks','scenario_names':[s['name'] for s in ss],
           'seeds':seeds,'episodes_per_seed':500,'n_policies':11,'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
           'public_preregistration':False,'primary_metric':'cumulative operational loss','primary_comparison':'handoffx_bayes - nominal_dp'}
    (conf/'study.json').write_text(json.dumps(study,indent=2)+'\n')
    for s in ss:(conf/(s['name']+'.json')).write_text(json.dumps(scenario_to_dict(s),indent=2,allow_nan=False)+'\n')
    items=[ROOT/'05_Experiments/EXPERIMENTAL_PROTOCOL.md',*sorted(conf.glob('*.json'))]
    lines=[hashlib.sha256(p.read_bytes()).hexdigest()+'  '+str(p.relative_to(ROOT)) for p in items]
    (ROOT/'05_Experiments/logs/PRE_RUN_SPECIFICATION_SHA256.txt').write_text('\n'.join(lines)+'\n')
    print('Prepared',len(ss),'scenarios,',len(seeds),'batches,',len(ss)*len(seeds)*500*11,'episode executions.')
if __name__=='__main__':main()
