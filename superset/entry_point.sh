#!/bin/bash
set -e

superset fab create-admin --username ${SUPERSET_ADMIN_USER} --firstname Superset --lastname Admin --email ${SUPERSET_ADMIN_EMAIL} --password ${SUPERSET_ADMIN_PASSWORD}
superset db upgrade
superset init
superset run -p ${SUPERSET_PORT} --with-threads -h 0.0.0.0
exec "$@"