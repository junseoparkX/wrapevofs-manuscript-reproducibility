"""Fenn-only fresh GA runs, immutable receipts and development-only rescoring."""
import argparse
import contextlib
import hashlib
import json
import os
import platform
import socket
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import sklearn
from sklearn.model_selection import StratifiedKFold
import wrapevofs
from wrapevofs.config import GAConfig
from wrapevofs.locking import score_candidate_feature_sets
from wrapevofs.selectors.genetic_rf import run_genetic_rf

HERE = Path(__file__).resolve().parent
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
now = lambda: datetime.now(timezone.utc).isoformat()


def save(path, obj):
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(obj, indent=2) + '\n')
    os.replace(temporary, path)


def load():
    p = json.loads((HERE / 'protocol.json').read_text())
    assert sha(HERE / 'protocol.json') == (HERE / 'FROZEN_BEFORE_NEW_CANDIDATES.sha256').read_text().strip()
    assert sha(Path(__file__)) == p['code_sha256'][Path(__file__).name]
    assert wrapevofs.__version__ == '0.2.0'
    assert [np.__version__, sklearn.__version__, joblib.__version__] == ['2.0.2', '1.6.1', '1.4.2']
    assert socket.gethostname() == 'fenn10'
    for c in p['conditions']:
        assert sha(HERE / 'private_development' / c['development_file']) == c['development_sha256']
    return p


def arrays(c):
    with np.load(HERE / 'private_development' / c['development_file'], allow_pickle=False) as d:
        assert set(d.files) == {'X', 'y', 'feature_names'}
        x = pd.DataFrame(d['X'], columns=d['feature_names'].astype(str))
        y = pd.Series(d['y'].astype(np.int8))
    assert x.shape == (c['development_rows'], c['feature_universe_size']) and np.isfinite(x).all().all()
    return x, y


def configuration(p, seed, directory, profile=False):
    values = {**p['ga'], 'backend': 'cpu', 'n_runs': 1, 'top_k': 1,
              'random_state': seed, 'n_jobs': 1, 'verbose': True, 'progress_interval': 1,
              'checkpoint_dir': str(directory / 'checkpoint'), 'resume_from_checkpoint': False}
    if profile:
        values['n_generations'] = 1
    return GAConfig(**values)


def job(c, bank, run, seed, p):
    directory = HERE / 'runs' / c['branch'] / f'bank_{bank:02d}' / f'run_{run:02d}'
    directory.mkdir(parents=True, exist_ok=True)
    receipt_path = directory / 'complete.json'
    identity = {'protocol_sha256': sha(HERE / 'protocol.json'), 'condition_id': c['condition_id'],
                'bank': bank, 'run': run, 'GA_seed': seed, 'development_sha256': c['development_sha256']}
    if receipt_path.exists():
        receipt = json.loads(receipt_path.read_text())
        assert receipt['identity'] == identity
        assert sha(directory / 'candidate.json') == receipt['candidate_sha256']
        return {**receipt, 'reused': True}
    assert not (directory / 'FAILED.json').exists(), 'No automatic retry of a failed job'
    assert not (directory / 'STARTED.json').exists(), 'Interrupted job requires explicit recovery; do not overwrite'
    save(directory / 'STARTED.json', {**identity, 'started_utc': now(), 'pid': os.getpid()})
    started = time.perf_counter()
    try:
        x, y = arrays(c)
        config = configuration(p, seed, directory)
        with (directory / 'stdout.log').open('w', buffering=1) as stdout, (directory / 'stderr.log').open('w', buffering=1) as stderr:
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                result = run_genetic_rf(x, y, c['target_k'], name=f"{c['branch']}_b{bank}_r{run}", config=config)
                assert result.metadata['actual_backend'] == 'cpu' and result.top_solutions
                solution = result.top_solutions[0]
                features = list(map(str, solution.selected_features))
                mask = np.asarray([f in set(features) for f in x.columns], dtype=np.uint8)
                assert hashlib.sha256(mask.tobytes()).hexdigest() == solution.stable_mask_hash
                scores = {}
                for scheme in p['score_schemes']:
                    rf_seed = seed if scheme == 'original_candidate_seed' else p['locking_cv_seed']
                    candidate = score_candidate_feature_sets(
                        x, y, {run: features}, locking_metric=p['locking']['metric'],
                        cv_folds=p['locking']['cv_folds'], random_state=p['locking_cv_seed'],
                        rf_params=p['locking']['rf_params'], n_jobs=1, run_seeds={run: rf_seed})[0]
                    scores[scheme] = {'locking_score': candidate.locking_score,
                                      'fold_scores': list(candidate.fold_locking_scores), 'RF_seed': rf_seed}
        checkpoint = json.loads((directory / 'checkpoint/checkpoint.json').read_text())
        assert checkpoint['current_generation'] == p['ga']['n_generations']
        assert len(result.history) == p['ga']['n_generations']
        result.history.to_csv(directory / 'ga_history.csv', index=False)
        candidate = {'identity': identity, 'features': features, 'feature_count': len(features),
                     'mask_hash': solution.stable_mask_hash, 'GA_base_score': float(solution.base_score),
                     'GA_objective': float(solution.raw_objective), 'scores': scores,
                     'GA_config': asdict(config), 'GA_metadata': result.metadata}
        save(directory / 'candidate.json', candidate)
        receipt = {'identity': identity, 'candidate_sha256': sha(directory / 'candidate.json'),
                   'checkpoint_sha256': sha(directory / 'checkpoint/checkpoint.json'),
                   'resume_state_sha256': sha(directory / 'checkpoint/resume_state.npz'),
                   'completed_generations': checkpoint['current_generation'], 'hostname': socket.gethostname(),
                   'elapsed_seconds': time.perf_counter() - started, 'completed_utc': now()}
        save(receipt_path, receipt)
        return {**receipt, 'reused': False}
    except BaseException as error:
        import traceback
        save(directory / 'FAILED.json', {'identity': identity, 'failed_utc': now(), 'error': repr(error), 'traceback': traceback.format_exc()})
        raise


