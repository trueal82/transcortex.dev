# transcortex.dev

Static website for transcortex.dev — bilingual (German/English), privacy-first.

- Fully static HTML, rendered at build time by a small Python-stdlib script
  (`build.py`). No client-side JavaScript.
- All assets (CSS, fonts) are served from the container — the site makes zero
  external requests (enforced by a `default-src 'self'` Content-Security-Policy).
- Served by nginx running **without any logging** — no access log, no error log.
- Runs unprivileged (non-root) in the container, listening on port 8080.

## Build & run

```sh
./build.sh                                  # renders site/ and builds the image
docker run -d --name transcortex -p 8080:8080 transcortex.dev:latest
```

Then open <http://localhost:8080>. Stop/remove with
`docker rm -f transcortex`.

Verify that the container logs nothing:

```sh
curl -s localhost:8080/ > /dev/null
docker logs transcortex   # must print nothing
```

## Editing content

- `pages/*.de.html`, `pages/*.en.html` — page content (HTML fragments)
- `templates/base.html` — shared layout (nav, footer, language switcher)
- `assets/css/style.css` — styling
- Contact options offer both Calendly (in a new tab) and email to
  `info@transcortex.dev`. No scheduler is embedded.
- `pages/contact-messages.json` — short email subjects and editable starter messages
  per page and language, also used by footer links. The builder encodes these
  into static mailto links; no JavaScript or form backend is needed.
- `.github/check-site.py` checks links, placeholders, and allowed email addresses.

## Local development

```sh
./dev.sh        # rebuilds site/ when sources change, serves at http://127.0.0.1:1234
./dev.sh 9000   # optional: pick a port
```

Watches `pages/`, `templates/`, and `assets/` every 10s and re-renders on
change. A failed build keeps the last good build served; Ctrl+C stops it.

## Site structure

| German (primary)        | English                |
|-------------------------|------------------------|
| `/`                     | `/en/`                 |
| `/leistungen/`          | `/en/services/`        |
| `/beispiele/`           | `/en/use-cases/`       |
| `/n8n-stack/`           | `/en/n8n-stack/`       |
| `/llm-automatisierung/` | `/en/llm-automation/`  |
| `/schulungen/`           | `/en/training/`        |
| `/kontakt/`             | `/en/contact/`         |
| `/unternehmen/`           | `/en/about/`           |
| `/impressum/`           | `/en/imprint/`         |
| `/datenschutz/`         | `/en/privacy/`         |

The retired German `/ueber-mich/` and `/team/` routes (with or without
a trailing slash) 301-redirect directly to `/unternehmen/`. The retired
`/en/team/` route redirects to `/en/about/` (see `nginx/default.conf`).

## Branching & CI

- **`develop`** (default) is the working branch. Every push and every PR
  runs CI: site render + link check, image build, and a container smoke
  test that also asserts the zero-logging guarantee.
- **`main`** is the release branch. Every push to `main` (direct or via
  merged PR) builds a new container and publishes it to GHCR:
  `ghcr.io/trueal82/transcortex.dev`, tagged `latest` plus the commit SHA.
- Dependabot keeps the GitHub Actions and the Docker base image current.

## License

[Apache-2.0](LICENSE) — with the exception of the bundled
[Inter font](assets/fonts/) and its [OFL license](assets/fonts/OFL.txt).
