"""Verify the public English downloads, not personal handoff files."""
from pathlib import Path
import hashlib
import json
import tempfile
import subprocess
import sys
import unittest
import xml.etree.ElementTree as ET
import zipfile

ROOT=Path(__file__).resolve().parents[1]
DOWNLOADS=ROOT/'public/blog/downloads'

class LearningResourceTests(unittest.TestCase):
    def test_archive_has_exact_public_inventory(self):
        expected={'run_examples.py','README.md','SHA256SUMS.txt',
                  'csv-validation/validate_sales.py','csv-validation/test_validate_sales.py',
                  'csv-validation/test_output_safety.py','csv-validation/sales_valid.csv',
                  'csv-validation/sales_invalid.csv','csv-validation/README.md',
                  'revisions/revision_demo.py','revisions/test_revision_demo.py','revisions/README.md'}
        with zipfile.ZipFile(DOWNLOADS/'technical-examples.zip') as archive:
            self.assertEqual(set(archive.namelist()),expected)
            for name in archive.namelist():
                self.assertFalse(name.startswith('/'))
                self.assertNotIn('..',Path(name).parts)

    def test_archive_checksums_match(self):
        with zipfile.ZipFile(DOWNLOADS/'technical-examples.zip') as archive:
            lines=archive.read('SHA256SUMS.txt').decode().splitlines()
            self.assertEqual(len(lines),len(archive.namelist())-1)
            for line in lines:
                digest,name=line.split('  ',1)
                self.assertEqual(hashlib.sha256(archive.read(name)).hexdigest(),digest)

    def test_archive_preserves_validator_source(self):
        with zipfile.ZipFile(DOWNLOADS/'technical-examples.zip') as archive:
            self.assertEqual(archive.read('csv-validation/validate_sales.py'),
                             (ROOT/'public/blog/exemplos/validacao-csv/validate_sales.py').read_bytes())

    def test_archive_runner_uses_english_paths(self):
        with zipfile.ZipFile(DOWNLOADS/'technical-examples.zip') as archive:
            runner=archive.read('run_examples.py').decode()
            self.assertIn("ROOT / 'csv-validation', ROOT / 'revisions'",runner)

    def test_archive_executes_without_repository(self):
        with tempfile.TemporaryDirectory() as directory:
            with zipfile.ZipFile(DOWNLOADS/'technical-examples.zip') as archive:
                archive.extractall(directory)
            result=subprocess.run([sys.executable,'-B','run_examples.py'],cwd=directory,
                                  capture_output=True,text=True,timeout=150)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            self.assertIn('"source_files_unchanged": true',result.stdout)
            self.assertIn('"diagnostics": 5',result.stdout)

    def test_presentation_has_ten_slides_and_notes(self):
        with zipfile.ZipFile(DOWNLOADS/'csv-validation-slides.pptx') as deck:
            slides=[n for n in deck.namelist() if n.startswith('ppt/slides/slide') and n.endswith('.xml')]
            notes=[n for n in deck.namelist() if n.startswith('ppt/notesSlides/notesSlide') and n.endswith('.xml')]
            self.assertEqual(len(slides),10)
            self.assertEqual(len(notes),10)
            text=''.join(deck.read(n).decode() for n in notes)
            self.assertIn('reproduce',text)

    def test_presentation_titles_match_english_sources(self):
        slides=json.loads((ROOT/'content/slides.json').read_text())
        with zipfile.ZipFile(DOWNLOADS/'csv-validation-slides.pptx') as deck:
            for i,slide in enumerate(slides,1):
                node=ET.fromstring(deck.read(f'ppt/slides/slide{i}.xml'))
                text=' '.join(e.text or '' for e in node.iter('{http://schemas.openxmlformats.org/drawingml/2006/main}t'))
                self.assertIn(slide['title'].replace('\n',' '),text)

    def test_learning_guides_match_reviewed_sources(self):
        for name in ['study-guide.md','presentation-script.md','learning-plan.md']:
            self.assertEqual((DOWNLOADS/name).read_bytes(),(ROOT/'content'/name).read_bytes())

if __name__=='__main__':
    unittest.main()
