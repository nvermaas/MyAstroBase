"""
    File name: astrobase_io.py
    Authors: Nico Vermaas
    Date created: 2019-10-13
    Description: This is the IO class for the astrobase_services that handles the communication
                 with AstroBase and the astrometry.net services.
                 It also has functionality to write to slack, stdout and logging.
"""

import os
import subprocess
import datetime
import requests
import logging

logger = logging.getLogger(__name__)

from astrobase_services.astrobase_interface import AstroBase

# The request header
ASTROBASE_HEADER = {
    'content-type': "application/json",
    'cache-control': "no-cache",
    'authorization': "Basic YWRtaW46YWRtaW4="
}

# some constants
ASTROBASE_HOST_DEV = "http://localhost:8000/astrobase"       # your local development environment with Django webserver
ASTROBASE_HOST_VM = "http://localhost:8000/astrobase"         # your local Ansible/Vagrant setup for testing
ASTROBASE_HOST_PROD = "http://localhost:8000/astrobase"      # the atdb production environment.

DEFAULT_ASTROBASE_HOST = ASTROBASE_HOST_DEV



def unicode_to_ascii(value, encoding='utf-8'):
    """
    :param value:
    :param encoding: UTF-8
    :return: String
    """
    try:
      # python 2
      if isinstance(value, unicode):
          return value.encode(encoding)
      return value
    except:
      # python 3
        return value

class AstroBaseIO:
    """
    This is the IO class for the astrobase_services that handles the communication
    with AstroBase and the astrometry.net services. 
    It also has functionality to write to slack, stdout and logging.
    """
    TIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"

    def __init__(self, astrobase_host, user='', password='', obs_mode_filter='', host_filter='', verbose=False, verbose_deep=False, testmode=False):
        """
        Constructor.
        :param host: the host name of the backend.
        :param username: The username known in Django Admin.
        :param verbose: more information about atdb_service at runtime.
        :param verbose_deep: more information about underlying astrobase_interface at runtime.
        :param testmode: runs the services in testmode if true. Look in services what this means per service.
        """

        # accept some presets to set host to dev, test, acc or prod
        self.host = astrobase_host
        if self.host=='dev':
            self.host = ASTROBASE_HOST_DEV
        elif self.host=='vm':
            self.host = ASTROBASE_HOST_VM
        elif self.host=='prod':
            self.host = ASTROBASE_HOST_PROD
        elif (not self.host.endswith('/')):
            self.host += '/'


        elif (not self.alta_host.endswith('/')):
            self.alta_host += '/'

        self.verbose = verbose
        self.verbose_deep = verbose_deep
        self.header = ASTROBASE_HEADER
        self.user = user
        self.password = password
        self.testmode = testmode
        self.obs_mode_filter = obs_mode_filter
        self.host_filter = host_filter
        self.astrobase_interface = AstroBase(self.host, self.verbose_deep)


    def verbose_print(self, info_str):
        """
        Print info string if verbose is enabled (default False)
        :param info_str: String to print
        """
        if self.verbose:
            timestamp = datetime.datetime.now().strftime(self.TIME_FORMAT)
            print(str(timestamp)+ ' - '+info_str)


    def get_dir_size(self, start_path='.'):
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(start_path, followlinks=True):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                total_size += os.path.getsize(fp)
        return total_size

