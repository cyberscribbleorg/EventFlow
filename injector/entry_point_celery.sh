#!/bin/sh

# Load environment variables or set default values
HIGH_PRIORITY_WORKERS=${INJECTOR_HIGH_PRIORITY_WORKERS:-3}
MEDIUM_PRIORITY_WORKERS=${INJECTOR_MEDIUM_PRIORITY_WORKERS:-2}
LOW_PRIORITY_WORKERS=${INJECTOR_LOW_PRIORITY_WORKERS:-1}
CONCURRENCY=${INJECTOR_WORKER_CONCURRENCY:-2}

for i in $(seq 1 $HIGH_PRIORITY_WORKERS); do
    celery -A celery_app worker --loglevel=info -Q high_priority -c $CONCURRENCY -n high_priority_worker$i &
done

for i in $(seq 1 $MEDIUM_PRIORITY_WORKERS); do
    celery -A celery_app worker --loglevel=info -Q default -c $CONCURRENCY -n default_worker$i &
done

for i in $(seq 1 $LOW_PRIORITY_WORKERS); do
    celery -A celery_app worker --loglevel=info -Q low_priority -c $CONCURRENCY -n low_priority_worker$i &
done

wait