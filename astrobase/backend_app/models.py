from django.db import models
from django.urls import reverse
from django.utils.timezone import datetime
from django.db.models import Sum

from .services.storage import OverwriteStorage

from django.conf import settings

import os
# constants
datetime_format_string = '%Y-%m-%dT%H:%M:%SZ'

TASK_TYPE_MASTER = 'master'
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
    TASK_TYPE_CHOICES = (
        (TASK_TYPE_MASTER, TASK_TYPE_MASTER),
        (TASK_TYPE_OBSERVATION,TASK_TYPE_OBSERVATION),
        (TASK_TYPE_DATAPRODUCT, TASK_TYPE_DATAPRODUCT),
    )

    name = models.CharField(max_length=100, default="unknown")
    task_type = models.CharField(max_length=20, choices = TASK_TYPE_CHOICES, default=TASK_TYPE_DATAPRODUCT)

    taskID = models.CharField('taskID', db_index=True, max_length=30, blank=True, null=True)
    creationTime = models.DateTimeField(default=datetime.utcnow, blank=True)

    new_status = models.CharField(max_length=50, default="defined", null=True)
    data_location = models.CharField(max_length=255, default=None, blank=True, null=True)

    # my_status is 'platgeslagen', because django-filters can not filter on a related property,
    # and I need services to be able to filter on a status to execute their tasks.
    my_status = models.CharField(db_index=True, max_length=50,default="defined")
    astrometry_url = models.CharField(max_length=50, default="http://nova.astrometry.net", null=True, blank=True)
    job = models.CharField(max_length=15, default="", null=True, blank=True)

    def __str__(self):
        return str(self.taskID) + ' ' + str(self.name)


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
    INSTRUMENT_CHOICES = (
        ("Powershot G2", "Powershot G2"),
        ("Powershot G15", "Powershot G15"),
        ("Canon 350D", "Canon 350D"),
        ("Canon 2000D","Canon 2000D"),
    )

    FILTER_CHOICES = (
        ("None", "None"),
        ("CLS", "CLS"),
    )

    PROCESS_TYPE_CHOICES = (
        ("observation", "observation"),
        ("pipeline","pipeline"),
    )

    ISO_CHOICES = (
        ("none", "none"),
        ("100", "100"),
        ("200","200"),
        ("400", "400"),
        ("800", "800"),
        ("1600", "1600"),
        ("3200", "3200"),
        ("6400", "6400"),
    )

    IMAGE_TYPE_CHOICES = (
        ("solar system", "solar system"),
        ("stars wide angle","stars wide angle"),
        ("stars zoomed-in", "stars zoomed-in"),
        ("deep sky", "deep sky"),
        ("moon", "moon"),
        ("spacecraft", "spacecraft"),
        ("scenery", "scenery"),
        ("technical", "technical"),
        ("event", "event"),
        ("other", "other"),
    )

    date = models.DateTimeField('date', null=True)

    # can be used to distinguish types of observations, like with powershot G2 or Kitt Peak
    instrument = models.CharField(max_length=50, choices = INSTRUMENT_CHOICES, default="Canon 2000D")
    filter = models.CharField(max_length=50, choices = FILTER_CHOICES, default="CLS")

    description = models.CharField(max_length=255, default="", null=True, blank=True)
    url = models.CharField(max_length=100, default="", null=True, blank=True)

    process_type = models.CharField(max_length=50, choices = PROCESS_TYPE_CHOICES, default="observation")

    # json object containing unmodelled parameters that are used by the 'executor' service
    # to create the parset based on a template and these parameters
    field_name = models.CharField(max_length=255, null=True)
    field_ra = models.FloatField('field_ra', null = True)
    field_dec = models.FloatField('field_dec', null = True)
    field_fov = models.FloatField('field_fov', null=True)

    ra_min = models.FloatField('ra_min', null=True, blank=True)
    ra_max = models.FloatField('ra_max', null=True, blank=True)
    dec_min = models.FloatField('dec_min', null=True, blank=True)
    dec_max = models.FloatField('dec_max', null=True, blank=True)
    ra_dec_fov = models.CharField(max_length=30, null=True, blank=True)
    box = models.CharField(max_length=255, null=True, blank=True)

    quality = models.CharField(max_length=30, default="good", null=True)

    # details about the imaging
    iso = models.CharField(max_length=4, null=True, choices = ISO_CHOICES, default="none")
    focal_length = models.IntegerField(default=200)
    exposure_in_seconds = models.IntegerField(default=0)
    stacked_images = models.IntegerField(default=1)
    # magnitude = models.FloatField(null = True, blank=True)
    magnitude = models.CharField(max_length=5, null=True, blank=True)
    image_type = models.CharField(max_length=20, null=True, choices = IMAGE_TYPE_CHOICES, default="other")
    used_in_hips = models.BooleanField(default=True)
    extra = models.TextField(null=True, blank=True)
    transient = models.CharField(max_length=30, null=True, blank=True)

    # relationships
    parent = models.ForeignKey('self', related_name='children', on_delete=models.SET_NULL, null=True, blank=True)

    # this translates a view-name (from urls.py) back to a url, to avoid hardcoded url's in the html templates
    # bad : <td><a href="/astrobase/observations/{{ observation.id }}/" target="_blank">{{ observation.taskID }} </a> </td>
    # good: <td><a href="{{ observation.get_absolute_url }}" target="_blank">{{ observation.taskID }} </a> </td>
    def get_absolute_url(self):
        return reverse('observation-detail-view-api', kwargs={'pk': self.pk})

    @property
    def size(self):
        try:
            # sum the sizes of all dataproducts with this taskID. In Mb
            size = get_sum_from_dataproduct_field(self.taskID,'size')
            return size
        except:
            return None

    @property
    def nr_of_dps(self):
        try:
            # sum the sizes of all dataproducts with this taskID. In Mb
            count = len(DataProduct.objects.filter(taskID=self.taskID))
            return count
        except:
            return None

    @property
    def derived_raw_image(self):
        # get the raw dataproduct

        # find object with 'datasetID'
        try:
            dataproduct = DataProduct.objects.get(dataproduct_type='raw',taskID=self.taskID)
            path = dataproduct.property_url
            return path
        except:
            return None

    @property
    def derived_annotated_image(self):
        # get the annotated dataproduct

        # find object with 'datasetID'
        try:
            dataproduct = DataProduct.objects.get(dataproduct_type='annotated',taskID=self.taskID)
            path = dataproduct.property_url
            return path
        except:
            return None

    @property
    def derived_annotated_transient_image(self):
        # get the annotated grid dataproduct

        # find object with 'datasetID'
        try:
            dataproduct = DataProduct.objects.get(dataproduct_type='annotated_transient',taskID=self.taskID)
            path = dataproduct.property_url
            return path
        except:
            return None

    @property
    def derived_annotated_grid_image(self):
        # get the annotated grid dataproduct

        # find object with 'datasetID'
        try:
            dataproduct = DataProduct.objects.get(dataproduct_type='annotated_grid',taskID=self.taskID)
            path = dataproduct.property_url
            return path
        except:
            return None

    @property
    def derived_annotated_grid_eq_image(self):
        # get the annotated equatorial grid dataproduct

        # find object with 'datasetID'
        try:
            dataproduct = DataProduct.objects.get(dataproduct_type='annotated_grid_eq',taskID=self.taskID)
            path = dataproduct.property_url
            return path
        except:
            return None

    @property
    def derived_annotated_stars_image(self):
        # get the annotated stars dataproduct

        # find object with 'datasetID'
        try:
            dataproduct = DataProduct.objects.get(dataproduct_type='annotated_stars',taskID=self.taskID)
            path = dataproduct.property_url
            return path
        except:
            return None

    @property
    def derived_sky_plot_image(self):
        # get the sky_plot dataproduct

        # find object with 'datasetID'
        try:
            dataproduct = DataProduct.objects.get(dataproduct_type='sky_plot',taskID=self.taskID)
            path = dataproduct.property_url
            return path
        except:
            return None

    @property
    def derived_sky_globe_image(self):
        # get the sky_globe dataproduct

        # find object with 'datasetID'
        try:
            dataproduct = DataProduct.objects.get(dataproduct_type='sky_globe',taskID=self.taskID)
            path = dataproduct.property_url
            return path
        except:
            return None

    @property
    def derived_fits(self):
        # get the sky_globe dataproduct

        # find object with 'datasetID'
        try:
            dataproduct = DataProduct.objects.get(dataproduct_type='fits',taskID=self.taskID)
            path = dataproduct.property_url
            return path
        except:
            return None

    @property
    def derived_parent_taskid(self):
        return self.parent.taskID

    def __str__(self):
        return str(self.taskID) + ' - ' + str(self.name) + ' - ' + str(self.field_name)


