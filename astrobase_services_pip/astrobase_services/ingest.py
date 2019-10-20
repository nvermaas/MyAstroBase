"""
    File name: ingest.py
    Author: Nico Vermaas
    Date created: 2019-10-14
    Description: - checks for new images or txt (meta data) files in a given directory (local_landing_pad)
                 - new images are then added as observation and dataproduct to the astrobase backend
"""

import os
import platform
import shutil
import json
from datetime import datetime
from astrobase_services.specification import do_specification

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

def do_ingest(astrobaseIO, local_landing_pad, local_data_dir):

    def create_metadata_json(filename, dirpath, name):
        """
        Create metadata json file for ingest
        :param filename:
        :param dirpath:
        :param name:
        :return:
        """
        path_to_json_file = os.path.join(dirpath, name) + ".json"
        path_to_image_file = os.path.join(dirpath, filename)
        ts = get_creation_date(path_to_image_file)
        creation_timestamp = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

        data = {}
        data['raw_image_file'] = filename
        data['name'] = name
        data['field_name'] = name
        data['field_ra'] = "0.0"
        data['field_dec'] = "0.0"
        data['field_fov'] = "0.0"
        data['date'] = creation_timestamp

        with open(path_to_json_file, 'w') as outfile:
            json.dump(data, outfile)


    def move_files(taskid, path_to_file):
        # create a directory for the dataproducts of this observation
        # /astrobase/data/<taskid>
        task_directory = os.path.join(local_data_dir, taskid)
        if not os.path.exists(task_directory):
            os.makedirs(task_directory)

        # create a raw directory (probably already exists)
        # /astrobase/data/raw
        raw_directory = os.path.join(local_data_dir, "raw")
        if not os.path.exists(raw_directory):
            os.makedirs(raw_directory)

        filename = os.path.basename(path_to_file)
        name, ext = filename.split(".")

        # move the original file to raw data directory
        raw_destination = os.path.join(raw_directory, filename)
        if os.path.isfile(raw_destination):
            os.remove(raw_destination)
        os.rename(path_to_file, raw_destination)

        # copy and rename the original new file to data directory
        new_filename=taskid + "_raw." + ext
        data_destination = os.path.join(task_directory, new_filename)
        shutil.copy2(raw_destination, data_destination)

        size = os.path.getsize(data_destination)
        return new_filename, size


    def ingest_from_metadata(dirpath,filename):
        """
        use the json metadata file to ingest the image and dataproducts
        :param dirpath:
        :param filename:
        :return:
        """

        path_to_json_file = os.path.join(dirpath, filename)

        with open(path_to_json_file) as json_file:
            data = json.load(json_file)
            raw_image_file = data['raw_image_file']

            observation_timestamp = datetime.strptime(data['date'],'%Y-%m-%d %H:%M:%S')
            date_timestamp = observation_timestamp.strftime("%Y%m%d")
            taskid = astrobaseIO.astrobase_interface.do_GET_NextTaskID(date_timestamp)

            # assume that the image file is in the current directory
            path_to_image_file = os.path.join(dirpath, raw_image_file)
            new_image_file, size = move_files(taskid, path_to_image_file)

            dataproducts = new_image_file + ":raw:raw:" + str(size)

            do_specification(astrobaseIO,
                             taskid=taskid,
                             initial_status="raw",
                             name=data['name'],
                             field_name=data['field_name'],
                             field_ra=data['field_ra'],
                             field_dec=data['field_dec'],
                             field_fov=data['field_fov'],
                             date=observation_timestamp,
                             observing_mode="unknown",
                             dataproducts=dataproducts
                             )

        # also move away the json file
        raw_directory = os.path.join(local_data_dir, "raw")
        raw_destination = os.path.join(raw_directory,name)+".json"
        if os.path.isfile(raw_destination):
            os.remove(raw_destination)
        os.rename(path_to_file, raw_destination)

        return taskid


    def ingest_from_image_obsolete(path_to_file):
        # determine the creation date of the observation
        # for now, look at the file.
        # Later look at the exif data of the jpg. Which requires the platform dependent Pillow lib.
        ts = get_creation_date(path_to_file)
        creation_timestamp = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

        date_timestamp = datetime.fromtimestamp(ts).strftime("%Y%m%d")
        taskid = astrobaseIO.astrobase_interface.do_GET_NextTaskID(date_timestamp)

        new_filename, size = move_files(taskid, path_to_file)

        # create a specification
        # add the new file as an Observation and a raw dataproduct
        dataproducts = new_filename + ":raw:raw:" + str(size)
        do_specification(astrobaseIO,
                         taskid=taskid,
                         initial_status="raw",
                         field_name=name,
                         date=creation_timestamp,
                         observing_mode="unknown",
                         dataproducts=dataproducts
                         )

        return taskid

    # --- start of function body ---
    # look for files in the 'landing_pad' directory

    for dirpath, dirnames, filenames in os.walk(local_landing_pad, followlinks=True):

        for filename in filenames:
            path_to_file = os.path.join(dirpath, filename)
            name,ext = filename.split(".")

            if ext == "json":
                taskid = ingest_from_metadata(dirpath,filename)
                astrobaseIO.report("*ingest* : added (metadata) observation " + taskid, "slack")
            else:
                # if there is an image file without an accompanying json metadata file
                # then create the metadata json
                path_to_json = os.path.join(dirpath,name)+'.json'
                if not os.path.isfile(path_to_json):

                    create_metadata_json(filename, dirpath,name)
                    astrobaseIO.report("*ingest* : created metadata for " + filename, "slack")

                    # metadata json file is created and will be picked up on the next heartbeat

                    #taskid = ingest_from_image(path_to_file)
                    #astrobaseIO.report("*ingest* : added (image) observation " + taskid, "slack")
