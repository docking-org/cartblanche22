#!/bin/bash
  
set -m
sudo rabbitmq-server -detached &
celery -A app.data.tasks.search_zinc worker -l INFO --concurrency 5 -n worker &
gunicorn  -b :5000 -w 2 --log-level=DEBUG --access-logfile - --error-logfile - application:application  --timeout 36000 --reload
  
fg %1