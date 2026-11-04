import unittest
from analyze import analyze, load, ROOT
class AnalysisTests(unittest.TestCase):
    def test_snapshot_grain(self):self.assertEqual(analyze()['snapshot']['rows'],540)
    def test_coverage(self):self.assertTrue(all(r['states']==27 and r['observations']==27 for r in analyze()['coverage']))
    def test_quarters(self):self.assertEqual(len(analyze()['coverage']),20)
    def test_latest(self):self.assertEqual(analyze()['snapshot']['latest_quarter'],'202601')
    def test_highest(self):self.assertEqual(analyze()['latest_ranking'][0]['state'],'Distrito Federal')
    def test_lowest(self):self.assertEqual(analyze()['latest_ranking'][-1]['state'],'Maranhão')
    def test_regional_coverage(self):self.assertEqual(sum(r['states'] for r in analyze()['regional_means']),27)
    def test_yoy_matching(self):self.assertTrue(all(r['prior_year_income_brl'] is not None for r in analyze()['exact_yoy']))
    def test_mean_is_not_sum(self):
        with load(ROOT/'income.csv') as db:self.assertAlmostEqual(db.execute('SELECT AVG(income_real_brl) FROM income WHERE quarter_code="202601"').fetchone()[0],3437.4074074074074)
    def test_join_does_not_multiply(self):self.assertEqual(len(analyze()['exact_yoy']),27)
    def test_unknown_prior_remains_null(self):
        with load(ROOT/'income.csv') as db:
            row=db.execute('SELECT p.income_real_brl FROM income c LEFT JOIN income p ON p.state_code=c.state_code AND p.year=c.year-1 AND p.quarter_number=c.quarter_number WHERE c.quarter_code="202102" LIMIT 1').fetchone();self.assertIsNone(row[0])
    def test_duplicate_key_rejected(self):
        import sqlite3
        with load(ROOT/'income.csv') as db:
            with self.assertRaises(sqlite3.IntegrityError):db.execute('INSERT INTO income SELECT * FROM income LIMIT 1')
if __name__=='__main__':unittest.main()
