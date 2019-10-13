"""
    File name: service_cleanup.py
    Author: Nico Vermaas - Astron
    Date created: 2018-12-11
    Date last modified: 2018-12-11
    Description: An ATDB service to add new dataproducts to a running observation.
                 This can be called from a SC4 trigger.
"""

STATUS_DPS_DEFINED = 'defined'

# --------------------------------------------------------------------------------------------------------
def do_add_dataproduct(atdb, taskid, node, data_dir, filename):
    # retrieve the parent observation to get some extra information that has to be stored with the dataproduct
    parent_id = atdb.atdb_interface.do_GET_ID(key='observations:taskID', value=taskid)
    if data_dir is not None:
        data_location = data_dir
    else:
        data_location = atdb.atdb_interface.do_GET(key='observations:data_location', id=parent_id, taskid=None)
    irods_collection = atdb.atdb_interface.do_GET(key='observations:irods_collection', id=parent_id, taskid=None)



    payload = "{"
#    payload += "name=" + filename + ','
#    payload += "taskID=" + str(taskid) + ','
#    payload += "parent=" + str(parent_id) + ','
#    payload += "node=" + str(node) + ','
#    payload += "filename=" + filename + ','
#    payload += "data_location=" + data_location + ','
#    payload += "irods_collection=" + irods_collection + ','
#    payload += "description=" + filename + ','
#    payload += "size=0" + ','
#    payload += "quality=?" + ','
#    payload += "new_status=" + str(STATUS_DPS_DEFINED)
    
    #payload += '"field_dec" : "' + str(field_dec) + '",'
    payload += '"name" : "' + str(filename) + '",'
    payload += '"taskID" : "' + str(taskid) + '",'
    payload += '"parent" : "' + str(parent_id) + '",'
    payload += '"node" : "' + str(node) + '",'
    payload += '"filename" : "' + str(filename) + '",'
    payload += '"data_location" : "' + str(data_location) + '",'
    payload += '"irods_collection" : "' + str(irods_collection) + '",'
    payload += '"description" : "' + str(filename) + '",'
    payload += '"size" : "0",'
    payload += '"quality" : "?",'
    payload += '"new_status=" : "' + str(STATUS_DPS_DEFINED) + '"'
    payload += "}"

    atdb.report('*add_dataproduct* is adding ' + filename + ' to Observation ' + str(taskid))
 #   atdb.atdb_interface.do_POST(resource='dataproducts', payload=payload)
    atdb.atdb_interface.do_POST_json(resource='dataproducts', payload=payload)


def do_add_dataproducts(atdb, taskid, dataproducts):
    """
    add a batch of dataproducts to a taskid.
    This function is not abstracted into a commandline call like 'service -o add_dataproducts', but could be if needed.
    :param atdb:
    :param taskid:
    :param dataproducts: json list of dataproducts to be added to the provided taskid
    """

    atdb.report('*add_dataproducts* is adding ' + str(len(dataproducts)) + 'dataproducts to Observation ' + str(taskid))
    return atdb.atdb_interface.do_POST_dataproducts(taskid,dataproducts)