#!/bin/bash
  
set -m

gunicorn -b :5000 -w 1 --access-logfile - --error-logfile - application:application --timeout 0 --reload &
celery -A app.data.tasks.search_zinc worker -l INFO --autoscale=6,4
  
fg %1


