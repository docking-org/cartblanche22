import os
from celery import Celery
from kombu import Queue
from config import Config

celery = Celery(__name__, 
                broker=Config.CELERY_BROKER_URL,
                backend=Config.CELERY_RESULT_BACKEND,
                result_extended=True,
                include=[
                           'cartblanche.data.tasks',
                           'cartblanche.data.tasks.search_smiles',
                           'cartblanche.data.tasks.search_zinc', 
                           'cartblanche.data.tasks.get_random', 
                         ]
                )

celery.conf.update(
    result_backend_transport_options=Config.CELERY_RESULT_BACKEND_TRANSPORT_OPTIONS,
    broker_transport_options=Config.CELERY_BROKER_TRANSPORT_OPTIONS,
)
# celery.conf.task_default_queue = 'default'
# celery.conf.task_queues = (
#     Queue('default',    routing_key='task.#'),
#     Queue('sw_tasks', routing_key='sw.#'),
# )
# celery.conf.task_default_exchange = 'tasks'
# celery.conf.task_default_exchange_type = 'topic'
# celery.conf.task_default_routing_key = 'task.default'
# celery.conf.task_routes = {
#     'cartblanche.data.tasks.search_smiles.sw_search':{
#         'queue': 'sw_tasks',
#         'routing_key': 'sw.search'
#     },
# }