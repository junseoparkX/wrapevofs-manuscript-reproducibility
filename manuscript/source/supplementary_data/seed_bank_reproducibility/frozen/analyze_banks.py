"""All registered bank pairs; independent reference versus package locking."""
import hashlib
import itertools
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import wrapevofs
from wrapevofs.config import LockingConfig
from wrapevofs.locking import LockingCandidate, lock_representative_run

HERE = Path(__file__).resolve().parent
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def jac(left, right):
    a, b = set(left['features']), set(right['features'])
    return len(a & b) / len(a | b)


def reference(candidates, scheme, delta):
    score = lambda c: c['scores'][scheme]['locking_score']
    highest = min(candidates, key=lambda c: (-score(c), c['feature_count'], c['mask_hash']))
    pool = [c for c in candidates if score(highest) - score(c) <= delta]
    # Match the published implementation's canonical summation order as well
    # as its strict (unexpanded) tolerance at the floating-point boundary.
    pool = sorted(pool, key=lambda c: (c['mask_hash'], c['identity']['run']))
    def key(c):
        overlap = np.mean([jac(c, other) for other in pool if other is not c]) if len(pool) > 1 else 1.0
        return (-overlap, -score(c), c['feature_count'], c['mask_hash'])
    locked = min(pool, key=key)
    return highest, locked, pool


def main():
    p = json.loads((HERE / 'protocol.json').read_text())
    assert sha(Path(__file__)) == p['code_sha256'][Path(__file__).name]
    ph = sha(HERE / 'protocol.json')
    assert ph == (HERE / 'FROZEN_BEFORE_NEW_CANDIDATES.sha256').read_text().strip()
    selections, pairs, checks, candidate_rows = [], [], [], []
    for condition in p['conditions']:
        with np.load(HERE / 'private_development' / condition['development_file'], allow_pickle=False) as d:
            universe = tuple(d['feature_names'].astype(str))
        banks = []
        for bank, seeds in enumerate(condition['seed_banks']):
            candidates = []
            for run, seed in enumerate(seeds):
                directory = HERE / 'runs' / condition['branch'] / f'bank_{bank:02d}' / f'run_{run:02d}'
                receipt = json.loads((directory / 'complete.json').read_text())
                assert receipt['identity']['protocol_sha256'] == ph and receipt['identity']['GA_seed'] == seed
                assert receipt['completed_generations'] == p['ga']['n_generations']
                assert sha(directory / 'candidate.json') == receipt['candidate_sha256']
                candidate = json.loads((directory / 'candidate.json').read_text())
                candidates.append(candidate)
                for scheme in p['score_schemes']:
                    scores = candidate['scores'][scheme]
                    assert len(scores['fold_scores']) == 5 and np.isfinite(scores['fold_scores']).all()
                    assert abs(np.mean(scores['fold_scores']) - scores['locking_score']) < 1e-12
                    candidate_rows.append({'condition': condition['condition_id'], 'bank': bank, 'run': run,
                        'GA_seed': seed, 'scheme': scheme, 'mask_hash': candidate['mask_hash'],
                        'feature_count': candidate['feature_count'], 'locking_score': scores['locking_score']})
            banks.append(candidates)
        for scheme in p['score_schemes']:
            for size in p['bank_sizes']:
                chosen = []
                for bank, candidates in enumerate(banks):
                    candidates = candidates[:size]
                    highest, locked, pool = reference(candidates, scheme, p['locking']['regret_tolerance'])
                    package_candidates = [LockingCandidate(
                        run_id=i, features=c['features'], locking_score=c['scores'][scheme]['locking_score'],
                        fold_locking_scores=c['scores'][scheme]['fold_scores'], seed=c['identity']['GA_seed'],
                        candidate_universe=universe) for i, c in enumerate(candidates)]
                    cfg = LockingConfig(enabled=True, strategy='regret_constrained_medoid',
                                        regret_tolerance=.01, locking_metric='macro_ovr_auroc', random_state=342)
                    package = lock_representative_run(package_candidates, cfg, software_version=wrapevofs.__version__)
                    assert set(package.selected_features) == set(locked['features'])
                    checks.append({'condition': condition['condition_id'], 'scheme': scheme, 'R': size,
                                   'bank': bank, 'package_reference_agree': True})
                    chosen.append((highest, locked))
                    selections.append({'condition': condition['condition_id'], 'scheme': scheme, 'R': size, 'bank': bank,
                        'highest_mask_hash': highest['mask_hash'], 'locked_mask_hash': locked['mask_hash'],
                        'highest_feature_count': highest['feature_count'], 'locked_feature_count': locked['feature_count'],
                        'eligible_pool_size': len(pool), 'unique_masks': len({c['mask_hash'] for c in candidates}),
                        'locked_development_regret': highest['scores'][scheme]['locking_score'] - locked['scores'][scheme]['locking_score']})
                for a, b in itertools.combinations(range(len(banks)), 2):
                    ah, al = chosen[a]; bh, bl = chosen[b]
                    high_j, lock_j = jac(ah, bh), jac(al, bl)
                    pairs.append({'condition': condition['condition_id'], 'scheme': scheme, 'R': size, 'bank_A': a, 'bank_B': b,
                        'highest_Jaccard': high_j, 'locked_Jaccard': lock_j, 'difference_locked_minus_highest': lock_j - high_j,
                        'highest_exact_agreement': int(ah['mask_hash'] == bh['mask_hash']),
                        'locked_exact_agreement': int(al['mask_hash'] == bl['mask_hash'])})
    out = HERE / 'results'
    out.mkdir(exist_ok=True)
    pair_frame = pd.DataFrame(pairs)
    means = pair_frame.groupby(['condition', 'scheme', 'R'], as_index=False)[
        ['highest_Jaccard', 'locked_Jaccard', 'difference_locked_minus_highest', 'highest_exact_agreement', 'locked_exact_agreement']].mean()
    for name, frame in [('all_candidates.csv', pd.DataFrame(candidate_rows)), ('selections.csv', pd.DataFrame(selections)),
                        ('bank_pairs.csv', pair_frame), ('condition_summary.csv', means)]:
        frame.to_csv(out / name, index=False)
    validation = {'completed_utc': datetime.now(timezone.utc).isoformat(), 'protocol_sha256': ph,
                  'registered_GA_runs': 240, 'package_reference_checks': len(checks), 'all_checks_passed': True,
                  'pair_rows': len(pairs), 'independent_participant_inferences': 0,
                  'output_sha256': {path.name: sha(path) for path in out.glob('*.csv')}}
    (out / 'analysis_validation.json').write_text(json.dumps(validation, indent=2) + '\n')
    print(means.to_csv(index=False), flush=True)


if __name__ == '__main__':
    main()
