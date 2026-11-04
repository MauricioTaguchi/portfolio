"""Regression tests for report destinations; all fixtures are synthetic."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).with_name('validate_sales.py')
CONTENT = b'sale_id,date,amount_brl\n0001,2026-11-03,12.90\n'

class OutputSafetyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.source = self.directory / 'sales.csv'
        self.output = self.directory / 'report.json'
        self.source.write_bytes(CONTENT)

    def run_cli(self):
        return subprocess.run(
            [sys.executable, '-B', str(SCRIPT), str(self.source), '--output', str(self.output)],
            capture_output=True, text=True, timeout=15)

    def assert_refused(self):
        result = self.run_cli()
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertEqual(result.stdout, '')
        self.assertEqual(self.source.read_bytes(), CONTENT)

    def test_existing_report_is_preserved(self):
        self.output.write_bytes(b'previous report')
        self.assert_refused()
        self.assertEqual(self.output.read_bytes(), b'previous report')

    def test_hard_link_cannot_overwrite_input(self):
        try:
            os.link(self.source, self.output)
        except OSError as error:
            self.skipTest(f'Hard links unavailable: {error}')
        self.assert_refused()
        self.assertEqual(self.output.read_bytes(), CONTENT)

    def test_symlink_cannot_overwrite_input(self):
        try:
            self.output.symlink_to(self.source)
        except OSError as error:
            self.skipTest(f'Symlinks unavailable: {error}')
        self.assert_refused()
        self.assertTrue(self.output.is_symlink())

    def test_dangling_symlink_does_not_create_target(self):
        target = self.directory / 'unrelated.json'
        try:
            self.output.symlink_to(target)
        except OSError as error:
            self.skipTest(f'Symlinks unavailable: {error}')
        self.assert_refused()
        self.assertFalse(target.exists())
        self.assertTrue(self.output.is_symlink())

    def test_directory_is_not_replaced(self):
        self.output.mkdir()
        self.assert_refused()
        self.assertTrue(self.output.is_dir())

    def test_missing_parent_is_operational_error(self):
        self.output = self.directory / 'absent' / 'report.json'
        self.assert_refused()
        self.assertFalse(self.output.parent.exists())

    def test_new_report_matches_stdout(self):
        result = self.run_cli()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(self.output.read_text()), json.loads(result.stdout))
        self.assertEqual(self.source.read_bytes(), CONTENT)

    def test_second_run_preserves_first_report(self):
        self.assertEqual(self.run_cli().returncode, 0)
        first = self.output.read_bytes()
        self.assert_refused()
        self.assertEqual(self.output.read_bytes(), first)

if __name__ == '__main__':
    unittest.main()
