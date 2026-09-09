#!/usr/bin/env python3
"""Check generated routes, local assets, language pairs and contact options."""
import importlib.util
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import parse_qs, urlsplit
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent.parent
site = ROOT / 'site'
spec = importlib.util.spec_from_file_location('site_builder', ROOT / 'build.py')
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)
messages = json.loads((ROOT / 'pages/contact-messages.json').read_text())
CALENDLY = 'https://calendly.com/alexander-truemper'

class Page(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.ids = []
        self.elements = []
        self.feed(text)
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.elements.append((tag, attrs))
        if 'id' in attrs:
            self.ids.append(attrs['id'])

errors = []
expected = {site / builder.page_url(slug, lang).lstrip('/') / 'index.html': (slug, lang)
            for slug in builder.PAGES for lang in ('de', 'en')}
actual = set(site.rglob('index.html'))
if actual != set(expected):
    errors.append(f'Page set mismatch: missing={set(expected) - actual}, extra={actual - set(expected)}')
parsed = {p: Page(p.read_text()) for p in actual}
for path, page in parsed.items():
    slug, lang = expected.get(path, ('', ''))
    def fail(message):
        errors.append(f'{path.relative_to(site)}: {message}')
    if len(page.ids) != len(set(page.ids)):
        fail('duplicate IDs')
    if sum(tag == 'h1' for tag, _ in page.elements) != 1:
        fail('expected exactly one H1')
    if re.search(r'\{[a-z_]+\}', path.read_text()):
        fail('unresolved template placeholder')
    email_count = booking_count = 0
    alternates = {}
    for tag, attrs in page.elements:
        if tag in ('script', 'iframe', 'embed', 'object'):
            fail(f'unexpected active or embedded content: {tag}')
        if tag == 'img' and 'alt' not in attrs:
            fail('image lacks alt text')
        if tag == 'link' and attrs.get('rel') == 'alternate':
            alternates[attrs.get('hreflang')] = attrs.get('href')
        for attr in ('href', 'src', 'poster'):
            value = attrs.get(attr)
            if value is None:
                continue
            parts = urlsplit(value)
            if parts.scheme == 'mailto':
                email_count += 1
                q = parse_qs(parts.query)
                if parts.path != 'info@transcortex.dev' or set(q) != {'subject', 'body'}:
                    fail('invalid email recipient or draft fields')
                elif slug and (q['subject'] != [messages[slug][lang]['subject']] or
                               q['body'] != [messages[slug][lang]['body'].replace('\n', '\r\n')]):
                    fail('email draft does not match page and language')
                continue
            if parts.scheme or parts.netloc:
                if tag != 'a' or value != CALENDLY:
                    fail(f'unexpected external URL: {value}')
                elif attrs.get('target') != '_blank' or 'noopener' not in attrs.get('rel', ''):
                    fail('Calendly must open safely in a new tab')
                else:
                    booking_count += 1
                continue
            target = site / parts.path.lstrip('/') if parts.path else path
            if target.is_dir():
                target /= 'index.html'
            if not target.is_file():
                fail(f'broken link or asset: {value}')
            elif parts.fragment and (target not in parsed or parts.fragment not in parsed[target].ids):
                fail(f'broken fragment: {value}')
    if not email_count or not booking_count:
        fail('missing email or Calendly contact option')
    if slug:
        wanted = {l: builder.page_url(slug, l) for l in ('de', 'en')}
        wanted['x-default'] = wanted['de']
        if alternates != wanted:
            fail('incorrect alternate-language links')
css = (site / 'assets/css/style.css').read_text()
if '@import' in css or re.search(r'url\([\s\'"]*(?:https?:|//)', css):
    errors.append('Stylesheet includes an external resource')
if errors:
    print('\n'.join(errors))
    sys.exit(1)
print(f'OK: {len(parsed)} pages; routes, fragments, local assets, language pairs and email/Calendly links verified')
