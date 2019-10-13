"""
Jobs contains the business logic for the different system jobs that have to be executed based on status changes
for Observations or DataProducts in AstroBase.
"""

import logging;

logger = logging.getLogger(__name__)

def dispatchJob(myTaskObject, new_status):
    """
    Adds a job to the jobs table (or executes it directly)
    :param (in) myObject: Observation or Dataproduct that triggers the action
    :param (in) status: The status that triggers the action
    """
    # logger.info("*** dispatchJob(" + str(myTaskObject) + "," + str(new_status) + ") ***")