def profile(p):
    directory = HERE / 'profile'
    directory.mkdir(exist_ok=True)
    c = p['conditions'][0]
    x, y = arrays(c)
    start = time.perf_counter()
    with (directory / 'stdout.log').open('w', buffering=1) as output:
        with contextlib.redirect_stdout(output):
            result = run_genetic_rf(x, y, c['target_k'], name='timing_only', config=configuration(p, 202611119, directory, True))
    elapsed = time.perf_counter() - start
    folds = list(StratifiedKFold(n_splits=5, shuffle=True, random_state=342).split(x, y))
    digest = hashlib.sha256()
    for tr, va in folds:
        digest.update(tr.astype('<i8').tobytes()); digest.update(va.astype('<i8').tobytes())
    report = {'hostname': socket.gethostname(), 'protocol_sha256': sha(HERE / 'protocol.json'),
              'condition': c['condition_id'], 'population': 50, 'generations': 1,
              'elapsed_seconds': elapsed, 'linear_total_hours_at_8_workers': elapsed * 50 * 240 / 8 / 3600,
              'timing_only_not_an_analysis_run': True, 'GA_seed_not_in_registered_banks': 202611119,
              'actual_backend': result.metadata['actual_backend'], 'locking_fold_hash': digest.hexdigest(),
              'versions': {'python': platform.python_version(), 'wrapevofs': wrapevofs.__version__,
                           'numpy': np.__version__, 'pandas': pd.__version__, 'sklearn': sklearn.__version__, 'joblib': joblib.__version__}}
    save(HERE / 'profile_report.json', report)
    print(json.dumps(report), flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--profile', action='store_true')
    args = parser.parse_args()
    p = load()
    if args.profile:
        return profile(p)
    start = time.perf_counter()
    jobs = [(c, b, r, seed, p) for r in range(20) for c in p['conditions']
            for b, bank in enumerate(c['seed_banks']) for seed in [bank[r]]]
    assert len(jobs) == p['total_GA_runs']
    save(HERE / 'run_status.json', {'state': 'running', 'started_utc': now(), 'pid': os.getpid(),
                                   'total': len(jobs), 'completed': 0, 'protocol_sha256': sha(HERE / 'protocol.json')})
    records = []
    with ProcessPoolExecutor(max_workers=p['workers']) as pool:
        futures = [pool.submit(job, *args) for args in jobs]
        for future in as_completed(futures):
            records.append(future.result())
            status = {'state': 'running', 'completed': len(records), 'total': len(jobs),
                      'elapsed_seconds': time.perf_counter() - start, 'updated_utc': now(), 'last': records[-1]['identity']}
            save(HERE / 'run_status.json', status)
            print(json.dumps(status), flush=True)
    save(HERE / 'training_manifest.json', {'hostname': socket.gethostname(), 'completed_utc': now(),
         'protocol_sha256': sha(HERE / 'protocol.json'), 'jobs': len(records), 'records': records,
         'elapsed_seconds': time.perf_counter() - start, 'outer_data_accesses': 0})
    from analyze_banks import main as analyze
    analyze()
    save(HERE / 'run_status.json', {'state': 'completed', 'completed': len(records), 'total': len(jobs),
                                  'elapsed_seconds': time.perf_counter() - start, 'completed_utc': now()})


if __name__ == '__main__':
    try:
        main()
    except BaseException as error:
        import traceback
        save(HERE / 'run_failure.json', {'failed_utc': now(), 'error': repr(error), 'traceback': traceback.format_exc()})
        raise
