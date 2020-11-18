"""
Jobs contains the business logic for the different system jobs that have to be executed based on status changes
for Observations or DataProducts in AstroBase.
"""

import logging;
from ..models import Observation, Job

logger = logging.getLogger(__name__)

def dispatch_job(command, observation_id):

    if command == "fitsing":
        observation = Observation.objects.get(id=observation_id)

        # parse the url into observation_dir and filenames
        path1 = observation.observation.derived_fits.split('astrobase/data')[1].split('/')
        path2 = observation.observation.derived_annotated_image.split('astrobase/data')[1].split('/')

        parameters = str(path1[1] + ',' + str(path1[2])) + ',' + str(path2[2])
        job = Job(command='fitsing', parameters=parameters, status="new")
        job.save()

    return "dispatched"