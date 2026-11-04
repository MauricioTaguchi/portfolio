"""Exercise real HTTP navigation and a download in Chromium; never silently skip."""
from __future__ import annotations
import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import tempfile
from threading import Thread
from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright
from check_blog import Page, require

ROOT = Path(__file__).resolve().parents[1]


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def exercise(base: str, screenshots: Path | None) -> dict:
    pages = sorted((ROOT/'docs/blog').glob('*.html'))
    if screenshots:
        screenshots.mkdir(parents=True, exist_ok=True)
    downloads = 0
    states = 0
    with sync_playwright() as playwright:
        options = {'headless': True}
        if os.environ.get('BROWSER_EXECUTABLE'):
            options['executable_path'] = os.environ['BROWSER_EXECUTABLE']
        browser = playwright.chromium.launch(**options)
        for width, height in [(1440, 1000), (390, 844)]:
            context = browser.new_context(viewport={'width': width, 'height': height}, accept_downloads=True)
            page = context.new_page()
            errors = []
            page.on('pageerror', lambda error: errors.append(str(error)))
            page.on('console', lambda message: errors.append(message.text) if message.type == 'error' and 'favicon.ico' not in message.location.get('url', '') else None)
            for local in pages:
                expected = Page(local.read_text(encoding='utf-8'))
                response = page.goto(base+local.name, wait_until='networkidle', timeout=30000)
                require(response is not None and response.status == 200, f'HTTP failure: {local.name}')
                require(page.title() == expected.title, f'Wrong title: {local.name}')
                require(page.locator('h1').count() == 1, f'Missing main heading: {local.name}')
                require(len(page.locator('main').inner_text()) > 100, f'Blank content: {local.name}')
                require(page.locator('vite-error-overlay').count() == 0, 'Framework error overlay')
                require(page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'), f'Horizontal overflow: {local.name} at {width}')
                require('Arial' in page.locator('body').evaluate('(el) => getComputedStyle(el).fontFamily'), 'Stylesheet was not applied')
                if screenshots:
                    page.screenshot(path=str(screenshots/f'{width}-{local.stem}.png'), full_page=True)
                states += 1
            page.goto(base+'index.html')
            page.locator('h2 a[href="validacao-csv.html"]').click()
            require(urlsplit(page.url).path.endswith('/validacao-csv.html'), 'Article navigation failed')
            page.locator('a[href="csv-validation-en.html"]').click()
            require(page.locator('html').get_attribute('lang') == 'en', 'Language navigation failed')
            page.goto(base+'reproduzir.html')
            page.locator('.toc a[href="#executar"]').click()
            require(urlsplit(page.url).fragment == 'executar', 'Contents anchor failed')
            page.locator('summary').first.click()
            require(page.locator('details').first.get_attribute('open') is not None, 'Practice answer did not open')
            with page.expect_download() as event:
                page.locator('a[download][href="exemplos/validacao-csv/test_output_safety.py"]').click()
            download = event.value
            require(download.failure() is None, 'Browser download failed')
            with tempfile.TemporaryDirectory() as directory:
                target = Path(directory)/'download.py'
                download.save_as(target)
                require(target.read_bytes() == (ROOT/'docs/blog/exemplos/validacao-csv/test_output_safety.py').read_bytes(), 'Downloaded file differs from the checked version')
            downloads += 1
            # This additionally verifies every downloadable resource over HTTP.
            for local in pages:
                for href in Page(local.read_text(encoding='utf-8')).links:
                    if href.startswith('exemplos/'):
                        response = page.request.get(base+href, timeout=30000)
                        require(response.status == 200, f'Resource HTTP error: {href}')
                        require(response.body() == (ROOT/'docs/blog'/href).read_bytes(), f'Resource mismatch: {href}')
            require(not errors, 'Browser errors: '+'; '.join(errors))
            context.close()
        browser.close()
    return {'status': 'passed', 'base_url': base, 'page_viewports': states,
            'browser_downloads': downloads, 'viewports': ['1440x1000', '390x844'],
            'flows': ['index-to-article', 'English edition', 'contents anchor', 'practice answer', 'download bytes']}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-url', help='Optional deployed blog URL; default serves docs locally.')
    parser.add_argument('--screenshots', type=Path)
    args = parser.parse_args()
    server = None
    try:
        if args.base_url:
            parsed = urlsplit(args.base_url)
            require(parsed.scheme == 'https' and parsed.hostname == 'mauriciotaguchi.com.br' and parsed.path.rstrip('/') == '/blog' and not parsed.query and not parsed.fragment and not parsed.username and not parsed.port, 'Unexpected deployed URL')
            base = args.base_url.rstrip('/')+'/'
        else:
            server = ThreadingHTTPServer(('127.0.0.1', 0), partial(QuietHandler, directory=str(ROOT/'docs')))
            Thread(target=server.serve_forever, daemon=True).start()
            base = f'http://127.0.0.1:{server.server_port}/blog/'
        print(json.dumps(exercise(base, args.screenshots), indent=2))
        return 0
    finally:
        if server:
            server.shutdown()
            server.server_close()


if __name__ == '__main__':
    raise SystemExit(main())
