"""8-class recall pipeline. Import this module before joblib.load."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import joblib
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.utils.validation import check_is_fitted
from sklearn.exceptions import NotFittedError

class DecisionRuleClassifier(ClassifierMixin, BaseEstimator):
    def __init__(self, base_estimator, multipliers=(1.,1.)):
        self.base_estimator=base_estimator
        self.multipliers=multipliers
    @property
    def classes_(self): return self.base_estimator.classes_
    @property
    def n_features_in_(self): return self.base_estimator.n_features_in_
    def fit(self, X=None, y=None):
        # This wrapper accepts an already fitted estimator; never refit the frozen model.
        check_is_fitted(self.base_estimator)
        return self
    def __sklearn_is_fitted__(self):
        try:
            check_is_fitted(self.base_estimator)
        except NotFittedError:
            return False
        return True
    def predict_proba(self,X): return self.base_estimator.predict_proba(X)
    def decision_function(self,X):
        p=np.asarray(self.predict_proba(X),dtype=np.float32);w=np.ones(8,dtype=np.float32);w[1],w[7]=self.multipliers
        return p*w
    def predict(self,X): return self.classes_[self.decision_function(X).argmax(axis=1)]

def load_bundle(path):
    root=Path(path)
    return joblib.load(root/'pipeline.joblib'),json.loads((root/'config.json').read_text())
def predict_frame(pipeline,config,frame):
    required=config['feature_names']
    if frame.columns.duplicated().any():raise ValueError('Duplicate columns')
    missing=sorted(set(required)-set(frame.columns))
    if missing:raise ValueError(f'Missing features: {missing}')
    X=frame.loc[:,required].apply(pd.to_numeric,errors='raise').astype(np.float64)
    X=X.replace([np.inf,-np.inf],np.nan)
    p=pipeline.predict_proba(X);pred=pipeline.predict(X)
    if not np.isfinite(p).all():raise ValueError('Nonfinite probabilities')
    result=pd.DataFrame({'input_row':np.arange(len(frame)),'predicted_class_id':pred,
        'predicted_class_name':[config['class_names'][int(i)] for i in pred]})
    for i,c in enumerate(config['class_names']): result['probability_'+c]=p[:,i]
    return result

def predict_csv(bundle,csv_path,output,chunksize=25000):
    pipeline,config=load_bundle(bundle);offset=0
    for i,frame in enumerate(pd.read_csv(csv_path,chunksize=chunksize)):
        result=predict_frame(pipeline,config,frame);result['input_row']+=offset;offset+=len(frame)
        result.to_csv(output,mode='w' if i==0 else 'a',header=i==0,index=False)
    return offset
