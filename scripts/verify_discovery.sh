#!/usr/bin/env bash
set -euo pipefail
echo "Scanning for hard-coded hosts/ports (excluding legacy)…"
grep -RInE "(http|https)://[a-zA-Z0-9.-]+:[0-9]{2,5}" --exclude-dir=legacy --exclude-dir=.git --exclude-dir=docs/images . || true
echo "If matches appear outside env/discovery patterns, refactor to discovery."
