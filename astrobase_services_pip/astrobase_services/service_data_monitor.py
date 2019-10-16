"""
    File name: service_do_data_monitor.py
    Author: Nico Vermaas
    Date created: 2019-10-14
    Description: - checks for new images in a given directory (_locallanding_pad)
                 - new images are then added as observation and dataproduct to the astrobase backend
"""

import os
import platform
from datetime import datetime
from service_specification import do_specification

def get_creation_date(path_to_file):
    """
    Try to get the date that a file was created, falling back to when it was
    last modified if that isn't possible.
    See http://stackoverflow.com/a/39501288/1709587 for explanation.
    """
    if platform.system() == 'Windows':
        return os.path.getmtime(path_to_file)
    else:
        stat = os.stat(path_to_file)
        try:
            return stat.st_birthtime
        except AttributeError:
            # We're probably on Linux. No easy way to get creation dates here,
            # so we'll settle for when its content was last modified.
            return stat.st_mtime




# --- Main Service -----------------------------------------------------------------------------------------------

def do_data_monitor(astrobaseIO, local_landing_pad, local_data_dir):

    # look for files in the 'landingpad' directory
    for dirpath, dirnames, filenames in os.walk(local_landing_pad, followlinks=True):
        for filename in filenames:
            path_to_file = os.path.join(dirpath, filename)
            name,ext = filename.split(".")
            size = os.path.getsize(path_to_file)

            # determine the creation date of the observation
            # for now, look at the file.
            # Later look at the exif data of the jpg. Which requires the platform dependent Pillow lib.
            ts = get_creation_date(path_to_file)
            creation_timestamp = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

            date_timestamp = datetime.fromtimestamp(ts).strftime("%Y%m%d")
            taskid = astrobaseIO.astrobase_interface.do_GET_NextTaskID(date_timestamp)

            # create a specification
            # add the new file as an Observation and a raw dataproduct
            dataproducts = filename+":raw:raw:"+str(size)
            do_specification(astrobaseIO,
                             taskid=taskid,
                             initial_status="raw",
                             field_name=name,
                             date=creation_timestamp,
                             observing_mode="unknown",
                             dataproducts=dataproducts
                             )


            # move the new file to the local_data_dir
            destination = os.path.join(local_data_dir,filename)
            os.rename(path_to_file, destination)

            astrobaseIO.report("*data_monitor* : added observation " + taskid, "slack")