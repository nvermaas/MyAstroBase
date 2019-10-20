"""
    File name: service_do_data_monitor.py
    Author: Nico Vermaas
    Date created: 2019-10-14
    Description: - checks for new images in a given directory (_locallanding_pad)
                 - new images are then added as observation and dataproduct to the astrobase backend
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
from astrobase_services.specification import add_dataproducts

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
    astrobaseIO.report("---- get_job_results(" + job_id + ")", "print")
    # login to astrometry with the API_KEY
    client = Client(apiurl=ASTROMETRY_API)
    client.login(apikey=ASTROMETRY_API_KEY)

    result = client.job_status(job_id, justdict=justdict)
    return result


def get_submission(astrobaseIO, job_id):
    """
    check of the pipeline at astrometry is done processing the submitted image
    :param job_id:
    :return:
    """
    # login to astrometry with the API_KEY
    astrobaseIO.report("---- get_submission(" + job_id + ")", "print")

    client = Client(apiurl=ASTROMETRY_API)
    client.login(apikey=ASTROMETRY_API_KEY)

    result = client.sub_status(job_id, justdict=True)
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
    astrobaseIO.report("-- do_submit_jobs()", "print")
    STATUS_START = "pending"
    STATUS_END = "submitted"

    taskIDs = astrobaseIO.astrobase_interface.do_GET_LIST(key='observations:taskID', query='my_status=' + STATUS_START)
    if len(taskIDs) > 0:

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
        astrobaseIO.report("-- check_submission_status("+ submission_id + ")", "print")
        # login to astrometry with the API_KEY
        client = Client(apiurl=ASTROMETRY_API)
        client.login(apikey=ASTROMETRY_API_KEY)

        #submission_result = client.sub_status(submission_id, justdict=True)
        #print("submission_result :"+str(submission_result))
        job_results = get_job_results(astrobaseIO, submission_id, False)
        print("job_results: " +str(job_results))

        try:
            if job_results['job']['status']=='success':
                return 'success'
            if job_results['job']['status']=='failure':
                return 'failure'
        except:
            return 'unfinished'
        return "unknown"

    # --- start of function body ---
    astrobaseIO.report("-- do_check_submission_status()", "print")

    STATUS_START = "submitted"
    query = 'my_status__in='+STATUS_START
    taskIDs = astrobaseIO.astrobase_interface.do_GET_LIST(key='observations:taskID', query=query)
    if len(taskIDs) > 0:

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



#-------------------------------------------------------------------------------------
def do_handle_processed_jobs(astrobaseIO, local_data_dir):

    def do_handle_results(results):
        astrobaseIO.report("--- do_handle_results()", "print")
        try:

            # extract the pointing and store it in the observation
            astrobaseIO.astrobase_interface.do_PUT(key='observations:field_ra',id=None, taskid=taskID,
                                                   value=results['calibration']['ra'])
            astrobaseIO.astrobase_interface.do_PUT(key='observations:field_dec',id=None, taskid=taskID,
                                                   value=results['calibration']['dec'])
            astrobaseIO.astrobase_interface.do_PUT(key='observations:field_fov',id=None, taskid=taskID,
                                                   value=results['calibration']['radius'])

            # if the field_name is unknown, then use the first object found in the field
            field_name = astrobaseIO.astrobase_interface.do_GET(key='observations:field_name',id=None, taskid=taskID)
            if field_name=="unknown":
                objects_in_field = results['objects_in_field']['objects_in_field']
                field_name = objects_in_field[0]
                astrobaseIO.astrobase_interface.do_PUT(key='observations:name',id=None, taskid=taskID, value=field_name)
                astrobaseIO.astrobase_interface.do_PUT(key='observations:field_name', id=None, taskid=taskID, value=field_name)

            # construct url to worldwidetelescope
            # http://www.worldwidetelescope.org/webclient/default.aspx?wtml=http%3a%2f%2fwww.worldwidetelescope.org%2fwwtweb%2fShowImage.aspx%3freverseparity%3dFalse%26scale%3d37.331496%26name%3dorion.jpg%26imageurl%3dhttp%3a%2f%2fnova.astrometry.net%2fimage%2f7030698%26credits%3dAstrometry.net%2bUser%2b(All%2bRights%2bReserved)%26creditsUrl%3d%26ra%3d87.805840%26dec%3d5.311333%26x%3d767.9%26y%3d968.7%26rotation%3d147.92%26thumb%3dhttp%3a%2f%2fnova.astrometry.net%2fimage%2f7030704%26wtml%3dtrue
            return True
        except:
            print('ERROR in do_handle_results: no results yet, waiting a heartbeat...')
            return False


    def do_create_dataproducts(astrobase, taskid, submission_id, local_data_dir):
        astrobaseIO.report("--- do_create_dataproducts("+taskid+","+submission_id+")", "print")
        submission = get_submission(astrobase, submission_id)

        try:
            job_id = str(submission['job_calibrations'][0][0])
            skyplot_id = str(submission['job_calibrations'][0][1])
        except:
            print('job_calibrations has no data yet, waiting a heartbeat...')

            # check if there is something wrong with the job
            # job_results = get_job_results(submission_id, True)

            return False

        # create a directory per job to store all the results
        task_directory = os.path.join(local_data_dir, taskid)
        if not os.path.exists(task_directory):
            os.makedirs(task_directory)

        # retrieve images and store as dataproducts
        # http://nova.astrometry.net/sky_plot/zoom0/2390269
        url = ASTROMETRY_URL + "/sky_plot/zoom0/" + skyplot_id
        destination = os.path.join(task_directory, job_id + "_sky_globe.jpg")
        urllib.request.urlretrieve(url, destination)
        size = os.path.getsize(destination)
        dp1 = job_id + "_sky_globe.jpg" + ":sky_globe:ready:"+str(size)

        # http://nova.astrometry.net/sky_plot/zoom1/2390269
        url = ASTROMETRY_URL + "/sky_plot/zoom1/" + skyplot_id
        destination = os.path.join(task_directory, job_id + "_sky_plot.jpg")
        urllib.request.urlretrieve(url, destination)
        size = os.path.getsize(destination)
        dp2 = job_id + "_sky_plot.jpg" + ":sky_plot:ready:"+str(size)

        # http://nova.astrometry.net/annotated_full/3675324
        url = ASTROMETRY_URL + "/annotated_full/" + job_id
        destination = os.path.join(task_directory,job_id+"_annotated.jpg")
        urllib.request.urlretrieve(url,destination)
        size = os.path.getsize(destination)
        dp3 = job_id+"_annotated.jpg" + ":annotated:ready:"+str(size)

        # http://nova.astrometry.net/red_green_image_full/3675324
        url = ASTROMETRY_URL + "/red_green_image_full/" + job_id
        destination = os.path.join(task_directory,job_id+"_redgreen.jpg")
        urllib.request.urlretrieve(url,destination)
        size = os.path.getsize(destination)
        dp4 = job_id+"_redgreen.jpg" + ":redgreen:ready:"+str(size)

        # http://nova.astrometry.net/extraction_image_full/3675324
        url = ASTROMETRY_URL + "/extraction_image_full/" + job_id
        destination = os.path.join(task_directory,job_id+"_extraction.jpg")
        urllib.request.urlretrieve(url,destination)
        size = os.path.getsize(destination)
        dp5 = job_id+"_extraction.jpg" + ":extraction:ready:"+str(size)

        dataproducts = dp2 + "," + dp3+ "," + dp4+ "," + dp5
        add_dataproducts(astrobase, taskid, dataproducts)
        return True

    # --- start of function body ---
    astrobaseIO.report("-- do_handle_processed_jobs()", "print")

    STATUS_START = "processed,waiting"
    query = 'my_status__in='+STATUS_START

    taskIDs = astrobaseIO.astrobase_interface.do_GET_LIST(key='observations:taskID', query=query)
    if len(taskIDs) > 0:

        # loop through the 'processing' observations
        for taskID in taskIDs:
            # get the astrometry submission_id to check
            # astrobaseIO.astrobase_interface.do_PUT(key='observations:new_status', id=None, taskid=taskID, value="downloading")

            submission_id = astrobaseIO.astrobase_interface.do_GET(key='observations:job',id=None, taskid=taskID)
            results =  get_job_results(astrobaseIO, submission_id,False)
            astrobaseIO.report("*processor* : handle results of job " + submission_id, "slack")

            # parse the results and update the observation

            ok = do_handle_results(results)
            if (not ok):
                # results could not be found, doesn't matter, continue
                #astrobaseIO.astrobase_interface.do_PUT(key='observations:new_status', id=None, taskid=taskID, value="waiting")
                pass

            # download the created images as dataproducts
            ok = do_create_dataproducts(astrobaseIO, taskID, submission_id, local_data_dir)

            if (ok):
                astrobaseIO.astrobase_interface.do_PUT(key='observations:new_status', id=None, taskid=taskID, value="done")


# --- Main Service -----------------------------------------------------------------------------------------------

def do_processor(astrobaseIO, local_data_url, local_data_dir):
    astrobaseIO.report("- do_processor()", "print")

    # submit new jobs to astrometry.net
    do_submit_jobs(astrobaseIO,local_data_url, local_data_dir)

    # check if the job is ready and handle results on success.
    do_check_submission_status(astrobaseIO)

    # handle the results
    do_handle_processed_jobs(astrobaseIO, local_data_dir)
