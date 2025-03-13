#!/bin/bash

set -o errexit
set -o pipefail
set -m

rabbitmq-server -detached &
celery -A cartblanche.run_celery.celery worker -l INFO -n worker --concurrency=40 &
celery -A cartblanche.run_celery.celery flower &
gunicorn  -b :5068 --worker-tmp-dir /tmp -w 12 --access-logfile - --error-logfile - application  --timeout 36000 --reload

fg %1
