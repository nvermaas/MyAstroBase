"""
Jobs contains the business logic for the different system jobs that have to be executed based on status changes
for Observations or DataProducts in AstroBase.
"""
import os
import logging;
import json
import datetime
import math

from ..models import Observation2, Job, Cutout, CutoutDirectory
from transients_app.services import algorithms as transients
from exoplanets.models import Exoplanet
from ..my_celery import app

logger = logging.getLogger(__name__)

def add_transient_to_job(observation):
    # create ephemeris for the transient
    # get the name of the transient and the timestamp for calculation
    objects_to_plot = transients.get_ephemeris_as_json(observation.transient,observation.date)

    observation.extra = objects_to_plot
    observation.save()


def add_exoplanets_to_job(observation):
    # create ephemeris for the transient
    objects_to_plot = transients.get_exoplanets_as_json(observation)

    observation.extra = objects_to_plot
    observation.save()


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
    task = app.send_task("astro_tasks.tasks.handle_job", kwargs=dict(id=str(job.id)))


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

    task = app.send_task("astro_tasks.tasks.handle_job", kwargs=dict(id=str(job.id)))


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

    task = app.send_task("astro_tasks.tasks.handle_job", kwargs=dict(id=str(job.id)))


def run_command_min_max(observation_id):
    # read min/max ra and dec from fits and store in database
    observation = Observation2.objects.get(id=observation_id)

    # parse the url into observation_dir and filenames
    path1 = observation.derived_fits.split('astrobase/data')[1].split('/')

    parameters = str(path1[1] + ',' + str(path1[2]))
    job = Job(command='box', job_service='celery', queue="celery", parameters=parameters, status="new")
    job.save()

    task = app.send_task("astro_tasks.tasks.handle_job", kwargs=dict(id=str(job.id)))


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

    task = app.send_task("astro_tasks.tasks.handle_job", kwargs=dict(id=str(job.id)))

def run_command_transient(observation_id):
    # draw a transient (planet, comet or asteroid) on the image

    observation = Observation2.objects.get(id=observation_id)

    if observation.transient == None:
        return "impossible"

    add_transient_to_job(observation)

    # parse the url into observation_dir and filenames
    parameter_fits = observation.derived_fits.split('astrobase/data')[1].split('/')
    parameter_input = observation.derived_annotated_image.split('astrobase/data')[1].split('/')
    parameter_output = observation.derived_annotated_image.split('astrobase/data')[1].split('/')

    parameters = str(parameter_fits[1]) + ',' + str(parameter_fits[2]) + ',' + str(parameter_input[2]) + ',' + str(
        parameter_output[2].replace(".", "_transient."))
    job = Job(command='transient', job_service='celery', queue="celery", parameters=parameters, extra=observation.extra,
              status="new")
    job.save()

    task = app.send_task("astro_tasks.tasks.handle_job", kwargs=dict(id=str(job.id)))


def run_command_exoplanets(observation_id):
    # draw a transient (planet, comet or asteroid) on the image

    observation = Observation2.objects.get(id=observation_id)

    add_exoplanets_to_job(observation)

    # parse the url into observation_dir and filenames
    parameter_fits = observation.derived_fits.split('astrobase/data')[1].split('/')
    parameter_input = observation.derived_annotated_image.split('astrobase/data')[1].split('/')
    parameter_output = observation.derived_annotated_image.split('astrobase/data')[1].split('/')

    parameters = str(parameter_fits[1]) + ',' + str(parameter_fits[2]) + ',' + str(parameter_input[2]) + ',' + str(
        parameter_output[2].replace(".", "_exoplanets."))
    job = Job(command='exoplanets', job_service='celery', queue="celery", parameters=parameters,
              extra=observation.extra, status="new")
    job.save()

    task = app.send_task("astro_tasks.tasks.handle_job", kwargs=dict(id=str(job.id)))


