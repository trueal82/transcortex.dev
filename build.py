#!/usr/bin/env python3
"""Render the bilingual static site from local page fragments and assets."""

import json
import shutil
from html import escape
from urllib.parse import quote, urlencode
from pathlib import Path

ROOT = Path(__file__).parent
OUT = ROOT / "site"

SITE_NAME = "Transcortex Labs"

# slug -> (de_url_dir, en_url_dir, {lang: (title, description)})
PAGES = {'index': ('',
           '',
           {'de': ('KI und Automatisierung für Unternehmen — Transcortex Labs',
                   'KI-Assistenten, Automatisierung und Schulungen für Mittelstand und Großunternehmen. '
                   'Transcortex Labs begleitet Sie von der Idee bis zur Umsetzung.'),
            'en': ('AI and Automation for Business — Transcortex Labs',
                   'AI assistants, automation, and training for SMEs and large enterprises. Transcortex Labs '
                   'supports you from the first idea through implementation.')}),
 'loesungen': ('loesungen',
               'solutions',
               {'de': ('Lösungen — Transcortex Labs',
                       'KI-Assistenten, Prozessautomatisierung und zentraler KI-Zugang: Entdecken Sie '
                       'passende Lösungen für Ihr Unternehmen.'),
                'en': ('Solutions — Transcortex Labs',
                       'Explore AI assistants, process automation, and central AI access for your '
                       'business.')}),
 'assistenten': ('loesungen/ki-assistenten',
                 'solutions/ai-assistants',
                 {'de': ('KI-Assistenten — Transcortex Labs',
                         'KI-Assistenten für Mitarbeitende: Dokumente bearbeiten, Wissen finden und Entwürfe '
                         'erstellen. Beratung, Integration und Schulung von Transcortex Labs.'),
                  'en': ('AI assistants — Transcortex Labs',
                         'AI assistants for employees: work with documents, find knowledge, and prepare '
                         'drafts. Consulting, integration, and training from Transcortex Labs.')}),
 'automatisierung': ('loesungen/prozessautomatisierung',
                     'solutions/process-automation',
                     {'de': ('Prozessautomatisierung — Transcortex Labs',
                             'Automatisieren Sie Datenübergaben, Aufträge und Dokumentenprozesse mit n8n. '
                             'Konkrete Beispiele, passende KI und ein messbarer Einstieg.'),
                      'en': ('Process automation — Transcortex Labs',
                             'Automate data handovers, orders, and document processes with n8n. Practical '
                             'examples, focused AI, and a measurable starting point.')}),
 'ki-zugang': ('loesungen/ki-zugang',
               'solutions/ai-access',
               {'de': ('Zentraler KI-Zugang — Transcortex Labs',
                       'Zentraler Zugang zu ausgewählten KI-Modellen: Anbindungen, Nutzungsübersicht und '
                       'abgestimmte Abrechnung für Unternehmen.'),
                'en': ('Central AI access — Transcortex Labs',
                       'Central access to selected AI models: integrations, usage reporting, and agreed '
                       'billing for your business.')}),
 'fuer-unternehmen': ('fuer-unternehmen',
                      'for-businesses',
                      {'de': ('Für Unternehmen — Transcortex Labs',
                              'KI und Automatisierung passend zu Ihrer Organisation. Unterstützung für '
                              'Mittelstand und Großunternehmen, von Pilot bis Betrieb.'),
                       'en': ('For businesses — Transcortex Labs',
                              'AI and automation tailored to your organisation. Support for SMEs and '
                              'enterprises, from pilot to operations.')}),
 'mittelstand': ('fuer-unternehmen/mittelstand',
                 'for-businesses/smes',
                 {'de': ('Mittelstand — Transcortex Labs',
                         'KI und Automatisierung für den Mittelstand: überschaubar starten, bestehende '
                         'Systeme nutzen und Mitarbeitende einbeziehen.'),
                  'en': ('Small & medium businesses — Transcortex Labs',
                         'AI and automation for SMEs: start small, use existing systems, and involve your '
                         'team.')}),
 'grossunternehmen': ('fuer-unternehmen/grossunternehmen',
                      'for-businesses/enterprises',
                      {'de': ('Großunternehmen — Transcortex Labs',
                              'KI für Großunternehmen: Fachbereiche, IT und Einkauf verbinden. Assistenten, '
                              'Modellzugang und Automatisierung gezielt einführen.'),
                       'en': ('Large enterprises — Transcortex Labs',
                              'AI for large enterprises: connect business teams, IT, and procurement. '
                              'Introduce assistants, model access, and automation.')}),
 'schulungen': ('schulungen',
                'training',
                {'de': ('Schulungen & Compliance — Transcortex Labs',
                        'Praxisnahe Schulungen zu KI-Kompetenz, Datenschutz, n8n und EU AI Act. Programme für '
                        'Mitarbeitende, Key User und Verantwortliche.'),
                 'en': ('Training & compliance — Transcortex Labs',
                        'Practical training in AI literacy, data protection, n8n, and EU AI Act for employees, '
                        'key users, and business owners.')}),
 'ki-kompetenz': ('schulungen/ki-kompetenz-datenschutz',
                  'training/ai-literacy-data-protection',
                  {'de': ('KI-Kompetenz & Datenschutz — Transcortex Labs',
                          'KI-Kompetenz und Datenschutz im Arbeitsalltag: rollenbezogene Schulungen mit '
                          'Übungen und nachvollziehbarem Schulungsnachweis.'),
                   'en': ('AI literacy & data protection — Transcortex Labs',
                          'AI literacy and data protection at work: role-specific training with practical '
                          'exercises and documented learning.')}),
 'n8n-schulungen': ('schulungen/n8n',
                    'training/n8n',
                    {'de': ('n8n-Schulungen — Transcortex Labs',
                            'Ihr Team entscheidet, wie viel es selbst übernehmen möchte. Key User lernen '
                            'kleine Änderungen an bestehenden Abläufen; technische Verantwortliche vertiefen '
                            'den Betrieb. Wir trennen diese Lernziele und üben an einer geeigneten '
                            'Testumgebung.'),
                     'en': ('n8n training — Transcortex Labs',
                            'Your team decides how much to manage itself. Key users learn small changes to '
                            'existing workflows; technical owners focus on operations. We separate these '
                            'learning goals and practise in an appropriate test environment.')}),
 'eu-ai-act': ('schulungen/eu-ai-act',
               'training/eu-ai-act',
               {'de': ('EU AI Act – Schulungen für Unternehmen — Transcortex Labs',
                       'Den EU AI Act verstehen: praxisnahe Schulungen zu Rollen, Risiken und Zuständigkeiten beim KI-Einsatz. Für Geschäftsführung, Fachbereiche und IT.'),
                'en': ('EU AI Act Training for Business — Transcortex Labs',
                       'Understand the EU AI Act with practical training on roles, risks, and responsibilities in AI use. For management, business teams, and IT.')}),
 'unternehmen': ('unternehmen',
                 'about',
                 {'de': ('Über uns — Transcortex Labs',
                         'Lernen Sie Transcortex Labs kennen: Erfahrung mit Geschäft und Technik, ein '
                         'direkter Ansprechpartner und ein Expertennetzwerk.'),
                  'en': ('About us — Transcortex Labs',
                         'Meet Transcortex Labs: business and technical experience, a direct contact, and an '
                         'expert network.')}),
 'whitepaper': ('whitepaper/ki-im-mittelstand',
                'whitepapers/ai-in-smes',
                {'de': ('Whitepaper — Transcortex Labs',
                        'Whitepaper für den Mittelstand: KI-Potenziale einordnen, einen Business Case '
                        'entwickeln und Umsetzung mit Schulung verbinden.'),
                 'en': ('Whitepaper — Transcortex Labs',
                        'Whitepaper for SMEs: assess AI opportunities, develop a business case, and connect '
                        'implementation with training.')}),
 'kontakt': ('kontakt',
             'contact',
             {'de': ('Kontakt und Erstgespräch — Transcortex Labs', 'Fragen zu KI-Assistenten, Automatisierung oder Schulungen? Besprechen Sie Ihr Vorhaben mit Transcortex Labs im kostenlosen Erstgespräch.'),
              'en': ('Contact and Consultation — Transcortex Labs', 'Questions about AI assistants, automation, or training? Discuss your project with Transcortex Labs in a free initial consultation.')}),
 'impressum': ('impressum',
               'imprint',
               {'de': ('Impressum — Transcortex Labs', 'Impressum und Anbieterkennzeichnung von Transcortex Labs.'),
                'en': ('Imprint — Transcortex Labs',
                       'Legal notice and provider identification of Transcortex Labs.')}),
 'datenschutz': ('datenschutz',
                 'privacy',
                 {'de': ('Datenschutzerklärung — Transcortex Labs', 'Informationen zur Datenverarbeitung auf transcortex.dev.'),
                  'en': ('Privacy Policy — Transcortex Labs',
                         'Information on data processing on transcortex.dev.')})}

