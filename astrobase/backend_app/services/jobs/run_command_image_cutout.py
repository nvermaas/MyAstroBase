import os
import logging;
import json
import datetime
import math

from ...models import Observation2, Job, Cutout, CutoutDirectory
from ...my_celery import app

logger = logging.getLogger(__name__)

def run_command_image_cutout(params):
    '''
    crop all images on a coordinate with a given size
    # http://localhost:8000/my_astrobase/run-command/?command=image_cutout&params=84,10,1,my_target,500
    '''

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
    observations = Observation2.objects.filter(ra_min__lte=search_ra) \
        .filter(ra_max__gte=search_ra) \
        .filter(dec_min__lte=search_dec) \
        .filter(dec_max__gte=search_dec).order_by('-date')

    my_observations = list(observations)

    # ...or that have the center of the image less than 1 field_of_view away from the search coordinate
    for o in Observation2.objects.all():
        dx = o.field_ra - search_ra
        dy = o.field_dec - search_dec
        distance = math.sqrt(dx ** 2 + dy ** 2)
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
            output_filename = os.path.join(directory, filename)

            parameters = str(parameter_fits[1]) + ',' + str(parameter_fits[2]) + ',' + str(
                parameter_input[2]) + ',' + output_filename
            job = Job(command='image_cutout', job_service='celery', queue='celery', parameters=parameters, extra=params,
                      status="new")

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
                    directory=directory,
                    filename=filename,
                    field_name=field_name,
                    field_ra=search_ra,
                    field_dec=search_dec,
                    field_fov=field_of_view,
                    cutout_size=size_in_pixels,
                    observation_date=observation.date,
                    observation_name=observation.name,
                    observation_taskID=observation.taskID,
                    observation_quality=observation.quality,
                    visible=False,
                    status="job_created"
                )

            # update the cutout_directory with the latest filename
            cutout_directory.thumbnail = cutout.derived_url
            cutout_directory.save()

            cutout.save()

            # cutout is saved, dispatch the job by saving it
            job.save()

            # trigger the job in celery
            task = app.send_task("astro_tasks.tasks.handle_cutout", kwargs=dict(id=str(job.id)), queue="cutout",
                         retry=True, retry_policy={
                                "max_retries": 3,
                                "interval_start": 0,
                                "interval_step": 1,
                                "interval_max": 5,
                            }
    )

        except Exception as error:
            print(f'failed to create job: {error}')