# --- remote ssh commands---------------------------------------------------------------------------------------

    # as found in copy_to_alta.py
    def run_on_node(self, hostname, command, background=True):
        """Run command on an ARTS node. Assumes ssh keys have been set up
            node: nr of node (string or int)
            command: command to run
            background: whether to run ssh in the banode: nr of node (string or int)ckground
        """
        if background:
            ssh_cmd = "ssh {} \"{}\" &".format(hostname, command)
        else:
            ssh_cmd = "ssh {} \"{}\"".format(hostname, command)
        # print("Executing '{}'".format(ssh_cmd))
        return os.system(ssh_cmd)


    # copy a dataproduct from its hardcoded name (like tabA.fits) to the name provided by the atdb specfication service
    def copy_dataproduct_remote(self, node, data_location, from_name, to_name):
        """ copy a dataproduct from its hardcoded name (like tabA.fits) to the name provided by the atdb specfication service
            node: nr of node (string or int)
            data_location: directory on the node where the source file is, and where the target file will be copied.
            from_name: file to copy
            to_name : the new file.
        """
        #print('copy dataproduct ' + node + ':/' + data_location + '/' + from_name + ' to ' + to_name)
        src = data_location + '/' + from_name
        tgt = data_location + '/' + to_name
        cmd = 'cp ' + src + ' ' + tgt

        self.run_on_node(node, cmd, background=False)


    # move/rename a remote dataproduct
    def move_dataproduct_remote(self, node, data_location, from_name, to_name):
        """ move/rename a remote dataproduct
            node: nr of node (string or int)
            data_location: directory on the node where the source file is, and where the target file will be copied.
            from_name: filename to rename
            to_name : new filename
        """
        #print('copy dataproduct ' + node + ':/' + data_location + '/' + from_name + ' to ' + to_name)
        src = data_location + '/' + from_name
        tgt = data_location + '/' + to_name
        cmd = 'mv ' + src + ' ' + tgt

        self.run_on_node(node, cmd, background=False)


    # scp a dataproduct from a node to a local dir
    def scp_dataproduct(self, node, from_location, from_name, to_location, to_name):
        """ secure copy a file from a node to the current machine
            node: nr of node (string or int)
            data_location: directory on the node where the source file is, and where the target file will be copied.
            from_name: file to copy
            to_name : the new file.
        """
        #print('copy dataproduct ' + node + ':/' + data_location + '/' + from_name + ' to ' + to_name)
        src = from_location + '/' + from_name
        tgt = to_location + '/' + to_name
        cmd = 'scp ' + node + ':' + src + ' ' + tgt
        os.system(cmd)


    # check if the specified file exist on the node.
    def check_dataproduct(self, node, data_location, filename):
        """ check if the dataproduct exists on the given location on the node)
            node: nr of node (string or int)
            data_location: directory on the node where the source file is, and where the target file will be copied.
            from_name: file to check
        """
        src = data_location + '/' + filename
        cmd = 'test -s ' + src
        if self.run_on_node(node, cmd, background=False) == 0:
            return True
        else:
            return False


    # returns filesize of a remote file
    def get_filesize_remote(self, node, filepath):
        cmd = 'ssh ' + node + ' stat -Lc%s ' + filepath
        try:
            size = subprocess.check_output(cmd, shell=True)
            size = size.split()[0].decode('utf-8')
            return size
        except Exception as err:
            # file does not exist?
            self.report('ERROR get_filesize_remote of' +filepath)
            return 0


    def remove_dataproduct_remote(self, node, data_location, filename):
        """ remove a dataproduct from the given location on the node)
            node: nr of node (string or int)
            data_location: directory on the node where the source file is, and where the target file will be copied.
            filename: file to remove
        """
        src = data_location + '/' + filename
        cmd = 'rm ' + src
        self.run_on_node(node, cmd, background=False)

    # --------------------------------------------------------------------------------------------------------
    # example: change status of observation with taskid=180223003 to valid.
    # change_status('observations','taskid:180223003','valid'
    def do_change_status(self, resource, search_key, status):

        my_key = resource + ':new_status'   # observations:new_status

        # id:27 or taskid:180223003
        params = search_key.split(':')
        search_field = params[0]            # taskid
        search_value = params[1]            # 180223003

        if search_field=='taskid':
            if my_key.startswith('observations'):
                self.astrobase_interface.do_PUT(key=my_key, id=None, taskid=search_value, value=status)
            if  my_key.startswith('dataproducts'):
                self.astrobase_interface.do_PUT_LIST(key=my_key, taskid=search_value, value=status)
        else:
            self.astrobase_interface.do_PUT(key=my_key, id=search_value, taskid=None, value=status)

# --------------------------------------------------------------------------------------------------------
    def do_delete_taskid(self, taskid):

        # find the observation
        cnt = 0
        id = self.astrobase_interface.do_GET_ID(key='observations:taskID', value=taskid)
        while (int(id) > 0):
            cnt += 1
            self.verbose_print('delete observation : ' + str(taskid) + ' (id = ' + str(id) + ')')
            self.astrobase_interface.do_DELETE(resource='observations', id=id)
            # check for more
            id = self.astrobase_interface.do_GET_ID(key='observations:taskID', value=taskid)
        print(str(cnt) + ' observations with taskID ' + str(taskid) + ' removed')

        cnt = 0
        id = self.astrobase_interface.do_GET_ID(key='dataproducts:taskID', value=taskid)
        while (int(id) > 0):
            cnt += 1
            self.verbose_print('delete dataproduct for taskID ' + str(taskid) + ' (id = ' + str(id) + ')')
            self.astrobase_interface.do_DELETE(resource='dataproducts', id=id)
            # check for more
            id = self.astrobase_interface.do_GET_ID(key='dataproducts:taskID', value=taskid)
        print(str(cnt) + ' dataproducts with taskID ' + str(taskid) + ' removed')


# --------------------------------------------------------------------------------------------------------
    def report(self, message, method='logging'):
        self.verbose_print(message)
        if 'ERROR' in message.upper():
            logging.error(message)
        else:
            logging.info(message)

        if 'print' in method:
            self.verbose_print(message)

        if 'slack' in method:
            self.send_message_to_apidorn_slack_channel(message)

    def send_message_to_apidorn_slack_channel(self, message_str):
        """
        Send a message to the Slack channel #atdb-logging
        With this channel a notification of Ingest ready (or failed) is given.
        Don't raise an Exception in case of error
        :param message_str: Message String
        """
        try:
            timestamp = datetime.datetime.now().strftime(self.TIME_FORMAT)
            message_str = unicode_to_ascii(message_str)
            payload = {"text": str(timestamp) + ' - ' + message_str}

            if (self.host == ASTROBASE_HOST_PROD):
                # in production send to 'atdb_logging'
               url = "https://hooks.slack.com/services/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"
            else:
                # otherwise send to 'atdb-test'
               url = "https://hooks.slack.com/services/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"

            res = requests.post(url, data=str(payload))
        except Exception as err:
            print("Error sending message to slack: " + str(err))