# file upload for images to the astrobase landing_pad
def my_directory_path(instance, filename):
    """
    overrides the location where the file is written and adds the provided directory to it.
    :param instance:
    :param filename:
    :return:
    """
    new_filename = instance.new_filename
    if new_filename!="":
        my_file = os.path.join(instance.directory, new_filename)
    else:
        my_file = os.path.join(instance.directory, filename)
    return my_file


# Files to upload (images and inspectionplots)
class AstroFile(models.Model):
    # using a custom 'storage' to overwrite existing files.
    # (because the 'delete' methods do not delete associated images).
    file = models.FileField(upload_to=my_directory_path, storage=OverwriteStorage(), blank=False, null=False)
    new_filename = models.CharField(max_length=80, blank=True)
    directory = models.CharField(max_length=128, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file.name


class DataProduct(TaskObject):
    # properties
    #file = models.FileField(upload_to=my_directory_path, storage=OverwriteStorage(), blank=False, null=False)

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
        path = data_host + '/' + self.taskID + '/' + self.filename

        return path


class Collection(models.Model):
    """
    A way to bundle observations into collections
    """
    COLLECTION_TYPE_CHOICES = (
        ("solar system", "solar system"),
        ("stars wide angle","stars wide angle"),
        ("stars zoomed-in", "stars zoomed-in"),
        ("deep sky", "deep sky"),
        ("moon", "moon"),
        ("spacecraft", "spacecraft"),
        ("scenery", "scenery"),
        ("technical", "technical"),
        ("event", "event"),
        ("other", "other"),
    )

    date = models.DateTimeField('date', null=True)
    name = models.CharField(max_length=100, default="unknown")
    collection_type = models.CharField(max_length=20, null=True, choices = COLLECTION_TYPE_CHOICES, default="other")
    description = models.CharField(max_length=255, default="", null=True, blank=True)

    # relationships
    observations = models.ManyToManyField(Observation)

    def __str__(self):
        return str(self.name)


# job to be executed async by the astrobase_services packages by polling the database
class Job(models.Model):
    creationTime = models.DateTimeField(default=datetime.utcnow, blank=True)
    # relationships
    command = models.CharField(max_length=200, default="", null=True)
    parameters = models.CharField(max_length=200, default="", null=True, blank=True)
    extra = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=50, default="defined", null=True)
    result = models.CharField(max_length=200, default="", null=True, blank=True)

    def __str__(self):
        return str(self.id) + ' - ' + str(self.command) + " (" + self.status + ")"


# only retrieve a limited number of fields for better performance
class ObservationBoxManager(models.Manager):
    def get_queryset(self):
        return super(ObservationBoxManager, self).get_queryset().filter(used_in_hips=True).exclude(box=None)\
            .only('taskID','name','field_ra','field_dec','field_fov','field_name','box','image_type','quality')

# this is a proxy model of Observation with limited fields
class ObservationBox(Observation):
    objects = ObservationBoxManager()

    @property
    def derived_fits(self):
        # get the sky_globe dataproduct

        # find object with 'datasetID'
        try:
            dataproduct = DataProduct.objects.get(dataproduct_type='fits',taskID=self.taskID)
            path = dataproduct.property_url
            return path
        except:
            return None

    class Meta:
        proxy = True

