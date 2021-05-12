#!/bin/sh
exec gunicorn -b :5000 -w 30 --access-logfile - --error-logfile - application:application --timeout 0