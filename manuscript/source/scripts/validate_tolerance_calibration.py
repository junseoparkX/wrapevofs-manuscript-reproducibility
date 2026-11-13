"""Reproduce development-only choices and check all-policy aggregate joins."""
from pathlib import Path
import argparse,csv,hashlib,json,subprocess,sys,tempfile
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'supplementary_data/tolerance_calibration'

def rows(name):return list(csv.DictReader((DATA/name).open(encoding='utf-8')))
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--package',action='store_true');args=parser.parse_args()
    audit=rows('candidate_development_audit.csv');assert len(audit)==240
    assert all(len(json.loads(r['features_json']))==int(r['feature_count']) for r in audit)
    universes=json.loads((DATA/'feature_universes.json').read_text())['universes']
    for r in audit:
        selected=set(json.loads(r['features_json']))
        assert hashlib.sha256(bytes(int(n in selected) for n in universes[r['branch']])).hexdigest()==r['mask_hash']
    expected=rows('learned_allowances.csv');locks=rows('policy_selections.csv')
    assert len(expected)==6 and len(locks)==384
    for mode in ['breakpoints','grid']:
        with tempfile.TemporaryDirectory() as td:
            dest=Path(td)/'result'
            subprocess.run([sys.executable,str(DATA/'calibrate_allowance.py'),'--input',str(DATA/'candidate_development_audit.csv'),
                '--output',str(dest),'--search',mode],check=True,stdout=subprocess.DEVNULL)
            for d in json.loads((dest/'decisions.json').read_text()):
                e=next(r for r in expected if r['branch']==d['branch'] and r['scheme']==d['scheme'])
                key='learned_delta' if mode=='breakpoints' else 'grid_calibrated_delta'
                assert d['learned_delta']==float(e[key])
                policy='breakpoint_calibrated' if mode=='breakpoints' else 'grid_calibrated'
                selected=sorted([r for r in locks if r['branch']==d['branch'] and r['scheme']==d['scheme'] and r['policy']==policy],key=lambda r:int(r['bank']))
                assert [r['mask_hash'] for r in selected]==d['selected_mask_hashes']
    metrics={r['task_id']:float(r['heldout_macro_AUROC']) for r in rows('selected_model_AUROC.csv')}
    summary=rows('policy_summary.csv');assert len(summary)==32
    for r in summary:
        branch=r['branch'];selected=[q for q in locks if q['scheme']==r['scheme'] and q['policy']==r['policy'] and (branch=='equal_branch_mean' or q['branch']==branch)]
        assert len(selected)==(48 if branch=='equal_branch_mean' else 16)
        assert abs(np.mean([metrics[q['task_id']] for q in selected])-float(r['mean_heldout_AUROC']))<1e-13
    primary=[r for r in rows('paired_AUROC_contrasts.csv') if r['scheme']=='original_candidate_seed']
    assert len(primary)==12
    for r in primary:
        new=next(q for q in summary if q['branch']==r['branch'] and q['scheme']==r['scheme'] and q['policy']=='breakpoint_calibrated')
        old=next(q for q in summary if q['branch']==r['branch'] and q['scheme']==r['scheme'] and q['policy']==r['comparator'])
        assert abs(float(new['mean_heldout_AUROC'])-float(old['mean_heldout_AUROC'])-float(r['AUROC_difference']))<1e-13
        assert float(r['simultaneous_CI95_low'])<=0<=float(r['simultaneous_CI95_high'])
    hierarchy=json.loads((DATA/'analysis_hierarchy.json').read_text())
    assert hierarchy['main_calibration_analysis']=='grid_calibrated'
    assert hierarchy['supplementary_calibration_analysis']=='breakpoint_calibrated'
    assert hierarchy['presentation_hierarchy_chosen_after_results']
    assert not hierarchy['prespecified_confirmatory_primary_analysis']
    main_grid=[r for r in rows('grid_calibration_AUROC_contrasts.csv') if r['scheme']=='original_candidate_seed']
    assert len(main_grid)==8
    for r in main_grid:
        a=next(q for q in summary if q['branch']==r['branch'] and q['scheme']==r['scheme'] and q['policy']=='grid_calibrated')
        comparator='highest_score' if r['comparator']=='fixed_0' else r['comparator']
        b=next(q for q in summary if q['branch']==r['branch'] and q['scheme']==r['scheme'] and q['policy']==comparator)
        assert abs(float(a['mean_heldout_AUROC'])-float(b['mean_heldout_AUROC'])-float(r['heldout_AUROC_difference']))<1e-13
        assert float(r['simultaneous_CI95_low'])<=0<=float(r['simultaneous_CI95_high'])
    package_checks=0
    if args.package:
        from wrapevofs import LockingCandidate,calibrate_tolerance
        from wrapevofs import __version__
        assert __version__=='0.3.0',__version__
        for branch in sorted(universes):
            for scheme in ['original_candidate_seed','common_RF_seed342']:
                banks={f'bank_{b:02d}':[] for b in range(16)}
                for r in audit:
                    if r['branch']!=branch:continue
                    banks[f"bank_{int(r['calibration_bank']):02d}"].append(LockingCandidate(
                        run_id=int(r['run']),features=json.loads(r['features_json']),
                        locking_score=float(r[scheme+'_score']),
                        fold_locking_scores=json.loads(r[scheme+'_folds_json']),
                        candidate_universe=universes[branch]))
                for policy,grid,col in [('breakpoint_calibrated',None,'learned_delta'),
                    ('grid_calibrated',[0.,.0025,.005,.0075,.01,.015,.02],'grid_calibrated_delta')]:
                    fitted=calibrate_tolerance(banks,delta_grid=grid)
                    e=next(r for r in expected if r['branch']==branch and r['scheme']==scheme)
                    assert fitted.selected_delta==float(e[col])
                    rr=sorted([r for r in locks if r['branch']==branch and r['scheme']==scheme and r['policy']==policy],key=lambda r:int(r['bank']))
                    assert [fitted.bank_results[f'bank_{b:02d}'].metadata['selected_stable_mask_hash'] for b in range(16)]==[r['mask_hash'] for r in rr]
                    package_checks+=1
    print(json.dumps({'status':'PASS','candidates':240,'calibration_choices_and_masks_reproduced':12,
        'aggregate_policy_rows_reproduced':32,'main_grid_original_AUROC_contrasts_checked':8,'breakpoint_original_AUROC_contrasts_checked':12,'heldout_rows_used_for_calibration':False,
        'package_API_choices_and_masks_reproduced':package_checks}))
if __name__=='__main__':main()
