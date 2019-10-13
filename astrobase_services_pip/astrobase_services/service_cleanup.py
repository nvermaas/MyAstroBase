"""
    File name: service_cleanup.py
    Author: Nico Vermaas - Astron
    Date created: 2018-11-23
    Date last modified: 2018-12-02
    Description: An ATDB service to remove dataproducts from the file system.
                 It looks in ATDB for Observations with status 'archived' or 'removing', and within thouse for
                 for dataproducts with status 'archived'. It removes those dataproducts and then puts the
                 statusses of dataproducta and observations to 'removed'.
"""

import os
import shutil

# STATUS_START = 'archived,removing'  # the statusses that trigger this service.
# STATUS_END   = 'removed'            # this service will leave the observation and dataproducts in this state
STATUS_SKIP  = 'ingesting'          # the operation of this service will be skipped for this status

# --------------------------------------------------------------------------------------------------------
def do_cleanup(atdb,STATUS_START,STATUS_END):
    # check if observations and dataproducts with status 'archived' or 'removing' and puts their status to 'removed'

    # get the list taskID of 'archived/removed' observations
    # query = 'my_status=' + STATUS_START + '&observing_mode__icontains=' + atdb.obs_mode_filter
    query = 'my_status='+STATUS_START+'&observing_mode__icontains=' + atdb.obs_mode_filter+'&data_location__icontains=' + atdb.host_filter

    taskIDs = atdb.atdb_interface.do_GET_LIST(key='observations:taskID', query=query)

    if len(taskIDs) > 0:
        atdb.report('*cleanup* found the following ' + STATUS_START + ' tasks : ' + str(taskIDs))

    # loop through the list of 'archived/removed' observations and gather its archived dataproducts,
    for taskID in taskIDs:
        # to prevent a race condition, check if the ingest_monitor is all finished by checking for 'ingesting' dps.
        still_ingesting = atdb.atdb_interface.do_GET_LIST(key='dataproducts:id',
                                                          query='taskID=' + taskID + '&my_status=' + STATUS_SKIP)

        # If there are still 'ingesting' dataproducts then abort the cleanup, next try on the next polling heartbeat.
        if len(still_ingesting) > 0:
            atdb.report(
                '*cleanup* is skipping a heartbeat. *ingest_monitor* is still handling : ' + str(still_ingesting))
        else:
            ids = atdb.atdb_interface.do_GET_LIST(key='dataproducts:id',
                                                  query='taskID=' + taskID + '&my_status__in=' + STATUS_START)
            for id in ids:
                # data_location = atdb.atdb_interface.do_GET(key='dataproducts:data_location', id=id, taskid=None)
                data_dir = atdb.atdb_interface.do_GET(key='dataproducts:data_location', id=id, taskid=None)

                # split off the host from the location
                # host should now always be onboard...
                try:
                    _, data_location = data_dir.split(':')
                except:
                    # ... just in case the host is not onboard
                    data_location = data_dir

                filename = atdb.atdb_interface.do_GET(key='dataproducts:filename', id=id, taskid=None)
                filepath = os.path.join(data_location, filename)

                # If a cluster or remote machine is used (like for ARTS SC4) then the 'node' field has the value of
                # a remote machine. In that case the dataproducts on that remote machine are searched.
                # Otherwise the dataproducts are searched on the local machine.
                node = atdb.atdb_interface.do_GET(key='dataproducts:node', id=id, taskid=None)

                try:
                    if (node is None):
                        atdb.report('removing (local)' + filepath)

                        if os.path.isfile(filepath):
                            os.remove(filepath)
                        else:
                            shutil.rmtree(filepath)

                    else:
                        atdb.report('removing (remote)' + filepath)
                        atdb.remove_dataproduct_remote(node, data_location, filename)

                except Exception as err:
                    atdb.report("ERROR by *cleanup* : \n"+str(err) + "...continuing.","print,slack")

                # whether removing worked or not, continue to put the dataproduct status on 'removed' (from view).
                atdb.atdb_interface.do_PUT(key='dataproducts:new_status', id=id, taskid=None, value=STATUS_END)

            # wether all dataproducts were succesfully removed or not, put the status of the observation on 'removed'
            atdb.atdb_interface.do_PUT(key='observations:new_status', id=None, taskid=taskID, value=STATUS_END)
            atdb.report("*cleanup* service: " + taskID + " " + STATUS_END,"slack")