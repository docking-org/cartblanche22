from celery import Celery


celery = Celery(__name__, 
                broker='redis://localhost:6379/0',
                backend='pyamqp://guest@localhost//',
                include=[
                           'cartblanche.data.tasks',
                           'cartblanche.data.tasks.search_smiles',
                           'cartblanche.data.tasks.search_zinc', 
                           'cartblanche.data.tasks.get_random', 
                         ]
                )
