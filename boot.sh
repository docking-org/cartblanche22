#!/bin/sh
exec gunicorn -b :5000 -w 2 --access-logfile - --error-logfile - application:application --timeout 0
