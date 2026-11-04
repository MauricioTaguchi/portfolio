"""Validate blog pages, local resources, sitemap and the publication mirror."""
from __future__ import annotations
from html.parser import HTMLParser
import json
from pathlib import Path
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://mauriciotaguchi.com.br/blog/'


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


class Page(HTMLParser):
    def __init__(self, text: str):
        super().__init__()
        self.ids: set[str] = set()
        self.links: list[str] = []
        self.headings = 0
        self.language = None
        self.canonical: list[str] = []
        self.title = ''
        self.description = ''
        self._in_title = False
        self.redirect = None
        self.robots = ''
        self.feed(text)
        self.close()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            require(attrs['id'] not in self.ids, f'Duplicate ID: {attrs["id"]}')
            self.ids.add(attrs['id'])
        if tag == 'h1':
            self.headings += 1
        if tag == 'html':
            self.language = attrs.get('lang')
        if tag == 'title':
            self._in_title = True
        if tag == 'meta' and attrs.get('http-equiv', '').lower() == 'refresh':
            value = attrs.get('content', '')
            require(value.startswith('0; url='), 'Unsupported redirect format')
            self.redirect = value[7:]
        if tag == 'meta' and attrs.get('name') == 'robots':
            self.robots = attrs.get('content', '')
        if tag == 'meta' and attrs.get('name') == 'description':
            self.description = attrs.get('content', '')
        if tag == 'link' and attrs.get('rel') == 'canonical':
            self.canonical.append(attrs.get('href', ''))
        for key in ('href', 'src'):
            if key in attrs:
                self.links.append(attrs[key])

    def handle_endtag(self, tag):
        if tag == 'title':
            self._in_title = False

    def handle_data(self, data):
        if self._in_title:
            self.title += data


def inventory(directory: Path) -> set[Path]:
    return {p.relative_to(directory) for p in directory.rglob('*') if p.is_file()}


def check(source: Path, published: Path) -> dict:
    source = source.resolve()
    paths = inventory(source)
    require(bool(paths), 'Blog is empty')
    require(paths == inventory(published), 'Publication mirror contains different paths')
    for path in sorted(paths):
        require('__pycache__' not in path.parts and path.suffix != '.pyc', f'Unexpected cache: {path}')
        require((source/path).read_bytes() == (published/path).read_bytes(), f'Mirror mismatch: {path}')
    pages = {path: Page((source/path).read_text(encoding='utf-8'))
             for path in sorted(paths) if path.suffix == '.html'}
    require(Path('index.html') in pages, 'Blog index is missing')
    links = 0
    canonicals = set()
    for path, page in pages.items():
        require(page.headings == 1, f'Expected one h1: {path}')
        require(page.language == 'en', f'Missing/unsupported language: {path}')
        require(bool(page.title.strip()) and bool(page.description.strip()), f'Missing metadata: {path}')
        expected = BASE + path.as_posix()
        if page.redirect:
            target = Path(page.redirect)
            require(target.as_posix() == page.redirect and target in pages and target != path, f'Invalid redirect target: {path}')
            require(pages[target].redirect is None, f'Redirect chains are not allowed: {path}')
            require('noindex' in page.robots, f'Redirect must be excluded from indexing: {path}')
            expected = BASE + target.as_posix()
        else:
            canonicals.add(expected)
        require(page.canonical == [expected], f'Invalid canonical URL: {path}')
        for href in page.links:
            parsed = urlsplit(href)
            if parsed.scheme or parsed.netloc or href == '../':
                continue
            target = (source/path).parent / unquote(parsed.path) if parsed.path else source/path
            target = target.resolve()
            require(target.is_relative_to(source), f'Unexpected local target: {path} -> {href}')
            if target.is_dir():
                target /= 'index.html'
            require(target.is_file(), f'Missing local resource: {path} -> {href}')
            if parsed.fragment:
                relative = target.relative_to(source)
                require(relative in pages, f'Fragment points to a non-HTML file: {href}')
                require(unquote(parsed.fragment) in pages[relative].ids, f'Missing anchor: {path} -> {href}')
            links += 1
    sitemap = ET.parse(source/'sitemap.xml').getroot()
    urls = [element.text for element in sitemap.findall('{http://www.sitemaps.org/schemas/sitemap/0.9}url/{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
    require(len(urls) == len(set(urls)), 'Duplicate sitemap URL')
    require(set(urls) == canonicals, 'Sitemap does not match the HTML pages')
    return {'status': 'passed', 'pages': len(pages), 'local_links_and_resources': links,
            'mirrored_files': len(paths), 'canonical_pages': len(canonicals),
            'legacy_redirects': sum(p.redirect is not None for p in pages.values()), 'sitemap_complete': True}


def main() -> int:
    try:
        print(json.dumps(check(ROOT/'public/blog', ROOT/'docs/blog'), indent=2))
        return 0
    except (OSError, ValueError, ET.ParseError) as error:
        print(f'Blog check failed: {error}')
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
