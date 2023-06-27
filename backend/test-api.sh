set -o errexit
set -o pipefail
set -m

rabbitmq-server -detached &
redis-server &
celery -A cartblanche.run_celery.celery worker -P eventlet -l INFO -n worker &
pytest tests

fg %1
