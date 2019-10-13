import logging;
import datetime
from django.db.models.signals import pre_save, post_save
from django.core.signals import request_started, request_finished
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from backend_app.models import TaskObject, Observation, DataProduct, Status
from . import jobs

"""
Signals sent from different parts of the backend are centrally defined and handled here.
"""

logger = logging.getLogger(__name__)


#--- HTTP REQUEST signals-------------

@receiver(request_started)
def request_started_handler(sender, **kwargs):
    logger.debug("signal : request_started")


@receiver(request_finished)
def request_finished_handler(sender, **kwargs):
    logger.debug("signal : request_finished")

#--- Observation and DataProduct signals-------------

@receiver(pre_save, sender=Observation)
def pre_save_observation_handler(sender, **kwargs):
    logger.info("SIGNAL : pre_save Observation(" + str(kwargs.get('instance')) + ")")
    handle_pre_save(sender, **kwargs)

@receiver(pre_save, sender=DataProduct)
def pre_save_dataproduct_handler(sender, **kwargs):
    logger.info("SIGNAL : pre_save DataProduct(" + str(kwargs.get('instance')) + ")")
    handle_pre_save(sender, **kwargs)


def handle_pre_save(sender, **kwargs):
    """
    pre_save handler for both Observation and Dataproduct. Mainly to check status changes and dispatch jobs in needed.
    :param (in) sender: The model class that sends the trigger
    :param (in) kwargs: The instance of the object that sends the trigger.
    """
    logger.info("handle_pre_save(" + str(kwargs.get('instance')) + ")")
    myTaskObject = kwargs.get('instance')

    # IF this object does not exist yet, then abort, and let it first be handled by handle_post_save (get get a id).
    if myTaskObject.id==None:
        return None

    # handle status change
    my_status = str(myTaskObject.my_status)
    new_status = str(myTaskObject.new_status)
    if (new_status!=None) and (my_status!=new_status):

        # set the new status
        myTaskObject.my_status = new_status

        # add the new to the status history by brewing a status object out of it
        myStatus = Status(name=new_status, taskObject=myTaskObject)
        myStatus.save()

        #myTaskObject.new_status = None

        # when an observation goes to valid, calculate its total size by counting its dataproducts
        # if (myTaskObject.task_type == 'observation') and 'valid' in myTaskObject.new_status:
        #    # calculate total size
        #    dps = DataProduct.objects.filter(taskID=myTaskObject.taskID)
        #    size = 0
        #    for dp in dps:
        #        size = size + dp.size
        #
        #    logger.info("total size of observation "+myTaskObject.taskID+ " = "+ str(size))
        #    # nv:11jun2019: this requires a database change first
        #    # myTaskObject.size = size

        if (myTaskObject.task_type == 'observation'):
                # convert the utc timestamp to a format that Django REST API understands
                # in its GUI, otherwise null values will be put in when hitting PUT.
                s,_ = str(myStatus.timestamp).split('.')
                myTimestamp = datetime.datetime.strptime(s, "%Y-%m-%d %H:%M:%S")

                if 'starting' in myTaskObject.new_status:
                    myTaskObject.timestamp_starting = myTimestamp
                elif 'running' in myTaskObject.new_status:
                    myTaskObject.timestamp_running = myTimestamp
                elif 'completing' in myTaskObject.new_status:
                    myTaskObject.timestamp_completing = myTimestamp
                elif 'ingesting' in myTaskObject.new_status:
                    myTaskObject.timestamp_ingesting = myTimestamp
                elif 'archived' in myTaskObject.new_status:
                    myTaskObject.timestamp_archived = myTimestamp
                elif 'aborted' in myTaskObject.new_status:
                    myTaskObject.timestamp_aborted = myTimestamp
                elif 'ingest_error' in myTaskObject.new_status:
                    myTaskObject.timestamp_ingest_error = myTimestamp

    # temporarily disconnect the post_save handler to save the dataproduct (again) and avoiding recursion.
    # I don't use pre_save, because then the 'created' key is not available, which is the most handy way to
    # determine if this dataproduct already exists. (I could also check the database, but this is easier).
    disconnect_signals()
    myTaskObject.save()
    connect_signals()

    # dispatch a job if the status has changed.
    if (new_status != None) and (my_status != new_status):
        jobs.dispatchJob(myTaskObject, new_status)


@receiver(post_save, sender=Observation)
def post_save_observation_handler(sender, **kwargs):
    #logger.info("SIGNAL : post_save Observation(" + str(kwargs.get('instance')) + ")")
    handle_post_save(sender, **kwargs)


@receiver(post_save, sender=DataProduct)
def post_save_dataproduct_handler(sender, **kwargs):
    #logger.info("SIGNAL : post_save DataProduct(" + str(kwargs.get('instance')) + ")")
    handle_post_save(sender, **kwargs)


def handle_post_save(sender, **kwargs):
    """
     pre_save handler for both Observation and Dataproduct. To create and write its initial status
    :param (in) sender: The model class that sends the trigger
    :param (in) kwargs: The instance of the object that sends the trigger.
    """
    logger.info("handle_post_save("+str(kwargs.get('instance'))+")")
    myTaskObject = kwargs.get('instance')

    # CREATE NEW OBSERVATION / DATAPRODUCT
    if kwargs['created']:
        logger.info("save new "+str(myTaskObject.task_type))

        # set status
        myTaskObject.my_status = myTaskObject.new_status

        # add the new to the status history by brewing a status object out of it
        myStatus = Status(name=myTaskObject.new_status, taskObject=myTaskObject)
        myStatus.save()

    # if there already is an observation with this taskID, then add this dataproduct to it
    if (myTaskObject.task_type == 'dataproduct'):
        logger.info("update dataproduct parent = " + str(myTaskObject.taskID))
        parent = Observation.objects.get(taskID=myTaskObject.taskID)
        myTaskObject.parent=parent

    # temporarily disconnect the post_save handler to save the dataproduct (again) and avoiding recursion.
    # I don't use pre_save, because then the 'created' key is not available, which is the most handy way to
    # determine if this dataproduct already exists. (I could also check the database, but this is easier).
    disconnect_signals()
    myTaskObject.save()
    connect_signals()

def connect_signals():
    #logger.info("connect_signals")
    pre_save.connect(pre_save_observation_handler, sender=Observation)
    pre_save.connect(pre_save_dataproduct_handler, sender=DataProduct)
    post_save.connect(post_save_observation_handler, sender=Observation)
    post_save.connect(post_save_dataproduct_handler, sender=DataProduct)


def disconnect_signals():
    #logger.info("disconnect_signals")
    pre_save.disconnect(pre_save_observation_handler, sender=Observation)
    pre_save.disconnect(pre_save_dataproduct_handler, sender=DataProduct)
    post_save.disconnect(post_save_observation_handler, sender=Observation)
    post_save.disconnect(post_save_dataproduct_handler, sender=DataProduct)