NAV_GROUPS = [("loesungen", ["assistenten", "automatisierung", "ki-zugang"]),
              ("fuer-unternehmen", ["mittelstand", "grossunternehmen"]),
              ("schulungen", ["ki-kompetenz", "n8n-schulungen", "eu-ai-act"])]

PAGE_LABELS = {'index': ('Start', 'Home'),
 'loesungen': ('Lösungen', 'Solutions'),
 'assistenten': ('KI-Assistenten', 'AI assistants'),
 'automatisierung': ('Prozessautomatisierung', 'Process automation'),
 'ki-zugang': ('Zentraler KI-Zugang', 'Central AI access'),
 'fuer-unternehmen': ('Für Unternehmen', 'For businesses'),
 'mittelstand': ('Mittelstand', 'Small & medium businesses'),
 'grossunternehmen': ('Großunternehmen', 'Large enterprises'),
 'schulungen': ('Schulungen & Compliance', 'Training & compliance'),
 'ki-kompetenz': ('KI-Kompetenz & Datenschutz', 'AI literacy & data protection'),
 'n8n-schulungen': ('n8n-Schulungen', 'n8n training'),
 'eu-ai-act': ('EU AI Act – Schulungen', 'EU AI Act training'),
 'unternehmen': ('Über uns', 'About us'),
 'whitepaper': ('Whitepaper', 'Whitepaper'),
 'kontakt': ('Kontakt', 'Contact'),
 'impressum': ('Impressum', 'Imprint'),
 'datenschutz': ('Datenschutz', 'Privacy')}

