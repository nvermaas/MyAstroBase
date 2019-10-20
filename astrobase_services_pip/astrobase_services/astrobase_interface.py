#!/usr/bin/python3
import sys
import os
import requests
import json
import argparse
import datetime

"""
astrobase_interface.py : a commandline tool to interface with the AstroBase REST API.
:author Nico Vermaas - Astron
"""
VERSION = "1.0.0"
LAST_UPDATE = "13 oct 2019"

# ====================================================================

# The request header
ASTROBASE_HEADER = {
    'content-type': "application/json",
    'cache-control': "no-cache",
    'authorization': "Basic YWRtaW46YWRtaW4="
}

# some constants
ASTROBASE_HOST_DEV = "http://localhost:8000/astrobase"       # your local development environment with Django webserver
ASTROBASE_HOST_VM = "http://localhost:8000/astrobase"         # your local Ansible/Vagrant setup for testing
ASTROBASE_HOST_PROD = "http://192.168.178.62:8018/astrobase"      # the astrobase production environment.

DEFAULT_ASTROBASE_HOST = ASTROBASE_HOST_DEV
TIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"


class AstroBase:
    """
    Interface class to the AstroBase REST API
    """
    def __init__(self, host, verbose=False):
        """
        Constructor.
        :param host: the host name of the backend.
        :param username: The username known in Django Admin.
        :param verbose: more information runtime.
        :param header: Request header for Astrobase REST requests with token authentication.
        """
        # accept some presets to set host to dev, test, acc or prod
        self.host = host
        if self.host=='dev':
            self.host = DEFAULT_ASTROBASE_HOST
        elif self.host=='vm':
            self.host = ASTROBASE_HOST_VM
        elif self.host=='prod':
            self.host = ASTROBASE_HOST_PROD
        if not self.host.endswith('/'):
            self.host += '/'

        self.verbose = verbose
        self.header = ASTROBASE_HEADER

    def verbose_print(self, info_str):
        """
        Print info string if verbose is enabled (default False)
        :param info_str: String to print
        """
        if self.verbose:
            timestamp = datetime.datetime.now().strftime(TIME_FORMAT)
            print(str(timestamp)+ ' - '+info_str)

    # === Backend requests ================================================================================
    @staticmethod
    def reconstruct_beams_obsolete(payload_string):
        """
        Normally, to translate the specification string to a json payload that the http requests understand,
        all substrings like 'a,b,c' are replaced with "a","b","c". But this should not be done for the beams list,
         which is given as something like beams=1..10,11,12 or beams=[1..10,11,12] in the specification.
         So this function reconstructs that stting. (a bit ugly, but as usual time constraints force me to cut a corner).
        :param payload_string:
        :return:
        """

        # find the part where the 'beams' are already converted to a messy string: "beams": ""beams" : "1..10" , "11" , "12" , "new_status"", "new_status"
        start = payload_string.find('"beams"') + 10

        if (start>=10):
            # if no beams were found, then ignore this step
            end = payload_string.find('"new_status"') -3

            # save the before and after parts of the string
            before = payload_string[0:start]
            after = payload_string[end:]

            # extract the middle part that needs to be changed: 1..10" , "11" , "12
            middle = payload_string[start:end]

            # remove all " and spaces, and surround it with "" again.
            middle = middle.replace("\"","")
            middle = middle.replace(" ","")
            middle = '"' + middle + '"'

            # reconstruct the payload string
            payload_string = before + middle + after

        return payload_string


    def jsonifyPayload_obsolete(self, payload):
        """
        {name=WSRTA180223003_B003.MS,filename=WSRTA180223003_B003.MS} =>
        {"name" : "WSRTA180223003_B003.MS" , "filename" : "WSRTA180223003_B003.MS"}
        :param payload:
        :return: payload_string
        """

        payload_string = str(payload).replace("{","{\"")
        payload_string = payload_string.replace("}", "\"}")
        payload_string = payload_string.replace("=", "\" : \"")
        payload_string = payload_string.replace(",", "\" , \"")

        # reconstruct the lists by moving the brackets outside the double quotes
        payload_string = payload_string.replace("\"[", "[\"")
        payload_string = payload_string.replace("]\"", "\"]")
        payload_string = payload_string.replace("/,", "/\",\"")
        payload_string = payload_string.replace("u\"", "\"")

        #payload_string = json.dumps(payload)
        # ugly: reconstruct beams string
        payload_string = self.reconstruct_beams_obsolete(payload_string)

        self.verbose_print("payload_string: [" + payload_string+"]")
        return payload_string

    def encodePayload(self, payload):
        """

        The POST body does not simply accept a payload dict, it needs to be translated to a string with some
        peculiarities
        :param payload:
        :return: payload_string
        """

        payload_string = str(payload).replace("'","\"")
        #payload_string = payload_string.replace(",", ",\n")

        # reconstruct the lists by moving the brackets outside the double quotes
        payload_string = payload_string.replace("\"[", "[\"")
        payload_string = payload_string.replace("]\"", "\"]")
        payload_string = payload_string.replace("/,", "/\",\"")
        payload_string = payload_string.replace("u\"", "\"")

        self.verbose_print("The payload_string: [" + payload_string+"]")
        return payload_string


    def GET_TaskObjectByTaskId(self, resource, taskid):
        """
        Do a http GET request to the alta backend to find the Observation with the given runId
        :runId runId:
        """

        url = self.host + resource
        # create the querystring, external_ref is the mapping of this element to the alta datamodel lookup field
        querystring = {"taskID": taskid}

        response = requests.request("GET", url, headers=self.header, params=querystring)
        self.verbose_print("[GET " + response.url + "]")

        try:
            json_response = json.loads(response.text)
            results = json_response["results"]
            taskobject = results[0]
            return taskobject
        except:
            raise (Exception(
                "ERROR: " + str(response.status_code) + ", " + str(response.reason) + ', ' + str(response.content)))

    # ------------------------------------------------------------------------------#
    #                                Main User functions                            #
    # ------------------------------------------------------------------------------#


    def do_GET_ID(self, key, value):
        """
        Get the id based on a field value of a resource. This is a generic way to retrieve the id.
        :param resource: contains the resource, for example 'observations', 'dataproducts'
        :param field: the field to search on, this will probably be 'name' or 'filename'
        :param value: the value of the 'field' to search on.
        :return id
        """

        # split key in resource and field
        params = key.split(":")
        resource = params[0]
        field = params[1]

        url = self.host + resource + "?" + field + "=" + value
        response = requests.request("GET", url, headers=self.header)
        self.verbose_print("[GET " + response.url + "]")
        self.verbose_print("Response: " + str(response.status_code) + ", " + str(response.reason))

        try:
            json_response = json.loads(response.text)
            results = json_response["results"]
            result = results[0]
            id = result['id']
            return id
        except:
            return '-1'
            #raise (Exception("ERROR: " + response.url + " not found."))


    def do_GET(self, key, id, taskid):
        """
        Do a http GET request to the astrobase backend to find the value of one field of an object
        :param key: contains the name of the resource and the name of the field separated by a colon.
        :param id: the database id of the object.
        :param taskid (optional): when the taskid (of an activity) is known it can be used instead of id.
        """

        # split key in resource and field
        params = key.split(":")
        resource = params[0]
        field = params[1]

        if taskid!=None:
            taskObject = self.GET_TaskObjectByTaskId(resource, taskid)
            id = taskObject['id']

        if id==None:
            # give up and throw an exception.
            raise (Exception("ERROR: no valid 'id' or 'taskid' provided"))

        url = self.host + resource + "/" + str(id) + "/"
        self.verbose_print(('url: ' + url))

        response = requests.request("GET", url, headers=self.header)
        self.verbose_print("[GET " + response.url + "]")
        self.verbose_print("Response: " + str(response.status_code) + ", " + str(response.reason))

        try:
            json_response = json.loads(response.text)
            value = json_response[field]
            return value
        except Exception as err:
          self.verbose_print("Exception : " + str(err))
          raise (
              Exception("ERROR: " + str(response.status_code) + ", " + str(response.reason) + ', ' + str(response.content)))


    #  python astrobase_interface.py -o GET_LIST --key observations:taskID --query status=valid
    def do_GET_LIST(self, key, query):
        """
        Do a http GET request to the astrobase backend to find the value of one field of an object
        :param key: contains the name of the resource and the name of the field separated by a dot.
        :param id: the database id of the object.
        :param taskid (optional): when the taskid (of an activity) is known it can be used instead of id.
        """
        self.verbose_print("do_GET_LIST(" + key + "," + query + ")")
        # split key in resource and field
        params = key.split(":")
        resource = params[0]
        field = params[1]

        url = self.host + resource + "?" + str(query)
        # self.verbose_print("url = " + url)

        response = requests.request("GET", url, headers=self.header)
        self.verbose_print("[GET " + response.url + "]")
        self.verbose_print("Response: " + str(response.status_code) + ", " + str(response.reason))

        try:
            json_response = json.loads(response.text)
            results = json_response["results"]
            #results = json.loads(response.text)
            # loop through the list of results and extract the requested field (probably taskID),
            # and add it to the return list.
            list = []
            for result in results:
                value = result[field]
                list.append(value)

            return list
        except Exception as err:
            self.verbose_print("Exception : " + str(err))
            raise (Exception(
                "ERROR: " + str(response.status_code) + ", " + str(response.reason) + ', ' + str(response.content)))


    def do_GET_NextTaskID(self, timestamp, taskid_postfix=""):
        """
        :param timestamp: timestamp on which the taskid is based
        :param taskid_postfix: optional addition to the taskid,
               like when taskid_postfix="_IMG" the taskid will become "190405001_IMG"
        :return: taskid
        """

        self.verbose_print("do_GET_NextTaskID(" + str(timestamp) + ")")

        # construct the url
        url = self.host + "get_next_taskid?timestamp=" + str(timestamp)+"&taskid_postfix="+taskid_postfix

        # do the request to the astrobase backend
        response = requests.request("GET", url, headers=self.header)
        self.verbose_print("[GET " + response.url + "]")
        self.verbose_print("Response: " + str(response.status_code) + ", " + str(response.reason))

        # parse the response
        try:
            json_response = json.loads(response.text)
            taskID = json_response["taskID"]
            return taskID
        except Exception as err:
            self.verbose_print("Exception : " + str(err))
            raise (Exception(
                "ERROR: " + str(response.status_code) + ", " + str(response.reason) + ', ' + str(response.content)))


    def do_GET_Observation(self, taskid):
        """
        Do a http request to the astrobase backend get all the observation parameters in the response
        :param taskid
        """
        self.verbose_print("do_GET_Observation(" + taskid + ")")

        # construct the url
        url = self.host + "observations?taskID=" + str(taskid)

        # do the request to the astrobase backend
        response = requests.request("GET", url, headers=self.header)
        self.verbose_print("[GET " + response.url + "]")

        # parse the response
        try:
            json_response = json.loads(response.text)
            results = json_response["results"]
            observation = results[0]
            return observation
        except Exception as err:
            self.verbose_print("Exception : " + str(err))
            raise (Exception(
                "ERROR: " + str(response.status_code) + ", " + str(response.reason) + ', ' + str(response.content)))


    def do_PUT(self, key='observations', id=None, value=None, taskid=None):
        """
        PUT a value to an existing field of a resource (table).
        :param key: contains the name of the resource and the name of the field separated by a dot. observations.description
        :param id: the database id of the object.
        :param value: the value that has to be PUT in the key. If omitted, an empty put will be done to trigger the signals.
        :param taskid (optional): when the taskid of an observation is known it can be used instead of id.
        """

        # split key in resource and field
        if key.find(':')>0:
            params = key.split(":")
            resource = params[0]
            field = params[1]
        else:
            resource = key
            field = None

        if taskid!=None:
            taskObject = self.GET_TaskObjectByTaskId(resource, taskid)
            id = taskObject['id']

        url = self.host + resource + "/" + str(id) + "/"
        if id==None:
            raise (Exception("ERROR: no valid 'id' or 'taskid' provided"))

        payload = {}
        if field!=None:
            payload[field]=value
            payload = self.encodePayload(payload)
        try:
            response = requests.request("PUT", url, data=payload, headers=self.header)
            self.verbose_print("[PUT " + response.url + "]")
            self.verbose_print("Response: " + str(response.status_code) + ", " + str(response.reason))
        except:
            raise (Exception(
                "ERROR: " + str(response.status_code) + ", " + str(response.reason) + ', ' + str(response.content)))


    # do_PUT_LIST(key = observations:new_status, taskid = 180223003, value = valid)
    def do_PUT_LIST(self, key='dataproducts', taskid=None, value=None):
        """
        PUT a value to an existing field of  resource (table).
        :param key: contains the name of the resource and the name of the field separated by a colon. observations:new_status
        :param value: the value that has to be PUT in the key. If omitted, an empty put will be done to trigger the signals.
        :param taskid: the value is PUT to all objects with the provided taskid
        """

        # split key in resource and field
        if key.find(':')>0:
            params = key.split(":")
            resource = params[0]
            field = params[1]
        else:
            resource = key
            field = None

        get_key = resource+':id'
        get_query= 'taskID='+taskid
        ids = self.do_GET_LIST(get_key,get_query)

        for id in ids:
            url = self.host + resource + "/" + str(id) + "/"
            self.verbose_print(('url: ' + url))

            payload = {}
            if field!=None:
                payload[field]=value
                payload = self.encodePayload(payload)
            try:
                response = requests.request("PUT", url, data=payload, headers=self.header)
                self.verbose_print("[PUT " + response.url + "]")
                self.verbose_print("Response: " + str(response.status_code) + ", " + str(response.reason))
            except:
                raise (Exception(
                    "ERROR: " + str(response.status_code) + ", " + str(response.reason) + ', ' + str(response.content)))



    def do_POST_json(self, resource, payload):
        """
        POST a payload to a resource (table). This creates a new object (observation or dataproduct)
        This function replaces the old do_POST function that still needed to convert the json content in a very ugly
        :param resource: contains the resource, for example 'observations', 'dataproducts'
        :param payload: the contents of the object to create in json format
        """

        url = self.host + resource + '/'
        self.verbose_print(('payload: ' + payload))

        try:
            response = requests.request("POST", url, data=payload, headers=self.header)
            self.verbose_print("[POST " + response.url + "]")
            self.verbose_print("Response: " + str(response.status_code) + ", " + str(response.reason))
            if not (response.status_code==200 or response.status_code==201):
                raise Exception()
        except Exception:
            raise (Exception("ERROR: " + str(response.status_code) + ", " + str(response.reason) + ', ' + str(response.content)))


    def do_POST_dataproducts(self, taskid, dataproducts):
        """
        POST (create) a batch of dataproducts for the (observation) with the given taskid.
        This is done with a custom made http request to the AstroBase backend
        :param taskid: taskid of the observation
        :param dataproducts: json list of dataproducts to be added to the provided taskid
        """

        # is 'dataproducts' a valid list of dataproducts?
        try:
            number_of_dataproducts = len(dataproducts)
            self.verbose_print("do_POST_dataproducts(" + taskid + "," + str(number_of_dataproducts) + ")")
        except Exception as err:
            raise (Exception(
                "ERROR: " + str(err)))

        # construct the url
        url = self.host + "post_dataproducts?taskID=" + str(taskid)

        # encode the dictonary as proper json
        payload = self.encodePayload(dataproducts)
        try:
            # do a POST request to the 'post_dataproducts' resource of the astrobase backend
            response = requests.request("POST", url, data=payload, headers=self.header)
            self.verbose_print("[POST " + response.url + "]")

            # if anything went wrong, throw an exception.
            if not (response.status_code==200 or response.status_code==201):
                raise Exception(str(response.status_code) + " - " + str(response.reason))
        except Exception as err:
            raise (Exception("ERROR: " + str(err)))

        # if it has all succeeded, give back the taskid as an indication of success
        return taskid


    def do_DELETE(self, resource, id):
        """
        Do a http DELETE request to the AstroBase backend
        """
        if id == None:
            raise (Exception("ERROR: no valid 'id' provided"))

        # if a range of ID's is given then do multiple deletes
        if (str(id).find('..')>0):
            self.verbose_print("Deleting " + str(id) + "...")
            s = id.split('..')
            start = int(s[0])
            end = int(s[1]) + 1
        else:
            # just a single delete
            start = int(id)
            end = int(id) + 1

        for i in range(start,end):
            url = self.host + resource + "/" + str(i) + "/"

            try:
                response = requests.request("DELETE", url, headers=self.header)
                self.verbose_print("[DELETE " + response.url + "]")
                self.verbose_print("Response: " + str(response.status_code) + ", " + str(response.reason))
            except:
                raise (Exception("ERROR: deleting " + url + "failed." + response.url))


