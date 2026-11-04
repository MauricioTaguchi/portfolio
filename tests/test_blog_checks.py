"""Tests for the verifier itself, using temporary miniature websites."""
import importlib.util
from pathlib import Path
import shutil
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('blog_checks', Path(__file__).resolve().parents[1]/'scripts/check_blog.py')
checks = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checks)

class BlogCheckTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.source = Path(temp.name)/'public'
        self.published = Path(temp.name)/'docs'
        self.source.mkdir()
        self.html = '<html lang="pt-BR"><head><title>Test</title><meta name="description" content="Test"><link rel="canonical" href="https://mauriciotaguchi.com.br/blog/index.html"></head><body><h1 id="start">Test</h1><a href="#start">Start</a></body></html>'
        (self.source/'index.html').write_text(self.html)
        (self.source/'sitemap.xml').write_text('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>https://mauriciotaguchi.com.br/blog/index.html</loc></url></urlset>')
        self.mirror()

    def mirror(self):
        shutil.copytree(self.source, self.published, dirs_exist_ok=True)

    def change(self, old, new):
        path = self.source/'index.html'
        path.write_text(path.read_text().replace(old, new))
        self.mirror()

    def test_valid_site(self):
        self.assertEqual(checks.check(self.source, self.published)['pages'], 1)

    def test_changed_mirror_fails(self):
        (self.published/'index.html').write_text('different')
        with self.assertRaisesRegex(ValueError, 'Mirror mismatch'):
            checks.check(self.source, self.published)

    def test_missing_resource_fails(self):
        self.change('</body>', '<img src="missing.png"></body>')
        with self.assertRaisesRegex(ValueError, 'Missing local resource'):
            checks.check(self.source, self.published)

    def test_missing_anchor_fails(self):
        self.change('href="#start"', 'href="#missing"')
        with self.assertRaisesRegex(ValueError, 'Missing anchor'):
            checks.check(self.source, self.published)

    def test_duplicate_id_fails(self):
        self.change('</body>', '<p id="start">Duplicate</p></body>')
        with self.assertRaisesRegex(ValueError, 'Duplicate ID'):
            checks.check(self.source, self.published)

    def test_invalid_canonical_fails(self):
        self.change('blog/index.html', 'blog/elsewhere.html')
        with self.assertRaisesRegex(ValueError, 'Invalid canonical'):
            checks.check(self.source, self.published)

    def test_sitemap_missing_page_fails(self):
        (self.source/'sitemap.xml').write_text('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"/>')
        self.mirror()
        with self.assertRaisesRegex(ValueError, 'Sitemap'):
            checks.check(self.source, self.published)

    def test_cache_is_rejected(self):
        (self.source/'example.pyc').write_bytes(b'cache')
        self.mirror()
        with self.assertRaisesRegex(ValueError, 'Unexpected cache'):
            checks.check(self.source, self.published)

if __name__ == '__main__':
    unittest.main()
