#!/usr/bin/env python3
"""Render templates/base.html + pages/*.{de,en}.html into static site/.

Standard library only. Output layout:

    site/index.html                                (de home)
    site/{leistungen,beispiele,n8n-stack,llm-automatisierung,schulungen,kontakt,unternehmen,impressum,datenschutz}/index.html
    site/en/{index,services,use-cases,n8n-stack,llm-automation,training,contact,about,imprint,privacy}/index.html
"""

import json
import shutil
from html import escape
from urllib.parse import quote, urlencode
from pathlib import Path

ROOT = Path(__file__).parent
OUT = ROOT / "site"

SITE_NAME = "Transcortex Labs"

# slug -> (de_url_dir, en_url_dir, {lang: (title, description)})
PAGES = {
    "index": ("", "", {
        "de": ("n8n-Beratung für KMU — Transcortex Labs",
               "Transcortex Labs verbindet Ihre Systeme mit n8n und generativer KI. Beratung und Umsetzung für KMU mit Fokus auf Handel und E-Commerce."),
        "en": ("n8n Consulting for German SMEs — Transcortex Labs",
               "Transcortex Labs connects your systems with n8n and generative AI. Consulting and implementation for German SMEs, with a focus on retail and e-commerce."),
    }),
    "leistungen": ("leistungen", "services", {
        "de": ("n8n-Beratung und Umsetzung — Transcortex Labs",
               "Von der Prozessanalyse zum n8n-Workflow: Transcortex Labs begleitet KMU bei Systemanbindung, KI-Integration, Hosting und Schulung."),
        "en": ("n8n Consulting and Implementation — Transcortex Labs",
               "From process assessment to working n8n workflows: Transcortex Labs helps SMEs with systems integration, practical AI, hosting, and team training."),
    }),
    "beispiele": ("beispiele", "use-cases", {
        "de": ("n8n-Beispiele für Handel und KMU — Transcortex Labs",
               "Produktdaten, Aufträge, Angebote und Kundendaten: Vier Beispiele zeigen, wo n8n im Arbeitsalltag helfen kann und wie sich der Nutzen prüfen lässt."),
        "en": ("n8n Use Cases for Retail and SMEs — Transcortex Labs",
               "Explore n8n workflows for supplier data, orders, quotes, and customer records, with practical objectives and ways to measure their value."),
    }),
    "n8n-stack": ("n8n-stack", "n8n-stack", {
        "de": ("n8n-Stack: Self-Hosting oder Cloud — Transcortex Labs",
               "n8n auf eigener Infrastruktur oder als SaaS: So passen Workflows, Datenhaltung und optionale KI zu den Anforderungen Ihres Unternehmens."),
        "en": ("n8n Stack: Self-Hosted or Cloud — Transcortex Labs",
               "Run n8n on your infrastructure or as SaaS. Understand how workflows, data storage, and optional AI fit your business requirements."),
    }),
    "llm-automatisierung": ("llm-automatisierung", "llm-automation", {
        "de": ("LLMs in der Prozessautomatisierung — Transcortex Labs",
               "Was bringt ein LLM im Workflow? Konkrete Anwendungen für Dokumente, Anfragen und Entwürfe — mit n8n, klaren Regeln und passenden Freigaben."),
        "en": ("LLMs in Process Automation — Transcortex Labs",
               "What does an LLM add to a workflow? Practical uses for documents, enquiries, and drafts, with n8n, clear rules, and appropriate approvals."),
    }),
    "schulungen": ("schulungen", "training", {
        "de": ("EUDR- und n8n-Schulungen — Transcortex Labs", "Praxisnahe EUDR-Mitarbeiterschulungen, n8n-Training für Key User und Administration. Wissen, Übungen und Unterstützung für Ihr Team."),
        "en": ("EUDR and n8n Training — Transcortex Labs", "Practical EUDR employee training, n8n key user workshops, and administration training. Knowledge, exercises, and support for your team."),
    }),
    "kontakt": ("kontakt", "contact", {
        "de": ("Kontakt und Erstgespräch — Transcortex Labs", "Fragen zu n8n, KI, EUDR oder Schulungen? Transcortex Labs hilft weiter. Kostenloses Erstgespräch von 30 Minuten anfragen."),
        "en": ("Contact and Consultation — Transcortex Labs", "Questions about n8n, AI, EUDR, or training? Transcortex Labs can help. Request a free 30-minute consultation."),
    }),
    "unternehmen": ("unternehmen", "about", {
        "de": ("Unternehmen — Transcortex Labs",
               "Automatisierung mit Blick fürs Geschäft: Lernen Sie Transcortex Labs kennen. Erfahrung in Handel und IT, ein direkter Ansprechpartner und ein Netzwerk für Spezialthemen."),
        "en": ("Company — Transcortex Labs",
               "Automation with your business in mind. Meet Transcortex Labs: retail and IT experience, a dedicated point of contact, and a network of specialists."),
    }),
    "impressum": ("impressum", "imprint", {
        "de": ("Impressum — Transcortex Labs", "Impressum und Anbieterkennzeichnung von Transcortex Labs."),
        "en": ("Imprint — Transcortex Labs", "Legal notice and provider identification of Transcortex Labs."),
    }),
    "datenschutz": ("datenschutz", "privacy", {
        "de": ("Datenschutzerklärung — Transcortex Labs", "Informationen zur Datenverarbeitung auf transcortex.dev."),
        "en": ("Privacy Policy — Transcortex Labs", "Information on data processing on transcortex.dev."),
    }),
}

NAV_LABELS = {
    "de": [("index", "Start"), ("leistungen", "Leistungen"), ("beispiele", "Beispiele"), ("n8n-stack", "n8n-Stack"), ("llm-automatisierung", "KI im Workflow"), ("schulungen", "Schulungen"), ("unternehmen", "Unternehmen")],
    "en": [("index", "Home"), ("leistungen", "Services"), ("beispiele", "Use cases"), ("n8n-stack", "n8n stack"), ("llm-automatisierung", "AI in workflows"), ("schulungen", "Training"), ("unternehmen", "Company")],
}

FOOTER_LINKS = {
    "de": [("kontakt", "Kontakt"), ("impressum", "Impressum"), ("datenschutz", "Datenschutz")],
    "en": [("kontakt", "Contact"), ("impressum", "Imprint"), ("datenschutz", "Privacy")],
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
    links = []
    for slug, label in NAV_LABELS[lang]:
        aria = ' aria-current="page"' if slug == current else ""
        links.append(f'<a href="{page_url(slug, lang)}"{aria}>{label}</a>')
    return "\n      ".join(links)


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
