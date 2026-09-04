import os
from celery import Celery

try:
    RABBITMQ_BROKER = os.environ['RABBITMQ_BROKER']
except:
    RABBITMQ_BROKER = "amqp://nvermaas:RaBbIt_2019@192.168.178.56:5672//"

print(f'connect to RABBITMQ_BROKER: {RABBITMQ_BROKER}')

app = Celery('my_celery',broker=RABBITMQ_BROKER)
app.conf.task_ignore_result = True

print(f'Celery conf: {app.conf} ')

app.conf.task_routes = {
    'astro_tasks.tasks.handle_cutout': {'queue': 'cutout'},
    'astro_tasks.tasks.*': {'queue': 'astro'},
    'dev_tasks.tasks.*': {'queue': 'dev_q'},
}

print(app.conf.task_routes)