# ------------------------------------------------------------------------------#
#                                Module level functions                         #
# ------------------------------------------------------------------------------#
def exit_with_error(message):
    """
    Exit the code for an error.
    :param message: the message to print.
    """
    print(message)
    sys.exit(-1)


def get_arguments(parser):
    """
    Gets the arguments with which this application is called and returns
    the parsed arguments.
    If a parfile is give as argument, the arguments will be overrided
    The args.parfile need to be an absolute path!
    :param parser: the argument parser.
    :return: Returns the arguments.
    """
    args = parser.parse_args()
    if args.parfile:
        args_file = args.parfile
        if os.path.exists(args_file):
            parse_args_params = ['@' + args_file]
            # First add argument file
            # Now add command-line arguments to allow override of settings from file.
            for arg in sys.argv[1:]:  # Ignore first argument, since it is the path to the python script itself
                parse_args_params.append(arg)
            print(parse_args_params)
            args = parser.parse_args(parse_args_params)
        else:
            raise (Exception("Can not find parameter file " + args_file))
    return args
# ------------------------------------------------------------------------------#
#                                Main                                           #
# ------------------------------------------------------------------------------#


def main():
    """
    The main module.
    """
    parser = argparse.ArgumentParser(fromfile_prefix_chars='@')
    parser.add_argument("-v","--verbose", default=False, help="More information at run time.",action="store_true")
    parser.add_argument("--host", nargs="?", default='test', help="Presets are 'dev', 'vm', 'test', 'acc', 'prod'. Otherwise give a full url like https://astrobase.astron.nl/astrobase")
    parser.add_argument("--version", default=False, help="Show current version of this program", action="store_true")
    parser.add_argument("--operation","-o", default="GET", help="GET, GET_ID, GET_LIST, POST, PUT, DELETE. Note that these operations will only work if you have the proper rights in the ALTA user database.")
    parser.add_argument("--id", default=None, help="id of the object to PUT to.")
    parser.add_argument("-t", "--taskid", nargs="?", default=None, help="Optional taskID which can be used instead of '--id' to lookup Observations or Dataproducts.")
    parser.add_argument("--key", default="observations.title", help="resource.field to PUT a value to. Example: observations.title")
    parser.add_argument("--query", "-q", default="taskID=180223003", help="Query to the REST API")
    parser.add_argument("--value", default="", help="value to PUT in the resource.field. If omitted it will PUT the object without changing values, but the built-in 'signals' will be triggered.")
    parser.add_argument("--payload", "-p", default="{}", help="Payload in json for the POST operation. To create new Observations or Dataproducts. (see examples)")
    parser.add_argument("--show_examples", "-e", default=False, help="Show some examples",action="store_true")
    parser.add_argument('--parfile', nargs='?', type=str,  help='Parameter file')

    args = get_arguments(parser)
    try:
        astrobase = AstroBase(args.host, args.verbose)

        if (args.show_examples):

            print('astrobase_interface.py version = '+ VERSION + " (last updated " + LAST_UPDATE + ")")
            print('---------------------------------------------------------------------------------------------')
            print()
            print('--- basic examples --- ')
            print()
            print("Show the 'status' for Observation with taskID 180720003")
            print("> astrobase_interface -o GET --key observations:my_status --taskid 180223003")
            print()
            print("GET the ID of Observation with taskID 180223003")
            print("> astrobase_interface -o GET_ID --key observations:taskID --value 180223003")
            print()
            print("GET the ID of Dataproduct with name WSRTA180223003_ALL_IMAGE.jpg")
            print("> astrobase_interface -o GET_ID --key dataproducts:name --value WSRTA180223003_ALL_IMAGE.jpg")
            print()
            print("GET the 'status' for Dataproduct with ID = 45")
            print("> astrobase_interface -o GET --key dataproducts:my_status --id 45")
            print()
            print("PUT the 'status' of dataproduct with ID = 45 on 'copied'")
            print("> astrobase_interface -o PUT --key dataproducts:new_status --id 45 --value copied")
            print()
            print("PUT the 'status' of observation with taskID 180720003 on 'valid'")
            print("> astrobase_interface -o PUT --key observations:new_status --value valid --taskid 180223003")
            print()
            print("DELETE dataproduct with ID = 46 from the database (no files will be deleted).")
            print("> astrobase_interface -o DELETE --key dataproducts --id 46")
            print()
            print("DELETE dataproducts with ID's ranging from 11..15 from the database (no files will be deleted).")
            print("> astrobase_interface -o DELETE --key dataproducts --id 11..15 -v")
            print()
            print('--- advanced examples --- ')
            print()
            print("GET_LIST of taskIDs for observations with status = 'valid'")
            print("> astrobase_interface -o GET_LIST --key observations:taskID --query status=valid")
            print()
            print("GET_LIST of IDs for dataproducts with status = 'invalid'")
            print("> astrobase_interface -o GET_LIST --key dataproducts:id --query status=invalid")
            print()
            print("PUT the field 'new_status' on 'valid' for all dataproducts with taskId = '180816001'")
            print("> astrobase_interface -o PUT_LIST --key dataproducts:new_status --taskid 180816001 --value valid")
            print('---------------------------------------------------------------------------------------------')
            return

        if (args.version):
            print('--- astrobase_interface.py version = '+ VERSION + " (last updated " + LAST_UPDATE + ") ---")
            return

        if (args.operation=='GET'):
            result = astrobase.do_GET(key=args.key, id=args.id, taskid=args.taskid)
            print(result)

        if (args.operation == 'GET_ID'):
            result = astrobase.do_GET_ID(key=args.key, value=args.value)
            print(result)

        if (args.operation == 'GET_LIST'):
            result = astrobase.do_GET_LIST(key=args.key, query=args.query)
            print(result)

        if (args.operation=='PUT_LIST'):
            astrobase.do_PUT_LIST(key=args.key, taskid=args.taskid, value=args.value)

        if (args.operation=='PUT'):
            astrobase.do_PUT(key=args.key, id=args.id, value=args.value, taskid=args.taskid)

        if (args.operation=='POST'):
            astrobase.do_POST_json(resource=args.key, payload=args.payload)

        if (args.operation=='DELETE'):
            astrobase.do_DELETE(resource=args.key, id=args.id)

    except Exception as exp:
        exit_with_error(str(exp))

    sys.exit(0)


if __name__ == "__main__":
    main()

