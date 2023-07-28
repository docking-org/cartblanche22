from celery import Celery


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
