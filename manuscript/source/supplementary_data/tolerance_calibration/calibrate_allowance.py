"""Reproduce development-only allowance choices from non-participant audit CSV.

python calibrate_allowance.py --input candidate_development_audit.csv --output out --search breakpoints
Requires Python3 and NumPy. Never reads a held-out score or prediction.
"""
from pathlib import Path
import argparse,csv,json,itertools
import numpy as np

SCHEMES=['original_candidate_seed','common_RF_seed342']
GRID=[0.,.0025,.005,.0075,.01,.015,.02]

def jaccard(a,b):return len(a&b)/len(a|b)
def choose(group,scheme,delta):
    top=max(c[scheme+'_score'] for c in group)
    pool=[c for c in group if top-c[scheme+'_score']<=delta]
    def key(c):
        peers=[q for q in pool if q is not c]
        overlap=float(np.mean([jaccard(c['features'],q['features']) for q in peers])) if peers else 1.
        return (-overlap,-c[scheme+'_score'],c['feature_count'],c['mask_hash'])
    return min(pool,key=key)

def write_csv(path,rows):
    with path.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(dict.fromkeys(k for r in rows for k in r)));w.writeheader();w.writerows(rows)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--input',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True);parser.add_argument('--search',choices=['grid','breakpoints'],default='breakpoints')
    args=parser.parse_args();candidates=[]
    for r in csv.DictReader(args.input.open(encoding='utf-8')):
        c={**r,'features':set(json.loads(r['features_json'])),'feature_count':int(r['feature_count']),
            'calibration_bank':int(r['calibration_bank']),'run':int(r['run'])}
        for s in SCHEMES:c[s+'_score']=float(r[s+'_score']);c[s+'_folds']=json.loads(r[s+'_folds_json'])
        candidates.append(c)
    curves=[];decisions=[]
    for branch in sorted({c['branch'] for c in candidates}):
        bank_ids=sorted({c['calibration_bank'] for c in candidates if c['branch']==branch})
        groups=[sorted([c for c in candidates if c['branch']==branch and c['calibration_bank']==b],key=lambda c:(c['mask_hash'],c['run'])) for b in bank_ids]
        assert len(groups)>=2 and all(len(g)==5 for g in groups)
        for scheme in SCHEMES:
            if args.search=='grid':grid=GRID
            else:
                grid=sorted({0.}|{max(q[scheme+'_score'] for q in group)-c[scheme+'_score'] for group in groups for c in group})
            rows=[];selections={}
            for delta in grid:
                chosen=[choose(g,scheme,delta) for g in groups];selections[delta]=chosen
                mean_score=float(np.mean([c[scheme+'_score'] for c in chosen]))
                folds=np.asarray([c[scheme+'_folds'] for c in chosen]);assert folds.shape==(len(groups),5)
                overlap=float(np.mean([jaccard(a['features'],b['features']) for a,b in itertools.combinations(chosen,2)]))
                rows.append({'delta':delta,'calibration_Jaccard':overlap,'calibration_mean_score':mean_score,
                             'bank_averaged_fold_scores':folds.mean(axis=0).tolist()})
            baseline=next(r for r in rows if r['delta']==0.)
            se=float(np.std(baseline['bank_averaged_fold_scores'],ddof=1)/np.sqrt(5))
            for r in rows:r.update({'delta0_score_SE':se,'score_feasible':r['calibration_mean_score']>=baseline['calibration_mean_score']-se})
            winner=min([r for r in rows if r['score_feasible']],key=lambda r:(-r['calibration_Jaccard'],-r['calibration_mean_score'],r['delta']))
            decisions.append({'branch':branch,'scheme':scheme,'learned_delta':winner['delta'],
                'fitted_Jaccard':winner['calibration_Jaccard'],'selected_mask_hashes':[c['mask_hash'] for c in selections[winner['delta']]]})
            curves.extend({'branch':branch,'scheme':scheme,**r} for r in rows)
    args.output.mkdir(parents=True,exist_ok=False)
    (args.output/'decisions.json').write_text(json.dumps(decisions,indent=2)+'\n',encoding='utf-8')
    write_csv(args.output/'training_curve.csv',curves)
    print(json.dumps([{k:v for k,v in d.items() if k!='selected_mask_hashes'} for d in decisions],indent=2))

if __name__=='__main__':main()