def dispatch_job(command, observation_id, params):
    # when 'queue' is specified in the Job object, then it will be picked up by Celery.
    # otherwise it will be picked up by the old pip instaled astrobase_services

    # test the 'astro' queue, which will be picked up by celery
    if command == "ping":
        job = Job(command='ping', job_service='celery', queue='celery', status="new")
        job.save()

    if command == "grid":
        run_command_grid(observation_id)

    if command == "grid_eq":
        run_command_grid_eq(observation_id)

    if command == "stars":
        run_command_stars(observation_id)

    if command == "min_max":
        run_command_min_max(observation_id)

    if command == "draw_extra":
        run_command_draw_extra(observation_id)

    if command == "transient":
        run_command_transient(observation_id)

    if command == "exoplanets":
        run_command_exoplanets(observation_id)


    # crop all images on a coordinate
    # http://localhost:8000/my_astrobase/run-command/?command=image_cutout&params=84,10,1
    if command == "image_cutout":
        # what cone to search for?
        cutout = params.split(',')
        directory = params.replace(',', '_')

        # which images contain this coordinate?
        search_ra = float(cutout[0].strip())
        search_dec = float(cutout[1].strip())
        field_of_view = float(cutout[2].strip())
        field_name = cutout[3]
        size_in_pixels = int(cutout[4])

        # if this cutout directory doesn't exist yet, then create it
        try:
            # cutout exists, update it
            cutout_directory = CutoutDirectory.objects.get(directory=directory)
            cutout_directory.status = 'job_recreated'

        except:
            # cutout doesn't exist, create it
            cutout_directory = CutoutDirectory(
                directory=directory,
                field_name=field_name,
                field_ra=search_ra,
                field_dec=search_dec,
                field_fov=field_of_view,
                status="job_created"
            )
        cutout_directory.save()

        # find all observations that have the search coordinate inside the image...
        observations = Observation2.objects.filter(ra_min__lte=search_ra)\
            .filter(ra_max__gte=search_ra)\
            .filter(dec_min__lte=search_dec)\
            .filter(dec_max__gte=search_dec).order_by('-date')

        my_observations = list(observations)

        # ...or that have the center of the image less than 1 field_of_view away from the search coordinate
        for o in Observation2.objects.all():
            dx = o.field_ra - search_ra
            dy = o.field_dec - search_dec
            distance = math.sqrt(dx ** 2 + dy **2)
            if distance < field_of_view:
                my_observations.append(o)
                print(o.name)

        # http://localhost:8000/my_astrobase/observations/?coordsearch=212,48
        for observation in my_observations:
            print(observation.derived_raw_image)

            try:

                # parse the url into observation_dir and filenames
                parameter_fits = observation.derived_fits.split('astrobase/data')[1].split('/')
                parameter_input = observation.derived_raw_image.split('astrobase/data')[1].split('/')

                # output tiles are named by their ra,dec,fov,taskID like 84_10_1_210101001.jpg
                filename = directory + '_' + str(observation.taskID) + '.jpg'
                output_filename = os.path.join(directory,filename)

                parameters = str(parameter_fits[1]) + ',' + str(parameter_fits[2]) + ',' + str(parameter_input[2]) + ',' + output_filename
                job = Job(command='image_cutout', job_service='celery', queue='celery', parameters=parameters, extra=params, status="new")

                # if this filename doesn't exist yet, then
                # create cutout object and add to database
                try:
                    # cutout exists, update it
                    cutout = Cutout.objects.get(filename=filename)
                    now = datetime.datetime.utcnow()
                    cutout.creationTime = now
                    cutout.status = 'job_recreated'

                except:
                    # cutout doesn't exist, create it
                    cutout = Cutout(
                        directory= directory,
                        filename = filename,
                        field_name = field_name,
                        field_ra = search_ra,
                        field_dec = search_dec,
                        field_fov = field_of_view,
                        cutout_size = size_in_pixels,
                        observation_date = observation.date,
                        observation_name = observation.name,
                        observation_taskID = observation.taskID,
                        observation_quality = observation.quality,
                        visible = False,
                        status = "job_created"
                    )

                # update the cutout_directory with the latest filename
                cutout_directory.thumbnail = cutout.derived_url
                cutout_directory.save()

                cutout.save()

                # cutout is saved, dispatch the job by saving it
                job.save()

                # trigger the job in celery
                task = app.send_task("astro_tasks.tasks.handle_cutout", kwargs=dict(id=str(job.id)))

            except:
                print('failed to create job')


    return "dispatched"