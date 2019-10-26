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
from astrobase_services.submit import get_submission, get_job_id


def get_fits_header(filename):

    fits_dict = {}
    with open(filename, "r") as fits_file:

        # read the file as a long line
        line = fits_file.readline()

        # split the long line in 80 character chunks
        n = 80
        chunks = [line[i:i + n] for i in range(0, len(line), n)]

        for chunk in chunks:
            try:
                # retrieve the key/value apier
                key,value_comment = chunk.split("=")

                # split off the comments from the value
                value,comment = value_comment.split("/")

                fits_dict[key.strip()]=value.strip()
            except:
                pass
        #print(str(fits_dict))
        return fits_dict



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
    # astrobaseIO.report("---- get_job_results(" + str(job_id) + ")", "print")
    # login to astrometry with the API_KEY
    client = Client(apiurl=ASTROMETRY_API)
    client.login(apikey=ASTROMETRY_API_KEY)

    result = client.job_status(job_id, justdict=justdict)
    return result



#-------------------------------------------------------------------------------------
def do_handle_processed_jobs(astrobaseIO, local_data_dir):

    def do_handle_results_obsolete(results):
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

        def add_dataproduct(job_id, sub_url,file_end, dataproduct_type):
            url = ASTROMETRY_URL + sub_url + job_id
            destination = os.path.join(task_directory, job_id + file_end)
            if not os.path.exists(destination):
                urllib.request.urlretrieve(url, destination)
                size = os.path.getsize(destination)
                dp = job_id + file_end + ":"+dataproduct_type+":ready:"+str(size)
                return "," + dp
            else:
                return ""

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
        dataproducts = ""

        url = ASTROMETRY_URL + "/sky_plot/zoom0/" + skyplot_id
        destination = os.path.join(task_directory, job_id + "_sky_globe.jpg")
        if not os.path.exists(destination):
            urllib.request.urlretrieve(url, destination)
            size = os.path.getsize(destination)
            dp = job_id + "_sky_globe.jpg" + ":sky_globe:ready:"+str(size)
            dataproducts = dataproducts + "," + dp

        # http://nova.astrometry.net/sky_plot/zoom1/2390269
        url = ASTROMETRY_URL + "/sky_plot/zoom1/" + skyplot_id
        destination = os.path.join(task_directory, job_id + "_sky_plot.jpg")
        if not os.path.exists(destination):
            urllib.request.urlretrieve(url, destination)
            size = os.path.getsize(destination)
            dp = job_id + "_sky_plot.jpg" + ":sky_plot:ready:"+str(size)
            dataproducts = dataproducts + "," + dp

        dataproducts = dataproducts + add_dataproduct(job_id,"/annotated_full/", "_annotated.jpg", "annotated")
        # dataproducts = dataproducts + add_dataproduct(job_id,"/red_green_image_full/", "_redgreen.jpg", "redgreen")
        # dataproducts = dataproducts + add_dataproduct(job_id,"/extraction_image_full/", "_extraction.jpg", "extraction")
        dataproducts = dataproducts + add_dataproduct(job_id,"/new_fits_file/", ".fits", str(job_id)+".fits")
        dataproducts = dataproducts + add_dataproduct(job_id,"/rdls_file/", "_rdls_file.fits", "nearby_stars_fits")
        dataproducts = dataproducts + add_dataproduct(job_id,"/wcs_file/", "_wcs_file.fits", "wcs_fits")
        dataproducts = dataproducts + add_dataproduct(job_id,"/axy_file/", "_axy_file.fits", "stars_fits")

        # if there are new dataproducts, then add them to the observation
        if dataproducts!='':
            # cut off the first ','
            add_dataproducts(astrobase, taskid, dataproducts[1:])


        # check if the wcs fitsfile exists to extract coordinates from
        # try to extract some metadata from the fits dataproduct
        fits_filename = os.path.join(task_directory, job_id + "_wcs_file.fits")
        if os.path.exists(fits_filename):
            fits_header = get_fits_header(fits_filename)
            ra = fits_header['CRVAL1']
            dec = fits_header['CRVAL2']

            astrobaseIO.astrobase_interface.do_PUT(key='observations:field_ra', id=None, taskid=taskid,
                                                   value=str(ra))
            astrobaseIO.astrobase_interface.do_PUT(key='observations:field_dec', id=None, taskid=taskid,
                                                   value=str(dec))
        return True


    # --- start of function body ---
    STATUS_START = "processed,waiting"
    query = 'my_status__in='+STATUS_START

    taskIDs = astrobaseIO.astrobase_interface.do_GET_LIST(key='observations:taskID', query=query)
    if len(taskIDs) > 0:
        astrobaseIO.report("-- do_handle_processed_jobs()", "print")

        # loop through the 'processing' observations
        for taskID in taskIDs:
            # get the astrometry submission_id to check
            # astrobaseIO.astrobase_interface.do_PUT(key='observations:new_status', id=None, taskid=taskID, value="downloading")

            submission_id = astrobaseIO.astrobase_interface.do_GET(key='observations:job',id=None, taskid=taskID)
            # job_id = get_job_id(submission_id)
            # results =  get_job_results(astrobaseIO, job_id, False)
            astrobaseIO.report("*processor* : handle results of job " + submission_id, "slack")

            # parse the results and update the observation

            #ok = do_handle_results(results)
            #if (not ok):
            #    # results could not be found, doesn't matter, continue
            #    #astrobaseIO.astrobase_interface.do_PUT(key='observations:new_status', id=None, taskid=taskID, value="waiting")
            #    pass

            # download the created images as dataproducts
            ok = do_create_dataproducts(astrobaseIO, taskID, submission_id, local_data_dir)

            if (ok):
                astrobaseIO.astrobase_interface.do_PUT(key='observations:new_status', id=None, taskid=taskID, value="done")


# --- Main Service -----------------------------------------------------------------------------------------------

def do_processor(astrobaseIO, local_data_url, local_data_dir):
    # astrobaseIO.report("- do_processor()", "print")

    # handle the results
    do_handle_processed_jobs(astrobaseIO, local_data_dir)
