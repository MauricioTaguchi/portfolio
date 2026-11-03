"""Check the static blog and its publication mirror with only the standard library."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "public/blog"
PUBLISHED = ROOT / "docs/blog"

class Page(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.ids = set()
        self.links = []
        self.headings = 0
        self.language = None
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            assert attrs["id"] not in self.ids, "Duplicate ID"
            self.ids.add(attrs["id"])
        if tag == "h1":
            self.headings += 1
        if tag == "html":
            self.language = attrs.get("lang")
        if "href" in attrs:
            self.links.append(attrs["href"])

def files(directory):
    return {p.relative_to(directory) for p in directory.rglob("*") if p.is_file() and "__pycache__" not in p.parts}

source_files = files(SOURCE)
assert source_files, "Blog is empty"
assert source_files == files(PUBLISHED), "Publication mirror contains different paths"
for path in source_files:
    assert (SOURCE/path).read_bytes() == (PUBLISHED/path).read_bytes(), f"Mirror mismatch: {path}"

links = 0
pages = list(SOURCE.glob("*.html"))
assert len(pages) == 5, "Expected index and four article/language pages"
for file in pages:
    page = Page(file.read_text(encoding="utf-8"))
    assert page.headings == 1, f"Expected one h1: {file.name}"
    assert page.language in {"pt-BR", "en"}
    for href in page.links:
        parsed = urlsplit(href)
        if parsed.scheme or parsed.netloc or href == "../":
            continue
        target = (file.parent / unquote(parsed.path)).resolve() if parsed.path else file
        assert target.is_relative_to(SOURCE.resolve()), "Unexpected local target"
        assert target.exists(), f"Missing local link: {file.name} -> {href}"
        if parsed.fragment and target.suffix == ".html":
            assert parsed.fragment in Page(target.read_text(encoding="utf-8")).ids, f"Missing anchor: {href}"
        links += 1
for path in [ROOT/"index.html", ROOT/"docs/index.html"]:
    assert "Explorar o blog" in path.read_text(encoding="utf-8")
assert (ROOT/"public/blog-entry.css").read_bytes() == (ROOT/"docs/blog-entry.css").read_bytes()
print(f"PASS: {len(pages)} pages, {links} local links, identical publication mirror and homepage entry.")
