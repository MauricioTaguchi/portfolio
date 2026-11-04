"""Keep the requested site monogram consistent without changing personal names."""
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
class BrandingTests(unittest.TestCase):
    def test_portfolio_wordmarks(self):
        source=(ROOT/'src/portfolio.tsx').read_text()
        self.assertEqual(source.count('>TM<span>'),3)
        self.assertNotIn('>MT<span>',source)
        self.assertIn('Maurício',source)
    def test_public_page_marks_and_mirror(self):
        pages=[p for p in (ROOT/'public').rglob('*.html') if 'class="brand"' in p.read_text()]
        self.assertEqual(len(pages),11)
        for p in pages:
            with self.subTest(page=str(p)):
                self.assertIn('>TM<span>',p.read_text())
                self.assertNotIn('>MT<span>',p.read_text())
                self.assertEqual(p.read_bytes(),(ROOT/'docs'/p.relative_to(ROOT/'public')).read_bytes())
    def test_html_generator_preserves_monogram(self):
        source=(ROOT/'scripts/build_hiring_resources.py').read_text()
        self.assertIn('>TM<span>',source)
        self.assertNotIn('>MT<span>',source)
    def test_favicon_and_mirror(self):
        icon=ROOT/'public/favicon.svg'
        self.assertEqual(ET.fromstring(icon.read_text()).get('aria-label'),'TM')
        self.assertEqual(icon.read_bytes(),(ROOT/'docs/favicon.svg').read_bytes())
