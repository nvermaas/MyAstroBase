"""
    File name: algorithms.py
    Author: Nico Vermaas
    Date created: 2019-11-13
    Description:  Business logic for AstroBase. These functions are called from the views (views.py).
"""
import logging
from ..models import Observation2

DATE_FORMAT = "%Y-%m-%d"
TIME_FORMAT = "%Y-%m-%d %H:%M:%SZ"
DJANGO_TIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"

logger = logging.getLogger(__name__)

def get_next_taskid(timestamp, taskid_postfix):
    """
    get the observation with a starttime closest to now.
    example url to directly access this function from the REST API:
    /astrobase/get_next_observation?my_status=scheduled&observing_mode=imaging
    :param timestamp: timestamp on which the taskid is based
    :param taskid_postfix: optional addition to the tasked, like 190405001_IMG
    :return: taskid
    """

    logger.info("get_next_taskid("+timestamp+")")

    count = 0
    while True:
        count += 1
        taskid = timestamp + str(count).zfill(3)  # 20180606001
        taskid = taskid[2:]  # 180606001

        # add an optional postfix, can be used to make pretty pipeline taskis' like 180905001_CAL
        if taskid_postfix != None:
            taskid = taskid + taskid_postfix  # 180606001_RAW

        # check if this taskid already exists. If it does, increase the counter and try again
        logger.info('checking taskid ' + str(taskid) + '..')
        found = Observation2.objects.filter(taskID=taskid).count()

        if found==0:
            return taskid

    return -1


# /astrobase/post_dataproducts?taskid=190405001
def add_dataproducts(taskID, dataproducts):
    """
    :param taskID: taskid of the observation
    :param dataproducts: json list of dataproducts to be added to the provided taskid
    :return:
    """
    number_of_dataproducts = len(dataproducts)
    logger.info("add_dataproducts("+taskID+','+str(number_of_dataproducts)+")")

    # get the common fields from the observation based on the given taskid
    parent = Observation2.objects.get(taskID=taskID)
    base_url = parent.derived_base_url

    for dp in dataproducts:
        # store the dataproduct in the observation

        if parent.size == None:
            parent.size = 0

        # depending on the dataproduct type
        type = dp['dataproduct_type']
        if type == 'raw':
            # do not store as field, because the raw dataproduct is derived from taskid in the model now
            parent.size = parent.size + int(dp['size'])

        if type == 'annotated':
            parent.annotated_image = dp['filename']
            parent.size = parent.size + int(dp['size'])

        if type == 'sky_plot':
            parent.sky_plot_image = dp['filename']
            parent.size = parent.size + int(dp['size'])

        if type == 'sky_globe':
            parent.sky_globe_image = dp['filename']
            parent.size = parent.size + int(dp['size'])

        if type == 'fits':
            parent.fits = dp['filename']
            parent.size = parent.size + int(dp['size'])

        if type == 'annotated_grid':
            parent.annotated_grid_image = dp['filename']
            parent.size = parent.size + int(dp['size'])

        if type == 'annotated_grid_eq':
            parent.annotated_grid_eq_image = dp['filename']
            parent.size = parent.size + int(dp['size'])

        if type == 'annotated_stars':
            parent.annotated_stars_image = dp['filename']
            parent.size = parent.size + int(dp['size'])

        if type == 'annotated_transient':
            parent.annotated_transient_image = dp['filename']
            parent.size = parent.size + int(dp['size'])

        if type == 'annotated_exoplanets':
            parent.annotated_exoplanets_image = dp['filename']
            parent.size = parent.size + int(dp['size'])

    parent.save()


