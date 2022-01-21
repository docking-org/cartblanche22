#!/bin/bash
  
set -m

gunicorn  -b :5001 -w 5 --log-level=DEBUG --access-logfile - --error-logfile - application:application  --timeout 0 --reload &
celery -A app.data.tasks.search_zinc worker -l INFO --concurrency=10
  
fg %1