#!/bin/bash
set -euo pipefail

# Build the SQLite database
uv run build_db.py

# Clone datasette-lite
rm -rf /tmp/datasette-lite
git clone --depth 1 https://github.com/simonw/datasette-lite.git /tmp/datasette-lite

# Prepare _site directory
rm -rf _site
mkdir _site
cp terminal-bench.db _site/
cp /tmp/datasette-lite/index.html _site/datasette-lite.html
cp /tmp/datasette-lite/webworker.js _site/
cp /tmp/datasette-lite/app.css _site/

# Modify index.html to hard-code the database URL
sed -i.bak "s|const sqliteUrls = urlParams.getAll('url').map(fixUrl);|const sqliteUrls = ['/terminal-bench-analysis/terminal-bench.db'];|" _site/datasette-lite.html

# Hide custom loading while keeping the elements required by its event handlers
sed -i.bak 's/<form id="load-custom">/<form id="load-custom" hidden>/' _site/datasette-lite.html

# Remove Plausible analytics
sed -i.bak '/<script defer data-domain="lite.datasette.io"/d' _site/datasette-lite.html
sed -i.bak '/window.plausible = window.plausible/d' _site/datasette-lite.html

# Clean up .bak files from sed
rm -f _site/*.bak
cp _site/datasette-lite.html _site/index.html
