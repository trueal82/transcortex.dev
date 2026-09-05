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
- External links (Calendly, LinkedIn, n8n, the founder's blog) are enforced
  via an exact-hostname allowlist in `.github/check-site.py` — any other
  external URL or mailto address fails CI.

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
| `/ueber-mich/`           | `/en/about/`           |
| `/impressum/`           | `/en/imprint/`         |
| `/datenschutz/`         | `/en/privacy/`         |

The retired `/team/` and `/en/team/` routes 301-redirect to `/ueber-mich/`
and `/en/about/` (see `nginx/default.conf`).

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