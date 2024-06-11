# celery.py
from celery import Celery
from kombu import Exchange, Queue

app = Celery('tasks', broker='redis://redis:6379/0')

app.conf.task_queues = (
    Queue('high_priority', Exchange('high_priority'), routing_key='high_priority'),
    Queue('default', Exchange('default'), routing_key='default'),
    Queue('low_priority', Exchange('low_priority'), routing_key='low_priority'),
)

app.conf.task_routes = {
    'tasks.do_inject.do_inject': {'queue': 'high_priority'},
    'tasks.do_extract.do_extract': {'queue': 'default'},
    'tasks.do_harvest.do_harvest': {'queue': 'low_priority'},
}

app.conf.update(
    result_backend='redis://redis:6379/0',
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    timezone='UTC',
    enable_utc=True,
)


from tasks import do_harvest, do_inject, do_extract
app.autodiscover_tasks(['tasks'])