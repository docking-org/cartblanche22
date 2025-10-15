#!/bin/bash

set -o errexit
set -o pipefail
set -m

# rabbitmq-server -detached &
celery -A cartblanche.run_celery.celery worker -l INFO -n worker --concurrency=30 2>&1 | tee -a /tmp/worker.log &
celery -A cartblanche.run_celery.celery flower 2>&1 | tee -a /tmp/flower.log &
gunicorn  -b :5068 --worker-tmp-dir /dev/shm -w 12 application  --timeout 36000 --reload 2>&1 | tee -a /tmp/gunicorn.log

fg %1
