"""
Jobs contains the business logic for the different system jobs that have to be executed based on status changes
for Observations or DataProducts in AstroBase.
"""

import logging;
from ..models import Observation, Job

logger = logging.getLogger(__name__)

def dispatch_job(command, observation_id):

    # /my_astrobase/run-command/?command=grid&observation_id=2410
    if command == "grid":
        observation = Observation.objects.get(id=observation_id)

        # parse the url into observation_dir and filenames
        path1 = observation.observation.derived_fits.split('astrobase/data')[1].split('/')
        path2 = observation.observation.derived_annotated_image.split('astrobase/data')[1].split('/')

        parameters = str(path1[1] + ',' + str(path1[2])) + ',' + str(path2[2]) + ',' + observation.field_name.replace(',','#')
        job = Job(command='grid', parameters=parameters, status="new")
        job.save()

    # /my_astrobase/run-command/?command=stars&observation_id=2410
    if command == "stars":
        observation = Observation.objects.get(id=observation_id)

        # parse the url into observation_dir and filenames
        path_to_fits = observation.observation.derived_fits.split('astrobase/data')[1].split('/')
        job_id = path_to_fits[2].split('.')

        parameters = str(path_to_fits[1] + ',' + str(job_id[0]))
        job = Job(command='stars', parameters=parameters, status="new")
        job.save()

    # read min/max ra and dec from fits and store in database
    if command == "min_max":
        observation = Observation.objects.get(id=observation_id)

        # parse the url into observation_dir and filenames
        path1 = observation.observation.derived_fits.split('astrobase/data')[1].split('/')

        parameters = str(path1[1] + ',' + str(path1[2]))
        job = Job(command='min_max', parameters=parameters, status="new")
        job.save()


    # update min/max ra and dec for all observations with a fits file
    # /my_astrobase/run-command?command=all_min_max
    if command == "all_min_max":
        # find all observations with a fits file, and create a min_max job for all of them
        #obs_with_fits = Observation.objects.filter(generated_dataproducts__dataproduct_type='fits')
        obs = Observation.objects.all()

        for observation in obs:

            try:
                path1 = observation.observation.derived_fits.split('astrobase/data')[1].split('/')
                parameters = str(path1[1] + ',' + str(path1[2]))
                job = Job(command='min_max', parameters=parameters, status="new")
                job.save()
                print('ok: ' + str(observation))
            except:
                print('failed: '+str(observation))


    return "dispatched"