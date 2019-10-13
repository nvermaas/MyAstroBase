"""
    File name: service_do_data_monitor.py
    Author: Nico Vermaas - Astron
    Date created: 2018-11-23
    Description: checks for completing observations. It then checks for all its defined dataproducts,
                 gathers their sizes, and finally puts the status to complete, incomplete 
                 (or completed when the skip_auto_ingest parameter was specified). 
                 During this operation, the status is briefly set to checking to prevent a race condition with itatdb)
"""

import os
import time

#STATUS_COMPLETING       = 'completing_sc4' # only works for this status
STATUS_COMPLETING       = 'completing'
STATUS_END              = 'valid'
STATUS_SKIP_AUTO_INGEST = 'completed'
STATUS_INCOMPLETE       = 'incomplete'
STATUS_CHECKING         = 'checking'
STATUS_DEFINED_DPS      = 'defined'
STATUS_VALID_DPS        = 'valid'
STATUS_INVALID_DPS      = 'invalid'

def get_size_local(atdb, filepath):
    """
    Get the size of a file (FITS) or directory (MS)
    dataproduct is locally searched through the filesystem
    :param atdb: instance of the atdb_interface
    :param filepath:
    :return: full path to search for (file or dir)
    """
    # get the size of the file (FITS) or directory (MS)
    if os.path.isfile(filepath):
        size = os.path.getsize(filepath)
    else:
        size = atdb.get_dir_size(filepath)
    return size


def get_size_remote(atdb, node, filepath):
    """
    Get the size of a file (FITS)
    dataproduct is remotely searched with a ssh command
    :param atdb: instance of the atdb_interface
    :param filepath: full path to search for (file or dir)
    """
    size = atdb.get_filesize_remote(node,filepath)
    return size


def translate_arts_filename(filename):
    """
    arts has hardcoded filenames like tabA.fits to tabL.fits. Reconstruct these filenames to find them.
    :param filename: filename from ATDB
    :return: arts_filename
    """
    # for science_mode=IAB every dataproduct has the same name: tabA.fits
    arts_filename = 'tabA.fits'

    try:
        # for science_mode=TAB, there are 12 different possible filenames, ranging from tabA.fits to tabL.fits
        # to make this algorithm more generic I check the filename itself, not the science_mode.

        # isolate the tab number
        i = filename.find('TAB') + 3
        j = filename.find('.fits')
        tab = filename[i:j]

        # translate the tab number to the character that is used by ARTS, 01 -> A, 02 -> B, ... , 12 -> L
        character = chr(64+int(tab))
        arts_filename = 'tab'+character+'.fits'

    except:
        # if this fails, then assume a non TAB observation and continue.
        pass

    return arts_filename

# --- Main Service -----------------------------------------------------------------------------------------------