FOOTER_LINKS = {
    "de": [("whitepaper", "Whitepaper"), ("kontakt", "Kontakt"), ("impressum", "Impressum"), ("datenschutz", "Datenschutz")],
    "en": [("whitepaper", "Whitepaper"), ("kontakt", "Contact"), ("impressum", "Imprint"), ("datenschutz", "Privacy")],
}

FOOTER_NOTE = {
    "de": "Diese Website verzichtet vollständig auf Tracking, Cookies und Server-Logs.",
    "en": "This website uses no tracking, no cookies, and no server logs.",
}


def page_url(slug: str, lang: str) -> str:
    """Absolute URL of a page in the given language."""
    de_dir, en_dir, _ = PAGES[slug]
    if lang == "de":
        return "/" if not de_dir else f"/{de_dir}/"
    return "/en/" if not en_dir else f"/en/{en_dir}/"


def render_fragment(template: str, **replacements: str) -> str:
    for key, value in replacements.items():
        template = template.replace("{" + key + "}", value)
    return template


def clean_partial(text: str) -> str:
    """Drop source-only HTML comments so they never reach the output."""
    lines = [line for line in text.splitlines() if not line.lstrip().startswith("<!--")]
    return "\n".join(lines).strip()


def render_nav(lang: str, current: str) -> str:
    def nav_link(slug: str, label: str | None = None) -> str:
        aria = ' aria-current="page"' if slug == current else ""
        return f'<a href="{page_url(slug, lang)}"{aria}>{escape(label or PAGE_LABELS[slug][lang == "en"])}</a>'

    groups = []
    for parent, children in NAV_GROUPS:
        active = ' nav-group--active' if current in [parent, *children] else ''
        overview = 'Alle Lösungen' if parent == 'loesungen' else ('Überblick' if lang == 'de' else 'Overview')
        if lang == 'en' and parent == 'loesungen':
            overview = 'All solutions'
        entries = nav_link(parent, overview) + ''.join(nav_link(child) for child in children)
        groups.append(f'<details class="nav-group{active}" name="site-navigation">'
                      f'<summary>{escape(PAGE_LABELS[parent][lang == "en"])}</summary>'
                      f'<div class="nav-panel">{entries}</div></details>')
    groups.append(nav_link('unternehmen'))
    label = 'Gespräch vereinbaren' if lang == 'de' else 'Let’s talk'
    groups.append(f'<a class="nav-contact" href="{page_url("kontakt", lang)}">{label}</a>')
    return '\n'.join(groups)


