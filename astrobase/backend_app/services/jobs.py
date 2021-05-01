"""
Jobs contains the business logic for the different system jobs that have to be executed based on status changes
for Observations or DataProducts in AstroBase.
"""

import logging;
import json
import datetime
from ..models import Observation, Job
from transients_app.services import algorithms as transients

logger = logging.getLogger(__name__)

def add_transient(observation):
    # create ephemeris for the transient
    # get the name of the transient and the timestamp for calculation
    transient = observation.transient

    timestamps = []
    timestamp = observation.date
    midnight = timestamp.replace(hour=0, minute=0, second=0)
    yesterday = midnight + datetime.timedelta(days=-1)
    tomorrow = midnight + datetime.timedelta(days=+1)
    tomorrow2 = midnight + datetime.timedelta(days=+2)
    tomorrow3 = midnight + datetime.timedelta(days=+3)

    timestamps.append(timestamp)
    timestamps.append(midnight)
    timestamps.append(yesterday)
    timestamps.append(tomorrow)
    timestamps.append(tomorrow2)
    timestamps.append(tomorrow3)

    list = []
    count = 0
    for t in timestamps:
        count += 1
        result = transients.get_asteroid(transient, t)
        designation = result['designation']

        line = {}

        line['ra'] = float(result['ra_decimal'])
        line['dec'] = float(result['dec_decimal'])
        if count == 1:
            line['label'] = designation
            line['shape'] = 'circle'
            line['size'] = 50
            line['color'] = 'yellow'
        else:
            line['label'] = str(t.day)
            line['shape'] = 'cross'
            line['size'] = 5
            line['color'] = 'red'

        list.append(line)

    extra = json.dumps(list)

    observation.extra = extra
    observation.save()


def dispatch_job(command, observation_id):

    # /my_astrobase/run-command/?command=grid&observation_id=2410
    # add a grid of 1 or 10 square degrees to the image
    if command == "grid":
        observation = Observation.objects.get(id=observation_id)

        # parse the url into observation_dir and filenames
        parameter_fits = observation.observation.derived_fits.split('astrobase/data')[1].split('/')

        # use annotated image as input image
        parameter_input = observation.observation.derived_annotated_image.split('astrobase/data')[1].split('/')
        parameter_output = observation.observation.derived_annotated_image.split('astrobase/data')[1].split('/')

        parameters = str(parameter_fits[1]) + ',' + \
                     str(parameter_fits[2]) + ',' + \
                     str(parameter_input[2]) + ','  + \
                     str(parameter_output[2].replace(".", "_grid.")) + ',' + \
                     observation.field_name.replace(',','#')

        print(parameters)
        job = Job(command='grid', parameters=parameters, status="new")
        job.save()


    # /my_astrobase/run-command/?command=grid&observation_id=2410
    # add a grid of 1 or 10 square degrees to the image and rotate the image to horizontal (equatorial)
    if command == "grid_eq":
        observation = Observation.objects.get(id=observation_id)

        # parse the url into observation_dir and filenames
        parameter_fits = observation.observation.derived_fits.split('astrobase/data')[1].split('/')

        # use annotated image as input image
        parameter_input = observation.observation.derived_annotated_image.split('astrobase/data')[1].split('/')
        parameter_output = observation.observation.derived_annotated_image.split('astrobase/data')[1].split('/')

        parameters = str(parameter_fits[1]) + ',' + \
                     str(parameter_fits[2]) + ',' + \
                     str(parameter_input[2]) + ','  + \
                     str(parameter_output[2].replace(".", "_grid.")) + ',' + \
                     observation.field_name.replace(',','#')

        parameters=parameters+',equatorial'
        job = Job(command='grid', parameters=parameters, status="new")
        job.save()

    # /my_astrobase/run-command/?command=stars&observation_id=2410
    # retrieve the stars from the fits that were used by astrometry.net,
    # and draw them with their magnitudes. (to get a feel of the limiting magnitude of the image)
    if command == "stars":
        observation = Observation.objects.get(id=observation_id)

        # parse the url into observation_dir and filenames
        parameter_fits = observation.observation.derived_fits.split('astrobase/data')[1].split('/')
        job_id = parameter_fits[2].split('.')

        parameters = str(parameter_fits[1] + ',' + str(job_id[0]))
        job = Job(command='stars', parameters=parameters, status="new")
        job.save()

    # read min/max ra and dec from fits and store in database
    if command == "min_max":
        observation = Observation.objects.get(id=observation_id)

        # parse the url into observation_dir and filenames
        path1 = observation.observation.derived_fits.split('astrobase/data')[1].split('/')

        parameters = str(path1[1] + ',' + str(path1[2]))
        job = Job(command='box', parameters=parameters, status="new")
        job.save()

    # update min/max ra and dec for all observations with a fits file
    # /my_astrobase/run-command?command=all_min_max (no longer used)
    if command == "all_min_max":
        # find all observations with a fits file, and create a min_max job for all of them
        #obs_with_fits = Observation.objects.filter(generated_dataproducts__dataproduct_type='fits')
        obs = Observation.objects.all()

        for observation in obs:
            try:
                path1 = observation.observation.derived_fits.split('astrobase/data')[1].split('/')
                parameters = str(path1[1] + ',' + str(path1[2]))
                job = Job(command='box', parameters=parameters, status="new")
                job.save()
                print('ok: ' + str(observation))
            except:
                print('failed: '+str(observation))

    # /my_astrobase/run-command/?command=draw_extra&observation_id=4131
    # the 'observation.extra' field contains instructions from what to draw.
    # the extra objects will be drawn on the 'annotated image'
    if command == "draw_extra":
        observation = Observation.objects.get(id=observation_id)

        # parse the url into observation_dir and filenames
        parameter_fits = observation.observation.derived_fits.split('astrobase/data')[1].split('/')
        parameter_input = observation.observation.derived_annotated_image.split('astrobase/data')[1].split('/')
        parameter_output = observation.observation.derived_annotated_image.split('astrobase/data')[1].split('/')

        parameters = str(parameter_fits[1]) + ',' + str(parameter_fits[2]) + ',' + str(parameter_input[2]) + ',' + str(parameter_output[2])
        job = Job(command='draw_extra', parameters=parameters, extra=observation.extra, status="new")
        job.save()


    # draw a transient (planet, comet or asteroid) on the image
    if command == "transient":
        observation = Observation.objects.get(id=observation_id)

        if observation.transient==None:
            return "impossible"

        add_transient(observation)

        # parse the url into observation_dir and filenames
        parameter_fits = observation.observation.derived_fits.split('astrobase/data')[1].split('/')
        parameter_input = observation.observation.derived_raw_image.split('astrobase/data')[1].split('/')
        parameter_output = observation.observation.derived_annotated_image.split('astrobase/data')[1].split('/')

        parameters = str(parameter_fits[1]) + ',' + str(parameter_fits[2]) + ',' + str(parameter_input[2]) + ',' + str(parameter_output[2].replace(".", "_transient."))
        job = Job(command='transient', parameters=parameters, extra=observation.extra, status="new")
        job.save()


    # kick off the hips generation (not currently in place)
    if command == "hips":
        job = Job(command='hips',status="new")
        job.save()

    return "dispatched"