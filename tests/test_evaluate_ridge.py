import copy
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np
from threadpoolctl import threadpool_limits

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
from evaluate_ridge import estimator, forecast, ridge_walk_forward, supervised, validate_model

MODEL = {'lags':12, 'alphas':[0.1,1.0,10.0,100.0,1000.0], 'inner_splits':3,
         'validation_months':12, 'tie_break':'larger_alpha', 'solver':'svd',
         'scaling':'train_fold_only', 'gap':0}


class RidgeTests(unittest.TestCase):
    def test_lags_and_targets_align(self):
        x,y,next_x = supervised(list(range(60)))
        np.testing.assert_array_equal(x[0], list(range(11,-1,-1)))
        self.assertEqual(y[0],12)
        np.testing.assert_array_equal(next_x[0], list(range(59,47,-1)))

    def test_scaler_fits_only_supplied_training_rows(self):
        x = np.array([[0.,0.],[2.,4.],[1000.,1000.]])
        fitted = estimator(1).fit(x[:2], np.array([1.,2.]))
        np.testing.assert_array_equal(fitted[0].mean_, [1.,2.])
        fitted.predict(x[2:])
        np.testing.assert_array_equal(fitted[0].mean_, [1.,2.])

    def test_inner_fits_exclude_validation_and_outer_target(self):
        seen=[]
        original=estimator
        class Spy:
            def __init__(self, alpha): self.inner=original(alpha)
            def fit(self,x,y):
                seen.append((len(y),float(y.max())))
                self.inner.fit(x,y)
                return self
            def predict(self,x): return self.inner.predict(x)
        with patch('evaluate_ridge.estimator', side_effect=Spy), threadpool_limits(limits=1):
            value,best,trials=forecast(list(range(120)),MODEL)
        self.assertEqual(seen[:3],[(72,83.),(84,95.),(96,107.)])
        self.assertEqual(seen[-1],(108,119.))
        self.assertEqual(len(seen),16)
        self.assertEqual(len(trials),5)
        self.assertTrue(np.isfinite(value))

    def test_current_future_and_holdout_do_not_change_earlier_forecast(self):
        rows=[{'period':f'{2005+i//12:04d}-{i%12+1:02d}',
               'monthly_pct':float(np.sin(i)+i/20)} for i in range(126)]
        p={'development_start':'2015-01','development_end':'2015-02','model':MODEL}
        changed=copy.deepcopy(rows)
        for row in changed[120:]: row['monthly_pct']=9999.
        with threadpool_limits(limits=1):
            before,_=ridge_walk_forward(rows,p)
            after,_=ridge_walk_forward(changed,p)
        self.assertEqual(before[0]['prediction'],after[0]['prediction'])
        holdout=copy.deepcopy(rows)
        for row in holdout[122:]: row['monthly_pct']=-999.
        with threadpool_limits(limits=1):
            self.assertEqual(ridge_walk_forward(rows,p),ridge_walk_forward(holdout,p))

    def test_invalid_inputs_and_changed_search_rejected(self):
        for history in ([1.]*30,[float('nan')]*120):
            with self.assertRaises(ValueError): supervised(history)
        changed=copy.deepcopy(MODEL)
        changed['alphas']=[1,2]
        with self.assertRaises(ValueError): validate_model(changed)


if __name__=='__main__': unittest.main()
