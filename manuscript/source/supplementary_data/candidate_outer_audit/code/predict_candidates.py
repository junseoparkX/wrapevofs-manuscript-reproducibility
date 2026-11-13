"""Validate server models, reproduce archived predictions, and predict all candidates locally."""
import csv
import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import sklearn

HERE = Path(__file__).resolve().parent
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
jsha = lambda x: hashlib.sha256(json.dumps(x, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def main():
    start = time.perf_counter()
    p = json.loads((HERE / 'protocol.json').read_text())
    ph = sha(HERE / 'protocol.json')
    assert ph == (HERE / 'FROZEN_BEFORE_NEW_PREDICTIONS.sha256').read_text().strip()
    assert sha(Path(__file__)) == p['code_sha256']['predict_candidates.py']
    assert sha(HERE / 'local_sources.json') == p['input_sha256']['local_sources']
    assert [sklearn.__version__, np.__version__, joblib.__version__] == ['1.6.1', '2.0.2', '1.4.2']
    training = json.loads((HERE / 'training_manifest.json').read_text())
    assert training['protocol_sha256'] == ph and training['fits'] == 150
    records = {(r['identity']['bank_id'], r['identity']['run_id']): r for r in training['records']}
    banks = json.loads((HERE / 'candidate_inventory.json').read_text())
    sources = {s['bank_id']: s for s in json.loads((HERE / 'local_sources.json').read_text())}
    raw, label_by_id, checks, max_original_error = [], {}, [], 0.0
    for bank in banks:
        source = sources[bank['bank_id']]
        directory = Path(source['directory'])
        for name, key in [('prepared_selection.npz', 'prepared_sha256'), ('outer_labels.npz', 'outer_labels_sha256'),
                          ('outer_predictions.csv', 'original_predictions_sha256'), ('locking_results.json', 'locking_results_sha256')]:
            assert sha(directory / name) == source[key]
        with np.load(directory / 'prepared_selection.npz', allow_pickle=False) as d:
            names = d['feature_names'].astype(str).tolist()
            x = d['x_outer'].astype(np.float32)
            ids, train_ids = d['outer_ids'].astype(str).tolist(), d['train_ids'].astype(str).tolist()
        with np.load(directory / 'outer_labels.npz', allow_pickle=False) as d:
            y = d['y_outer'].astype(np.int8)
        assert len(x) == len(y) == len(ids) and not set(ids) & set(train_ids)
        assert jsha(ids) == source['outer_ids_sha256'] and jsha(train_ids) == source['train_ids_sha256']
        for participant, label in zip(ids, y):
            if participant in label_by_id:
                assert label_by_id[participant] == int(label)
            label_by_id[participant] = int(label)
        predictions = {}
        for c in bank['candidates']:
            record = records[(bank['bank_id'], c['run_id'])]
            identity = record['identity']
            assert identity['features'] == c['features'] and identity['mask_hash'] == c['mask_hash']
            assert identity['feature_order_sha256'] == jsha(c['features'])
            assert identity['protocol_sha256'] == ph and identity['seed'] == bank['final_seed']
            assert identity['development_sha256'] == bank['development_sha256']
            assert identity['RF_params'] == p['RF_params'] and record['hostname'] == 'fenn10'
            path = HERE / 'private_models' / record['model_file']
            assert sha(path) == record['model_sha256']
            model = joblib.load(path)
            assert len(model.estimators_) == 500 and model.classes_.tolist() == [0, 1, 2, 3]
            assert model.random_state == bank['final_seed']
            probe = np.random.default_rng(p['synthetic_probe_seed']).normal(size=(16, len(c['features']))).astype(np.float32)
            assert np.array_equal(model.predict_proba(probe), np.asarray(record['synthetic_probe_probability']))
            probabilities = model.predict_proba(x[:, [names.index(f) for f in c['features']]])
            assert probabilities.shape == (len(y), 4) and np.isfinite(probabilities).all()
            predictions[c['run_id']] = probabilities
        with (directory / 'outer_predictions.csv').open(newline='', encoding='utf-8') as f:
            prior = list(csv.DictReader(f))
        for policy, run in bank['policy_runs'].items():
            indexed = {r['patient_id']: r for r in prior if r['method'] == policy}
            assert set(indexed) == set(ids)
            reference = np.array([[float(indexed[i][f'prob_class_{c}']) for c in range(4)] for i in ids])
            error = float(np.max(np.abs(reference - predictions[run])))
            max_original_error = max(max_original_error, error)
            assert error < 1e-12, (bank['bank_id'], policy, error)
            checks.append({'bank_id': bank['bank_id'], 'policy': policy, 'run_id': run,
                           'maximum_original_probability_difference': error, 'outer_rows': len(y)})
        raw.append((bank, ids, predictions))
        print(json.dumps({'bank': bank['bank_id'], 'candidates': 5, 'original_policy_max_error': max_original_error}), flush=True)
    ids = sorted(label_by_id)
    assert len(ids) == 491
    lookup = {i: n for n, i in enumerate(ids)}
    y = np.asarray([label_by_id[i] for i in ids], dtype=np.int8)
    assert np.bincount(y).tolist() == [66, 147, 165, 113]
    probabilities = np.full((3, 5, 2, 491, 4), np.nan)
    coverage = np.zeros((3, 5, 2, 491), dtype=np.int8)
    folds = np.zeros((3, 2, 491), dtype=np.int8)
    for bank, row_ids, predictions in raw:
        b, r = p['branches'].index(bank['branch']), bank['repeat'] - 1
        ix = np.asarray([lookup[i] for i in row_ids])
        folds[b, r, ix] = bank['fold']
        for run, values in predictions.items():
            probabilities[b, run, r, ix] = values
            coverage[b, run, r, ix] += 1
    assert np.all(coverage == 1) and np.isfinite(probabilities).all()
    assert np.array_equal(folds[0], folds[1]) and np.array_equal(folds[0], folds[2])
    private = HERE / 'private_predictions'
    private.mkdir(exist_ok=True)
    payload = private / 'candidate_oof.npz'
    np.savez_compressed(payload, probabilities=probabilities, y=y, participant_ids=np.asarray(ids), folds=folds)
    report = {'completed_utc': datetime.now(timezone.utc).isoformat(), 'protocol_sha256': ph,
              'participants': 491, 'candidate_model_fits': 150, 'original_policy_checks': 120,
              'maximum_original_probability_difference': max_original_error,
              'all_synthetic_probes_exact': True, 'OOF_coverage_exactly_once_per_repeat': True,
              'outer_data_uploaded': False, 'payload_sha256': sha(payload),
              'elapsed_seconds': time.perf_counter() - start, 'checks': checks}
    (HERE / 'prediction_verification.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: v for k, v in report.items() if k != 'checks'}), flush=True)


if __name__ == '__main__':
    main()
