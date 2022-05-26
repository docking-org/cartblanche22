#!/bin/bash
  
set -m

rabbitmq-server -detached &
celery -A app.data.tasks.search_zinc worker -l INFO --concurrency=120 &
gunicorn  -b :5000 -w 2 --log-level=DEBUG --access-logfile - --error-logfile - application:application  --timeout 36000 --reload
  
fg %1