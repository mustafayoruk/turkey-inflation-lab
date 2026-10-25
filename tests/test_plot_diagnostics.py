import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from plot_diagnostics import describe


class DiagnosticTests(unittest.TestCase):
    def fixture(self):
        rows=[]
        for i in range(108):
            period=f'{2015+i//12:04d}-{i%12+1:02d}'
            for method,error in [('ridge',3. if i==0 else 4. if i==1 else 0.),('naive',5.)]:
                rows.append({'target_period':period,'method':method,'error':error,
                             'actual':0.,'prediction':error})
        return rows

    def test_independent_error_concentration_arithmetic(self):
        result=describe(self.fixture())
        self.assertEqual(result['top3_squared_error_share'],(16+9)/25)
        self.assertEqual(result['ridge_lower_absolute_error_months'],108)
        self.assertEqual(result['largest_errors'][0]['target_period'],'2015-02')
        self.assertFalse(result['holdout_scored'])

    def test_unpaired_or_duplicate_origins_rejected(self):
        rows=self.fixture()
        with self.assertRaises(ValueError): describe(rows[:-1])
        rows=copy.deepcopy(rows)
        rows[0]['target_period']=rows[2]['target_period']
        with self.assertRaises(ValueError): describe(rows)
