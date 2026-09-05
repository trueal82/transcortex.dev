#!/usr/bin/env bash
# Build the transcortex.dev site image: render static HTML, then docker build.
set -euo pipefail
cd "$(dirname "$0")"

python3 build.py
docker build -t transcortex.dev:latest .

echo
echo "Image built: transcortex.dev:latest"
echo "Run: docker run -d --name transcortex -p 8080:8080 transcortex.dev:latest"