#!/bin/bash
  
set -m

mkdir -p /tmp/logs
celery -A app.data.tasks.search_zinc worker -l INFO --concurrency=30 --logfile=/tmp/logs/workerlog &
gunicorn  -b :5000 -w 10 --log-level=DEBUG --access-logfile - --error-logfile - application:application  --timeout 10 --reload
  
fg %1
