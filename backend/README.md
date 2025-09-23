# Setup Cartblanche instance for development

NOTE: It is recommended to run the development instance inside the cluster, otherwise you will need to manually tunnel every tin machines.

## Setup backend
### Step 1: Install backend dependecies


`conda env create -f environment.yml`

To enable cartblanche's conda environment: `conda activate cb-env`</br>
To disable cartblanch's conda environment: `conda deactivate`

### Step 2: Start Flask app

`gunicorn  -b :5000 -w 3 --log-level=DEBUG --access-logfile - --error-logfile - application  --timeout 36000 --reload`

NOTE: If port is already in use, change 5000 to something else

### Step 3: Setup Celery

If Celery is not already install in the server

`celery -A cartblanche.run_celery.celery worker -l INFO -n worker3 --concurrency=5`

## Setup React app

