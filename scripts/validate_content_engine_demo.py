"""Fail closed before uploading the reviewed static diagram to public Pages.

This checks the publishing boundary and common accidental additions. A human must
still review changed text and images for private information before merging.
"""

from html.parser import HTMLParser
from pathlib import Path
import re

PUBLIC = Path(__file__).resolve().parents[1] / "public"
EXPECTED = {"index.html", *(f"images/{name}.png" for name in ("john", "kyle", "scott", "promptson"))}


class EntryPoint(HTMLParser):
    def __init__(self):
        super().__init__()
        self.robots = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "meta" and attrs.get("name", "").lower() == "robots":
            self.robots.append({v.strip().lower() for v in attrs.get("content", "").split(",")})
        if tag == "a":
            assert "nofollow" in attrs.get("rel", "").split(), "Anchor missing nofollow"
        assert tag not in {"form", "iframe", "object", "embed", "base"}, f"Unexpected active element: {tag}"
        assert not (tag == "script" and "src" in attrs), "External script requires review"


def main():
    assert PUBLIC.is_dir() and not PUBLIC.is_symlink(), "Missing or linked public folder"
    entries = list(PUBLIC.rglob("*"))
    assert not any(p.is_symlink() for p in entries), "Symlinks must never be published"
    actual = {p.relative_to(PUBLIC).as_posix() for p in entries if p.is_file()}
    assert actual == EXPECTED, f"Public file inventory changed: {actual ^ EXPECTED}"
    assert {p.relative_to(PUBLIC).as_posix() for p in entries if p.is_dir()} == {"images"}
    for name in sorted(actual):
        p = PUBLIC / name
        assert p.stat().st_size < 2_000_000, f"Unexpected size: {name}"
        if p.suffix == ".png":
            assert p.read_bytes().startswith(b"\x89PNG\r\n\x1a\n"), f"Not a PNG: {name}"
            continue
        html = p.read_text(encoding="utf-8")
        entry = EntryPoint()
        entry.feed(html)
        assert entry.robots == [{"noindex", "nofollow"}], f"Missing/conflicting robots in {name}"
        assert not re.search(r"\b(fetch\s*\(|XMLHttpRequest|WebSocket|EventSource|sendBeacon\s*\(|import\s*\()", html), "Network execution requires review"
        assert not re.search(r"file://|/Users/|-----BEGIN .*PRIVATE KEY|github_pat_|gh[pousr]_[A-Za-z0-9]{20,}|sk-(?:proj-)?[A-Za-z0-9_-]{20,}|pat[A-Za-z0-9]{14}\.", html), "Potential private material"
        urls = set(re.findall(r"https?://[^\s<>\"'`]+", html))
        assert all(u in {"http://www.w3.org/2000/svg", "https://fonts.googleapis.com", "https://fonts.gstatic.com", "https://github.com/CannaPlanners-Dev/lifted-content-gen"} or u.startswith("https://fonts.googleapis.com/css2?") for u in urls), f"Unexpected remote URL: {urls}"
        images = set(re.findall(r"images/[A-Za-z0-9_.-]+", html))
        assert images == EXPECTED - {"index.html"}, f"Image references changed: {images}"
    print("Validated: only index.html + four PNGs; noindex,nofollow; no API execution; no source/docs in public artifact.")


if __name__ == "__main__":
    main()
