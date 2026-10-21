#!/usr/bin/env bash
# Starts the app for the Playwright suite with a fresh database. Playwright runs this as its webServer
# when E2E_BASE_URL isn't set. The reset happens here because webServer starts before any test code runs.
set -euo pipefail

cd "$(dirname "$0")/.."

PYTHON="${PYTHON:-.venv/bin/python}"
PORT="${E2E_PORT:-8765}"
export DJANGO_SETTINGS_MODULE=eypstats.e2e

mkdir -p e2e/.data
rm -rf e2e/.data/media

if [ -z "${DATABASE_URL:-}" ]; then
  rm -f e2e/.data/e2e.sqlite3
  "$PYTHON" manage.py migrate --no-input -v 0
else
  "$PYTHON" manage.py migrate --no-input -v 0
  "$PYTHON" manage.py flush --no-input -v 0
fi

"$PYTHON" manage.py collectstatic --no-input -v 0

# Keep-alive above Node fetch's 4 s, so the test runner never reuses a connection gunicorn has just closed.
exec "$PYTHON" -m gunicorn eypstats.wsgi \
  --bind "127.0.0.1:$PORT" \
  --workers "${E2E_SERVER_WORKERS:-2}" \
  --threads "${E2E_SERVER_THREADS:-4}" \
  --keep-alive 10 \
  --access-logfile - \
  --log-level warning
