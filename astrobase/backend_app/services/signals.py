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

    if (myTaskObject.task_type == 'observation'):
        # note that task_type == 'master' will be omitted here
        myObservation = kwargs.get('instance')

        logger.info("update observation = " + str(myObservation.taskID))

        # if this observation has a parent..
        parent = myObservation.parent
        if parent != None:
            if myObservation.field_ra == 0.0:
                myObservation.field_ra = parent.field_ra
            if myObservation.field_dec == 0.0:
                myObservation.field_dec = parent.field_dec
            if myObservation.field_fov == 0.0:
                myObservation.field_fov = parent.field_fov

            if myObservation.observing_mode == "unknown":
                myObservation.observing_mode = parent.observing_mode

            # check if the following values have been set before. If not copy them from the master
            if myObservation.quality == '':
                myObservation.quality = parent.quality

            if myObservation.iso == "none":
                myObservation.iso = parent.iso

                # This is not a bug.
                # Default Focal_length is 200, but I can't check for that default to determine
                # if the value has been initially set or changed. So I piggyback on 'iso' for that.
                # if iso wasn't set, then I assume that focal_length wasn't set either

                myObservation.focal_length = parent.focal_length
                myObservation.stacked_images = parent.stacked_images
                myObservation.date = parent.date

            if myObservation.exposure_in_seconds == 0:
                myObservation.exposure_in_seconds = parent.exposure_in_seconds

            if myObservation.stacked_images == 1:
                myObservation.stacked_images = parent.stacked_images

            if myObservation.image_type == 'other':
                myObservation.image_type = parent.image_type

            # myObservation.save()


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