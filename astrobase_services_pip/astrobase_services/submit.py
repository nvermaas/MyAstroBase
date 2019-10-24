"""
    File name: submit.py
    Author: Nico Vermaas
    Date created: 2019-10-23
    Description: - submit job to astrometry.net
"""
ASTROMETRY_URL = "http://nova.astrometry.net"
ASTROMETRY_API = "http://nova.astrometry.net/api/"
ASTROMETRY_API_KEY = "otrkmikbckoopfje"

import os
import platform
from datetime import datetime
import requests,json
import urllib.request

from astrobase_services.astrometry_client import Client

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


def get_job_id(submission_id):

    client = Client(apiurl=ASTROMETRY_API)
    client.login(apikey=ASTROMETRY_API_KEY)
    submission_result = client.sub_status(submission_id, justdict=True)
    print("submission_result :" + str(submission_result))

    try:
        job_id = str(submission_result['jobs'][0])
        return job_id
    except:
        return None


def get_job_results(astrobaseIO, job_id, justdict):
    """
    {'objects_in_field':
        ['The star 61Leo', 'The star υ2Hya', 'The star φLeo', 'The star υ1Hya',
         'The star γCrt', 'The star Alkes (αCrt)', 'The star μHya', 'The star λHya',
         'The star δCrt', 'The star νHya', 'Part of the constellation Hydra (Hya)',
         'Part of the constellation Crater (Crt)'],
     'machine_tags':
        ['The star 61Leo', 'The star υ2Hya', 'The star φLeo', 'The star υ1Hya', 'The star γCrt',
         'The star Alkes (αCrt)', 'The star μHya', 'The star λHya', 'The star δCrt', 'The star νHya',
         'Part of the constellation Hydra (Hya)', 'Part of the constellation Crater (Crt)'],
     'status': 'success',
     'tags':
        ['The star 61Leo', 'The star υ2Hya', 'The star φLeo', 'The star υ1Hya',
         'The star γCrt', 'The star Alkes (αCrt)', 'The star μHya', 'The star λHya',
         'The star δCrt', 'The star νHya', 'Part of the constellation Hydra (Hya)',
         'Part of the constellation Crater (Crt)'],
     'calibration':
            {'orientation': 180.47305689878488,
            'dec': -11.294944542800003,
            'pixscale': 541.8204596987174,
            'radius': 20.721878048048463,
            'parity': 1.0,
            'ra': 166.270006359},
            'original_filename': 'SouthPoleTransformed/1565.png'
            }

    :param job_id:
    :return:
    """
    # astrobaseIO.report("---- get_job_results(" + str(job_id) + ")", "print")
    # login to astrometry with the API_KEY
    client = Client(apiurl=ASTROMETRY_API)
    client.login(apikey=ASTROMETRY_API_KEY)

    result = client.job_status(job_id, justdict=justdict)
    return result


def get_submission(astrobaseIO, submission_id):
    """
    check of the pipeline at astrometry is done processing the submitted image
    :param submission_id:
    :return:
    """
    # login to astrometry with the API_KEY
    astrobaseIO.report("---- get_submission(" + submission_id + ")", "print")

    client = Client(apiurl=ASTROMETRY_API)
    client.login(apikey=ASTROMETRY_API_KEY)

    result = client.sub_status(submission_id, justdict=True)
    return result

