#!/bin/bash
# wait-for-it.sh

set -e

host="$1"
shift
cmd="$@"

until PGPASSWORD=$DB_PASS psql -h "$host" -U "$DB_USER" -d "$DB_NAME" -c '\q'; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

>&2 echo "Postgres is up - executing command"
exec $cmd