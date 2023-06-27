set -e

rabbitmq-server -detached &
redis-server &
celery -A cartblanche.run_celery.celery worker -P eventlet -l INFO -n worker &
pytest tests

fg %1
