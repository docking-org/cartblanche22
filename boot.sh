#!/bin/bash
  
set -m

celery -A app.data.tasks.search_zinc worker -l INFO --concurrency=30 &
gunicorn  -b :5000 -w 10 --log-level=DEBUG --access-logfile - --error-logfile - application:application  --timeout 10 --reload
  
fg %1