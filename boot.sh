#!/bin/sh
exec gunicorn -b :5000 -w 4 --access-logfile - --error-logfile - application:application --timeout 0