def render_breadcrumbs(slug: str, lang: str) -> str:
    if slug == 'index':
        return ''
    home = 'Start' if lang == 'de' else 'Home'
    name = 'Seitenpfad' if lang == 'de' else 'Breadcrumb'
    parts = [f'<li><a href="{page_url("index", lang)}">{home}</a></li>']
    for parent, children in NAV_GROUPS:
        if slug in children:
            parts.append(f'<li><a href="{page_url(parent, lang)}">{escape(PAGE_LABELS[parent][lang == "en"])}</a></li>')
    parts.append(f'<li aria-current="page">{escape(PAGE_LABELS[slug][lang == "en"])}</li>')
    return f'<nav class="breadcrumbs" aria-label="{name}"><ol>{"".join(parts)}</ol></nav>'


def render_footer_nav(lang: str) -> str:
    return ' <span aria-hidden="true">·</span> '.join(
        f'<a href="{page_url(slug, lang)}">{label}</a>' for slug, label in FOOTER_LINKS[lang]
    )


def render_alternates(slug: str) -> str:
    lines = [
        f'<link rel="alternate" hreflang="de" href="{page_url(slug, "de")}">',
        f'<link rel="alternate" hreflang="en" href="{page_url(slug, "en")}">',
        f'<link rel="alternate" hreflang="x-default" href="{page_url(slug, "de")}">',
    ]
    return "\n    ".join(lines)


def render_lang_switch(slug: str, lang: str) -> str:
    other = "en" if lang == "de" else "de"
    return f'<a href="{page_url(slug, other)}" lang="{other}" hreflang="{other}" rel="alternate">{other.upper()}</a>'


def main() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    base = (ROOT / "templates" / "base.html").read_text(encoding="utf-8")
    contact_messages = json.loads((ROOT / "pages" / "contact-messages.json").read_text(encoding="utf-8"))

    for slug, (_, _, titles) in PAGES.items():
        for lang in ("de", "en"):
            fragment = (ROOT / "pages" / f"{slug}.{lang}.html").read_text(encoding="utf-8")
            message = contact_messages[slug][lang]
            email_url = escape("mailto:info@transcortex.dev?" + urlencode({
                "subject": message["subject"],
                "body": message["body"].replace("\n", "\r\n"),
            }, quote_via=quote), quote=True)
            contact = render_fragment(
                clean_partial((ROOT / "templates" / "partials" / f"contact.{lang}.html").read_text(encoding="utf-8")),
                email_url=email_url,
            )
            title, description = titles[lang]
            html = render_fragment(
                base,
                lang=lang,
                home_url=page_url("index", lang),
                skip_label="Zum Inhalt" if lang == "de" else "Skip to content",
                menu_label="Menü" if lang == "de" else "Menu",
                nav_label="Hauptnavigation" if lang == "de" else "Main navigation",
                breadcrumbs=render_breadcrumbs(slug, lang),
                title=f"{title}",
                description=description,
                nav=render_nav(lang, slug),
                alternates=render_alternates(slug),
                lang_switch=render_lang_switch(slug, lang),
                footer_note=FOOTER_NOTE[lang],
                footer_nav=render_footer_nav(lang),
                contact=contact,
                content=render_fragment(fragment, contact=contact, email_url=email_url),
            )
            out_dir = OUT / ("" if lang == "de" else "en") / PAGES[slug][0 if lang == "de" else 1]
            out_dir.mkdir(parents=True, exist_ok=True)
            (out_dir / "index.html").write_text(html, encoding="utf-8")

    # Static assets, copied verbatim.
    shutil.copytree(ROOT / "assets", OUT / "assets")

    pages = sum(1 for _ in OUT.rglob("index.html"))
    print(f"rendered {pages} pages into {OUT}/")


if __name__ == "__main__":
    main()
