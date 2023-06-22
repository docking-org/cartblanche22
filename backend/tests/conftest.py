import pytest
from cartblanche import celery 
from cartblanche.app import create_app
from cartblanche.celery_worker import init_celery
from flask.testing import FlaskClient

#pytests for flask app. also creates a celery app for taking tasks

@pytest.fixture(scope='session')
def flask_app_client():
    app = create_app(__name__)
    return app.test_client()

