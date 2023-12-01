#!/bin/bash

set -o errexit
set -o pipefail
set -m

rabbitmq-server -detached &
celery -A cartblanche.run_celery.celery worker -l INFO -n worker &
celery -A cartblanche.run_celery.celery flower &
gunicorn  -b :5068 --worker-tmp-dir /dev/shm -w 5 --threads=4 --worker-class=gthread --log-level=DEBUG --access-logfile - --error-logfile - application  --timeout 36000 --reload

fg %1
