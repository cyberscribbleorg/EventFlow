#!/bin/sh

NUMBER_OF_WORKERS=${INJECTOR_NUMBER_OF_WORKERS:-2}
CONCURRENCY=${INJECTOR_CONCURRENCY:-1}

for i in $(seq 1 $NUMBER_OF_WORKERS); do
    celery -A celery_app worker --loglevel=info -Q high_priority -c $CONCURRENCY -n workerh$i &
done

celery -A celery_app worker --loglevel=info -Q default -c $CONCURRENCY -n workerd1 &
celery -A celery_app worker --loglevel=info -Q default -c $CONCURRENCY -n workerd2 &

celery -A celery_app worker --loglevel=info -Q low_priority -c $CONCURRENCY -n workerl1 &

wait