from celery import Celery
from kombu import Queue

celery = Celery(__name__, 
                result_backend_transport_options={'master_name': 'cartblanche-master'},
                result_extended=True,
                include=[
                           'cartblanche.data.tasks',
                           'cartblanche.data.tasks.search_smiles',
                           'cartblanche.data.tasks.search_zinc', 
                           'cartblanche.data.tasks.get_random', 
                         ]
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
# celery.conf.broker_transport_options = { 'master_name': "cartblanche-master" }