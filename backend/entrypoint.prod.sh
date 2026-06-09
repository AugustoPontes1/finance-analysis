#!/bin/bash
set -e

echo "Waiting for PostgreSQL..."
while ! nc -z "$DB_HOST" "$DB_PORT"; do
  sleep 1
done

echo "Running migrations..."
python manage.py migrate --noinput

echo "Starting Gunicorn (ASGI/uvicorn workers)..."
exec gunicorn configs.asgi:application \
  -k uvicorn.workers.UvicornWorker \
  -w "${GUNICORN_WORKERS:-4}" \
  --bind "0.0.0.0:${DJANGO_APP_PORT:-8080}" \
  --timeout 120 \
  --keep-alive 5 \
  --log-level info \
  --access-logfile - \
  --error-logfile -
