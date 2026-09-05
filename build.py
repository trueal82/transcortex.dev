#!/usr/bin/env python3
"""Render templates/base.html + pages/*.{de,en}.html into static site/.

Standard library only. Output layout:

    site/index.html                                (de home)
    site/{leistungen,beispiele,ueber-mich,impressum,datenschutz}/index.html
    site/en/{index,services,use-cases,about,imprint,privacy}/index.html
"""

import shutil
from pathlib import Path

ROOT = Path(__file__).parent
OUT = ROOT / "site"

SITE_NAME = "Transcortex Labs"

# slug -> (de_url_dir, en_url_dir, {lang: (title, description)})
PAGES = {
    "index": ("", "", {
        "de": ("KI-Automatisierung für KMU — Transcortex Labs",
               "Prozesse mit n8n und LLMs automatisieren: für KMU, die die erste Digitalisierungswelle verpasst haben — direkt in die KI-Ära statt Rückstand aufholen."),
        "en": ("AI automation for SMEs — Transcortex Labs",
               "Automate processes with n8n and LLMs: for SMEs that missed the first digitalization wave — leap straight into the AI era."),
    }),
    "leistungen": ("leistungen", "services", {
        "de": ("Leistungen — Transcortex Labs",
               "Potenzialanalyse, n8n-Workflow-Entwicklung, KI-/LLM-Integration, Self-Hosting und Schulung für KMU."),
        "en": ("Services — Transcortex Labs",
               "Potential analysis, n8n workflow development, AI/LLM integration, self-hosting, and enablement for SMEs."),
    }),
    "beispiele": ("beispiele", "use-cases", {
        "de": ("Beispiele — Transcortex Labs",
               "Konkrete n8n- und LLM-Automatisierungen für KMU: Rechnungseingang, E-Mail-Triage, Angebotserstellung, CRM-Abgleich."),
        "en": ("Use cases — Transcortex Labs",
               "Concrete n8n and LLM automations for SMEs: invoice intake, email triage, quote generation, CRM sync."),
    }),
    "ueber-mich": ("ueber-mich", "about", {
        "de": ("Über mich — Transcortex Labs",
               "Transcortex Labs ist das eigenständige Projekt von Alexander Trümper: zertifiziert in Azure AI, SAP Integration Suite und n8n."),
        "en": ("About me — Transcortex Labs",
               "Transcortex Labs is the independent venture of Alexander Trümper: certified in Azure AI, SAP Integration Suite, and n8n."),
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
    "de": [("index", "Start"), ("leistungen", "Leistungen"), ("beispiele", "Beispiele"), ("ueber-mich", "Über mich")],
    "en": [("index", "Home"), ("leistungen", "Services"), ("beispiele", "Use cases"), ("ueber-mich", "About")],
}

FOOTER_LINKS = {
    "de": [("impressum", "Impressum"), ("datenschutz", "Datenschutz")],
    "en": [("impressum", "Imprint"), ("datenschutz", "Privacy")],
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

    for slug, (_, _, titles) in PAGES.items():
        for lang in ("de", "en"):
            fragment = (ROOT / "pages" / f"{slug}.{lang}.html").read_text(encoding="utf-8")
            contact = clean_partial((ROOT / "templates" / "partials" / f"contact.{lang}.html").read_text(encoding="utf-8"))
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
                content=render_fragment(fragment, contact=contact),
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