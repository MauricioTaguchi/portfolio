"""Offline regression checks for the CSV tutorial. Run: python -m unittest -v."""
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from validate_sales import validate

ROOT = Path(__file__).resolve().parent
HEADER = 'sale_id,date,amount_brl\n'

class ValidationTests(unittest.TestCase):
    def report(self, row, **kwargs):
        return validate(io.StringIO(HEADER + row), **kwargs)

    def codes(self, report):
        return {issue['code'] for issue in report['issues']}

    def test_valid_record(self):
        self.assertTrue(self.report('0001,2026-10-01,150.00\n')['valid'])

    def test_leading_zero_ids_stay_distinct(self):
        self.assertTrue(self.report('0001,2026-10-01,1.00\n1,2026-10-01,1.00\n')['valid'])

    def test_duplicate_flags_all_occurrences(self):
        r = self.report('A,2026-10-01,1\nA,2026-10-01,2\n')
        self.assertEqual([x['record'] for x in r['issues']], [1, 2])
        self.assertEqual(self.codes(r), {'duplicate_id'})

    def test_missing_id(self):
        self.assertIn('required', self.codes(self.report(',2026-10-01,1\n')))

    def test_whitespace_only_id(self):
        self.assertFalse(self.report('  ,2026-10-01,1\n')['valid'])

    def test_blank_date(self):
        self.assertIn('required', self.codes(self.report('1,,1\n')))

    def test_impossible_date(self):
        self.assertIn('invalid_date', self.codes(self.report('1,2026-02-30,1\n')))

    def test_ambiguous_date(self):
        self.assertIn('invalid_date', self.codes(self.report('1,01/10/2026,1\n')))

    def test_non_padded_date(self):
        self.assertFalse(self.report('1,2026-1-1,1\n')['valid'])

    def test_leap_day(self):
        self.assertTrue(self.report('1,2024-02-29,1\n')['valid'])

    def test_blank_amount(self):
        self.assertFalse(self.report('1,2026-10-01,\n')['valid'])

    def test_zero_negative_nonfinite_scientific_and_precision(self):
        for amount in ['0', '-1.00', 'NaN', 'Infinity', '1e3', '1.234', 'R$ 10.00', '+1.00']:
            with self.subTest(amount=amount):
                self.assertFalse(self.report(f'1,2026-10-01,{amount}\n')['valid'])

    def test_brazilian_format_is_explicit(self):
        stream = io.StringIO('sale_id;date;amount_brl\n1;2026-10-01;12,90\n')
        self.assertTrue(validate(stream, delimiter=';', decimal_separator=',')['valid'])

    def test_decimal_comma_not_guessed(self):
        self.assertFalse(self.report('1,2026-10-01,"12,90"\n')['valid'])

    def test_quoted_delimiter_in_id(self):
        self.assertTrue(self.report('"A,B",2026-10-01,1\n')['valid'])

    def test_multiline_id_line_numbers(self):
        r = self.report('"A\nB",2026-10-01,0\n')
        self.assertEqual(r['issues'][0]['record'], 1)
        self.assertEqual(r['issues'][0]['line_end'], 3)

    def test_extra_or_missing_column(self):
        for row in ['1,2026-10-01,1,EXTRA\n', '1,2026-10-01\n', '\n']:
            with self.subTest(row=row):
                self.assertIn('column_count', self.codes(self.report(row)))

    def test_empty_file(self):
        r = validate(io.StringIO(''))
        self.assertFalse(r['complete'])
        self.assertIn('schema', self.codes(r))

    def test_header_only(self):
        self.assertIn('empty_dataset', self.codes(self.report('')))

    def test_duplicate_reordered_unknown_headers(self):
        for header in ['sale_id,date,date', 'date,sale_id,amount_brl', 'id,date,amount_brl']:
            with self.subTest(header=header):
                self.assertFalse(validate(io.StringIO(header+'\n'))['complete'])

    def test_unclosed_quote(self):
        r = self.report('"1,2026-10-01,1\n')
        self.assertFalse(r['complete'])
        self.assertIn('malformed_csv', self.codes(r))

    def test_record_limit_marks_incomplete(self):
        with patch('validate_sales.MAX_RECORDS', 1):
            r = self.report('1,2026-10-01,1\n2,2026-10-01,1\n')
        self.assertFalse(r['complete'])
        self.assertEqual(r['records_checked'], 1)

    def test_invalid_configuration(self):
        with self.assertRaises(ValueError):
            validate(io.StringIO(''), delimiter='|')
        with self.assertRaises(ValueError):
            validate(io.StringIO(''), decimal_separator=':')

    def test_fixture_exact_diagnostics(self):
        with (ROOT/'sales_invalid.csv').open(newline='', encoding='utf-8') as stream:
            r = validate(stream)
        self.assertEqual(r['records_checked'], 6)
        self.assertEqual(r['issue_count'], 5)
        self.assertEqual([x['record'] for x in r['issues']], [2, 3, 4, 5, 6])

    def run_cli(self, *args):
        return subprocess.run([sys.executable, str(ROOT/'validate_sales.py'), *map(str,args)], capture_output=True, text=True)

    def test_cli_clean_exit_zero(self):
        p = self.run_cli(ROOT/'sales_valid.csv')
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertTrue(json.loads(p.stdout)['valid'])

    def test_cli_invalid_exit_one_and_preserves_source(self):
        source = ROOT/'sales_invalid.csv'
        before = hashlib.sha256(source.read_bytes()).digest()
        p = self.run_cli(source)
        self.assertEqual(p.returncode, 1, p.stderr)
        self.assertEqual(before, hashlib.sha256(source.read_bytes()).digest())

    def test_cli_missing_file_exit_two(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(self.run_cli(Path(d)/'missing.csv').returncode, 2)

    def test_cli_bom_and_report_output(self):
        with tempfile.TemporaryDirectory() as d:
            source, out = Path(d)/'input.csv', Path(d)/'report.json'
            source.write_text(HEADER+'1,2026-10-01,1\n', encoding='utf-8-sig')
            p = self.run_cli(source, '--output', out)
            self.assertEqual(p.returncode, 0, p.stderr)
            self.assertEqual(json.loads(out.read_text()), json.loads(p.stdout))

    def test_cli_refuses_input_overwrite(self):
        with tempfile.TemporaryDirectory() as d:
            source = Path(d)/'input.csv'
            content = HEADER+'1,2026-10-01,1\n'
            source.write_text(content)
            self.assertEqual(self.run_cli(source, '--output', source).returncode, 2)
            self.assertEqual(source.read_text(), content)

    def test_cli_invalid_encoding(self):
        with tempfile.TemporaryDirectory() as d:
            source = Path(d)/'input.csv'
            source.write_bytes(b'\xff\xfe\xfa')
            self.assertEqual(self.run_cli(source).returncode, 2)

if __name__ == '__main__':
    unittest.main()
