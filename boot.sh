#!/bin/sh
exec gunicorn -b :5000 -w 5 --access-logfile - --error-logfile - application:application --timeout 0 &
exec redis-server & 
exec celery -A app.data.tasks.search_zinc worker -l INFO --autoscale=20,3 & 


fg %1