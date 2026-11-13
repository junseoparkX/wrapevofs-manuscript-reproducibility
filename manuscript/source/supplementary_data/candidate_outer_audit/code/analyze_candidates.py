"""Conditional fixed-bank trade-offs and independent-half run-selection optimism."""
import csv
import hashlib
import json
import math
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from sklearn.metrics import roc_auc_score

HERE = Path(__file__).resolve().parent
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def write(path, rows):
    with path.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def weighted_auc(y, probability, weights):
    """Exact weighted rank-pair AUROC, including half credit for score ties."""
    result = []
    for c in range(4):
        order = np.argsort(probability[:, c], kind='stable')
        score, positive = probability[order, c], y[order] == c
        starts = np.r_[0, np.flatnonzero(score[1:] != score[:-1]) + 1]
        pos = np.add.reduceat(weights[:, order] * positive[None, :], starts, axis=1)
        neg = np.add.reduceat(weights[:, order] * (~positive)[None, :], starts, axis=1)
        before = np.cumsum(neg, axis=1) - neg
        result.append(np.sum(pos * (before + 0.5 * neg), axis=1) / (pos.sum(axis=1) * neg.sum(axis=1)))
    return np.mean(result, axis=0)


def jaccard(a, b):
    a, b = set(a['features']), set(b['features'])
    return len(a & b) / len(a | b)