def do_data_monitor(atdb):
    # get the list taskID of 'completed' observations

    task_end_status = STATUS_END

    # query = 'my_status='+STATUS_COMPLETING+'&observing_mode__icontains=' + atdb.obs_mode_filter
    query = 'my_status='+STATUS_COMPLETING+'&observing_mode__icontains=' + atdb.obs_mode_filter+'&data_location__icontains=' + atdb.host_filter

    taskIDs = atdb.atdb_interface.do_GET_LIST(key='observations:taskID', query=query)

    if len(taskIDs) > 0:
        atdb.report('*data_monitor* found the following '+STATUS_COMPLETING+' tasks : ' + str(taskIDs))

    # loop through the list of 'completed' observations and check if its 'defined' dataproducts have manifested
    for taskID in taskIDs:
        observing_mode = atdb.atdb_interface.do_GET(key='observations:observing_mode', id=None, taskid=taskID)

        atdb.atdb_interface.do_PUT(key='observations:new_status', id=None, taskid=taskID, value=STATUS_CHECKING)
        atdb.report("*data_monitor* : " + taskID + " " + STATUS_CHECKING,"slack")

        # should this observation be automatically ingested and removed? or is the skip flag set?
        skip_ingest = atdb.atdb_interface.do_GET(key='observations:skip_auto_ingest', id=None, taskid=taskID)
        if str(skip_ingest) == 'True':
            task_end_status = STATUS_SKIP_AUTO_INGEST

        ids = atdb.atdb_interface.do_GET_LIST(key='dataproducts:id', query='taskID=' + taskID + '&my_status='+STATUS_DEFINED_DPS)
        # atdb.report("ids = " + str(ids), "slack")

        for id in ids:

            # check if the file exists and get its size.
            # data_location = atdb.atdb_interface.do_GET(key='dataproducts:data_location', id=id, taskid=None)
            data_dir = atdb.atdb_interface.do_GET(key='dataproducts:data_location', id=id, taskid=None)

            # split off the host from the location
            # host should now always be onboard...
            try:
                _, data_location = data_dir.split(':')
            except:
                # ... just in case the host is not onboard
                data_location = data_dir

            try:
                filename = atdb.atdb_interface.do_GET(key='dataproducts:filename', id=id, taskid=None)
                filepath = os.path.join(data_location, filename)

                # If a cluster or remote machine is used (like for ARTS SC4) then the 'node' field has the value of
                # a remote machine. In that case the dataproducts on that remote machine are searched.
                # Otherwise the dataproducts are searched on the local machine.
                node = atdb.atdb_interface.do_GET(key='dataproducts:node', id=id, taskid=None)

                # get the size of the file (FITS) or directory (MS)
                if (node is None):
                    # dataproducts are local
                    atdb.report('checking dataproduct (local) ' + filepath + '...')
                    size = get_size_local(atdb, filepath)
                else:
                    # dataproducts are on a remote machine
                    #filename_arts = translate_arts_filename(filename)
                    #atdb.report('translate_arts_filename '+filename + ' -> '+filename_arts)

                    # copy the dataproduct remotely. This is currently the safest option as long as
                    # the ARTS4 scripts are not adjusted to use the ATDB metadata.
                    # atdb.report('copy_dataproduct_remote (' + filename_arts + ',' + filename + ')')
                    # atdb.copy_dataproduct_remote(node, data_location, filename_arts, filename)

                    # scp from remote to local works, but commented out because it is not needed (now).
                    #atdb.report('scp_dataproduct (' + filename + ',/home/vagrant/atdb-client/ff/' + filename + ')')
                    #atdb.scp_dataproduct(node, data_location, filename, '/home/vagrant/atdb-client/ff', filename)

                    # renaming a remote dataproduct works and is much faster than remote copy, to be used later?
                    # rename the dataproduct from tab?.fits to its expected filename (like ARTS190103001_CB19.fits)
                    #atdb.report('move_dataproduct_remote (' + filename_arts + ',' + filename + ')')
                    #atdb.move_dataproduct_remote(node, data_location, filename_arts, filename)

                    # check the filesize
                    atdb.report('checking dataproduct (remote on node '+node+') ' + filepath + '...')
                    size = get_size_remote(atdb, node, filepath)

                    # renaming a remote dataproduct works and is much faster than remote copy, to be used later?
                    # rename the dataproduct back to its original name (temporarily).
                    # atdb.report('move_dataproduct_remote (' + filename + ',' + filename_arts + ')')
                    # atdb.move_dataproduct_remote(node, data_location, filename, filename_arts)


                atdb.report('...size = ' + str(size))
                atdb.atdb_interface.do_PUT(key='dataproducts:size', id=id, taskid=None, value=size)

                # very simple validation functionality, just checking for file/dir size > 0 bytes.
                if int(size) > 0:
                    atdb.atdb_interface.do_PUT(key='dataproducts:new_status', id=id, taskid=None, value=STATUS_VALID_DPS)
                else:
                    atdb.atdb_interface.do_PUT(key='dataproducts:new_status', id=id, taskid=None, value=STATUS_INVALID_DPS)
                    atdb.report("ERROR by *data_monitor* : "+filepath+ " not found.","print,slack")
                    task_end_status = STATUS_INCOMPLETE

            except Exception as err:
                # file not found. What should I do, wait for it? (leave status on 'defined') or give it an error status?
                atdb.atdb_interface.do_PUT(key='dataproducts:new_status', id=id, taskid=None, value=STATUS_INVALID_DPS)
                message = "ERROR by *data_monitor* : " + str(err)
                atdb.report("ERROR by *data_monitor* : " + str(err),"print,slack")
                task_end_status = STATUS_INCOMPLETE

        # do a final check for 'invalid' dataproducts (which may be put in manually or otherwise through the REST API or GUI).
        invalids = atdb.atdb_interface.do_GET_LIST(key='dataproducts:id',
                                                   query='taskID=' + taskID + '&my_status='+STATUS_INVALID_DPS)
        if (len(invalids) > 0):
            task_end_status = STATUS_INCOMPLETE

        # when all dps have been checked, put observation status back to 'complete' or 'incomplete'.
        atdb.atdb_interface.do_PUT(key='observations:new_status', id=None, taskid=taskID, value=task_end_status)
        atdb.report("*data_monitor* : " + taskID + " " + task_end_status,"slack")