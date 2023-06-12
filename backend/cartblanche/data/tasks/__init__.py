from config import Config
import random
from cartblanche import celery

from celery import chord, signature, chain, group

@celery.task
def start_search_task(task, submission, callback=None, children=None, task_id_progress=None):
    if isinstance(task, list):
        tasks = []
        for i in task:
            tasks.append(signature(i))

        if callback:
            callback = signature(callback)
            if task_id_progress:
                tasks[0].set(task_id=str(task_id_progress))    
         
            task = chord(group(tasks))(callback)
            task.parent.save()            
                
            children = task.parent.children[0].id
        else:
            task = chain(tasks)()
    else:
        task = signature(task)
        task = task.apply_async()

    return({'id':task.id, 'submission':submission, 'zinc22progress': children or task_id_progress})
    


