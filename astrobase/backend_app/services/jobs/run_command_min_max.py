import os
import logging;
import json
import datetime
import math

from ...models import Observation2, Job
from ...my_celery import app

logger = logging.getLogger(__name__)

def run_command_min_max(observation_id):
    # read min/max ra and dec from fits and store in database
    observation = Observation2.objects.get(id=observation_id)

    # parse the url into observation_dir and filenames
    path1 = observation.derived_fits.split('astrobase/data')[1].split('/')

    parameters = str(path1[1] + ',' + str(path1[2]))
    job = Job(command='box', job_service='celery', queue="celery", parameters=parameters, status="new")
    job.save()

    task = app.send_task("astro_tasks.tasks.handle_job", kwargs=dict(id=str(job.id)),queue="astro",
                         retry=True, retry_policy={
                                "max_retries": 3,
                                "interval_start": 0,
                                "interval_step": 1,
                                "interval_max": 5,
                            }
    )
