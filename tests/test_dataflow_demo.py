"""Keep the public sample isolated while retaining the upstream chart behavior."""
import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import zipfile
import io
import ast
import json

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('dataflow_demo', ROOT/'scripts/build_dataflow_demo.py')
demo = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(demo)

APP = '''onConnect={() => setConnectionOpen(true)}
disabled={combinedBusy} onChange={(event) => { const file
Use the instant sample or connect the API to persist datasets, jobs, and lineage.
The portfolio sample is ready. Connect the API to enable persistent workflows.
The API is unavailable. The local demo remains functional.
className={`primary file-button${combinedBusy ? " disabled" : ""}`} aria-disabled={combinedBusy}
"Upload dataset"
"Export preview CSV (up to 100 rows)"
'''


class DataFlowDemoTests(unittest.TestCase):
    def test_case_study_and_public_demo_pin_the_same_source(self):
        assignments=ast.parse((ROOT/'scripts/build_hiring_resources.py').read_text()).body
        pin=next(ast.literal_eval(node.value) for node in assignments if isinstance(node,ast.Assign)
                 and any(isinstance(target,ast.Name) and target.id=='DATAFLOW_COMMIT' for target in node.targets))
        self.assertEqual(pin,demo.COMMIT)
        self.assertEqual(json.loads((ROOT/'public/demos/dataflow/source.json').read_text())['commit'],demo.COMMIT)

    def test_public_boundary_disables_uploads_and_connections(self):
        adapted = demo.adapt_app(APP)
        self.assertIn('disabled={true} onChange=', adapted)
        self.assertIn('API connections are disabled.', adapted)
        self.assertIn('aria-disabled={true}', adapted)
        self.assertNotIn('setConnectionOpen(true)', adapted)
        self.assertIn('Export preview CSV (up to 100 rows)', adapted)
        self.assertIn('reset when you reload', adapted)

    def test_changed_or_duplicated_upload_hook_fails_closed(self):
        hook = 'disabled={combinedBusy} onChange={(event) => { const file'
        for source in (APP.replace(hook, 'changed'), APP + hook):
            with self.subTest(source=source), self.assertRaisesRegex(ValueError, 'boundary changed'):
                demo.adapt_app(source)

    def test_changed_connection_hook_fails_closed(self):
        with self.assertRaisesRegex(ValueError, 'boundary changed'):
            demo.adapt_app(APP.replace('onConnect={() => setConnectionOpen(true)}', 'changed'))

    def test_chart_scope_and_truncation_notices_are_required(self):
        source = ' chart records loaded from the local preview. Remaining data is not plotted.'
        demo.verify_chart_scope(source)
        for phrase in (' chart records loaded', ' from the local preview', 'Remaining data is not plotted.'):
            with self.subTest(phrase=phrase), self.assertRaises(ValueError):
                demo.verify_chart_scope(source.replace(phrase, ''))

    def test_local_source_uses_the_pinned_commit_not_dirty_working_files(self):
        with tempfile.TemporaryDirectory() as temporary:
            checkout = Path(temporary)
            def git(*args):
                return subprocess.run(['git', '-C', str(checkout), *args], check=True, capture_output=True, text=True).stdout.strip()
            git('init', '-q')
            (checkout/'frontend').mkdir()
            source = checkout/'frontend/source.ts'
            source.write_text('reviewed')
            (checkout/'LICENSE').write_text('license')
            git('add', 'frontend', 'LICENSE')
            git('-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.test', 'commit', '-qm', 'Fixture source')
            commit = git('rev-parse', 'HEAD')
            source.write_text('uncommitted')
            with patch.object(demo, 'COMMIT', commit):
                archive = demo.source_archive(checkout)
            with zipfile.ZipFile(io.BytesIO(archive)) as bundle:
                self.assertEqual(bundle.read('dataflow/frontend/source.ts'), b'reviewed')


if __name__ == '__main__':
    unittest.main()
