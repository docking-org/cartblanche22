#!/bin/bash

set -o errexit
set -o pipefail
set -m

rabbitmq-server -detached &
celery -A cartblanche.run_celery.celery worker -l INFO -n worker --max-tasks-per-child=1 &
celery -A cartblanche.run_celery.celery flower &
gunicorn  -b :5068 -w 10 --log-level=DEBUG --access-logfile - --error-logfile - application  --timeout 36000 --reload --max-requests 3

fg %1
