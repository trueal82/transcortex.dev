#!/usr/bin/env python3
"""Sanity-check rendered site/: no broken internal links, no external URLs,
no unreplaced template placeholders. Exits non-zero on the first class of
failure; prints every problem found."""

import re
import sys
from pathlib import Path

site = Path(__file__).resolve().parent.parent / "site"
errors = []

for page in site.rglob("index.html"):
    html = page.read_text(encoding="utf-8")
    for attr in ("href", "src"):
        for url in re.findall(rf'{attr}="([^"]+)"', html):
            if url.startswith(("http://", "https://", "mailto:")):
                errors.append(f"{page}: external URL {url}")
            elif url.startswith("#"):
                continue
            else:
                path = url.split("#")[0].rstrip("/") or "/"
                target = site / path.lstrip("/")
                if path.endswith("/"):
                    target = target / "index.html"
                if not target.exists():
                    errors.append(f"{page}: broken link {url}")
    for placeholder in re.findall(r"\{[a-z_]+\}", html):
        errors.append(f"{page}: unreplaced placeholder {placeholder}")

if errors:
    print("\n".join(errors))
    sys.exit(1)
print(f"OK: {len(list(site.rglob('index.html')))} pages, no broken links, no external URLs")