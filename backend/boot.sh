#!/bin/bash

set -o errexit
set -o pipefail
set -m

export RABBITMQ_NODENAME=rabbit@localhost
rabbitmq-server -detached &

until rabbitmqctl status > /dev/null 2>&1; do
    echo "Waiting for RabbitMQ..."
    sleep 2
done
echo "RabbitMQ is ready"

celery -A cartblanche.run_celery.celery worker -l INFO -n worker --concurrency=30 2>&1 | tee -a /tmp/worker.log &
celery -A cartblanche.run_celery.celery flower 2>&1 | tee -a /tmp/flower.log &
gunicorn  -b :${PORT:-5068} --worker-tmp-dir /dev/shm -w 12 application  --timeout 36000 --reload 2>&1 | tee -a /tmp/gunicorn.log

fg %1
