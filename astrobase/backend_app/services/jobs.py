"""
Jobs contains the business logic for the different system jobs that have to be executed based on status changes
for Observations or DataProducts in AstroBase.
"""

import logging;
from ..models import Observation, Job

logger = logging.getLogger(__name__)

def dispatch_job(command, observation_id):

    if command == "grid":
        observation = Observation.objects.get(id=observation_id)

        # parse the url into observation_dir and filenames
        path1 = observation.observation.derived_fits.split('astrobase/data')[1].split('/')
        path2 = observation.observation.derived_annotated_image.split('astrobase/data')[1].split('/')

        parameters = str(path1[1] + ',' + str(path1[2])) + ',' + str(path2[2]) + ',' + observation.field_name.replace(',','#')
        job = Job(command='grid', parameters=parameters, status="new")
        job.save()

    # read min/max ra and dec from fits and store in database
    if command == "min_max":
        observation = Observation.objects.get(id=observation_id)

        # parse the url into observation_dir and filenames
        path1 = observation.observation.derived_fits.split('astrobase/data')[1].split('/')

        parameters = str(path1[1] + ',' + str(path1[2]))
        job = Job(command='min_max', parameters=parameters, status="new")
        job.save()

    return "dispatched"