#-------------------------------------------------------------------------------------
def do_submit_jobs(astrobaseIO, local_data_url, local_data_dir):

    def submit_job_to_astrometry(path_to_file):
        """
        http://astrometry.net/doc/net/api.html
        :param path_to_file:
        :return:
        """
        astrobaseIO.report("-- submit_job_to_astrometry(" + path_to_file + ")", "print")
        # login to astrometry with the API_KEY
        client = Client(apiurl=ASTROMETRY_API)
        client.login(apikey=ASTROMETRY_API_KEY)

        result = client.upload(fn=path_to_file)

        #url = local_data_url + "/" + filename
        #url = "http://localhost/cetus.jpg"
        #url = "http://uilennest.net/static/astrobase/cetus.jpg"
        #result = client.url_upload(url=url)

        print(result)
        job = result['subid']
        job_status = result['status']
        return job, job_status

    # --- start of function body ---

    STATUS_START = "pending"
    STATUS_END = "submitted"

    taskIDs = astrobaseIO.astrobase_interface.do_GET_LIST(key='observations:taskID', query='my_status=' + STATUS_START)
    if len(taskIDs) > 0:
        astrobaseIO.report("-- do_submit_jobs()", "print")

        # loop through the 'processing' observations
        for taskID in taskIDs:

            astrobaseIO.astrobase_interface.do_PUT(key='observations:new_status', id=None, taskid=taskID, value="submitting")

            # find the raw dataproducts
            ids = astrobaseIO.astrobase_interface.do_GET_LIST(key='dataproducts:id', query='taskID=' + taskID + '&dataproduct_type=raw')
            for id in ids:
                # retrieve the raw image
                filename = astrobaseIO.astrobase_interface.do_GET(key='dataproducts:filename', id=id, taskid=None)
                directory = os.path.join(local_data_dir,taskID)
                path_to_file = os.path.join(directory,filename)

                astrobaseIO.report("*processor* : processing " + filename, "slack")

                # do the magic!
                # when using files
                submission_id, submission_status = submit_job_to_astrometry(path_to_file)

                # when using urls
                #submission_id, submission_status = submit_job_to_astrometry(filename)

                if submission_status=="success":
                    # write the current job to the observation.
                    astrobaseIO.astrobase_interface.do_PUT(key='observations:job', id=None, taskid=taskID, value=submission_id)

                    # when all raw dps have been processed, put observation to 'processed'.
                    astrobaseIO.astrobase_interface.do_PUT(key='observations:new_status', id=None, taskid=taskID, value="submitted")
                    astrobaseIO.report("*processor* : submitted job " + str(submission_id) + " for " + taskID + " " + STATUS_END,"slack")
                else:
                    astrobaseIO.astrobase_interface.do_PUT(key='observations:new_status', id=None, taskid=taskID, value="failed submitting")
                    astrobaseIO.report("*processor* : submitted job " + str(submission_id) + " for " + taskID + " failed.","slack")

#-------------------------------------------------------------------------------------
def do_check_submission_status(astrobaseIO):

    def check_submission_status(submission_id):
        """
        check of the pipeline at astrometry is done processing the submitted image
        :param submission_id:
        :return:
        """
        # astrobaseIO.report("-- check_submission_status("+ submission_id + ")", "print")

        try:
            job_id = get_job_id(submission_id)
            job_results = get_job_results(astrobaseIO, job_id, False)
            print("job_results: " + str(job_results))
            if job_results['job']['status']=='success':
                return 'success'
            if job_results['job']['status']=='failure':
                return 'failure'
        except:
            return 'unfinished'
        return "unknown"

    # --- start of function body ---

    STATUS_START = "submitted"
    query = 'my_status__in='+STATUS_START
    taskIDs = astrobaseIO.astrobase_interface.do_GET_LIST(key='observations:taskID', query=query)
    if len(taskIDs) > 0:
        astrobaseIO.report("-- do_check_submission_status()", "print")

        # loop through the 'submitted' and check for the success status
        for taskID in taskIDs:
            # astrobaseIO.astrobase_interface.do_PUT(key='observations:new_status', id=None, taskid=taskID, value="processing")

            # get the astrometry submission_id to check
            submission_id = astrobaseIO.astrobase_interface.do_GET(key='observations:job', id=None, taskid=taskID)
            job_status = check_submission_status(submission_id)
            astrobaseIO.report("*processor* : status of job " + submission_id + " = " + job_status, "print")

            if job_status == 'success':
                astrobaseIO.astrobase_interface.do_PUT(key='observations:new_status', id=None,taskid=taskID,value="processed")
            if job_status == 'failure':
                astrobaseIO.astrobase_interface.do_PUT(key='observations:new_status', id=None,taskid=taskID,value="failed")


# --- Main Service -----------------------------------------------------------------------------------------------

def do_submit(astrobaseIO, local_data_url, local_data_dir):
    #astrobaseIO.report("- do_submit()", "print")

    # submit new jobs to astrometry.net
    do_submit_jobs(astrobaseIO,local_data_url, local_data_dir)

    # check if the job is ready and handle results on success.
    do_check_submission_status(astrobaseIO)

