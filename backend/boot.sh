#!/bin/bash

set -o errexit
set -o pipefail
set -m

rabbitmq-server -detached &
celery -A cartblanche.run_celery.celery worker -P eventlet -l INFO -n worker &
celery -A cartblanche.run_celery.celery worker flower &
pytest tests &
gunicorn  -b :5000 -w 40 --log-level=DEBUG --access-logfile - --error-logfile - application  --timeout 36000 --reload

fg %1
