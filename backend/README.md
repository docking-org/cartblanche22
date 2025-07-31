# Setup CB's backend for development

## Conda environment

`conda create env -f environment.yml`

## Start Flask

`gunicorn  -b :5000 -w 3 --log-level=DEBUG --access-logfile - --error-logfile - application  --timeout 36000 --reload`

NOTE: If port is already in use, change 5000 to something else

## Start Celery

`celery -A cartblanche.run_celery.celery worker -l INFO -n worker3 --concurrency=5`
