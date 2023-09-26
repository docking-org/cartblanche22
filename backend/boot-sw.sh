#!/bin/bash
  
set -m
celery -A cartblanche.run_celery.celery worker -l INFO -n sw-worker -Q sw_tasks &
fg %1
