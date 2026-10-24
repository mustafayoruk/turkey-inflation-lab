"""Nested chronological Ridge evaluation; the final holdout is never scored."""
import argparse
import csv
import hashlib
import json
import platform
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import sklearn
from sklearn.linear_model import Ridge
from sklearn.model_selection import TimeSeriesSplit
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from threadpoolctl import threadpool_limits

from evaluate_baselines import (METHODS, load_snapshot, read_limited, summarize,
                                validate_protocol, walk_forward)


def validate_model(model):
    expected = {'lags': 12, 'alphas': [0.1, 1.0, 10.0, 100.0, 1000.0],
                'inner_splits': 3, 'validation_months': 12,
                'tie_break': 'larger_alpha', 'solver': 'svd',
                'scaling': 'train_fold_only', 'gap': 0}
    if model != expected:
        raise ValueError('This version implements only the declared small Ridge design.')


def supervised(history, lags=12):
    values = np.asarray(history, dtype=float)
    if len(values) < lags + 38 or not np.isfinite(values).all():
        raise ValueError('Insufficient finite history for three 12-month validation folds.')
    features = np.asarray([values[t-lags:t][::-1] for t in range(lags, len(values))])
    return features, values[lags:], values[-lags:][::-1].reshape(1, -1)


def estimator(alpha):
    return make_pipeline(StandardScaler(), Ridge(alpha=alpha, solver='svd'))


def forecast(history, model):
    validate_model(model)
    x, y, next_x = supervised(history, model['lags'])
    splitter = TimeSeriesSplit(n_splits=3, test_size=12, gap=0)
    folds = list(splitter.split(x))
    trials = []
    for alpha in model['alphas']:
        losses = []
        for train, validation in folds:
            fitted = estimator(alpha).fit(x[train], y[train])
            losses.append(float(np.mean(np.abs(fitted.predict(x[validation])-y[validation]))))
        trials.append({'alpha': alpha, 'inner_mae': sum(losses)/len(losses)})
    best = min(trials, key=lambda row: (row['inner_mae'], -row['alpha']))
    fitted = estimator(best['alpha']).fit(x, y)
    return float(fitted.predict(next_x)[0]), best, trials


def ridge_walk_forward(rows, protocol):
    predictions, tuning = [], []
    for index, row in enumerate(rows):
        if not protocol['development_start'] <= row['period'] <= protocol['development_end']:
            continue
        history = [past['monthly_pct'] for past in rows[:index]]
        value, best, trials = forecast(history, protocol['model'])
        predictions.append({'target_period': row['period'],
                            'origin_period': rows[index-1]['period'], 'method': 'ridge',
                            'actual': row['monthly_pct'], 'prediction': value,
                            'error': value-row['monthly_pct']})
        for trial in trials:
            tuning.append({'target_period': row['period'], **trial,
                           'selected': trial['alpha'] == best['alpha'],
                           'training_targets': len(history)-12})
    if not predictions:
        raise ValueError('No development origins.')
    return predictions, tuning


def write_csv(path, rows):
    with path.open('w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def run(snapshot, contract_path, output):
    raw = read_limited(contract_path)
    protocol = json.loads(raw)
    validate_protocol(protocol)
    validate_model(protocol['model'])
    rows, source = load_snapshot(snapshot, protocol)
    if output.exists():
        raise FileExistsError(output)
    started = time.perf_counter()
    with threadpool_limits(limits=1):
        ridge, tuning = ridge_walk_forward(rows, protocol)
    predictions = sorted(walk_forward(rows, protocol)+ridge,
                         key=lambda row: (row['target_period'], row['method']))
    methods = (*METHODS, 'ridge')
    results = summarize(predictions, protocol['subperiods'], methods)
    manifest = {'protocol_id': protocol['protocol_id'],
                'protocol_sha256': hashlib.sha256(raw).hexdigest(),
                'source_csv_sha256': source['cpi_sha256'],
                'code_sha256': {name: hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
                                for name in ['evaluate_ridge.py', 'evaluate_baselines.py', 'prepare_cpi.py']},
                'python_version': platform.python_version(), 'sklearn_version': sklearn.__version__,
                'numpy_version': np.__version__, 'created_at': datetime.now(timezone.utc).isoformat(),
                'evaluation_mode': protocol['evaluation_mode'], 'holdout_scored': False,
                'fit_count': len(ridge)*16, 'workers': 1,
                'elapsed_compute_seconds': time.perf_counter()-started}
    output.mkdir(parents=True, exist_ok=False)
    write_csv(output/'predictions.csv', predictions)
    write_csv(output/'metrics.csv', results)
    write_csv(output/'tuning.csv', tuning)
    (output/'protocol.json').write_bytes(raw)
    (output/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n', encoding='utf-8')
    return results


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--snapshot', type=Path, required=True)
    parser.add_argument('--contract', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    try:
        print(json.dumps(run(args.snapshot, args.contract, args.output), indent=2))
    except (ValueError, OSError, KeyError, TypeError) as exc:
        parser.exit(1, 'Ridge run failed: '+str(exc)+'\n')
