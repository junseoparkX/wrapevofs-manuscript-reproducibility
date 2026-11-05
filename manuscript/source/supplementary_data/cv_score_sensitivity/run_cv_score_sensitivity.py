"""Exhaustive paired CV-score sensitivity on frozen aggregate masks and scores.

Standard-library computation; optional independent NumPy verification. No model
fitting, participant data, held-out predictions or outcomes are read.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import itertools
import json
import math
import platform
import socket
import statistics
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

POLICIES = ('highest_score', 'legacy_top3', 'unrestricted_medoid', 'regret_medoid')
SCHEMES = ('leave_one_fold_out', 'fold_bootstrap')
TOL = 1e-12


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def mean(values):
    total = 0.0
    for x in values:
        total += x
    return total / len(values)


def weighted_scores(bank, counts):
    return [mean_sum([c['folds'][f] * counts[f] for f in range(5)]) / sum(counts) for c in bank]


def mean_sum(values):
    total = 0.0
    for value in values:
        total += value
    return total


def choose(bank, scores, jaccard, delta):
    n = len(bank)
    canonical = sorted(range(n), key=lambda i: (bank[i]['hash'], bank[i]['run']))
    best = max(scores)
    eligible = [i for i in canonical if best - scores[i] <= delta]
    highest = min(range(n), key=lambda i: (-scores[i], bank[i]['count'], bank[i]['hash']))
    legacy_pool = sorted(range(n), key=lambda i: (-scores[i], bank[i]['hash'], bank[i]['run']))[:3]
    legacy_pool = [i for i in canonical if i in legacy_pool]
    selections = {'highest_score': (highest, [highest])}
    for policy, pool in [('legacy_top3', legacy_pool), ('unrestricted_medoid', canonical), ('regret_medoid', eligible)]:
        if len(pool) == 1:
            selected = pool[0]
        else:
            overlaps = {i: mean([jaccard[i][j] for j in pool if i != j]) for i in pool}
            if policy == 'legacy_top3':
                selected = min(pool, key=lambda i: (-overlaps[i], -scores[i], bank[i]['run']))
            else:
                selected = min(pool, key=lambda i: (-overlaps[i], -scores[i], bank[i]['count'], bank[i]['hash']))
        selections[policy] = (selected, pool)
    assert best - scores[selections['regret_medoid'][0]] <= delta
    return selections, eligible


def independent_numpy(bank, counts, delta):
    """Independent array/mask implementation; does not call choose/weighted_scores."""
    import numpy as np
    data = np.asarray([c['folds'] for c in bank], dtype=np.float64)
    w = np.asarray(counts, dtype=np.float64)
    score = np.sum(data * w[None, :], axis=1) / np.sum(w)
    masks = np.asarray([[v == '1' for v in c['mask']] for c in bank])
    similarity = np.zeros((5, 5))
    for i in range(5):
        for j in range(5):
            similarity[i, j] = np.count_nonzero(masks[i] & masks[j]) / np.count_nonzero(masks[i] | masks[j])
    ordered = sorted(range(5), key=lambda i: (bank[i]['hash'], bank[i]['run']))
    high = sorted(range(5), key=lambda i: (-score[i], bank[i]['count'], bank[i]['hash']))[0]
    pool3 = set(sorted(range(5), key=lambda i: (-score[i], bank[i]['hash'], bank[i]['run']))[:3])
    pools = {'legacy_top3': [i for i in ordered if i in pool3], 'unrestricted_medoid': ordered,
             'regret_medoid': [i for i in ordered if float(np.max(score)-score[i]) <= delta]}
    result = {'highest_score': high}
    for policy, pool in pools.items():
        if len(pool) == 1:
            result[policy] = pool[0]
            continue
        av = {i: float(np.mean([similarity[i,j] for j in pool if i != j])) for i in pool}
        if policy == 'legacy_top3':
            keys = [( -av[i], -score[i], bank[i]['run'], i) for i in pool]
        else:
            keys = [(-av[i], -score[i], bank[i]['count'], bank[i]['hash'], i) for i in pool]
        result[policy] = min(keys)[-1]
    return list(map(float, score)), result


def read_banks(paths, protocol):
    banks, meta = defaultdict(list), {}
    checks = Counter()
    original = {}
    for cohort, path in paths.items():
        expected = next(x for x in protocol['inputs'] if x['cohort'] == cohort)
        assert sha(path) == expected['sha256']
        with path.open(encoding='utf-8-sig', newline='') as f:
            rows = list(csv.DictReader(f))
        for row in rows:
            if cohort == 'TCGA':
                key = f"TCGA__{row['outer_repeat']}__{row['outer_fold']}__{row['branch']}"
                metadata = {'cohort': cohort, 'bank_id': key, 'branch': row['branch'], 'center': '', 'cap': '', 'repeat': row['outer_repeat'], 'outer_fold': row['outer_fold']}
            else:
                key = f"AMPAD__{row['center']}__{row['branch']}__{row['cap']}"
                metadata = {'cohort': cohort, 'bank_id': key, 'branch': row['branch'], 'center': row['center'], 'cap': row['cap'], 'repeat': '', 'outer_fold': ''}
            meta[key] = metadata
            features = frozenset(json.loads(row['canonical_features']))
            mask = row['canonical_mask']
            assert hashlib.sha256(bytes(int(c) for c in mask)).hexdigest() == row['stable_mask_hash']
            assert len(features) == mask.count('1') == int(row['feature_count'])
            folds = tuple(map(float, json.loads(row['fold_locking_scores'])))
            assert len(folds) == 5 and all(math.isfinite(x) for x in folds)
            banks[key].append({'run': int(row['run_id']), 'features': features, 'mask': mask,
                               'hash': row['stable_mask_hash'], 'count': len(features), 'folds': folds,
                               'saved_score': float(row['locking_score']), 'universe': row['candidate_universe_sha256']})
            if row['selected'].lower() == 'true':
                assert key not in original
                original[key] = row['stable_mask_hash']
        checks['candidate_mask_hashes_verified'] += len(rows)
    matrices = {}
    for key, bank in banks.items():
        bank.sort(key=lambda c: (c['hash'], c['run']))
        assert len(bank) == 5 and len({c['hash'] for c in bank}) == 5
        assert len({c['run'] for c in bank}) == 5 and len({c['universe'] for c in bank}) == 1
        assert len({len(c['mask']) for c in bank}) == 1
        checks['banks_without_duplicate_masks'] += 1
        matrix = []
        for a in bank:
            line = []
            for b in bank:
                intersection, union = len(a['features'] & b['features']), len(a['features'] | b['features'])
                assert intersection == sum(x == y == '1' for x,y in zip(a['mask'], b['mask']))
                assert union == sum(x == '1' or y == '1' for x,y in zip(a['mask'], b['mask']))
                line.append(intersection/union)
            matrix.append(line)
        matrices[key] = matrix
    return banks, meta, original, matrices, checks


def write_csv(path, rows):
    with path.open('w', encoding='utf-8', newline='') as f:
        columns = list(dict.fromkeys(k for r in rows for k in r))
        writer = csv.DictWriter(f, fieldnames=columns); writer.writeheader(); writer.writerows(rows)


def describe(xs):
    return {'n': len(xs), 'mean': math.fsum(xs)/len(xs), 'median': statistics.median(xs), 'min': min(xs), 'max': max(xs)} if xs else {'n': 0}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for arg in ['tcga', 'ampad', 'protocol', 'output']:
        parser.add_argument('--'+arg, type=Path, required=True)
    parser.add_argument('--execution-label', required=True)
    parser.add_argument('--validate-numpy', action='store_true')
    args = parser.parse_args()
    started = datetime.now(timezone.utc).isoformat(); timer = time.perf_counter()
    protocol = json.loads(args.protocol.read_text(encoding='utf-8'))
    assert protocol['delta'] == .01
    out = args.output; out.mkdir(parents=True, exist_ok=True)
    banks, meta, originals, matrices, checks = read_banks({'TCGA': args.tcga, 'AMPAD': args.ampad}, protocol)
    assert len(banks) == 54
    vectors = []
    for omitted in range(5):
        counts = tuple(0 if f == omitted else 1 for f in range(5))
        vectors.append({'scheme': SCHEMES[0], 'weight_id': 'lofo_'+str(omitted+1), 'counts': counts, 'multiplicity': 1, 'denominator': 5})
    bootstrap = []
    for counts in itertools.product(range(6), repeat=5):
        if sum(counts) != 5:
            continue
        multiplicity = math.factorial(5)//math.prod(math.factorial(c) for c in counts)
        bootstrap.append({'scheme': SCHEMES[1], 'weight_id': 'b_'+''.join(map(str,counts)), 'counts': counts, 'multiplicity': multiplicity, 'denominator': 3125})
    assert len(bootstrap) == 126 and sum(v['multiplicity'] for v in bootstrap) == 3125
    independent_counts = Counter(tuple(sequence.count(f) for f in range(5)) for sequence in itertools.product(range(5), repeat=5))
    assert {v['counts']: v['multiplicity'] for v in bootstrap} == dict(independent_counts)
    checks['ordered_bootstrap_samples_independently_enumerated'] = 3125
    vectors += bootstrap
    weight_rows = [{**{k:v for k,v in item.items() if k != 'counts'}, **{f'count_fold_{i+1}': item['counts'][i] for i in range(5)}, 'probability': item['multiplicity']/item['denominator']} for item in vectors]
    case_rows, bank_rows, probability_rows, baseline_rows = [], [], [], []
    max_uniform_saved_difference = 0.0
    for key in sorted(banks):
        bank, j = banks[key], matrices[key]
        uniform = weighted_scores(bank, (1,1,1,1,1))
        initial, initial_eligible = choose(bank, uniform, j, .01)
        assert bank[initial['regret_medoid'][0]]['hash'] == originals[key], (key, 'uniform does not reproduce archived lock')
        checks['uniform_archived_regret_selections_reproduced'] += 1
        max_uniform_saved_difference = max(max_uniform_saved_difference, max(abs(c['saved_score']-x) for c,x in zip(bank, uniform)))
        same_initial = initial['regret_medoid'][0] == initial['highest_score'][0]
        for policy in POLICIES:
            i, pool = initial[policy]
            baseline_rows.append({**meta[key], 'policy': policy, 'selected_run': bank[i]['run'], 'selected_mask_hash': bank[i]['hash'],
                                  'uniform_score': uniform[i], 'stored_score': bank[i]['saved_score'], 'uniform_score_gap': max(uniform)-uniform[i],
                                  'pool_size': len(pool), 'initial_proposed_equals_highest': same_initial})
        if args.validate_numpy:
            import numpy as np
            assert uniform == [float(np.mean(c['folds'])) for c in bank]
            checks['uniform_numpy_means_bitwise_equal'] += 5
            for counts in protocol['independent_check_vectors']:
                score = weighted_scores(bank, counts)
                selected, eligible = choose(bank, score, j, .01)
                numpy_score, numpy_selected = independent_numpy(bank, counts, .01)
                assert score == numpy_score, (key, counts, 'weighted score arithmetic')
                assert {p:selected[p][0] for p in POLICIES} == numpy_selected, (key, counts, 'independent selection')
                checks['independent_numpy_policy_choices_matched'] += 4
        per_scheme = defaultdict(list)
        for vector in vectors:
            scores = weighted_scores(bank, vector['counts'])
            selected, eligible = choose(bank, scores, j, .01)
            initial_set, eligible_set = set(initial_eligible), set(eligible)
            for policy in POLICIES:
                i, pool = selected[policy]; original = initial[policy][0]
                row = {**meta[key], 'scheme': vector['scheme'], 'weight_id': vector['weight_id'],
                       'fold_counts': '|'.join(map(str,vector['counts'])), 'multiplicity': vector['multiplicity'], 'denominator': vector['denominator'],
                       'policy': policy, 'selected_run': bank[i]['run'], 'selected_mask_hash': bank[i]['hash'],
                       'original_run': bank[original]['run'], 'original_mask_hash': bank[original]['hash'],
                       'signature_retained': bank[i]['hash'] == bank[original]['hash'],
                       'run_retained': bank[i]['run'] == bank[original]['run'],
                       'jaccard_to_original': j[i][original], 'selected_score': scores[i], 'best_score': max(scores),
                       'perturbed_score_gap': max(scores)-scores[i], 'selected_uniform_score_gap': max(uniform)-uniform[i],
                       'policy_pool_size': len(pool), 'regret_pool_size': len(eligible),
                       'regret_pool_run_ids': '|'.join(str(bank[q]['run']) for q in eligible),
                       'regret_pool_changed': eligible_set != initial_set,
                       'regret_pool_jaccard': len(eligible_set & initial_set)/len(eligible_set | initial_set),
                       'initial_proposed_equals_highest': same_initial}
                case_rows.append(row); per_scheme[(vector['scheme'],policy)].append(row)
        for (scheme,policy), cases in per_scheme.items():
            denominator = cases[0]['denominator']; assert sum(r['multiplicity'] for r in cases) == denominator
            expectation = lambda field: math.fsum(r['multiplicity']*r[field] for r in cases)/denominator
            counts = Counter()
            for r in cases:
                counts[r['selected_mask_hash']] += r['multiplicity']
            probabilities = [counts[c['hash']]/denominator for c in bank]
            assert math.isclose(math.fsum(probabilities),1.0,abs_tol=1e-15)
            entropy = -math.fsum(p*math.log2(p) for p in probabilities if p)
            bank_rows.append({**meta[key], 'scheme': scheme, 'policy': policy, 'count_vectors': len(cases), 'resample_mass': denominator,
                              'retention_probability': expectation('signature_retained'), 'change_probability': 1-expectation('signature_retained'),
                              'expected_jaccard_to_original': expectation('jaccard_to_original'), 'selection_entropy_bits': entropy,
                              'selection_entropy_normalized': entropy/math.log2(5), 'mean_perturbed_score_gap': expectation('perturbed_score_gap'),
                              'max_perturbed_score_gap': max(r['perturbed_score_gap'] for r in cases),
                              'probability_gap_above_delta': math.fsum(r['multiplicity'] for r in cases if r['perturbed_score_gap'] > .01)/denominator,
                              'expected_selected_uniform_score_gap': expectation('selected_uniform_score_gap'),
                              'regret_pool_change_probability': expectation('regret_pool_changed'),
                              'expected_regret_pool_size': expectation('regret_pool_size'), 'expected_regret_pool_jaccard': expectation('regret_pool_jaccard'),
                              'distinct_selected_signatures': sum(p>0 for p in probabilities), 'initial_proposed_equals_highest': same_initial})
            for c,p in zip(bank, probabilities):
                probability_rows.append({**meta[key], 'scheme': scheme, 'policy': policy, 'run_id': c['run'], 'mask_hash': c['hash'],
                                         'selection_multiplicity': counts[c['hash']], 'total_multiplicity': denominator, 'selection_probability': p})
    checks['weighted_policy_decisions'] = len(case_rows)
    checks['all_mask_and_run_retention_identical_no_duplicates'] = int(all(r['signature_retained']==r['run_retained'] for r in case_rows))
    metrics = ['retention_probability','change_probability','expected_jaccard_to_original','selection_entropy_bits','mean_perturbed_score_gap','expected_selected_uniform_score_gap','regret_pool_change_probability','expected_regret_pool_size','expected_regret_pool_jaccard']
    groups = {'ALL54': lambda r: True, 'TCGA': lambda r:r['cohort']=='TCGA', 'AMPAD':lambda r:r['cohort']=='AMPAD',
              'NONRUSH48':lambda r:r['center']!='rush','AMPAD_NONRUSH18':lambda r:r['cohort']=='AMPAD' and r['center']!='rush', 'RUSH6':lambda r:r['center']=='rush'}
    for cohort in ['TCGA','AMPAD']:
        for branch in ['svm_l1','xgboost','boruta_rf']:
            groups[cohort+'__'+branch] = lambda r,c=cohort,b=branch:r['cohort']==c and r['branch']==b
    group_rows, paired_rows, paired_bank_rows = [], [], []
    lookup = {(r['bank_id'],r['scheme'],r['policy']):r for r in bank_rows}
    for key in sorted(banks):
        for scheme in SCHEMES:
            med = lookup[(key,scheme,'regret_medoid')]; high = lookup[(key,scheme,'highest_score')]
            paired_bank_rows.append({**meta[key], 'scheme': scheme, 'initial_proposed_equals_highest':med['initial_proposed_equals_highest'],
                                     **{metric+'_difference_proposed_minus_highest':med[metric]-high[metric] for metric in metrics}})
    for group, predicate in groups.items():
        for scheme in SCHEMES:
            for policy in POLICIES:
                selected = [r for r in bank_rows if predicate(r) and r['scheme']==scheme and r['policy']==policy]
                group_rows.append({'group':group,'scheme':scheme,'policy':policy,'banks':len(selected),
                                   **{metric:math.fsum(r[metric] for r in selected)/len(selected) for metric in metrics},
                                   'minimum_bank_retention':min(r['retention_probability'] for r in selected),'maximum_bank_retention':max(r['retention_probability'] for r in selected),
                                   'minimum_bank_expected_jaccard':min(r['expected_jaccard_to_original'] for r in selected),'maximum_bank_expected_jaccard':max(r['expected_jaccard_to_original'] for r in selected),
                                   'maximum_perturbed_score_gap':max(r['max_perturbed_score_gap'] for r in selected),
                                   'mean_probability_gap_above_delta':math.fsum(r['probability_gap_above_delta'] for r in selected)/len(selected)})
            for stratum in ['all','initial_same','initial_different']:
                selected = [r for r in paired_bank_rows if predicate(r) and r['scheme']==scheme and (stratum=='all' or r['initial_proposed_equals_highest']==(stratum=='initial_same'))]
                if not selected: continue
                for metric in metrics:
                    values=[r[metric+'_difference_proposed_minus_highest'] for r in selected]
                    paired_rows.append({'group':group,'scheme':scheme,'stratum':stratum,'metric':metric, **describe(values),
                                        'positive_banks':sum(x>TOL for x in values),'zero_banks':sum(abs(x)<=TOL for x in values),'negative_banks':sum(x< -TOL for x in values)})
    outputs={'weight_vectors.csv':weight_rows,'uniform_policy_baselines.csv':baseline_rows,'weighted_case_results.csv':case_rows,
             'bank_policy_summary.csv':bank_rows,'candidate_selection_probabilities.csv':probability_rows,'group_policy_summary.csv':group_rows,
             'paired_bank_comparison.csv':paired_bank_rows,'paired_group_summary.csv':paired_rows}
    for name,content in outputs.items(): write_csv(out/name,content)
    summary={'primary_design':'paired fold-score sensitivity; equal bank weights; multinomially weighted complete bootstrap enumeration',
             'banks':54,'primary_banks':{'TCGA':30,'AMPAD':24},'secondary_without_Rush_banks':48,'delta':.01,
             'model_fits':0,'held_out_accesses':0,'original_fold_arrays_unchanged':True,'signature_retention_unit':'mask hash; all54 banks contain5unique masks',
             'checks':dict(checks),'maximum_uniform_recomputed_vs_stored_score_difference':max_uniform_saved_difference,
             'primary_group_rows':[r for r in group_rows if r['group'] in ['ALL54','TCGA','AMPAD','NONRUSH48','AMPAD_NONRUSH18','RUSH6']],
             'primary_paired_rows':[r for r in paired_rows if r['group'] in ['ALL54','TCGA','AMPAD','NONRUSH48'] and r['stratum']=='all'],
             'limitations':protocol['limits']}
    (out/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    manifest={'execution_label':args.execution_label,'hostname':socket.gethostname(),'platform':platform.platform(),'python':sys.version,
              'started_utc':started,'completed_utc':datetime.now(timezone.utc).isoformat(),'elapsed_seconds':time.perf_counter()-timer,
              'script_sha256':sha(Path(__file__)),'protocol_sha256':sha(args.protocol),'input_sha256':{args.tcga.name:sha(args.tcga),args.ampad.name:sha(args.ampad)},
              'model_fits':0,'held_out_accesses':0,'numpy_validation_enabled':args.validate_numpy,
              'output_sha256':{name:sha(out/name) for name in list(outputs)+['summary.json']}}
    (out/'run_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print(json.dumps({'hostname':manifest['hostname'],'elapsed_seconds':manifest['elapsed_seconds'],'checks':dict(checks),
                      'main':[r for r in group_rows if r['group'] in ['TCGA','AMPAD','ALL54','NONRUSH48'] and r['policy'] in ['highest_score','regret_medoid']]},indent=2))


if __name__ == '__main__':
    main()
