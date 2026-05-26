#!/bin/sh
set -e

PORT="${PORT:-8000}"
WORKERS="${GUNICORN_WORKERS:-1}"
TIMEOUT="${GUNICORN_TIMEOUT:-300}"

echo "==> Collecte des fichiers statiques..."
python manage.py collectstatic --noinput

echo "==> Démarrage Gunicorn sur 0.0.0.0:${PORT} (workers=${WORKERS}, timeout=${TIMEOUT}s)"
exec gunicorn config.wsgi:application \
  --bind "0.0.0.0:${PORT}" \
  --workers "${WORKERS}" \
  --threads 2 \
  --timeout "${TIMEOUT}" \
  --access-logfile - \
  --error-logfile -
