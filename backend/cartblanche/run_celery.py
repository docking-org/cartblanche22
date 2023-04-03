from cartblanche import celery 
from cartblanche.app import create_app
from cartblanche.celery_worker import init_celery

app = create_app(__name__)
init_celery(app, celery)
