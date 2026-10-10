"""Frozen 8-class holdout blending; load only trusted bundles created by this project."""
from pathlib import Path
import hashlib
import importlib.metadata
import json
import platform
import joblib
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.utils.validation import check_is_fitted

BASE_ORDER = ('DT', 'RF', 'XGBoost')


def _sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


class BlendingClassifier(ClassifierMixin, BaseEstimator):
    def __init__(self, base_pipelines=None, meta_estimator=None, features=None, class_names=None):
        self.base_pipelines = base_pipelines
        self.meta_estimator = meta_estimator
        self.features = features
        self.class_names = class_names

    def initialize_pretrained(self):
        if self.base_pipelines is None or self.meta_estimator is None:
            raise ValueError('Require fitted base pipelines and meta estimator.')
        if list(self.base_pipelines) != list(BASE_ORDER):
            raise ValueError('Base order must be DT, RF, XGBoost.')
        for model in list(self.base_pipelines.values()) + [self.meta_estimator]:
            check_is_fitted(model)
            if not np.array_equal(model.classes_, np.arange(8)):
                raise ValueError('Class order must be IDs 0..7.')
        if len(self.features) != 44 or len(self.class_names) != 8:
            raise ValueError('Require 44 raw features and 8 classes.')
        self.classes_ = np.arange(8)
        self.n_features_in_ = len(self.features)
        self.feature_names_in_ = np.asarray(self.features, dtype=object)
        self.is_fitted_ = True
        return self

    def fit(self, X, y=None, **kwargs):
        raise RuntimeError('This wrapper is inference-only. Fit bases on train and meta on val in the Kaggle notebook.')

    def __sklearn_is_fitted__(self):
        return bool(getattr(self, 'is_fitted_', False))

    def _frame(self, frame):
        check_is_fitted(self)
        if isinstance(frame, pd.DataFrame):
            if frame.columns.duplicated().any():
                raise ValueError('Duplicate column names.')
            missing = [name for name in self.features if name not in frame.columns]
            if missing:
                raise ValueError(f'Missing features: {missing}')
            selected = frame.loc[:, self.features].apply(pd.to_numeric, errors='raise')
        else:
            array = np.asarray(frame)
            if array.ndim != 2 or array.shape[1] != len(self.features):
                raise ValueError('Array must have shape (n,44) in recorded feature order.')
            selected = pd.DataFrame(array, columns=self.features).apply(pd.to_numeric, errors='raise')
        # Reuse per-base fixed train-median preprocessors; no fit on query.
        selected = selected.astype(np.float64).replace([np.inf, -np.inf], np.nan)
        return selected

    def build_meta_features(self, frame):
        selected = self._frame(frame)
        if len(selected) == 0:
            return np.empty((0, 24), dtype=np.float32)
        blocks = []
        for name in BASE_ORDER:
            p = np.asarray(self.base_pipelines[name].predict_proba(selected), dtype=np.float32)
            if p.shape != (len(selected), 8) or not np.isfinite(p).all():
                raise ValueError(f'Invalid probabilities from {name}.')
            if not np.allclose(p.sum(axis=1), 1.0, rtol=1e-5, atol=1e-5):
                raise ValueError(f'Invalid probability sums from {name}.')
            blocks.append(p)
        return np.ascontiguousarray(np.concatenate(blocks, axis=1), dtype=np.float32)

    def predict_proba(self, X):
        z = self.build_meta_features(X)
        if len(z) == 0:
            return np.empty((0, 8), dtype=np.float32)
        p = np.asarray(self.meta_estimator.predict_proba(z), dtype=np.float32)
        if p.shape != (len(z), 8) or not np.isfinite(p).all():
            raise ValueError('Invalid meta probabilities.')
        return p

    def predict(self, X):
        return self.classes_[self.predict_proba(X).argmax(axis=1)]

    def predict_proba_raw(self, frame):
        return self.predict_proba(frame)

    def predict_raw(self, frame):
        return self.predict(frame)


def load_bundle(bundle_dir):
    root = Path(bundle_dir)
    manifest = json.loads((root / 'bundle_checksums.json').read_text(encoding='utf-8'))
    for relative, expected in manifest['files'].items():
        if _sha(root / relative) != expected:
            raise ValueError(f'Bundle checksum mismatch: {relative}')
    metadata = json.loads((root / 'bundle_metadata.json').read_text(encoding='utf-8'))
    for name in ['numpy', 'pandas', 'scipy', 'scikit-learn', 'xgboost', 'joblib']:
        if importlib.metadata.version(name) != metadata['versions'][name]:
            raise RuntimeError(f'Runtime version mismatch: {name}. Use requirements_runtime.txt.')
    if platform.python_version().split('.')[:2] != metadata['versions']['python'].split('.')[:2]:
        raise RuntimeError('Python major/minor mismatch.')
    model = joblib.load(root / 'pipeline.joblib')
    check_is_fitted(model)
    if list(model.features) != metadata['raw_features'] or list(model.class_names) != metadata['class_names']:
        raise ValueError('Serialized schema differs from bundle metadata.')
    return model


def predict_csv(bundle_dir, csv_path, output_path, chunksize=1024):
    model = load_bundle(bundle_dir)
    output = Path(output_path)
    first = True
    for frame in pd.read_csv(csv_path, chunksize=chunksize):
        probabilities = model.predict_proba_raw(frame)
        prediction = probabilities.argmax(axis=1)
        result = pd.DataFrame({'predicted_id': prediction,
                               'predicted_label': [model.class_names[i] for i in prediction]})
        for i, label in enumerate(model.class_names):
            result[f'p_{label}'] = probabilities[:, i]
        result.to_csv(output, mode='w' if first else 'a', header=first, index=False)
        first = False
    return output
