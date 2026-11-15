import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import numpy as np
import pandas as pd

spec = importlib.util.spec_from_file_location('audit', Path(__file__).resolve().parents[1] / 'model/science_audit.py')
a = importlib.util.module_from_spec(spec)
spec.loader.exec_module(a)

class AuditTests(unittest.TestCase):
    def fixture(self):
        rng = np.random.default_rng(42)
        n = 80
        return pd.DataFrame(dict(fuel=np.tile(['heptane', 'methanol'], n//2),
            test_end=np.tile(['completion', 'completion', 'extinction', 'extinction'], n//4),
            o2_pct=rng.uniform(15, 30, n), pressure_atm=np.tile([.704, .996], n//2),
            co2_pct=np.zeros(n), he_pct=np.zeros(n), d0_mm=rng.uniform(1, 4, n),
            burn_rate_mm2_s=rng.uniform(.1, .3, n), run_id=np.repeat(np.arange(n//4), 4)))

    def test_known_confusion(self):
        y = np.array([0]*27 + [1]*172)
        p = np.array([.1]*8 + [.9]*19 + [.1]*2 + [.9]*170)
        m = a.class_metrics(y, p)
        self.assertEqual(m['confusion_matrix_rows_actual_completion_extinction'], [[8,19],[2,170]])
        self.assertAlmostEqual(m['balanced_accuracy_at_0_5'], (8/27+170/172)/2, places=5)

    def test_raw_pressure_boundaries(self):
        f = self.fixture().iloc[:2].copy()
        f['fuel'] = 'heptane'
        r = a.pressure_coverage(f, .1, [.702, .704, .85])['heptane']
        self.assertEqual([x['pressure_evidence_level'] for x in r['example_pressure_checks']],
                         ['Unsupported', 'Not assessed', 'Limited Evidence'])

    def test_group_isolation(self):
        f = self.fixture()
        y = f.test_end.eq('extinction').to_numpy(int)
        groups = f.run_id.to_numpy()
        for train, test in a.make_cv(y, groups, 5, 7)[0]:
            self.assertFalse(set(groups[train]) & set(groups[test]))

    def test_missing_class(self):
        self.assertIsNone(a.class_metrics(np.ones(5, dtype=int), np.full(5,.9))['per_class_at_0_5']['completion']['recall'])

    def test_end_to_end(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            data = root/'fixture.csv'
            self.fixture().to_csv(data,index=False)
            for group in [None, 'run_id']:
                out = root/('group' if group else 'row')
                paths = a.run_audit(data,out,7,2,5,group,.1,[.85])
                self.assertTrue(all(p.exists() for p in paths))
                r = json.loads(paths[0].read_text())
                self.assertEqual(r['counts']['classification_rows'],80)
                self.assertEqual(len(r['fold_training_prevalence_baselines']),6)
                self.assertEqual(len(r['provenance']['dataset_sha256']),64)
                self.assertEqual(len(pd.read_csv(paths[2])),6)
            with self.assertRaises(ValueError):
                a.run_audit(data,root/'invalid',7,2,5,None,float('nan'),[])

if __name__ == '__main__':
    unittest.main()
