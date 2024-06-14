#!/bin/bash
set -e

superset fab create-admin --username ${SUPERSET_ADMIN_USER} --firstname Superset --lastname Admin --email ${SUPERSET_ADMIN_EMAIL} --password ${SUPERSET_ADMIN_PASSWORD}

superset db upgrade

superset init

superset run -p ${SUPERSET_PORT} --with-threads -h 0.0.0.0 &

check_superset() {
  curl -s -o /dev/null -w "%{http_code}" http://localhost:${SUPERSET_PORT}/health
}

echo "Waiting for Superset to start..."
while [ "$(check_superset)" != "200" ]; do
  sleep 5
done
echo "Superset is up and running!"

python /app/create_conn.py

wait