def main():
    start = time.perf_counter()
    p = json.loads((HERE / 'protocol.json').read_text())
    ph = sha(HERE / 'protocol.json')
    assert sha(Path(__file__)) == p['code_sha256']['analyze_candidates.py']
    verified = json.loads((HERE / 'prediction_verification.json').read_text())
    payload = HERE / 'private_predictions/candidate_oof.npz'
    assert verified['protocol_sha256'] == ph and sha(payload) == verified['payload_sha256']
    with np.load(payload, allow_pickle=False) as d:
        probability, y, folds = d['probabilities'], d['y'], d['folds']
    assert probability.shape == (3, 5, 2, 491, 4)
    banks = json.loads((HERE / 'candidate_inventory.json').read_text())
    out = HERE / 'results'
    out.mkdir(exist_ok=True)
    candidate_rows, bank_rows, split_rows, geometry_rows = [], [], [], []
    policy_prob = np.full((3, 4, 2, 491, 4), np.nan)
    hindsight_prob = np.full((3, 2, 491, 4), np.nan)
    rng = np.random.default_rng(p['selection_optimism']['seed'])
    max_auc_error, independent_auc_checks = 0.0, 0
    for bank in banks:
        b, r = p['branches'].index(bank['branch']), bank['repeat'] - 1
        ix = np.flatnonzero(folds[b, r] == bank['fold'])
        labels = y[ix]
        values = probability[b, :, r][:, ix, :]
        candidates = bank['candidates']
        assert [c['run_id'] for c in candidates] == list(range(5))
        full_auc = np.asarray([roc_auc_score(labels, v, multi_class='ovr', average='macro') for v in values])
        priority = np.asarray(sorted(range(5), key=lambda run: (-candidates[run]['locking_score'], candidates[run]['feature_count'], candidates[run]['mask_hash'])))
        winner = int(priority[np.argmax(full_auc[priority])])
        hindsight_prob[b, r, ix] = values[winner]
        for c in candidates:
            candidate_rows.append({'bank_id': bank['bank_id'], 'branch': bank['branch'], 'repeat': bank['repeat'], 'fold': bank['fold'],
                                   'run_id': c['run_id'], 'feature_count': c['feature_count'], 'development_score': c['locking_score'],
                                   'development_regret': c['development_regret'], 'eligible': int(c['eligible']),
                                   'outer_macro_ovr_auroc': full_auc[c['run_id']]})
        for policy_index, policy in enumerate(p['policies']):
            run = bank['policy_runs'][policy]
            policy_prob[b, policy_index, r, ix] = values[run]
            c = candidates[run]
            pool = [s for s in candidates if s['eligible']]
            pool_j = np.mean([jaccard(c, s) for s in pool if s['run_id'] != run]) if c['eligible'] and len(pool) > 1 else float('nan')
            full_j = np.mean([jaccard(c, s) for s in candidates if s['run_id'] != run])
            geometry_rows.append({'bank_id': bank['bank_id'], 'branch': bank['branch'], 'policy': policy, 'run_id': run,
                                  'development_regret': c['development_regret'], 'exceeds_delta': int(c['development_regret'] > .01),
                                  'eligible_pool_size': len(pool), 'eligible_pool_mean_jaccard': pool_j, 'full_bank_mean_jaccard': full_j})
        # Fixed-cardinality, uniformly sampled subsets of the verified bank universe.
        # Recover its cardinality from the source candidate masks rather than the feature union.
        n = bank['null_universe_size']
        null, observed = [], []
        for i, a in enumerate(candidates):
            for c in candidates[i + 1:]:
                ka, kb = a['feature_count'], c['feature_count']
                null.append(sum(math.comb(ka, t) * math.comb(n - ka, kb - t) / math.comb(n, kb) * t / (ka + kb - t)
                                for t in range(max(0, ka + kb - n), min(ka, kb) + 1)))
                observed.append(jaccard(a, c))
        bank_rows.append({'bank_id': bank['bank_id'], 'branch': bank['branch'], 'outer_participants': len(ix),
                          'outer_AUROC_min': full_auc.min(), 'outer_AUROC_max': full_auc.max(), 'outer_AUROC_range': np.ptp(full_auc),
                          'hindsight_winner_run': winner, 'locked_run': bank['policy_runs']['regret_constrained_medoid'],
                          'hindsight_apparent_advantage_over_locked': full_auc[winner] - full_auc[bank['policy_runs']['regret_constrained_medoid']],
                          'mean_candidate_jaccard': np.mean(observed), 'uniform_null_expected_jaccard': np.mean(null),
                          'universe_size': n})
        reps = p['selection_optimism']['splits_per_bank']
        half_a = np.zeros((reps, len(ix)), dtype=np.int64)
        class_ix = [np.flatnonzero(labels == c) for c in range(4)]
        for k in range(reps):
            for indices in class_ix:
                chosen = rng.permutation(indices)[:len(indices) // 2]
                half_a[k, chosen] = 1
        half_b = 1 - half_a
        auc_a = np.asarray([weighted_auc(labels, v, half_a) for v in values])
        auc_b = np.asarray([weighted_auc(labels, v, half_b) for v in values])
        for run in range(5):
            for h, weights, computed in [('a', half_a, auc_a), ('b', half_b, auc_b)]:
                for k in range(2):
                    reference = roc_auc_score(labels, values[run], multi_class='ovr', average='macro', sample_weight=weights[k])
                    error = abs(reference - computed[run, k])
                    max_auc_error = max(max_auc_error, error)
                    assert error < 1e-12
                    independent_auc_checks += 1
        winner_a = priority[np.argmax(auc_a[priority], axis=0)]
        winner_b = priority[np.argmax(auc_b[priority], axis=0)]
        k = np.arange(reps)
        apparent = .5 * (auc_a[winner_a, k] + auc_b[winner_b, k])
        independent = .5 * (auc_b[winner_a, k] + auc_a[winner_b, k])
        for k in range(reps):
            row = {'bank_id': bank['bank_id'], 'branch': bank['branch'], 'split': k,
                   'selected_on_A_run': int(winner_a[k]), 'selected_on_B_run': int(winner_b[k]),
                   'apparent_selection_half_AUROC': apparent[k], 'independent_half_AUROC': independent[k],
                   'selection_optimism': apparent[k] - independent[k]}
            for policy, run in bank['policy_runs'].items():
                row[f'fixed_{policy}_half_AUROC'] = .5 * (auc_a[run, k] + auc_b[run, k])
            split_rows.append(row)
        print(json.dumps({'analyzed': bank['bank_id'], 'split_diagnostics': reps}), flush=True)
    assert np.isfinite(policy_prob).all() and np.isfinite(hindsight_prob).all()
    # Matched participant-cluster bootstrap for the original development-only rules.
    rng = np.random.default_rng(p['bootstrap']['seed'])
    weights = []
    for _ in range(p['bootstrap']['replicates']):
        sample = np.concatenate([rng.choice(ix, len(ix), replace=True) for ix in [np.flatnonzero(y == c) for c in range(4)]])
        weights.append(np.bincount(sample, minlength=491))
    weights = np.asarray(weights)
    point = np.empty((3, 4, 2))
    boot = np.empty((3, 4, 2, len(weights)))
    oof_rows = []
    for b, branch in enumerate(p['branches']):
        for policy_index, policy in enumerate(p['policies']):
            for r in range(2):
                value = policy_prob[b, policy_index, r]
                point[b, policy_index, r] = roc_auc_score(y, value, multi_class='ovr', average='macro')
                boot[b, policy_index, r] = weighted_auc(y, value, weights)
            oof_rows.append({'branch': branch, 'policy': policy, 'mean_repeated_OOF_AUROC': point[b, policy_index].mean()})
        for run in range(5):
            scores = [roc_auc_score(y, probability[b, run, r], multi_class='ovr', average='macro') for r in range(2)]
            oof_rows.append({'branch': branch, 'policy': f'fixed_run_{run}', 'mean_repeated_OOF_AUROC': np.mean(scores)})
        oof_rows.append({'branch': branch, 'policy': 'hindsight_fold_winner_apparent',
                         'mean_repeated_OOF_AUROC': np.mean([roc_auc_score(y, hindsight_prob[b, r], multi_class='ovr', average='macro') for r in range(2)])})
    contrast_rows = []
    for b, branch in enumerate(p['branches']):
        for comparator in range(3):
            delta = point[b, 3].mean() - point[b, comparator].mean()
            bootstrap_delta = boot[b, 3].mean(axis=0) - boot[b, comparator].mean(axis=0)
            lo, hi = np.quantile(bootstrap_delta, [.025, .975])
            contrast_rows.append({'branch': branch, 'comparator': p['policies'][comparator], 'regret_minus_comparator': delta,
                                  'conditional_CI95_low': lo, 'conditional_CI95_high': hi})
    summaries = []
    for branch in p['branches'] + ['all_branches']:
        bs = [row for row in bank_rows if branch == 'all_branches' or row['branch'] == branch]
        ss = [row for row in split_rows if branch == 'all_branches' or row['branch'] == branch]
        optimism = np.asarray([row['selection_optimism'] for row in ss])
        summary = {'branch': branch, 'banks': len(bs), 'splits_per_bank': 200,
                   'mean_within_bank_outer_AUROC_range': np.mean([row['outer_AUROC_range'] for row in bs]),
                   'median_within_bank_outer_AUROC_range': np.median([row['outer_AUROC_range'] for row in bs]),
                   'mean_hindsight_apparent_advantage_over_locked': np.mean([row['hindsight_apparent_advantage_over_locked'] for row in bs]),
                   'mean_apparent_selection_half_AUROC': np.mean([row['apparent_selection_half_AUROC'] for row in ss]),
                   'mean_independent_half_AUROC': np.mean([row['independent_half_AUROC'] for row in ss]),
                   'mean_selection_optimism': optimism.mean(), 'median_selection_optimism': np.median(optimism),
                   'split_distribution_q025_not_CI': np.quantile(optimism, .025), 'split_distribution_q975_not_CI': np.quantile(optimism, .975),
                   'mean_observed_candidate_jaccard': np.mean([row['mean_candidate_jaccard'] for row in bs]),
                   'mean_uniform_null_expected_jaccard': np.mean([row['uniform_null_expected_jaccard'] for row in bs])}
        for policy in p['policies']:
            summary[f'fixed_{policy}_half_AUROC'] = np.mean([row[f'fixed_{policy}_half_AUROC'] for row in ss])
        summaries.append(summary)
    outputs = {'all_candidate_outer_metrics.csv': candidate_rows, 'bank_diagnostics.csv': bank_rows,
               'independent_half_selection_diagnostics.csv': split_rows, 'summary_by_branch.csv': summaries,
               'original_policy_geometry.csv': geometry_rows, 'repeated_oof_AUROC.csv': oof_rows,
               'paired_original_policy_contrasts.csv': contrast_rows}
    for name, rows in outputs.items():
        write(out / name, rows)
    validation = {'completed_utc': datetime.now(timezone.utc).isoformat(), 'protocol_sha256': ph,
                  'candidate_rows': len(candidate_rows), 'banks': len(bank_rows), 'split_diagnostic_rows': len(split_rows),
                  'original_policy_rows': len(geometry_rows), 'independent_sklearn_weighted_AUC_checks': independent_auc_checks,
                  'maximum_weighted_AUC_error': max_auc_error, 'all_original_policies_and_branches_retained': True,
                  'split_dispersion_is_not_inferential_CI': True, 'elapsed_seconds': time.perf_counter() - start,
                  'output_sha256': {name: sha(out / name) for name in outputs}}
    (out / 'analysis_validation.json').write_text(json.dumps(validation, indent=2) + '\n')
    print(json.dumps(summaries, indent=2))


if __name__ == '__main__':
    main()
