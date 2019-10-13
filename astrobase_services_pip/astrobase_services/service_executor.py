"""
    File name: service_executor.py
    Author: Nico Vermaas - Astron
    Date created: 2018-11-23
    Date last modified: 2018-12-14
    Description:  checks for scheduled observations. When the specified starttime is almost reached,
                  a parset is put on the messagebus so the system can start, and the status in ATDB is set to running.
                  This will happen 10 minutes before the actual starttime when the telescopes are free,
                  or 1 minute before the actual starttime when there is already a running observation.
                  The executor also checks for running observations.
                  When the specified endtime is reached this service waits for 30 seconds and then sets
                  the ATDB status to 'completing' (for imaging) or 'combine' (for arts_sc1)
"""
import os
import time
import datetime


try:
    #import atdb_parset_generator as atdb_parset_generator

    # the dependency on the messagebus (needs to be installed on the system where the executor runs
    from apertif.messaging.RPC import RPCWrapper
    #from apertif.messaging.send_file import send_and_wait_files

    skip_parset_generator = False
except Exception as e:
    skip_parset_error_message = "ERROR: apertif.messaging.RPC could not be loaded :" + str(e) + \
                                "\nContinuing without parset generation/start observation"
    skip_parset_generator = True



# T = 11 minute, start the parset generation.
MINUTES_LEFT_TO_START_PARSET_DEFAULT = 10
MINUTES_LEFT_TO_START_PARSET_IF_RUNNING = 1
COMPLETING_ERROR_TRESHOLD = -15
COMPLETING_ERROR_TRESHOLD_IMAGING = -1

STATUS_SCHEDULED      = 'scheduled'   # the statusses that trigger this service.
STATUS_STARTING       = 'starting'
STATUS_RUNNING        = 'running'
STATUS_COMBINE        = 'combine'
STATUS_COMPLETING     = 'completing'  # this service will leave the observation in this state
STATUS_ERROR_NO_COMPLETING     = 'error (no completing)'  # this service will leave the observation in this state

# --- Helper Function ---------------------------------------------------------------------------------------------
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

def send_parset_to_bus(parset_path, timeout=20.0):
    """
    Send parset to the bus and wait for response
    :param parset_path: path to the parset file
    :param timeout: number of seconds to wait for responses from controllers (opt)
    :return: reply: reply from the bus for this parset file
    """
    reply = send_and_wait_files(parset_path, timeout=timeout)
    reply = reply[parset_path]
    return reply


def get_minutes_left(atdb, target_timestring):
    """
    Determine how many minutes is left until the target_time is reached
    :param target_timestring: The target time defined as string "YYYY-MM-DDThh:mm:ss"
    :return: minutes left
             A negative number of minutes means that the current time has already reached the target_time,
             there is no time left.
              A positive number of minutes means that there is still time left
    """
    now = datetime.datetime.utcnow()
    target_time = datetime.datetime.strptime(target_timestring, atdb.TIME_FORMAT)

    # Convert to Unix timestamp
    d1_ts = time.mktime(now.timetuple())
    d2_ts = time.mktime(target_time.timetuple())
    minutes_left = round(((d2_ts - d1_ts) / 60), 2)

    return minutes_left

@timeit
def start_observation(atdb, taskID):
    """
    Start the observation by:
    - creating a parset file from template (location)
    - sending the generated parset file to message bus (not in testmode)
    - set status of the observation to 'starting'
    :param atdb: Instance of atdb
    :param taskID: The taskID of the observation to start
    """
    atdb.report('*executor* : start_observation :' + taskID, "slack")

    # Get all observation parameters
    observation = atdb.atdb_interface.do_GET_Observation(taskID)

    parset_template = observation['parset_location']
    parset_dir, _ = os.path.split(parset_template)


    if not atdb.testmode:
        # Make (blocking) RPC call to parset_rpc service to
        # generate the parset for the specified observation.

        # nv: 23 may 2019 This is a temporary switch to enable/disable the previous API of the parset_generator
        new_new_parset = True
        if new_new_parset:
            # KJW 25 jun 2019. Increase timeout to 30s (>> 20.0 = timeout in parset_rpc)
            # to ensure that the RPC call doesn't timeout before parset_rpc.
            with RPCWrapper('APERTIF', 'ParsetRPC', timeout=30.0) as parset_rpc:
                parset_file = parset_rpc.rpc(
                                'send_start_observation',
                                observation,
                                template_path=parset_template,
                                parset_dir=parset_dir)
            atdb.report('*executor* : created and sent (new new) parset ' + parset_file, "slack")

        else:
            # nv: 23 may 2019 keep this alive for imaging as long as no new Apertif software is deployed
            with RPCWrapper('APERTIF', 'ParsetRPC') as parset_rpc:
                parset_file = parset_rpc.rpc(
                                'create_start_observation_parset',
                                observation,
                                template_path=parset_template,
                                parset_dir=parset_dir)
            atdb.report('*executor* : created and sent (old new) parset ' + parset_file, "slack")

            time.sleep(int(5)) # Vanessa wants 5 seconds, KJ wants no seconds
            reply = str(send_parset_to_bus(str(parset_file)))
            atdb.report('*executor* : sent parset to messagebus ', "slack")

            # when the file isn't shared over nfs fast enough we could have an error
            if "Error" in reply:
                # {'status': 'Error', 'error_messages': 'Unable to open file /opt/apertif/share/parsets/190509039.parset'}
                message = "*executor* : WARNING " + reply +", retrying..."
                atdb.report(message, "slack")
                return

        atdb.atdb_interface.do_PUT(key='observations:new_status', id=None, taskid=taskID, value=STATUS_STARTING)
        message = "*executor* :" + taskID + " " + STATUS_STARTING
    else:
        atdb.atdb_interface.do_PUT(key='observations:new_status', id=None, taskid=taskID, value=STATUS_STARTING)
        message = "*executor* :" + taskID + " " + STATUS_STARTING + ' (testmode)'

    atdb.report(message,"slack")

    # take a short breath to give this status a chance to arrive in ATDB,
    # to prevent an occasional race condition with the next step for observations that
    # are timed less than a minute apart.. (just to be on the safer side).
    time.sleep(int(3))

