#!/bin/bash
  
set -m

redis-server &
celery -A app.data.tasks.search_zinc worker -l INFO --concurrency=10 &
celery -A app.data.tasks.search_zinc flower --address=127.0.0.1 --port=5002 --broker=redis://localhost:6379/0 --result-backend=redis://localhost:6379/0 &
gunicorn  -b :5000 -w 5 --log-level=DEBUG --access-logfile - --error-logfile - application:application  --timeout 0 --reload
  
fg %1