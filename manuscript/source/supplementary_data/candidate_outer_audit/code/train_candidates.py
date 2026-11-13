"""Fenn-only training from previously authorized development arrays."""
import hashlib
import json
import os
import platform
import socket
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import sklearn
from sklearn.ensemble import RandomForestClassifier

HERE = Path(__file__).resolve().parent
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def fit(bank, candidate, protocol):
    start = time.perf_counter()
    source = Path(protocol['remote_development_directory']) / bank['development_file']
    assert sha(source) == bank['development_sha256']
    with np.load(source, allow_pickle=False) as d:
        names = d['feature_names'].astype(str).tolist()
        x = d['X'][:, [names.index(f) for f in candidate['features']]].astype(np.float32)
        y = d['y'].astype(np.int8)
    assert len(y) == bank['development_rows'] and np.isfinite(x).all()
    model = RandomForestClassifier(**protocol['RF_params'], random_state=bank['final_seed'], n_jobs=1)
    model.fit(x, y)
    assert model.classes_.tolist() == [0, 1, 2, 3] and len(model.estimators_) == 500
    identity = {'bank_id': bank['bank_id'], 'run_id': candidate['run_id'], 'mask_hash': candidate['mask_hash'],
                'features': candidate['features'], 'feature_order_sha256': candidate['feature_order_sha256'],
                'seed': bank['final_seed'], 'RF_params': protocol['RF_params'],
                'development_sha256': bank['development_sha256'], 'protocol_sha256': sha(HERE / 'protocol.json')}
    directory = HERE / 'private_models'
    directory.mkdir(exist_ok=True)
    path = directory / f"{bank['bank_id']}__run_{candidate['run_id']}.joblib"
    assert not path.exists(), 'Refuse to overwrite a model'
    temporary = path.with_suffix('.tmp')
    joblib.dump(model, temporary, compress=3)
    os.replace(temporary, path)
    probe = np.random.default_rng(protocol['synthetic_probe_seed']).normal(size=(16, len(candidate['features']))).astype(np.float32)
    record = {'identity': identity, 'model_file': path.name, 'model_sha256': sha(path),
              'hostname': socket.gethostname(), 'tree_count': 500,
              'synthetic_probe_probability': model.predict_proba(probe).tolist(),
              'completed_utc': datetime.now(timezone.utc).isoformat(), 'elapsed_seconds': time.perf_counter() - start}
    path.with_suffix('.json').write_text(json.dumps(record, indent=2) + '\n')
    return record


def main():
    start = time.perf_counter()
    p = json.loads((HERE / 'protocol.json').read_text())
    assert socket.gethostname() == 'fenn10'
    assert sha(Path(__file__)) == p['code_sha256']['train_candidates.py']
    assert sha(HERE / 'candidate_inventory.json') == p['input_sha256']['candidate_inventory']
    assert sha(HERE / 'protocol.json') == (HERE / 'FROZEN_BEFORE_NEW_PREDICTIONS.sha256').read_text().strip()
    assert [sklearn.__version__, np.__version__, joblib.__version__] == ['1.6.1', '2.0.2', '1.4.2']
    banks = json.loads((HERE / 'candidate_inventory.json').read_text())
    records = []
    with ProcessPoolExecutor(max_workers=p['workers']) as pool:
        futures = [pool.submit(fit, b, c, p) for b in banks for c in b['candidates']]
        for future in as_completed(futures):
            records.append(future.result())
            if len(records) % 10 == 0:
                print(json.dumps({'completed': len(records), 'total': 150, 'elapsed_seconds': time.perf_counter() - start}), flush=True)
    assert len(records) == 150
    records.sort(key=lambda r: (r['identity']['bank_id'], r['identity']['run_id']))
    result = {'hostname': socket.gethostname(), 'protocol_sha256': sha(HERE / 'protocol.json'),
              'versions': {'python': platform.python_version(), 'numpy': np.__version__, 'sklearn': sklearn.__version__, 'joblib': joblib.__version__},
              'fits': 150, 'elapsed_seconds': time.perf_counter() - start,
              'completed_utc': datetime.now(timezone.utc).isoformat(), 'outer_data_accesses': 0, 'records': records}
    (HERE / 'training_manifest.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k != 'records'}), flush=True)


if __name__ == '__main__':
    main()
