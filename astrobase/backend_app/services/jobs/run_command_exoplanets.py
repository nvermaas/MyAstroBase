import os
import logging;
import json
import datetime
import math

from ...models import Observation2, Job
from transients_app.services import algorithms as transients_algorithms
from exoplanets.models import Exoplanet
from ...my_celery import app

logger = logging.getLogger(__name__)


def run_command_exoplanets(observation_id):
    """"
    draw exoplanet host stars on the raw image of an observation
    example: http://localhost:8000/my_astrobase/run-command?command=exoplanets&observation_id=1695
    """

    observation = Observation2.objects.get(id=observation_id)

    # construct objects to plot, and save them in the observation.extra field
    objects_to_plot = transients_algorithms.get_exoplanets_as_json(observation)
    observation.extra = objects_to_plot
    observation.save()

    # parse the url into observation_dir and filenames
    parameter_fits = observation.derived_fits.split('astrobase/data')[1].split('/')
    parameter_input = observation.derived_annotated_image.split('astrobase/data')[1].split('/')
    parameter_output = observation.derived_annotated_image.split('astrobase/data')[1].split('/')

    parameters = str(parameter_fits[1]) + ',' + str(parameter_fits[2]) + ',' + str(parameter_input[2]) + ',' + str(
        parameter_output[2].replace(".", "_exoplanets."))
    job = Job(command='exoplanets', job_service='celery', queue="celery", parameters=parameters,
              extra=observation.extra, status="new")
    job.save()

    task = app.send_task("astro_tasks.tasks.handle_job", kwargs=dict(id=str(job.id)), queue="astro",
                         retry=True, retry_policy={
                                "max_retries": 3,
                                "interval_start": 0,
                                "interval_step": 1,
                                "interval_max": 5,
                            }
    )
