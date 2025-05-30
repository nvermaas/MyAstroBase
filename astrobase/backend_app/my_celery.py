import os
from celery import Celery

try:
    RABBITMQ_BROKER = os.environ['RABBITMQ_BROKER']
except:
    RABBITMQ_BROKER = "amqp://nvermaas:RaBbIt_2019@192.168.178.126:5672"

app = Celery('my_celery',backend='rpc://',broker=RABBITMQ_BROKER)
app.conf.task_routes = {
    'astro_tasks.tasks.*': {'queue': 'astro'},
    'astro_tasks.tasks.handle_cutout': {'queue': 'cutout'},
    'dev_tasks.tasks.*': {'queue': 'dev_q'},
}