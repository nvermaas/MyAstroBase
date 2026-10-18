import os
import logging;
import json
import datetime
import math

from ...models import Observation2, Job
from ...my_celery import app

logger = logging.getLogger(__name__)
def run_command_draw_extra(observation_id):
    # /my_astrobase/run-command/?command=draw_extra&observation_id=4131
    # the 'observation.extra' field contains instructions from what to draw.
    # the extra objects will be drawn on the 'annotated image'
    observation = Observation2.objects.get(id=observation_id)

    # parse the url into observation_dir and filenames
    parameter_fits = observation.derived_fits.split('astrobase/data')[1].split('/')
    parameter_input = observation.derived_annotated_image.split('astrobase/data')[1].split('/')
    parameter_output = observation.derived_annotated_image.split('astrobase/data')[1].split('/')

    parameters = str(parameter_fits[1]) + ',' + str(parameter_fits[2]) + ',' + str(parameter_input[2]) + ',' + str(
        parameter_output[2])
    job = Job(command='draw_extra', job_service='celery', queue="celery", parameters=parameters,
              extra=observation.extra, status="new")
    job.save()

    task = app.send_task("astro_tasks.tasks.handle_job", kwargs=dict(id=str(job.id)),queue="astro",
                         retry=True, retry_policy={
                                "max_retries": 3,
                                "interval_start": 0,
                                "interval_step": 1,
                                "interval_max": 5,
                            }
    )