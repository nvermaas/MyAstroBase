"""
Jobs contains the business logic for the different system jobs that have to be executed based on status changes
for Observations or DataProducts in AstroBase.
"""
import os
import logging;
import json
import datetime
import math

from ...models import Observation2, Job
from ...my_celery import app

logger = logging.getLogger(__name__)

def run_command_stars(observation_id):
    # /my_astrobase/run-command/?command=stars&observation_id=2410
    # retrieve the stars from the fits that were used by astrometry.net,
    # and draw them with their magnitudes. (to get a feel of the limiting magnitude of the image)

    observation = Observation2.objects.get(id=observation_id)

    # parse the url into observation_dir and filenames
    parameter_fits = observation.derived_fits.split('astrobase/data')[1].split('/')
    job_id = parameter_fits[2].split('.')

    parameters = str(parameter_fits[1] + ',' + str(job_id[0]))
    job = Job(command='stars', job_service='celery', queue="celery", parameters=parameters, status="new")
    job.save()

    task = app.send_task("astro_tasks.tasks.handle_job", kwargs=dict(id=str(job.id)),queue="astro",
                         retry=True, retry_policy={
                                "max_retries": 3,
                                "interval_start": 0,
                                "interval_step": 1,
                                "interval_max": 5,
                            }
    )

