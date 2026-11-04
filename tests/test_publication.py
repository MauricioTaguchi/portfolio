"""Build and publication checks with synthetic files and an offline clock."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('publication', Path(__file__).resolve().parents[1]/'scripts/check_publication.py')
publication = importlib.util.module_from_spec(spec)
spec.loader.exec_module(publication)


class PublicationTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        for folder in ('public', 'docs'):
            (self.root/folder).mkdir()
            (self.root/folder/'CNAME').write_text(publication.HOST, encoding='utf-8')
            (self.root/folder/'blog-entry.css').write_bytes(b'body{}')
        (self.root/'index.html').write_text('<a href="%BASE_URL%blog/">Read</a>', encoding='utf-8')
        (self.root/'docs/index.html').write_text('<a href="./blog/">Read</a>', encoding='utf-8')
        self.now = 0.0

    def sleep(self, duration):
        self.now += duration

    def verify(self, fetch):
        return publication.wait_for_publication({'index.html': b'new'}, timeout=3, interval=1,
                                                fetch=fetch, clock=lambda: self.now, sleep=self.sleep)

    def test_valid_build_assets(self):
        publication.check_local(self.root)

    def test_source_domain_missing(self):
        (self.root/'public/CNAME').unlink()
        with self.assertRaises(OSError):
            publication.check_local(self.root)

    def test_built_domain_missing(self):
        (self.root/'docs/CNAME').unlink()
        with self.assertRaises(OSError):
            publication.check_local(self.root)

    def test_domain_mismatch(self):
        (self.root/'docs/CNAME').write_text('other.example', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'CNAME differs'):
            publication.check_local(self.root)

    def test_wrong_domain_in_both_copies(self):
        for folder in ('public', 'docs'):
            (self.root/folder/'CNAME').write_text('other.example', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'Unexpected custom domain'):
            publication.check_local(self.root)

    def test_home_link_missing(self):
        (self.root/'docs/index.html').write_text('<p>No link</p>', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'blog link missing'):
            publication.check_local(self.root)

    def test_home_link_in_comment_is_not_enough(self):
        (self.root/'index.html').write_text('<!-- <a href="/blog/">Read</a> -->', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'blog link missing'):
            publication.check_local(self.root)

    def test_style_mismatch(self):
        (self.root/'docs/blog-entry.css').write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError, 'styles differ'):
            publication.check_local(self.root)

    def test_matching_remote_bytes(self):
        self.assertEqual(self.verify(lambda *args: b'new')['attempts'], 1)

    def test_stale_deployment_retried(self):
        calls = []
        def fetch(*args):
            calls.append(args)
            return b'old' if len(calls) == 1 else b'new'
        self.assertEqual(self.verify(fetch)['attempts'], 2)
        self.assertEqual(self.now, 1)

    def test_wrong_remote_content_never_passes(self):
        with self.assertRaisesRegex(TimeoutError, 'did not match'):
            self.verify(lambda *args: b'wrong')
        self.assertEqual(self.now, 3)

    def test_network_failure_is_failure(self):
        def fetch(*args):
            raise OSError('Temporary failure')
        with self.assertRaisesRegex(TimeoutError, 'Temporary failure'):
            self.verify(fetch)

    def test_checks_every_file(self):
        calls = []
        def fetch(name, size, timeout):
            calls.append(name)
            return {'index.html': b'html', 'styles.css': b'css'}[name]
        result = publication.wait_for_publication({'index.html': b'html', 'styles.css': b'css'}, fetch=fetch)
        self.assertEqual(result['files_compared'], 2)
        self.assertEqual(calls, ['index.html', 'styles.css'])

    def test_empty_inventory_rejected(self):
        with self.assertRaises(ValueError):
            publication.wait_for_publication({})
        with self.assertRaises(ValueError):
            publication.inventory(self.root/'missing')

    def test_inventory_includes_code_and_styles(self):
        folder = self.root/'blog'
        (folder/'examples').mkdir(parents=True)
        for name in ('index.html', 'styles.css', 'examples/demo.py'):
            (folder/name).write_bytes(b'content')
        self.assertEqual(set(publication.inventory(folder)), {'index.html', 'styles.css', 'examples/demo.py'})

    def test_inventory_rejects_bytecode(self):
        folder = self.root/'blog'
        folder.mkdir()
        (folder/'index.html').write_bytes(b'html')
        (folder/'example.pyc').write_bytes(b'cache')
        with self.assertRaisesRegex(ValueError, 'bytecode'):
            publication.inventory(folder)

    def test_cross_origin_redirect_rejected(self):
        handler = publication.SameOriginRedirect()
        with self.assertRaisesRegex(ValueError, 'redirect'):
            handler.redirect_request(None, None, 302, '', {}, 'https://other.example/blog/')

    def test_insecure_redirect_rejected(self):
        with self.assertRaisesRegex(ValueError, 'redirect'):
            publication.SameOriginRedirect().redirect_request(None, None, 302, '', {}, 'http://mauriciotaguchi.com.br/blog/')


if __name__ == '__main__':
    unittest.main()
