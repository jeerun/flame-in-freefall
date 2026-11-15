"""Verify exported coefficients and actual Console inference against a Python refit.
Run: py model/check_parity.py (requires Node.js, numpy, pandas, scikit-learn).
Does not overwrite training/model artifacts. Not a predictive-performance audit.

Since Nov 15, 2026 the console uses the per-fuel model, so the refit here is the recipe of
model/train_per_fuel.py (imported, not copied) and the hand calculation adds each fuel's own slopes.
"""
import argparse
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
import platform
import subprocess
import sys
import numpy as np
import pandas as pd
import sklearn
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression, LinearRegression

ROOT = Path(__file__).resolve().parents[1]


def check(root=ROOT):
    spec = importlib.util.spec_from_file_location('training_per_fuel', root/'model/train_per_fuel.py')
    per_fuel = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(per_fuel)
    train = per_fuel.train                      # model/train.py next to it: the scope, the inputs and the base columns
    df = pd.read_csv(root/'data/clean/flex_clean.csv')
    # The training script's own scope, design and estimators, so this cannot drift from what was exported.
    scope = per_fuel.scope_of(df)
    ext = scope[scope.test_end.isin(['Extinction', 'Completion'])]
    rate = scope[scope.burn_rate_mm2_s.notna()]
    clf = per_fuel.classifier()
    reg = per_fuel.regressor()
    clf.fit(per_fuel.design(ext), ext.test_end.eq('Extinction').astype(int))
    reg.fit(per_fuel.design(rate), rate.burn_rate_mm2_s)
    # Read artifact through JS, never parse/eval JavaScript with Python.
    runner = root/'tests/console_prediction_runner.cjs'
    def js(cases):
        proc = subprocess.run(['node', str(runner)], input=json.dumps(cases), text=True,
                              capture_output=True, check=True, timeout=30)
        return json.loads(proc.stdout)
    model = js([])['model']
    if model['meta'].get('mock') is not False:
        raise ValueError('Expected a real, non-mock export.')
    if [f['key'] for f in model['features']] != [train.KEYS[c] for c in train.NUM]:
        raise ValueError('Feature ordering differs from training.')
    if {f['key'] for f in model['fuels']} != {'heptane','methanol'}:
        raise ValueError('Fuel encoding changed; review checker.')
    cases = []
    for i, row in scope.iterrows():
        cases.append({'id': f'data_row_{i}', 'fuel': row.fuel,
                      'values': {train.KEYS[k]: float(row[k]) for k in train.NUM}})
    for fuel in ['heptane','methanol']:
        defaults = {f['key']:f['default'] for f in model['features']}
        cases.append({'id':fuel+'_default','fuel':fuel,'values': defaults})
        cases.append({'id':fuel+'_pressure_gap','fuel':fuel,'values':{**defaults,'p':.85}})
        for i, vals in enumerate(itertools.product(*[(f['min'],f['max']) for f in model['features']])):
            cases.append({'id':fuel+f'_corner_{i}','fuel':fuel,
                          'values':dict(zip(defaults, vals))})
        rng = np.random.default_rng(7)
        for i in range(250):
            cases.append({'id':fuel+f'_random_{i}','fuel':fuel,
                          'values':{f['key']:float(rng.uniform(f['min'],f['max'])) for f in model['features']}})
    # Deliberately invalid physical combinations above are numerical stress probes only.
    frame = pd.DataFrame([{'fuel': c['fuel'], **{k: c['values'][train.KEYS[k]] for k in train.NUM}} for c in cases])
    x = per_fuel.design(frame)
    py_p = clf.predict_proba(x)[:,1]
    py_k = reg.predict(x)
    actual = js(cases)['predictions']
    got = {key:np.array([v[key] for v in actual],float) for key in ['pOut','pKeep','K','rawK']}
    def linear(part):
        own = part.get('fuel_coef', {})     # each fuel's own slopes, added to the shared ones
        return np.array([part['intercept']+part['fuel'][c['fuel']]+
                         sum((part['coef'][key]+own.get(c['fuel'], {}).get(key, 0))*val for key,val in c['values'].items()) for c in cases])
    z = linear(model['extinction'])
    artifact_p = 1/(1+np.exp(-z))
    artifact_k = linear(model['burn_rate'])
    errors = {
        'artifact_vs_js_pOut':float(np.max(abs(artifact_p-got['pOut']))),
        'artifact_vs_js_rawK':float(np.max(abs(artifact_k-got['rawK']))),
        'completion_complement':float(np.max(abs(1-got['pOut']-got['pKeep']))),
        'zero_clamp':float(np.max(abs(np.maximum(0,got['rawK'])-got['K']))),
        'refit_vs_js_pOut':float(np.max(abs(py_p-got['pOut']))),
        'refit_vs_js_rawK':float(np.max(abs(py_k-got['rawK']))),
        'refit_vs_js_clampedK':float(np.max(abs(np.maximum(0,py_k)-got['K']))),
    }
    tolerances = {k:(1e-4 if k.startswith('refit') else 1e-12) for k in errors}
    passed = all(np.isfinite(v) and v<=tolerances[k] for k,v in errors.items())
    hashes = {p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in
              ['model/train.py','model/train_per_fuel.py','console/model.js','console/index.html','data/clean/flex_clean.csv']}
    return {'passed':bool(passed), 'case_count':len(cases), 'source_rows':len(scope),
            'classification_rows':len(ext),'regression_rows':len(rate),
            'negative_raw_K_cases':int(np.sum(got['rawK']<0)),
            'max_absolute_errors':errors,'absolute_tolerances':tolerances,
            'export_matches_refit_rounded_coefficients':{
                'extinction':per_fuel.as_parts(*train.raw_coefficients(clf))==model['extinction'],
                'burn_rate':per_fuel.as_parts(*train.raw_coefficients(reg))==model['burn_rate']},
            'sha256':hashes,'versions':{'python':platform.python_version(),'sklearn':sklearn.__version__,
                'numpy':np.__version__,'pandas':pd.__version__,
                'node':subprocess.check_output(['node','--version'],text=True).strip()},
            'limitations':['Numerical inference parity only; not out-of-sample performance or safety validation.',
                'Executes actual pure Console functions in Node VM; does not test browser DOM, sliders, formatting, or live hosted deployment.',
                'Refits the current training configuration (model/train_per_fuel.py), not a serialized historical Python estimator.',
                'Random/corner cases include physically invalid and OOD combinations; used only as arithmetic stress probes.',
                'Training pipeline changes require review of the explicit fit/scope setup in this checker.']}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'model/parity_report.json')
    args=parser.parse_args()
    result=check()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps(result,indent=2))
    return 0 if result['passed'] else 1

if __name__=='__main__':
    sys.exit(main())
