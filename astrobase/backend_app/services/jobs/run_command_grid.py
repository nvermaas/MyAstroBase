"""
Jobs contains the business logic for the different system jobs that have to be executed based on status changes
for Observations or DataProducts in AstroBase.
"""
import os
import logging;
import json
import datetime
import math

from ...models import Observation2, Job, Cutout, CutoutDirectory
from transients_app.services import algorithms as transients_algorithms
from exoplanets.models import Exoplanet
from ...my_celery import app

logger = logging.getLogger(__name__)

def run_command_grid(observation_id):
    # /my_astrobase/run-command/?command=grid&observation_id=2410
    # add a grid of 1 or 10 square degrees to the image

    observation = Observation2.objects.get(id=observation_id)

    # parse the url into observation_dir and filenames
    parameter_fits = observation.derived_fits.split('astrobase/data')[1].split('/')

    # use annotated image as input image
    parameter_input = observation.derived_annotated_image.split('astrobase/data')[1].split('/')
    parameter_output = observation.derived_annotated_image.split('astrobase/data')[1].split('/')

    parameters = str(parameter_fits[1]) + ',' + \
                 str(parameter_fits[2]) + ',' + \
                 str(parameter_input[2]) + ',' + \
                 str(parameter_output[2].replace(".", "_grid.")) + ',' + \
                 observation.field_name.replace(',', '#')

    print(parameters)
    job = Job(command='grid', job_service='celery', queue="celery", parameters=parameters, status="new")
    job.save()
    print(f"celery.send_task(astro_tasks.tasks.handle_job({job.id}))")
    task = app.send_task("astro_tasks.tasks.handle_cutout", kwargs={"id": str(job.id)},queue="astro",
                         retry=True, retry_policy={
                                "max_retries": 3,
                                "interval_start": 0,
                                "interval_step": 1,
                                "interval_max": 5,
                            }
    )


def run_command_grid_eq(observation_id):
    # /my_astrobase/run-command/?command=grid_eq&observation_id=2410
    # add a grid of 1 or 10 square degrees to the image and rotate the image to horizontal (equatorial)
    observation = Observation2.objects.get(id=observation_id)

    # parse the url into observation_dir and filenames
    parameter_fits = observation.derived_fits.split('astrobase/data')[1].split('/')

    # use annotated image as input image
    parameter_input = observation.derived_raw_image.split('astrobase/data')[1].split('/')
    parameter_output = observation.derived_raw_image.split('astrobase/data')[1].split('/')

    parameters = str(parameter_fits[1]) + ',' + \
                 str(parameter_fits[2]) + ',' + \
                 str(parameter_input[2]) + ',' + \
                 str(parameter_output[2].replace(".", "_grid.")) + ',' + \
                 observation.field_name.replace(',', '#')

    parameters = parameters + ',equatorial'
    job = Job(command='grid', job_service='celery', queue="celery", parameters=parameters, status="new")
    job.save()

    task = app.send_task("astro_tasks.tasks.handle_job", kwargs=dict(id=str(job.id)), queue="astro",
                         retry=True, retry_policy={
                                "max_retries": 3,
                                "interval_start": 0,
                                "interval_step": 1,
                                "interval_max": 5,
                            }
    )
