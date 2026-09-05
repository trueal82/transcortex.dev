#!/usr/bin/env bash
# Local dev loop: rebuild site/ when sources change, serve it with
# Python's built-in HTTP server. Usage: ./dev.sh [port]  (default 1234)
set -euo pipefail
cd "$(dirname "$0")"

PORT="${1:-1234}"
INTERVAL=10
WATCH_DIRS="pages templates assets"

fingerprint() {
  find $WATCH_DIRS -type f -print0 | sort -z | xargs -0 shasum -a 256 | shasum -a 256
}

python3 build.py
python3 -m http.server "$PORT" --bind 127.0.0.1 --directory site &
SERVER_PID=$!
trap 'kill "$SERVER_PID" 2>/dev/null; exit' INT TERM

echo "Serving site/ at http://127.0.0.1:${PORT} (Ctrl+C to stop)"
echo "Watching ${WATCH_DIRS} for changes every ${INTERVAL}s"

open "http://127.0.0.1:${PORT}" 2>/dev/null || true

last=$(fingerprint)
while true; do
  sleep "$INTERVAL"
  current=$(fingerprint)
  if [ "$current" != "$last" ]; then
    echo "== change detected $(date +%H:%M:%S), rebuilding =="
    python3 build.py || echo "build FAILED — serving last good build"
    last=$current
  fi
done