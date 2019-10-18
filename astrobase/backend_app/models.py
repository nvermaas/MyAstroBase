from django.db import models
from django.urls import reverse
from django.utils.timezone import datetime
from django.db.models import Sum

from django.conf import settings

import os
# constants
datetime_format_string = '%Y-%m-%dT%H:%M:%SZ'

TASK_TYPE_OBSERVATION = 'observation'
TASK_TYPE_DATAPRODUCT = 'dataproduct'

TYPE_RAW = 'raw'
TYPE_PROCESSED = 'processed'
TYPE_ANNOTATED = 'annotated'
TYPE_FITS = 'fits'

# common model functions
def get_sum_from_dataproduct_field(taskID, field):
    """
    sum the values of a field for certain taskID. (used to sum total of dataproduct sizes)
    :param taskID:
    :param field:
    :return:
    """
    query = field + '__sum'
    sum_value = DataProduct.objects.filter(taskID=taskID).aggregate(Sum(field))[query]
    if sum_value == None:
        sum_value = 0.0
    return sum_value

"""
a base class of both Observation and Dataproducts
"""
class TaskObject(models.Model):
    name = models.CharField(max_length=100, default="unknown")
    task_type = models.CharField(max_length=20, default=TASK_TYPE_DATAPRODUCT)

    taskID = models.CharField('taskID', db_index=True, max_length=30, blank=True, null=True)
    creationTime = models.DateTimeField(default=datetime.utcnow, blank=True)

    new_status = models.CharField(max_length=50, default="defined", null=True)
    data_location = models.CharField(max_length=255, default=None, blank=True, null=True)

    # my_status is 'platgeslagen', because django-filters can not filter on a related property,
    # and I need services to be able to filter on a status to execute their tasks.
    my_status = models.CharField(db_index=True, max_length=50,default="defined")
    job = models.CharField(max_length=15, default="", null=True)

    def __str__(self):
        return str(self.id)


class Status(models.Model):
    name = models.CharField(max_length=50, default="unknown")
    timestamp = models.DateTimeField(default=datetime.utcnow, blank=True)
    taskObject = models.ForeignKey(TaskObject, related_name='status_history', on_delete=models.CASCADE, null=False)

    @property
    def property_taskID(self):
        return self.taskObject.taskID

    @property
    def property_task_type(self):
        return self.taskObject.task_type

    # the representation of the value in the REST API
    def __str__(self):
        formatedDate = self.timestamp.strftime(datetime_format_string)
        return str(self.name)+' ('+str(formatedDate)+')'


class Observation(TaskObject):
    date = models.DateTimeField('start time', null=True)
    # can be used to distinguish types of observations, like with powershot G2 or Kitt Peak
    observing_mode = models.CharField(max_length=50, default="digcam")

    # can be used to distinguish types of observations, like for ARTS.
    process_type = models.CharField(max_length=50, default="observation")

    # json object containing unmodelled parameters that are used by the 'executor' service
    # to create the parset based on a template and these parameters
    field_name = models.CharField(max_length=50, null=True)
    field_ra = models.FloatField('field_ra', null = True)
    field_dec = models.FloatField('field_dec', null = True)
    field_fov = models.FloatField('field_fov', null=True)

    quality = models.CharField(max_length=30, default="unknown")

    # this translates a view-name (from urls.py) back to a url, to avoid hardcoded url's in the html templates
    # bad : <td><a href="/astrobase/observations/{{ observation.id }}/" target="_blank">{{ observation.taskID }} </a> </td>
    # good: <td><a href="{{ observation.get_absolute_url }}" target="_blank">{{ observation.taskID }} </a> </td>
    def get_absolute_url(self):
        return reverse('observation-detail-view-api', kwargs={'pk': self.pk})

    @property
    def size(self):
        # sum the sizes of all dataproducts with this taskID. In Mb
        size = get_sum_from_dataproduct_field(self.taskID,'size')
        return size

    def __str__(self):
        return str(self.taskID)


class DataProduct(TaskObject):
    # properties
    filename = models.CharField(max_length=200, default="unknown")
    description = models.CharField(max_length=255, default="unknown")
    dataproduct_type = models.CharField('Dataproduct Type', default=TYPE_RAW, max_length=50)
    size = models.BigIntegerField(default=0)
    quality = models.CharField(max_length=30, default="unknown")

    # relationships
    parent = models.ForeignKey(Observation, related_name='generated_dataproducts', on_delete=models.CASCADE, null=False)

    # this translates a view-name (from urls.py) back to a url, to avoid hardcoded url's in the html templates
    # bad : <td><a href="/astrobase/observations/{{ observation.id }}/" target="_blank">{{ observation.taskID }} </a> </td>
    # good: <td><a href="{{ observation.get_absolute_url }}" target="_blank">{{ observation.taskID }} </a> </td>
    def get_absolute_url(self):
        return reverse('dataproduct-detail-view-api', kwargs={'pk': self.pk})

    def __str__(self):
        return self.filename

    @property
    def property_url(self):
        data_host = settings.DATA_HOST
        directory = os.path.join(data_host, self.taskID)
        path = os.path.join(directory,self.filename)
        return path