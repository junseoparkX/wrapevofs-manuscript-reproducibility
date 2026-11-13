"""Preflight: strict locking reference, duplicates/ties, and original scorer."""
import hashlib
import json
from pathlib import Path

import numpy as np
from wrapevofs.config import LockingConfig
from wrapevofs.locking import LockingCandidate, lock_representative_run, score_candidate_feature_sets
from analyze_banks import reference
from run_experiment import arrays, save

HERE = Path(__file__).resolve().parent
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p = json.loads((HERE / 'protocol.json').read_text())
    rng = np.random.default_rng(202611118)
    universe = tuple(f'f{i}' for i in range(35))
    tested = 0
    for size in [5, 10, 20]:
        for trial in range(100):
            candidates = []
            for run in range(size):
                mask = rng.random(35) < .3
                mask[0] = True
                if run and trial % 7 == 0:
                    mask = np.asarray([f in candidates[0]['features'] for f in universe])
                features = [f for f, keep in zip(universe, mask) if keep]
                score = float(rng.integers(800, 840) / 1000)
                candidates.append({'identity': {'run': run}, 'features': features, 'feature_count': len(features),
                    'mask_hash': hashlib.sha256(mask.astype(np.uint8).tobytes()).hexdigest(),
                    'scores': {'test': {'locking_score': score}}})
            _, expected, _ = reference(candidates, 'test', .01)
            actual = lock_representative_run(
                [LockingCandidate(run_id=i, features=c['features'], locking_score=c['scores']['test']['locking_score'],
                                  candidate_universe=universe) for i, c in enumerate(candidates)],
                LockingConfig(enabled=True, strategy='regret_constrained_medoid'))
            assert set(actual.selected_features) == set(expected['features']), (size, trial)
            tested += 1
    inventory_path = HERE.parent / 'v19_common_rf_seed_20261105/bank_inventory.json'
    inventory = {b['bank_id']: b for b in json.loads(inventory_path.read_text())}
    baseline = []
    for c in p['conditions']:
        x, y = arrays(c)
        b = inventory[c['condition_id']]
        candidate = b['candidates'][0]
        checked = score_candidate_feature_sets(
            x, y, {0: candidate['scoring_features']}, locking_metric=p['locking']['metric'], cv_folds=5,
            random_state=342, rf_params=p['locking']['rf_params'], n_jobs=1, run_seeds={0: candidate['original_seed']})[0]
        error = float(np.max(np.abs(np.asarray(checked.fold_locking_scores) - candidate['original_fold_scores'])))
        assert error < 1e-12, (c['condition_id'], error)
        baseline.append({'condition': c['condition_id'], 'five_original_folds_max_error': error})
    report = {'protocol_sha256': sha(HERE / 'protocol.json'), 'synthetic_reference_checks': tested,
              'duplicates_and_ties_included': True, 'original_development_scoring_checks': baseline,
              'all_checks_passed': True, 'outer_data_accesses': 0,
              'script_sha256': sha(Path(__file__))}
    save(HERE / 'preflight_verification.json', report)
    print(json.dumps(report), flush=True)


if __name__ == '__main__':
    main()
