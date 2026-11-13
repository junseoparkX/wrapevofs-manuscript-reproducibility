"""Freeze a retrospective fixed-bank audit before generating new outer predictions."""
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PREVIOUS = ROOT / 'manuscript/latex_v19_overleaf/v19_work/experiments'
SUPP = ROOT / 'manuscript/latex_v19_overleaf/supplementary_data'
BRANCHES = ['svm_l1', 'xgboost', 'boruta_rf']
POLICIES = ['highest_locking_score', 'legacy_top3_medoid', 'unrestricted_medoid', 'regret_constrained_medoid']
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
jsha = lambda x: hashlib.sha256(json.dumps(x, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def main():
    assert not (HERE / 'protocol.json').exists(), 'Never overwrite a frozen experiment'
    inventory = PREVIOUS / 'common_rf_seed_20261105/bank_inventory.json'
    original_sources = PREVIOUS / 'common_rf_outer_eval_20261105/local_source_inventory.json'
    sources = {s['bank_id']: s for s in json.loads(original_sources.read_text())}
    geometry_path = SUPP / 'tcga_nested_v1_v2/candidate_level_geometry.csv'
    with geometry_path.open(newline='', encoding='utf-8') as f:
        geometry = {(int(r['outer_repeat']), int(r['outer_fold']), r['branch'], int(r['run_id'])): r for r in csv.DictReader(f)}
    banks, local_sources = [], []
    for original in json.loads(inventory.read_text()):
        if original['cohort'] != 'TCGA':
            continue
        bank = {k: v for k, v in original.items() if k not in ['candidates', 'center', 'cap']}
        _, repeat, fold, branch = bank['bank_id'].split('__')
        repeat, fold = int(repeat), int(fold)
        bank.update(repeat=repeat, fold=fold, final_seed=50000 + repeat * 1000 + fold * 100 + BRANCHES.index(branch) * 10)
        source = dict(sources[bank['bank_id']])
        directory = Path(source['directory'])
        locks_path = directory / 'locking_results.json'
        locks = json.loads(locks_path.read_text())
        source['locking_results_sha256'] = sha(locks_path)
        source['original_predictions_sha256'] = sha(directory / 'outer_predictions.csv')
        for name, key in [('prepared_selection.npz', 'prepared_sha256'), ('outer_labels.npz', 'outer_labels_sha256'), ('prepared_manifest.json', 'manifest_sha256')]:
            assert sha(directory / name) == source[key]
        candidates = []
        for c in sorted(original['candidates'], key=lambda c: c['run_id']):
            r = geometry[(repeat, fold, branch, c['run_id'])]
            features = c['scoring_features']
            assert features == c['features'] and set(features) == set(json.loads(r['canonical_features']))
            assert c['stable_mask_hash'] == r['stable_mask_hash']
            candidates.append({'run_id': c['run_id'], 'source_seed': 42 + c['run_id'], 'features': features,
                               'feature_count': len(features), 'mask_hash': c['stable_mask_hash'],
                               'feature_order_sha256': jsha(features), 'locking_score': float(r['locking_score']),
                               'development_regret': float(r['absolute_regret']), 'eligible': r['eligible'].lower() == 'true'})
        assert len(candidates) == 5 and len({c['mask_hash'] for c in candidates}) == 5
        policy_runs = {}
        for policy in POLICIES:
            matches = [c for c in candidates if set(c['features']) == set(locks['feature_sets'][policy])]
            assert len(matches) == 1 and matches[0]['features'] == locks['feature_sets'][policy]
            policy_runs[policy] = matches[0]['run_id']
        universe_sizes = {len(geometry[(repeat, fold, branch, c['run_id'])]['canonical_mask']) for c in candidates}
        assert len(universe_sizes) == 1
        bank.update(candidates=candidates, policy_runs=policy_runs, null_universe_size=universe_sizes.pop())
        banks.append(bank)
        local_sources.append(source)
    assert len(banks) == 30 and sum(len(b['candidates']) for b in banks) == 150
    for name, obj in [('candidate_inventory.json', banks), ('local_sources.json', local_sources)]:
        (HERE / name).write_text(json.dumps(obj, indent=2) + '\n')
    protocol = {
        'schema': 'TCGA-all-five-candidates-retrospective-audit-v1',
        'frozen_utc': datetime.now(timezone.utc).isoformat(),
        'status': 'Retrospective conditional diagnostic; parent outer outcomes were previously analyzed.',
        'authorization': 'User requested immediately running useful strengthening experiments on fenn; original selections remain fixed.',
        'remote_directory': '/data2/junseo/wrapevofs/v19_candidate_outer_audit_20261112',
        'remote_development_directory': '/data2/junseo/wrapevofs/v19_common_rf_seed_20261105/private_development',
        'banks': 30, 'candidates': 150, 'participants': 491, 'branches': BRANCHES, 'policies': POLICIES,
        'RF_params': banks[0]['rf_params'], 'workers': 4, 'hard_timeout_seconds': 1800,
        'final_seed': 'Original common condition seed: 50000 + repeat*1000 + fold*100 + branch_index*10.',
        'candidate_feature_order': 'Original saved order, identical to original evaluated policy masks.',
        'versions': {'sklearn': '1.6.1', 'numpy': '2.0.2', 'joblib': '1.4.2'},
        'synthetic_probe_seed': 20261112,
        'reproduction_gate': 'Every existing candidate-based policy prediction must reproduce to absolute 1e-12 before interpreting new metrics.',
        'fixed_bank_diagnostics': ['All five outer-test AUROCs and within-bank spread',
                                   'Original four policies: full OOF AUROC and development gap violations',
                                   'Exact fixed-cardinality uniform-null Jaccard reference',
                                   'Hindsight fold-winner apparent advantage, explicitly not an unbiased gain'],
        'selection_optimism': {
            'splits_per_bank': 200, 'seed': 20261112,
            'split': 'Per-class random approximately half/half, all participants retained; complementary halves used symmetrically.',
            'selection': 'Select max-AUROC run on half A; evaluate same run on A and B; repeat swapping A/B.',
            'tie': 'Higher original development score, fewer features, smaller stable mask hash.',
            'estimand': 'Mean across two directions of selection-half AUROC minus independent-evaluation-half AUROC, conditional on fixed bank/models/outer partition.',
            'uncertainty': 'Repeated-split dispersion is descriptive Monte Carlo variability, not a confidence interval or 6000 independent cohorts.',
            'fixed_rule_comparison': 'Report symmetric half-evaluation AUROC for all four fixed development-only policies.',
        },
        'bootstrap': {'replicates': 2000, 'seed': 20261112,
                      'unit': 'Class-stratified participant clusters; preserve repeats and branches jointly.',
                      'scope': 'Paired conditional OOF differences for all four original policies; nominal exploratory 95% percentile intervals.'},
        'interpretation': ['No new GA, Direct, RFECV, tolerance, seed, or selected-mask tuning.',
                           'AUC ratio is not a clinical retention measure; report absolute AUROC differences.',
                           'This experiment cannot establish equivalence, external validity, or biomarker stability.'],
        'data_boundary': 'Train using existing server development arrays; only code/aggregate inventory uploaded. Predict and analyze outer data locally; no outer values, labels, IDs, or predictions uploaded.',
        'input_sha256': {'original_bank_inventory': sha(inventory), 'original_local_sources': sha(original_sources),
                         'candidate_geometry': sha(geometry_path), 'candidate_inventory': sha(HERE / 'candidate_inventory.json'),
                         'local_sources': sha(HERE / 'local_sources.json')},
        'code_sha256': {n: sha(HERE / n) for n in ['freeze_experiment.py', 'train_candidates.py', 'predict_candidates.py', 'analyze_candidates.py']},
    }
    (HERE / 'protocol.json').write_text(json.dumps(protocol, indent=2) + '\n')
    (HERE / 'FROZEN_BEFORE_NEW_PREDICTIONS.sha256').write_text(sha(HERE / 'protocol.json') + '\n')
    print(json.dumps({'banks': 30, 'fits': 150, 'protocol_sha256': sha(HERE / 'protocol.json'), 'data_transfer': 'code and aggregate candidate inventory only'}))


if __name__ == '__main__':
    main()
