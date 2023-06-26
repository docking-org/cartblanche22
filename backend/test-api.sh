#!/bin/bash

set -o errexit
set -o pipefail
set -m

celery -A cartblanche.run_celery.celery worker -P eventlet -l INFO -n worker &
pytest tests

fg %1
