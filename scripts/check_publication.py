"""Check build-critical assets and, optionally, exact published blog bytes."""
from __future__ import annotations

import argparse
from html.parser import HTMLParser
import json
from pathlib import Path
import time
from typing import Callable
from urllib.error import URLError
from urllib.parse import quote, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

ROOT = Path(__file__).resolve().parents[1]
HOST = 'mauriciotaguchi.com.br'
BASE = f'https://{HOST}/blog/'


class Links(HTMLParser):
    def __init__(self, text: str):
        super().__init__()
        self.anchors: set[str] = set()
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            href = dict(attrs).get('href')
            if href:
                self.anchors.add(href)


def check_local(root: Path) -> None:
    """These inputs must survive a clean Vite build, not just exist in docs."""
    source, output = root/'public', root/'docs'
    if (source/'CNAME').read_bytes() != (output/'CNAME').read_bytes():
        raise ValueError('CNAME differs between public and docs.')
    if (source/'CNAME').read_text(encoding='utf-8').strip() != HOST:
        raise ValueError('Unexpected custom domain.')
    if (source/'blog-entry.css').read_bytes() != (output/'blog-entry.css').read_bytes():
        raise ValueError('Homepage blog styles differ between public and docs.')
    for path, accepted in [(root/'index.html', {'%BASE_URL%blog/', './blog/', '/blog/'}),
                           (output/'index.html', {'./blog/', '/blog/'})]:
        if not (Links(path.read_text(encoding='utf-8')).anchors & accepted):
            raise ValueError(f'Homepage blog link missing: {path.relative_to(root)}')


def inventory(directory: Path) -> dict[str, bytes]:
    files: dict[str, bytes] = {}
    for path in sorted(directory.rglob('*')):
        if path.is_symlink():
            raise ValueError('Published assets must not be symbolic links.')
        if path.is_file():
            if '__pycache__' in path.parts or path.suffix == '.pyc':
                raise ValueError('A bytecode cache is present in published assets.')
            files[path.relative_to(directory).as_posix()] = path.read_bytes()
    if not files or 'index.html' not in files:
        raise ValueError('Published blog index is missing.')
    return files


class SameOriginRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        target = urlsplit(newurl)
        if (target.scheme != 'https' or target.hostname != HOST or target.port
                or target.username or target.password or not target.path.startswith('/blog/')):
            raise ValueError('Unexpected publication redirect.')
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def fetch_asset(relative: str, size: int, timeout: float) -> bytes:
    request = Request(BASE + quote(relative, safe='/'),
                      headers={'Cache-Control': 'no-cache', 'User-Agent': 'Portfolio-publication-check'})
    with build_opener(SameOriginRedirect()).open(request, timeout=timeout) as response:
        if response.status != 200:
            raise OSError(f'Unexpected HTTP status for {relative}: {response.status}')
        # One extra byte is sufficient to reject a larger/stale response.
        return response.read(size + 1)


def wait_for_publication(
    expected: dict[str, bytes], *, timeout: float = 180, interval: float = 10,
    fetch: Callable[[str, int, float], bytes] = fetch_asset,
    clock: Callable[[], float] = time.monotonic,
    sleep: Callable[[float], None] = time.sleep,
) -> dict:
    """Retry stale/missing responses within a deadline; never report them as success."""
    if timeout <= 0 or interval <= 0 or not expected:
        raise ValueError('Positive time limits and a nonempty inventory are required.')
    deadline = clock() + timeout
    attempts = 0
    reason = 'No publication response.'
    while clock() < deadline:
        attempts += 1
        try:
            for relative, content in expected.items():
                remaining = deadline - clock()
                if remaining <= 0:
                    raise TimeoutError('Publication deadline exceeded.')
                received = fetch(relative, len(content), min(10.0, remaining))
                if received != content:
                    raise ValueError(f'Deployed content is different: {relative}')
            return {'status': 'passed', 'files_compared': len(expected), 'attempts': attempts}
        except (OSError, URLError, ValueError) as error:
            reason = str(error)
        remaining = deadline - clock()
        if remaining <= 0:
            break
        sleep(min(interval, remaining))
    raise TimeoutError(f'Published blog did not match this checkout. {reason}')


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--remote', action='store_true', help='Verify exact HTTPS blog bytes after deployment.')
    args = parser.parse_args()
    try:
        check_local(ROOT)
        result = {'status': 'passed', 'custom_domain_preserved': True, 'homepage_link_present': True}
        if args.remote:
            result['published'] = wait_for_publication(inventory(ROOT/'docs/blog'))
        print(json.dumps(result, indent=2))
        return 0
    except (OSError, ValueError, URLError) as error:
        print(f'Publication check failed: {error}')
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