@timeit
def end_observation(atdb, taskID, minutes_left):

    observing_mode  = atdb.atdb_interface.do_GET(key='observations:observing_mode', id=None, taskid=taskID)
    if ('ARTS_SC4' in observing_mode.upper()):
        # nv: 1 feb 2019, from now on the ARTS controller will send the 'completing' message.
        atdb.report("*executor* : " + taskID + " expecting ARTS_SC4 controller to send " + STATUS_COMPLETING,"slack")

    elif ('ARTS_SC1' in observing_mode.upper()):
        # nv: 13 may 2019, from now on the ARTS controller will send the 'completing' message.
        atdb.report("*executor* : " + taskID + " expecting ARTS_SC1 controller to send " + STATUS_COMPLETING,"slack")

    elif ('IMAGING' in observing_mode.upper()):
        #atdb.report('go to sleep for 30 seconds to give the datawriter time to complete writing...','print')
        #time.sleep(int(30))
        #atdb.atdb_interface.do_PUT(key='observations:new_status', id=None, taskid=taskID, value=STATUS_COMPLETING)
        #atdb.report("*executor* : " + taskID + " " + STATUS_COMPLETING,"slack")

        # nv: 27 feb 2019, from now on the IMAGING controller will send the 'completing' message. (deactivated the next day)
        # nv: 27 may 2019, reactivated it.
        atdb.report("*executor* : " + taskID + " expecting datawriter_control to send " + STATUS_COMPLETING,"slack")

        # the imaging backstop for backward compatiliby
        # if the controller has not sent 'completing' after 1 minute, then I do it.
        if (minutes_left < COMPLETING_ERROR_TRESHOLD_IMAGING):
            # arts sc1, prepare observation to be picked up by the 'combine' service. Only for 'arts_sc1_timing'
            atdb.atdb_interface.do_PUT(key='observations:new_status', id=None, taskid=taskID, value=STATUS_COMPLETING)
            atdb.report("*executor* : imaging backstop, " + taskID + " " + STATUS_COMPLETING, "slack")

    # the backstop
    # if the controller has not sent 'completing' after 15 minutes, then set an error
    if (minutes_left < COMPLETING_ERROR_TRESHOLD):
        # arts sc1, prepare observation to be picked up by the 'combine' service. Only for 'arts_sc1_timing'
        atdb.atdb_interface.do_PUT(key='observations:new_status', id=None, taskid=taskID, value=STATUS_ERROR_NO_COMPLETING)
        atdb.report("*executor* : backstop, " + taskID + " " + STATUS_ERROR_NO_COMPLETING, "slack")


def get_minutes_left_to_start_parset(atdb):
    # This is where the 'algorithm' is called to determine how much time is needed for the telescopes to slew
    # into position between observations. To be expanded later.

    # default
    minutes_left = MINUTES_LEFT_TO_START_PARSET_DEFAULT

    # check if there are 'running' or 'starting' observations. If so, change the slew time.
    query = 'my_status__in=' + STATUS_STARTING + ',' + STATUS_RUNNING + '&observing_mode__icontains=' + atdb.obs_mode_filter
    taskIDs = atdb.atdb_interface.do_GET_LIST(key='observations:taskID', query=query)
    if len(taskIDs) > 0:
        minutes_left = MINUTES_LEFT_TO_START_PARSET_IF_RUNNING

    atdb.report('parset starting window = ' + str(minutes_left))
    return minutes_left


