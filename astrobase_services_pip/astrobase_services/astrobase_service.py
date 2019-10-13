#!/usr/bin/python3
"""
    File name: astrobase_service.py
    Authors: Nico Vermaas
    Date created: 2019-10-13
    Description: The main program that controls all astrobase_services.
"""

import os
import sys

import argparse
import time
import logging
import logging.config

from astrobase_io import AstroBaseIO, DEFAULT_ASTROBASE_HOST
from service_specification import do_specification
from service_scheduler import do_scheduler
from service_executor import do_executor
from service_data_monitor import do_data_monitor
from service_cleanup import do_cleanup
from service_add_dataproduct import do_add_dataproduct


from pkg_resources import get_distribution
try:
    pkg_version = get_distribution('astrobase_services').version
except:
    pkg_version = '0.9'

LAST_UPDATE = "13 oct 2019"

# ====================================================================

def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        if 'log_time' in kw:
            name = kw.get('log_name', method.__name__.upper())
            kw['log_time'][name] = int((te - ts) * 1000)
        else:
            print('execution time: %r  %2.2f ms' % \
                  (method.__name__, (te - ts) * 1000))
        return result
    return timed

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
    try:
        logging_config_file = os.path.join(os.path.dirname(__file__), 'astrobase_service_logging.ini')
        logging.config.fileConfig(logging_config_file)
        logger = logging.getLogger('astrobase_service')
    except:
        pass

    parser = argparse.ArgumentParser(fromfile_prefix_chars='@')

    # Specification parameters (required)
    parser.add_argument("--field_name",
                        default="unknown",
                        help="SPECIFICATION parameter")
    parser.add_argument("--field_ra",
                        default=None,
                        help="SPECIFICATION parameter. Right Ascension in decimal degrees like 202.4842")
    parser.add_argument("--field_dec",
                        default=None,
                        help="SPECIFICATION parameter. Declination in decimal degrees like 47.2306")
    parser.add_argument("--field_fov",
                        default=None,
                        help="SPECIFICATION parameter. Field of View in decimal degrees like 12.2306")
    # Specification or Scheduler parameters (required)
    parser.add_argument("--date",
                        default=None,
                        help="SPECIFICATION or SCHEDULING parameter. Format like 2018-02-23 21:03:33")
    # Specification and Datamonitor parameters (required)
    parser.add_argument("--data_location",
                        default=None,
                        help="SPECIFICATION and DATA_MONITOR parameter. This is where EXECUTOR must write the data and DATA_MONITOR will monitor it.")
    # Specification parameters (optional)
    parser.add_argument("--taskid", nargs="?",
                        default=None,
                        help="Optional taskID which can be used instead of '--id' to lookup Observations or Dataproducts.")
    parser.add_argument("--taskid_postfix",
                        nargs="?",
                        default="",
                        help="Optional postfix to be added to generated taskid by SPECIFICATION service (used for pipelines).")
    parser.add_argument("--ndps",
                        default=None,
                        help="(Optional) SPECIFICATION parameter: Number of dataproducts to add. For known beam patterns this is handled by the --pattern argument")
    parser.add_argument("--observing_mode",
                        default='imaging',
                        help="SPECIFICATION parameter: imaging, imaging_pointing, arts_sc1_timing, arts_sc1_baseband, arts_sc4_record, arts_sc4_survey, arts_sc4_dump,")
    parser.add_argument("--process_type",
                        default='system',
                        help="SPECIFICATION parameter: science_observation, science_driftscan, system_pointing, system_reservation")
    parser.add_argument("--dataproducts",
                        default=None,
                        help="List of dataproducts and their status. Example: dataproducts=IMG_2881.jpg:raw,IMG_2881_annotated.jpg:available")

    parser.add_argument("--filename",
                        default=None,
                        help="Filename of dataproduct added to a running observation. Like ARTS190101001_CB01_TAB01.fits")
    # Non-workflow general parameters
    parser.add_argument("--status",
                        default=None,
                        help="status to be set by the set-status operation")
    parser.add_argument("--resource","-r",
                        default='observations',
                        help="observations or dataproducts")
    parser.add_argument("--search_key", "-k",
                        default='taskid:180223003',
                        help="Search key used for various services")

    # Global parameters (required)
    parser.add_argument("--operation","-o",
                        default="None",
                        help="specification, scheduler, executor, data_monitor, start_ingest, ingest_monitor, cleanup, delete_taskid, change_status")

    # Global parameters
    parser.add_argument("--obs_mode_filter",
                        default="",
                        help="This instance of the service only acts on Observations that have this (substring) value in their observing_mode. "
                             "That makes it possible to run multiple instances of a service on different locations. "
                             "For example: executor --obs_mode_filter=ARTS will only execute observations for ARTS without interfering with imaging")
    parser.add_argument("--status_filter",
                        default=None,
                        help="The 'start_ingest' can react to a specific status, like 'valid' or 'valid_priority. Default is None, then the start_ingest service will listen for both 'valid_priority' and 'valid', in that order.")
    parser.add_argument("--host_filter",
                        default="",
                        help="When specified, the service checks if the 'data_location' contains this value and will only execute when that is the case.")
    parser.add_argument("--interval",
                        default=None,
                        help="Polling interval in seconds. When enabled this instance of the program will run in monitoring mode.")
    parser.add_argument("--testmode",
                        default=False,
                        help="Test mode. Writes to ATDB, but does not start/stop observations, does not execute ingests and does not delete data from disk.",
                        action="store_true")
    parser.add_argument("--astrobase_host",
                        nargs="?",
                        default=DEFAULT_ASTROBASE_HOST,
                        help="Presets are 'dev', 'vm', 'prod'. Otherwise give a full url like https://localhost:8000/astrobase")
    parser.add_argument("-u","--user",
                        nargs="?",
                        default='vagrant',
                        help="Username.")
    parser.add_argument("-p", "--password",
                        nargs="?",
                        default='vagrant',
                        help="Password.")
    # Global parameters (for info)
    parser.add_argument("-v", "--verbose",
                        default=False,
                        help="More information about astrobase_services at run time.",
                        action="store_true")
    parser.add_argument("-v2", "--verbose_deep",
                        default=False,
                        help="More information about astrobase_interface at run time.",
                        action="store_true")
    parser.add_argument("--version",
                        default=False,
                        help="Show current version of this program.",
                        action="store_true")
    parser.add_argument("--examples", "-e",
                        default=False,
                        help="Show some examples",
                        action="store_true")
    # All parameters in a file
    parser.add_argument('--parfile',
                        nargs='?',
                        type=str,
                        help='Parameter file')

    args = get_arguments(parser)
    try:
        astrobase_service = AstroBaseIO(args.astrobase_host, args.user, args.password, args.obs_mode_filter,
                               args.host_filter, args.verbose, args.verbose_deep, args.testmode)

        # don't spam the channel for every added dataproduct
        if (args.operation != 'add_dataproduct'):
            host_filter_text = ''
            if args.host_filter!='':
                host_filter_text = " for host "+ args.host_filter

            obs_mode_filter_text = ''
            if args.obs_mode_filter!='':
                obs_mode_filter_text = " for observing_mode "+ args.obs_mode_filter

            if args.testmode:
                message = 'starting *'+args.operation+'* ' + obs_mode_filter_text + host_filter_text + ' service version '+pkg_version+'... (testmode)'
            else:
                message ='starting *' + args.operation+'* ' + obs_mode_filter_text + host_filter_text + ' service version '+pkg_version+'...'

            astrobase_service.report(message)
            astrobase_service.send_message_to_apidorn_slack_channel(message)

        if (args.examples):

            print('astrobase_service.py version = '+ pkg_version + " (last updated " + LAST_UPDATE + ")")
            print('--------------------------------------------------------------')
            print()
            print('--- Examples --- ')
            print()
            print('--------------------------------------------------------------')
            return

        # --------------------------------------------------------------------------------------------------------
        if (args.version):
            print('--- astrobase_service.py version = '+ pkg_version + " (last updated " + LAST_UPDATE + ") ---")
            return

        # --------------------------------------------------------------------------------------------------------
        if (args.operation=='specification'):
            do_specification(astrobase_service,
                             taskid=args.taskid,
                             taskid_postfix=args.taskid_postfix,
                             initial_status=args.status,
                             ndps=args.ndps,
                             field_name=args.field_name,
                             date=args.date,
                             field_ra=args.field_ra,
                             field_dec=args.field_dec,
                             field_fov=args.field_fov,
                             data_location=args.data_location,
                             observing_mode=args.observing_mode,
                             process_type=args.process_type,
                             dataproducts=args.dataproducts
                             )

        # --------------------------------------------------------------------------------------------------------
        if (args.operation == 'scheduler'):
            do_scheduler(astrobase_service, taskid=args.taskid, starttime=args.starttime, endtime=args.endtime)

        # --------------------------------------------------------------------------------------------------------

        if (args.operation == 'executor'):

            do_executor(astrobase_service)
            if args.interval:
                print('*executor* starting polling ' + astrobase_service.host + ' every ' + args.interval + ' secs')
                while True:
                    try:
                        time.sleep(int(args.interval))
                        do_executor(astrobase_service)
                    except:
                        print('*** executor crashed! ***')
                        print(sys.exc_info()[0])
                        print('trying to continue...')
                        astrobase_service.send_message_to_apidorn_slack_channel("*executor service* crashed! ... restarting.")

        # --------------------------------------------------------------------------------------------------------
        if (args.operation == 'data_monitor'):
            do_data_monitor(astrobase_service)
            if args.interval:
                print('*data_monitor* starting polling ' + astrobase_service.host + ' every ' + args.interval + ' secs')
                while True:
                    try:
                        time.sleep(int(args.interval))
                        do_data_monitor(astrobase_service)
                    except:
                        print('*** data_monitor crashed! ***')
                        print(sys.exc_info()[0])
                        print('trying to continue...')
                        astrobase_service.send_message_to_apidorn_slack_channel("*data_monitor service* crashed! ... restarting.")

        # --------------------------------------------------------------------------------------------------------
        if (args.operation == 'cleanup'):
            # the 'archived' status is written by the 'ingest_monitor' service
            # or the 'removing' status is set from the GUI or otherwise.

            do_cleanup(astrobase_service,'archived','removed')
            do_cleanup(astrobase_service,'removing', 'removed (manual)')

            if args.interval:
                print('*cleanup* starting polling ' + astrobase_service.host + ' every ' + args.interval + ' secs')
                while True:
                    try:
                        time.sleep(int(args.interval))
                        do_cleanup(astrobase_service, 'archived', 'removed')
                        do_cleanup(astrobase_service, 'removing', 'removed (manual)')
                    except:
                        print('*** cleanup crashed! ***')
                        print(sys.exc_info()[0])
                        print('trying to continue...')
                        astrobase_service.send_message_to_apidorn_slack_channel("*cleanup service* crashed! ... restarting.")

        # --------------------------------------------------------------------------------------------------------
        if (args.operation == 'add_dataproduct'):
            do_add_dataproduct(astrobase_service, taskid=args.taskid, node=args.node, data_dir=args.data_dir, filename=args.filename)

        # --------------------------------------------------------------------------------------------------------
        if (args.operation=='change_status'):
            astrobase_service.do_change_status(resource=args.resource, search_key=args.search_key, status=args.status)

        # --------------------------------------------------------------------------------------------------------
        if (args.operation=='delete_taskid'):
            astrobase_service.do_delete_taskid(taskid=args.taskid)

        # --------------------------------------------------------------------------------------------------------

    except Exception as exp:
        message = str(exp)
        astrobase_service.send_message_to_apidorn_slack_channel(message)
        exit_with_error(str(exp))

    sys.exit(0)


if __name__ == "__main__":
    main()

