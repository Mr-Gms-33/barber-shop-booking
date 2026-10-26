#!/bin/sh
set -e
echo "Waiting for database and running migrations..."
i=0
until alembic upgrade head; do
  i=$((i + 1))
  if [ "$i" -ge 15 ]; then
    echo "Alembic failed after 15 attempts"
    exit 1
  fi
  echo "Retry $i/15..."
  sleep 3
done
echo "Starting API on port ${PORT:-8000}"
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
