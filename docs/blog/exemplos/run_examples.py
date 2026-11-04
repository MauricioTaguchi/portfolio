"""Run both offline tutorials and check their results. Requires Python 3.11+."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent


def run(arguments: list[str], *, cwd: Path, expected: int = 0) -> str:
    result = subprocess.run([sys.executable, '-B', *arguments], cwd=cwd,
                            env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'},
                            capture_output=True, text=True, timeout=120)
    if result.returncode != expected:
        raise RuntimeError(f'Unexpected exit code {result.returncode} (expected {expected}).\n'
                           f'{result.stdout}\n{result.stderr}')
    if arguments[:2] == ['-m', 'unittest']:
        print(result.stderr.strip())
    return result.stdout


def execute(output: Path) -> dict:
    csv_dir, revisions = ROOT / 'validacao-csv', ROOT / 'revisoes'
    if not csv_dir.is_dir() or not revisions.is_dir():
        raise ValueError('Keep this script next to both complete example directories.')
    before = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in csv_dir.glob('*.csv')}
    for folder in (csv_dir, revisions):
        run(['-m', 'unittest', 'discover', '-v'], cwd=folder)
    print(run(['revision_demo.py'], cwd=revisions).strip())
    valid = json.loads(run(['validate_sales.py', 'sales_valid.csv'], cwd=csv_dir))
    invalid = json.loads(run(['validate_sales.py', 'sales_invalid.csv', '--output', str(output)],
                             cwd=csv_dir, expected=1))
    if not valid['valid'] or not valid['complete']:
        raise RuntimeError('The valid fixture was not accepted.')
    if invalid['valid'] or not invalid['complete'] or invalid['records_checked'] != 6 or invalid['issue_count'] != 5:
        raise RuntimeError('The invalid fixture did not produce the documented diagnostics.')
    if json.loads(output.read_text(encoding='utf-8')) != invalid:
        raise RuntimeError('The saved report differs from standard output.')
    after = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in csv_dir.glob('*.csv')}
    if before != after:
        raise RuntimeError('An input fixture changed.')
    return {'status': 'passed', 'valid_fixture_exit': 0, 'invalid_fixture_exit': 1,
            'invalid_records': 6, 'diagnostics': 5, 'source_files_unchanged': True}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, help='Existing directory for a NEW invalid-report.json.')
    args = parser.parse_args(argv)
    if sys.version_info < (3, 11):
        print('Python 3.11 or later is required.', file=sys.stderr)
        return 2
    try:
        if args.output_dir:
            directory = args.output_dir.resolve()
            if not directory.is_dir():
                raise ValueError('The output directory must already exist.')
            output = directory / 'invalid-report.json'
            if os.path.lexists(output):
                raise ValueError('invalid-report.json already exists; choose another directory.')
            summary = execute(output)
            print(f'Report saved: {output}')
        else:
            with tempfile.TemporaryDirectory(prefix='tutorial-') as directory:
                summary = execute(Path(directory) / 'invalid-report.json')
            print('Temporary report checked and removed; no report left in the source directory.')
        print(json.dumps(summary, indent=2))
        return 0
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as error:
        print(f'Verification failed: {error}', file=sys.stderr)
        return 2

if __name__ == '__main__':
    raise SystemExit(main())
