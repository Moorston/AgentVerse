#!/usr/bin/env bash
set -euo pipefail

echo "==> Installing Python dependencies..."
uv sync

echo "==> Installing web dependencies..."
cd apps/web && npm install && cd ../..

echo "==> Setup complete!"