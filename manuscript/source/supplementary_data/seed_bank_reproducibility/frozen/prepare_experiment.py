"""Freeze a new-seed experiment; extract development arrays only."""
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    assert not (HERE / 'protocol.json').exists(), 'Do not replace a frozen protocol'
    original_path = ROOT / 'experimental_validation_if7/13_tcga_gbmlgg_fully_nested_150_colab/tcga_nested_protocol.json'
    original = json.loads(original_path.read_text())
    wheel = original_path.parent / original['software']['wheel_filename']
    assert sha(wheel) == original['software']['wheel_sha256']
    shutil.copyfile(wheel, HERE / wheel.name)
    private = HERE / 'private_development'
    private.mkdir(exist_ok=True)
    conditions = []
    for branch_index, branch in enumerate(original['branches']):
        directory = ROOT / 'analysis/tcga_nested_v1_v2_complete_20260812/raw_drive_results/repeat_01/fold_01' / branch
        source, manifest_path = directory / 'prepared_selection.npz', directory / 'prepared_manifest.json'
        manifest = json.loads(manifest_path.read_text())
        assert sha(source) == manifest['prepared_selection_sha256']
        # Explicit allowlist: never load x_outer, outer IDs or outer labels.
        with np.load(source, allow_pickle=False) as data:
            x = data['x_train']
            y = data['y_train']
            names = data['feature_names'].astype(str)
            target = int(data['target_k'][0])
        assert len(y) == 392 and x.shape == (392, len(names))
        assert names.tolist() == manifest['direct_features']
        assert target == manifest['rfecv_target_k'] and np.isfinite(x).all()
        path = private / (branch + '.npz')
        np.savez_compressed(path, X=x, y=y, feature_names=names)
        conditions.append({
            'condition_id': 'TCGA__1__1__' + branch, 'branch': branch,
            'development_file': path.name, 'development_sha256': sha(path),
            'development_rows': len(y), 'feature_universe_size': len(names), 'target_k': target,
            'source_prepared_sha256': sha(source), 'source_manifest_sha256': sha(manifest_path),
            'source_development_ID_sha256': manifest['train_ids_sha256'],
            'seed_banks': [[202611120 + branch_index * 10000 + bank * 1000 + run
                            for run in range(20)] for bank in range(4)],
        })
    seeds = [s for c in conditions for bank in c['seed_banks'] for s in bank]
    assert len(seeds) == len(set(seeds)) == 240 and not set(seeds) & set(range(42, 47))
    ga = {key: original['ga'][key] for key in [
        'population_size', 'n_generations', 'crossover_rate', 'mutation_rate',
        'elitism_count', 'initial_off_ratio', 'size_penalty_lambda', 'fitness_mode',
        'fitness_metric', 'cv_folds', 'rf_params', 'gpu_rf_params']}
    protocol = {
        'schema': 'fresh-seed-bank-rerun-v1', 'frozen_utc': datetime.now(timezone.utc).isoformat(),
        'question': 'Does regret-constrained locking yield more reproducible feature sets than highest development score under independent GA seed banks?',
        'authorization': 'User requested checking these experiments and running missing work on Fenn.',
        'remote_directory': '/data2/junseo/wrapevofs/v19_seed_bank_rerun_20261112',
        'conditions': conditions, 'bank_sizes': [5, 10, 20], 'independent_banks_per_condition': 4,
        'total_GA_runs': 240, 'workers': 8, 'hard_timeout_seconds': 259200,
        'condition_selection': 'First outer repeat and first outer fold, all three branches; fixed before generating candidates, no selection by results.',
        'backend': 'cpu', 'original_backend': 'gpu',
        'deterministic_stages': 'Reuse original training-only preprocessing, Direct universe/order and RFECV target; same inputs imply the same deterministic stages. All GA candidates are generated anew.',
        'ga': ga, 'locking': original['locking'], 'locking_cv_seed': 342,
        'score_schemes': {
            'original_candidate_seed': 'Primary: locking CV partitions use 342; RF random_state is the candidate GA seed, as in the original pipeline.',
            'common_RF_seed342': 'Secondary: all candidate RF evaluators use seed342 on the same fixed CV partitions, separating scorer randomness from candidate generation.',
        },
        'primary_metric': 'Within each condition and bank size: average across all six pairs of independent banks of Jaccard(locked_i,locked_j) minus Jaccard(highest_i,highest_j).',
        'secondary_metrics': ['Exact feature-set agreement', 'Eligible pool size', 'Unique masks', 'Selected feature count', 'Development score regret'],
        'R_comparison': 'Nested prefixes within each independent bank; R values are correlated and are all reported.',
        'duplicates': 'Retain multiplicity as voting candidates; report unique masks separately.',
        'highest_tie': 'Higher development score, fewer features, smaller stable mask hash, then first candidate for identical masks.',
        'inference': 'Descriptive exploratory conditional analysis; six pairs are not six independent experiments; branches share participants. No participant CI or p-value is computed.',
        'stopping_rule': 'All registered jobs, regardless of result direction; preserve checkpoints on failure and timeout. No automatic retries of failed jobs.',
        'data_boundary': 'Upload only three processed outer-training matrices without participant IDs. Never load or upload outer values, outer labels, outer IDs or predictions.',
        'claim_boundary': 'This is a new CPU-backend extension conditional on fixed development participants, Direct and RFECV. It is not reproduction of GPU trajectories or a participant-resampling, external validation or general biomarker stability experiment.',
        'package': original['software'], 'original_protocol_sha256': sha(original_path),
        'code_sha256': {name: sha(HERE / name) for name in ['prepare_experiment.py', 'run_experiment.py', 'analyze_banks.py']},
    }
    (HERE / 'protocol.json').write_text(json.dumps(protocol, indent=2) + '\n')
    (HERE / 'FROZEN_BEFORE_NEW_CANDIDATES.sha256').write_text(sha(HERE / 'protocol.json') + '\n')
    print(json.dumps({'conditions': len(conditions), 'runs': 240, 'protocol_sha256': sha(HERE / 'protocol.json'),
                      'development_bytes': sum(p.stat().st_size for p in private.glob('*.npz')),
                      'outer_arrays_loaded': False, 'participant_IDs_exported': False}))


if __name__ == '__main__':
    main()