@timeit
def handle_running_to_completing(atdb):
    # get the list taskID of 'running' observations for the required obs_mode_filter (arts, imaging or all)
    query = 'my_status=' + STATUS_RUNNING + '&observing_mode__icontains=' + atdb.obs_mode_filter
    taskIDs = atdb.atdb_interface.do_GET_LIST(key='observations:taskID', query=query)
    if len(taskIDs) > 0:
        atdb.report('*executor* found the following ' + STATUS_RUNNING + ' tasks : ' + str(taskIDs))

    # loop through the 'running' observations and check if they should be 'completed'
    for taskID in taskIDs:
        # check if their endtime has arrived.
        endtime = atdb.atdb_interface.do_GET(key='observations:endtime', id=None, taskid=taskID)
        minutes_left = get_minutes_left(atdb, endtime)
        atdb.report(taskID + ' completing in ' + str(minutes_left) + ' minutes... and counting')

        # T = 0 minute, complete the observation.
        if minutes_left < 0:
            end_observation(atdb, taskID, minutes_left)

@timeit
def handle_starting_to_running(atdb):
    query = 'my_status=' + STATUS_STARTING + '&observing_mode__icontains=' + atdb.obs_mode_filter
    taskIDs = atdb.atdb_interface.do_GET_LIST(key='observations:taskID', query=query)
    if len(taskIDs) > 0:
        atdb.report('*executor* found the following ' + STATUS_STARTING + ' tasks : ' + str(taskIDs))

        # loop through the 'started' observations
        for taskID in taskIDs:
            # check if their starttime has arrived.
            starttime = atdb.atdb_interface.do_GET(key='observations:starttime', id=None, taskid=taskID)
            minutes_left = get_minutes_left(atdb, starttime)
            if minutes_left < 0:
                atdb.atdb_interface.do_PUT(key='observations:new_status', id=None, taskid=taskID, value=STATUS_RUNNING)
                atdb.report("*executor* : " + taskID + " " + STATUS_RUNNING,"slack")


def get_next_scheduled_observation(atdb):
    # for which datawriter? split off the 'wcudata1:/' or 'wcudata2:/' from the data_location
    datawriter = ""
    next_taskID, next_minutes_left = atdb.atdb_interface.do_GET_NextObservation(STATUS_SCHEDULED, atdb.obs_mode_filter, datawriter)
    return next_taskID,next_minutes_left


@timeit
def handle_scheduled_to_starting(atdb):

    # get the next scheduled observation (if any).
    taskID, minutes_left = get_next_scheduled_observation(atdb)

    if taskID!=None:
        atdb.report("*executor* : next scheduled observation is "+str(taskID)+" in "+str(minutes_left)+ " minutes.")

        # T = -11 minute, start the parset generation.
        # TODO: should there be an upper limit also where observations are too late to be put on 'running'?
        #       Comment Boudewijn: yes: that should be the time required to get the message to the controller
        #                          My estimate would be 3 seconds

        if minutes_left < get_minutes_left_to_start_parset(atdb):

            if minutes_left < -1:
                # too late to start
                atdb.atdb_interface.do_PUT(key='observations:new_status', id=None, taskid=taskID,
                                           value='error (too late)' + '')
                atdb.report("ERROR by *executor*: " + taskID + " too late to start. Aborted.","slack")

                # recursion!
                # when an observation is 'too late' then find the next one within the same heartbeat
                handle_scheduled_to_starting(atdb)

                return

            if not skip_parset_generator:
                try:
                    start_observation(atdb, taskID)
                except Exception as err:
                    # nv: 3 jun 2019, when the parset_rpc times out, the observation ends in a error state,
                    # but there is probably still more than enough time to try again. So put it back on 'scheduled' and
                    # see if the next 'heartbeat' is more succsful... )report the error though)
                    # atdb.atdb_interface.do_PUT(key='observations:new_status', id=None, taskid=taskID, value=STATUS_SCHEDULED)
                    # atdb.report("ERROR by *executor* in parset_generator: " + str(err)+', retrying...', "slack")

                    # KJW: 25 jun 2019. When parset_rpc times out it is not safe to retry since
                    # the start_observation is probably half done (i.e. on some but not all telescopes/controllers).
                    # Not all controllers can handle another start_observation for the same observation. Simply give up.
                    atdb.atdb_interface.do_PUT(key='observations:new_status', id=None, taskid=taskID, value='error (start obs)')
                    atdb.report("ERROR by *executor*: " + taskID + " error starting observation. " + str(err), "slack")
                    return

            else:
                atdb.report("*executor* : "+skip_parset_error_message,"slack")
                atdb.atdb_interface.do_PUT(key='observations:new_status', id=None, taskid=taskID, value=STATUS_STARTING)
                atdb.report("*executor* : "+taskID+" "+STATUS_STARTING+" (skip parset_generator)","slack")

# --- Main Service -----------------------------------------------------------------------------------------------

def do_executor(atdb):

    # --- from RUNNING to COMPLETING  ------------------------
    # loop through 'running observations' and complete them when their endtime has arrived.
    # note that the end status is different for imaging (completing) and arts_sc1 (combine).
    handle_running_to_completing(atdb)

    # --- from STARTING to RUNNING  ------------------------
    # get the list taskID of 'running' observations for the required obs_mode_filter (arts, imaging or all)
    handle_starting_to_running(atdb)

    # --- from SCHEDULED to STARTING  ------------------------
    # get the list taskID of 'scheduled' observations for the required obs_mode_filter (arts, imaging or all)
    handle_scheduled_to_starting(atdb)
