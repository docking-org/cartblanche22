#!/bin/bash
  
set -m

rabbitmq-server -detached &
celery -A cartblanche.run_celery.celery worker -l INFO -n worker &
celery -A cartblanche.run_celery.celery worker flower &
gunicorn  -b :5000 -w 40 --log-level=DEBUG --access-logfile - --error-logfile - application  --timeout 36000 --reload

fg %1
