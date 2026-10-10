"""Inference helper: load only your own trusted bundle. Match requirements_runtime.txt."""
from pathlib import Path
import json
import joblib
import numpy as np
import pandas as pd

def load_bundle(bundle_dir):
    root=Path(bundle_dir)
    metadata=json.loads((root/'bundle_metadata.json').read_text())
    return joblib.load(root/'pipeline.joblib'),metadata

def predict_frame(pipeline,metadata,frame):
    required=metadata['input_features_required']
    if frame.columns.duplicated().any(): raise ValueError('Duplicate column names')
    missing=sorted(set(required)-set(frame.columns))
    if missing: raise ValueError(f'Missing columns: {missing}')
    numeric=frame.loc[:,required].apply(pd.to_numeric,errors='raise').astype(np.float64)
    numeric=numeric.replace([np.inf,-np.inf],np.nan)
    probability=pipeline.predict_proba(numeric)
    if not np.isfinite(probability).all(): raise ValueError('Invalid probabilities')
    labels=probability.argmax(axis=1)
    out=pd.DataFrame({'input_row_index':np.arange(len(frame)),
                      'predicted_class_id':labels,
                      'predicted_class_name':[metadata['class_order'][int(i)] for i in labels]})
    for i,c in enumerate(metadata['class_order']): out['probability_'+c]=probability[:,i]
    return out

def predict_csv(bundle_dir,csv_path,output_path,chunksize=25000):
    pipeline,metadata=load_bundle(bundle_dir)
    offset=0
    for i,chunk in enumerate(pd.read_csv(csv_path,chunksize=chunksize)):
        result=predict_frame(pipeline,metadata,chunk)
        result['input_row_index']+=offset;offset+=len(chunk)
        result.to_csv(output_path,index=False,mode='w' if i==0 else 'a',header=i==0)
    return offset
