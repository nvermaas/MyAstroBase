"""
    File name: service_scheduler.py
    Author: Nico Vermaas - Astron
    Date created: 2018-11-23
    Date last modified: 2018-11-23
    Description: Add starttime and endtime to an existing observation and PUT it status on 'scheduled'
"""

STATUS_END   = 'scheduled'  # this service will leave the observation in this state

# --------------------------------------------------------------------------------------------------------
def do_scheduler(atdb, taskid, starttime, endtime):
    # Add starttime and endtime to an existing observation and PUT it status on 'scheduled'

    # put starttime into the databasse
    if starttime != None:
        atdb.atdb_interface.do_PUT(key='observations:starttime', id=None, taskid=taskid, value=starttime)

    # put endtime into the databasse
    if endtime != None:
        atdb.atdb_interface.do_PUT(key='observations:endtime', id=None, taskid=taskid, value=endtime)

    # put the observation on 'scheduled'
    atdb.atdb_interface.do_PUT(key='observations:new_status', id=None, taskid=taskid, value=STATUS_END)
