from django.db import models
from django.urls import reverse
from django.utils.timezone import datetime
from .services.storage import OverwriteStorage
from django.conf import settings

import os
# constants
datetime_format_string = '%Y-%m-%dT%H:%M:%SZ'

TASK_TYPE_MASTER = 'master'
TASK_TYPE_OBSERVATION = 'observation'
TASK_TYPE_DATAPRODUCT = 'dataproduct'


class Observation2(models.Model):
    INSTRUMENT_CHOICES = (
        ("Powershot G2", "Powershot G2"),
        ("Powershot G15", "Powershot G15"),
        ("Canon 350D", "Canon 350D"),
        ("Canon 2000D","Canon 2000D"),
        ("other", "other"),
    )

    FILTER_CHOICES = (
        ("None", "None"),
        ("CLS", "CLS"),
        ("other", "other"),
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

    TASK_TYPE_CHOICES = (
        (TASK_TYPE_MASTER, TASK_TYPE_MASTER),
        (TASK_TYPE_OBSERVATION,TASK_TYPE_OBSERVATION),
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

    date = models.DateTimeField('date', null=True)

    # can be used to distinguish types of observations, like with powershot G2 or Kitt Peak
    instrument = models.CharField(max_length=50, choices = INSTRUMENT_CHOICES, default="Canon 2000D")
    filter = models.CharField(max_length=50, choices = FILTER_CHOICES, default="CLS")

    description = models.CharField(max_length=255, default="", null=True, blank=True)
    url = models.CharField(max_length=100, default="", null=True, blank=True)

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
    size = models.BigIntegerField(null=True, blank=True)
    dps = models.TextField(null=True, blank=True)

    fits = models.CharField(max_length=30, null=True, blank=True)
    annotated_image = models.CharField(max_length=30, null=True, blank=True)
    annotated_transient_image = models.CharField(max_length=40, null=True, blank=True)
    annotated_exoplanets_image = models.CharField(max_length=40, null=True, blank=True)
    annotated_grid_image = models.CharField(max_length=40, null=True, blank=True)
    annotated_grid_eq_image = models.CharField(max_length=40, null=True, blank=True)
    annotated_stars_image = models.CharField(max_length=40, null=True, blank=True)
    sky_plot_image = models.CharField(max_length=30, null=True, blank=True)
    sky_globe_image = models.CharField(max_length=30, null=True, blank=True)

    transient = models.CharField(max_length=30, null=True, blank=True)

    # relationships
    parent = models.ForeignKey('self', related_name='children', on_delete=models.SET_NULL, null=True, blank=True)

    # this translates a view-name (from urls.py) back to a url, to avoid hardcoded url's in the html templates
    # bad : <td><a href="/astrobase/observations/{{ observation.id }}/" target="_blank">{{ observation.taskID }} </a> </td>
    # good: <td><a href="{{ observation.get_absolute_url }}" target="_blank">{{ observation.taskID }} </a> </td>
    def get_absolute_url(self):
        return reverse('observation2-detail-view-api', kwargs={'pk': self.pk})

    @property
    def derived_base_url(self):
        data_host = settings.DATA_HOST
        path = data_host + '/' + self.taskID
        return path

    @property
    def derived_raw_image(self):
        try:
            data_host = settings.DATA_HOST
            path = data_host + '/' + self.taskID + '/' + str(self.taskID)+"_raw.jpg"
            return path
        except:
            return None

    @property
    def derived_fits(self):
        if self.fits == None:
            return None
        try:
            data_host = settings.DATA_HOST
            path = data_host + '/' + self.taskID + '/' + str(self.fits)
            return path
        except:
            return None

    @property
    def derived_annotated_image(self):
        if self.annotated_image == None:
            return None
        try:
            data_host = settings.DATA_HOST
            path = data_host + '/' + self.taskID + '/' + str(self.annotated_image)
            return path
        except:
            return None

    @property
    def derived_annotated_transient_image(self):
        if self.annotated_transient_image == None:
            return None
        try:
            data_host = settings.DATA_HOST
            path = data_host + '/' + self.taskID + '/' + str(self.annotated_transient_image)
            return path
        except:
            return None

    @property
    def derived_annotated_exoplanets_image(self):
        if self.annotated_exoplanets_image == None:
            return None
        try:
            data_host = settings.DATA_HOST
            path = data_host + '/' + self.taskID + '/' + str(self.annotated_exoplanets_image)
            return path
        except:
            return None

    @property
    def derived_annotated_grid_image(self):
        if self.annotated_grid_image == None:
            return None
        try:
            data_host = settings.DATA_HOST
            path = data_host + '/' + self.taskID + '/' + str(self.annotated_grid_image)
            return path
        except:
            return None

    @property
    def derived_annotated_grid_eq_image(self):
        if self.annotated_grid_eq_image == None:
            return None
        try:
            data_host = settings.DATA_HOST
            path = data_host + '/' + self.taskID + '/' + str(self.annotated_grid_eq_image)
            return path
        except:
            return None

    @property
    def derived_annotated_stars_image(self):
        if self.annotated_stars_image == None:
            return None
        try:
            data_host = settings.DATA_HOST
            path = data_host + '/' + self.taskID + '/' + str(self.annotated_stars_image)
            return path
        except:
            return None

    @property
    def derived_sky_plot_image(self):
        if self.sky_plot_image == None:
            return None
        try:
            data_host = settings.DATA_HOST
            path = data_host + '/' + self.taskID + '/' + str(self.sky_plot_image)
            return path
        except:
            return None

    @property
    def derived_sky_globe_image(self):
        if self.sky_globe_image == None:
            return None
        try:
            data_host = settings.DATA_HOST
            path = data_host + '/' + self.taskID + '/' + str(self.sky_globe_image)
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


class Collection2(models.Model):
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
    observations = models.ManyToManyField(Observation2)

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
class Observation2BoxManager(models.Manager):
    def get_queryset(self):
        return super(Observation2BoxManager, self).get_queryset().filter(used_in_hips=True).exclude(box=None)\
            .only('taskID','name','field_ra','field_dec','field_fov','field_name','box','image_type','quality')


# this is a proxy model of Observation with limited fields
class Observation2Box(Observation2):
    objects = Observation2BoxManager()

    @property
    def derived_fits(self):
        try:
            data_host = settings.DATA_HOST
            path = data_host + '/' + self.taskID + '/' + str(self.fits)
            return path
        except:
            return None

    class Meta:
        proxy = True
