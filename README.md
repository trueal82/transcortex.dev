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
- Placeholders in imprint/privacy pages are marked `TODO` and must be replaced
  with real legal data before going live.

## Site structure

| German (primary)        | English                |
|-------------------------|------------------------|
| `/`                     | `/en/`                 |
| `/team/`                | `/en/team/`            |
| `/impressum/`           | `/en/imprint/`         |
| `/datenschutz/`         | `/en/privacy/`         |