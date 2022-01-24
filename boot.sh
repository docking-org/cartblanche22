#!/bin/bash
  
set -m

redis-server &
celery -A app.data.tasks.search_zinc worker -l INFO --concurrency=10 &
gunicorn  -b :5000 -w 5 --log-level=DEBUG --access-logfile - --error-logfile - application:application  --timeout 0 --reload
  
fg %1