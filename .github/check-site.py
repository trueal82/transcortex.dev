#!/usr/bin/env python3
"""Sanity-check rendered site/: no broken internal links, no external URLs
outside the allowlist, no unreplaced template placeholders. Exits non-zero on
the first class of failure; prints every problem found."""

import re
import sys
from pathlib import Path
from urllib.parse import urlsplit

# Exact external hostnames this site is allowed to link to.
ALLOWED_HOSTS = {
    "alexander.truemper.cc",  # founder's blog
    "calendly.com",            # booking link
    "docs.n8n.io",             # n8n documentation
    "n8n.io",                  # n8n product site
    "truemper.cc",             # email domain
    "www.linkedin.com",        # founder's LinkedIn profile
}
# Allowed mailto: recipients (exact address).
ALLOWED_MAILTO = {"alexander@truemper.cc"}


def external_error(url: str) -> str | None:
    """Error message if url is an external URL outside the allowlist."""
    parts = urlsplit(url)
    if parts.scheme in ("http", "https"):
        if parts.hostname not in ALLOWED_HOSTS:
            return f"external URL not on allowlist {url}"
    elif parts.scheme == "mailto":
        if parts.path not in ALLOWED_MAILTO:
            return f"mailto not on allowlist {url}"
    return None


site = Path(__file__).resolve().parent.parent / "site"
errors = []

for page in site.rglob("index.html"):
    html = page.read_text(encoding="utf-8")
    for attr in ("href", "src"):
        for url in re.findall(rf'{attr}="([^"]+)"', html):
            err = external_error(url)
            if err:
                errors.append(f"{page}: {err}")
            elif url.startswith(("http://", "https://", "mailto:")):
                continue  # allowlisted external URL — not an internal path
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
print(f"OK: {len(list(site.rglob('index.html')))} pages, no broken links, no unapproved external URLs")