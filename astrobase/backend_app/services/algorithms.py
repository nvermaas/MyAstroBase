"""
    File name: algorithms.py
    Author: Nico Vermaas
    Date created: 2019-11-13
    Description:  Business logic for AstroBase. These functions are called from the views (views.py).
"""
import time
import datetime
import logging
from .common import timeit
from ..models import Observation, DataProduct

DATE_FORMAT = "%Y-%m-%d"
TIME_FORMAT = "%Y-%m-%d %H:%M:%SZ"
DJANGO_TIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"

logger = logging.getLogger(__name__)

def get_delta_in_minutes(timestamp1,timestamp2):
    """
    return minutes between 2 dates
    :param timestamp1:
    :param timestamp2:
    :return:
    """
    date1 = datetime.datetime.strptime(timestamp1, TIME_FORMAT)
    date2 = datetime.datetime.strptime(timestamp2, TIME_FORMAT)
    minutes = (date2 - date1).total_seconds() / 60.0
    return int(minutes)



@timeit
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
        found = Observation.objects.filter(taskID=taskid).count()

        if found==0:
            return taskid

    return -1


# /astrobase/post_dataproducts?taskid=190405001
@timeit
def add_dataproducts(taskID, dataproducts):
    """
    :param taskID: taskid of the observation
    :param dataproducts: json list of dataproducts to be added to the provided taskid
    :return:
    """
    number_of_dataproducts = len(dataproducts)
    logger.info("add_dataproducts("+taskID+','+str(number_of_dataproducts)+")")

    # get the common fields from the observation based on the given taskid
    parent = Observation.objects.get(taskID=taskID)
    parent_data_location = parent.data_location

    for dp in dataproducts:
        new_status = dp.get('new_status','defined')
        data_location = dp.get('data_dir',parent_data_location)
        size = dp.get('size', 0)
        myDataProduct = DataProduct(taskID=taskID,
                                    dataproduct_type=dp['dataproduct_type'],
                                    data_location=data_location,
                                    filename=dp['filename'],
                                    name=dp['filename'],
                                    description=dp['filename'],
                                    task_type='dataproduct',
                                    new_status=new_status,
                                    parent=parent,
                                    size=dp['size'],
                                    )

        logger.info('addding dataproduct: '+str(myDataProduct))
        myDataProduct.save()


