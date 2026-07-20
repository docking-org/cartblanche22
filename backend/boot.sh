#!/bin/bash

set -o errexit
set -o pipefail
set -m


celery -A cartblanche.run_celery.celery worker -l INFO -n ${CELERY_WORKER_NAME:-worker} --concurrency=30 2>&1 | tee -a /tmp/worker.log &
celery -A cartblanche.run_celery.celery flower 2>&1 | tee -a /tmp/flower.log &
gunicorn  -b :${PORT:-5068} --worker-tmp-dir /dev/shm -w 12 application  --timeout 36000 --reload 2>&1 | tee -a /tmp/gunicorn.log

fg %1
