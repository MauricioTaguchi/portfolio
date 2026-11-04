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
        self.html = '<html lang="en"><head><title>Test</title><meta name="description" content="Test"><link rel="canonical" href="https://mauriciotaguchi.com.br/blog/index.html"></head><body><h1 id="start">Test</h1><a href="#start">Start</a></body></html>'
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

class EnglishRoutingTests(unittest.TestCase):
    setUp = BlogCheckTests.setUp
    mirror = BlogCheckTests.mirror
    change = BlogCheckTests.change

    def add_alias(self, target='index.html', robots='noindex,follow'):
        text = ('<html lang="en"><head><title>Moved</title>'
                '<meta name="description" content="Moved">'
                f'<meta http-equiv="refresh" content="0; url={target}">'
                f'<meta name="robots" content="{robots}">'
                f'<link rel="canonical" href="{checks.BASE}{target}"></head>'
                f'<body><h1>Moved</h1><a href="{target}">Continue</a></body></html>')
        (self.source/'legacy.html').write_text(text)
        self.mirror()

    def test_valid_legacy_route(self):
        self.add_alias()
        result = checks.check(self.source,self.published)
        self.assertEqual(result['canonical_pages'],1)
        self.assertEqual(result['legacy_redirects'],1)

    def test_unknown_redirect_rejected(self):
        self.add_alias('missing.html')
        with self.assertRaisesRegex(ValueError,'Invalid redirect target'):
            checks.check(self.source,self.published)

    def test_self_redirect_rejected(self):
        self.add_alias('legacy.html')
        with self.assertRaisesRegex(ValueError,'Invalid redirect target'):
            checks.check(self.source,self.published)

    def test_redirect_requires_noindex(self):
        self.add_alias(robots='index,follow')
        with self.assertRaisesRegex(ValueError,'excluded from indexing'):
            checks.check(self.source,self.published)

    def test_non_english_page_rejected(self):
        self.change('lang="en"','lang="fr"')
        with self.assertRaisesRegex(ValueError,'language'):
            checks.check(self.source,self.published)

if __name__ == '__main__':
    unittest.main()
