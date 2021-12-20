#!/bin/bash
  
set -m

gunicorn -b :5000 -w 5 --access-logfile - --error-logfile - application:application --timeout 0 &
redis-server &
celery -A app.data.tasks.search_zinc worker -l INFO
  
fg %1


