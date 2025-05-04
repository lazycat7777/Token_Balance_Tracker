#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset

echo "Ожидание доступности базы данных PostgreSQL..."

until PGPASSWORD="$POSTGRES_PASSWORD" psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "SELECT 1" > /dev/null 2>&1; do
  echo "БД ещё не готова — ждём 1 секунду..."
  sleep 1
done

echo "База данных готова!"

echo "Запуск Django сервера..."
python -m uvicorn core.asgi:application --reload --host 0.0.0.0 --port 8000



