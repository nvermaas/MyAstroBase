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

from astrobase_services.specification import do_specification
from astrobase_services.submit import do_submit
from astrobase_services.processor import do_processor
from astrobase_services.ingest import do_ingest
from astrobase_services.cleanup import do_cleanup
from astrobase_services.astrobase_io import AstroBaseIO, DEFAULT_ASTROBASE_HOST

from pkg_resources import get_distribution
try:
    pkg_version = get_distribution('astrobase_services').version
except:
    pkg_version = '1.0.0'

LAST_UPDATE = "3 nov 2019"

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

def do_test():
    ASTROMETRY_URL = "http://nova.astrometry.net"
    ASTROMETRY_API = "http://nova.astrometry.net/api/"
    ASTROMETRY_API_KEY = "otrkmikbckoopfje"
    from astrobase_services.astrometry_client import Client

    # login to astrometry with the API_KEY
    client = Client(apiurl=ASTROMETRY_API)
    client.login(apikey=ASTROMETRY_API_KEY)

    # url = "http://uilennest.net/static/astrobase/orion.jpg"
    # url = "http://localhost/cetus.jpg"
    # url = "http://uilennest.net/static/astrobase/cetus.jpg"
    #result = client.url_upload(url=url)
    path_to_file = "/home/nvermaas/www/astrobase/landing_pad/orion.jpg"
    path_to_file = "D:\my_astrobase\orion.jpg"
    result = client.upload(fn=path_to_file)

#...get_or_create_image(df)
#  File "process_submissions.py", line 586, in get_or_create_image
#    img = create_source_list(df)
#  File "process_submissions.py", line 673, in create_source_list
#    raise e
#TypeError: cannot perform reduce with flexible type

    print(result)

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
        logger = logging.getLogger('astrobaseIO')
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
    parser.add_argument("--local_data_dir",
                        default="astrobase_datadir",
                        help="ingest parameter. This is the local directory where the data will be.")
    parser.add_argument("--local_landing_pad",
                        default="astrobase_datadir\landing_pad",
                        help="Directory where ingest will check for incoming raw files.")
    parser.add_argument("--local_data_url",
                        nargs="?",
                        default=os.path.join(DEFAULT_ASTROBASE_HOST),
                        help="url where the raw files can be found by PROCESSOR for job submission")
    parser.add_argument("--override_data_location",
                        default=None,
                        help="override the default data_location that is set by the backend.")

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
                        help="ingest, processing, cleanup, testing")

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
        astrobaseIO = AstroBaseIO(args.astrobase_host, args.user, args.password, args.obs_mode_filter,
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

            astrobaseIO.report(message)
            astrobaseIO.send_message_to_apidorn_slack_channel(message)

        if (args.examples):

            print('astrobaseIO.py version = '+ pkg_version + " (last updated " + LAST_UPDATE + ")")
            print('--------------------------------------------------------------')
            print()
            print('--- Examples --- ')
            print()
            print('--------------------------------------------------------------')
            return

        # --------------------------------------------------------------------------------------------------------
        if (args.version):
            print('--- astrobaseIO.py version = '+ pkg_version + " (last updated " + LAST_UPDATE + ") ---")
            return

        # --------------------------------------------------------------------------------------------------------
        if (args.operation=='specification'):
            do_specification(astrobaseIO,
                             taskid=args.taskid,
                             initial_status=args.status,
                             name = args.field_name,
                             field_name=args.field_name,
                             date=args.date,
                             field_ra=args.field_ra,
                             field_dec=args.field_dec,
                             field_fov=args.field_fov,
                             observing_mode=args.observing_mode,
                             process_type=args.process_type,
                             dataproducts=args.dataproducts,
                             data_location=args.override_data_location
                             )

         # --------------------------------------------------------------------------------------------------------
        if (args.operation == 'ingest'):
            do_ingest(astrobaseIO, args.local_landing_pad, args.local_data_dir)
            if args.interval:
                print('*ingest* starting polling ' + astrobaseIO.host + ' every ' + args.interval + ' secs')
                while True:
                    try:
                        time.sleep(int(args.interval))
                        do_ingest(astrobaseIO, args.local_landing_pad, args.local_data_dir)
                    except:
                        print('*** ingest crashed! ***')
                        print(sys.exc_info()[0])
                        print('trying to continue...')
                        astrobaseIO.send_message_to_apidorn_slack_channel("*ingest service* crashed! ... restarting.")

        # --------------------------------------------------------------------------------------------------------
        if (args.operation == 'submit'):
            do_submit(astrobaseIO, args.local_data_url, args.local_data_dir)
            if args.interval:
                print('*submit* starting polling ' + astrobaseIO.host + ' every ' + args.interval + ' secs')
                while True:
                    try:
                        time.sleep(int(args.interval))
                        do_submit(astrobaseIO, args.local_data_url, args.local_data_dir)
                    except:
                        print('*** submit crashed! ***')
                        print(sys.exc_info()[0])
                        print('trying to continue...')
                        astrobaseIO.send_message_to_apidorn_slack_channel(
                            "*submit service* crashed! ... restarting.")


        # --------------------------------------------------------------------------------------------------------
        if (args.operation == 'processor'):
            try:
                do_processor(astrobaseIO, args.local_data_url, args.local_data_dir)
            except:
                print('*** processor crashed on first run! ***')
                print(sys.exc_info()[0])
                print('trying to continue...')
                astrobaseIO.send_message_to_apidorn_slack_channel("*processor service* crashed on first run! ... trying to continue.")

            if args.interval:
                print('*processor* starting polling ' + astrobaseIO.host + ' every ' + args.interval + ' secs')
                while True:
                    try:
                        time.sleep(int(args.interval))
                        do_processor(astrobaseIO, args.local_data_url, args.local_data_dir)

                    except:
                        print('*** processor crashed! ***')
                        print(sys.exc_info()[0])
                        print('trying to continue...')
                        astrobaseIO.send_message_to_apidorn_slack_channel("*processor * crashed! ... restarting.")

        # --------------------------------------------------------------------------------------------------------
        if (args.operation == 'cleanup'):

            do_cleanup(astrobaseIO, args.local_data_dir)

            if args.interval:
                print(
                    '*cleanup* starting polling ' + astrobaseIO.host + ' every ' + args.interval + ' secs')
                while True:
                    try:
                        time.sleep(int(args.interval))
                        do_cleanup(astrobaseIO, args.local_data_dir)

                    except:
                        print('*** cleanup crashed! ***')
                        print(sys.exc_info()[0])
                        print('trying to continue...')
                        astrobaseIO.send_message_to_apidorn_slack_channel("*cleanup service* crashed! ... restarting.")

        # --------------------------------------------------------------------------------------------------------
        if (args.operation=='change_status'):
            astrobaseIO.do_change_status(resource=args.resource, search_key=args.search_key, status=args.status)

        # --------------------------------------------------------------------------------------------------------
        if (args.operation=='testing'):
            do_test()

        # --------------------------------------------------------------------------------------------------------


    except Exception as exp:
        message = str(exp)
        astrobaseIO.send_message_to_apidorn_slack_channel(message)
        exit_with_error(str(exp))

    sys.exit(0)


if __name__ == "__main__":
    main()

