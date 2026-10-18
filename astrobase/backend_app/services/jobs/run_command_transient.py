import os
import logging;
import json
import datetime
import math

from ...models import Observation2, Job
from transients_app.services import algorithms as transients_algorithms
from ...my_celery import app

logger = logging.getLogger(__name__)

def run_command_transient(observation_id):
    """"
    draw a transient (planet, comet or asteroid) on the raw image of an observation
    example: http://localhost:8000/my_astrobase/run-command?command=transient&observation_id=1305
    """

    observation = Observation2.objects.get(id=observation_id)

    if observation.transient == None:
        return "impossible"

    # construct objects to plot, and save them in the observation.extra field
    objects_to_plot = transients_algorithms.get_transients_as_json(observation.transient, observation.date)
    observation.extra = objects_to_plot
    observation.save()

    # parse the url into observation_dir and filenames
    parameter_fits = observation.derived_fits.split('astrobase/data')[1].split('/')
    parameter_input = observation.derived_annotated_image.split('astrobase/data')[1].split('/')
    parameter_output = observation.derived_annotated_image.split('astrobase/data')[1].split('/')

    parameters = str(parameter_fits[1]) + ',' + str(parameter_fits[2]) + ',' + str(parameter_input[2]) + ',' + str(
        parameter_output[2].replace(".", "_transient."))
    job = Job(command='transient', job_service='celery', queue="celery", parameters=parameters, extra=observation.extra,
              status="new")
    job.save()

    task = app.send_task("astro_tasks.tasks.handle_job", kwargs=dict(id=str(job.id)),queue="astro",
                         retry=True, retry_policy={
                                "max_retries": 3,
                                "interval_start": 0,
                                "interval_step": 1,
                                "interval_max": 5,
                            }
    )


def run_command_asteroids(observation_id):
    """"
    draw the brighest asteroids in the field of view of the image
    example: http://localhost:8000/my_astrobase/run-command?command=asteroids&observation_id=1208
    """

    observation = Observation2.objects.get(id=observation_id)

    # there may be a dedicated transient also... draw it
    if observation.transient:
        objects_to_plot = transients_algorithms.get_transients_as_json(observation.transient, observation.date)
        observation.extra = objects_to_plot
        observation.save()

    objects_to_plot = transients_algorithms.get_asteroids_as_json(observation)
    observation.extra = objects_to_plot
    observation.save()

    # parse the url into observation_dir and filenames
    parameter_fits = observation.derived_fits.split('astrobase/data')[1].split('/')
    parameter_input = observation.derived_annotated_image.split('astrobase/data')[1].split('/')
    parameter_output = observation.derived_annotated_image.split('astrobase/data')[1].split('/')

    parameters = str(parameter_fits[1]) + ',' + str(parameter_fits[2]) + ',' + str(parameter_input[2]) + ',' + str(
        parameter_output[2].replace(".", "_transient."))
    job = Job(command='asteroids', job_service='celery', queue="celery", parameters=parameters, extra=observation.extra,
              status="new")
    job.save()

    task = app.send_task("astro_tasks.tasks.handle_job", kwargs=dict(id=str(job.id)), queue="astro",
                         retry=True, retry_policy={
                                "max_retries": 3,
                                "interval_start": 0,
                                "interval_step": 1,
                                "interval_max": 5,
                            }
    )