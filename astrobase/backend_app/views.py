import logging
import json
import os

from . import config
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import ListView

from rest_framework import generics, pagination, status, viewsets
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, FileUploadParser
from rest_framework.views import APIView

from django_filters import rest_framework as filters
from django.shortcuts import render, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.db.models import Q

from .models import Observation2, AstroFile, Collection2, Job, Observation2Box, Cutout, CutoutDirectory
from .serializers import Observation2Serializer, AstroFileSerializer, Collection2Serializer, JobSerializer, \
    Observation2BoxSerializer, CutoutSerializer, CutoutDirectorySerializer \

from .forms import FilterForm
from .services import algorithms, jobs

logger = logging.getLogger(__name__)

# ---------- filters (in the REST API) ---------

# example: /my_astrobase/observations/?observing_mode__icontains=powershot_g2
class Observation2Filter(filters.FilterSet):

    # example of an OR filter.
    # this filters a range of fields for the given value of 'fieldsearch='.
    # example: http://localhost:8000/my_astrobase/observations/?fieldsearch=aurora
    fieldsearch = filters.CharFilter(field_name='fieldsearch', method='search_my_fields')

    # example: http://localhost:8000/my_astrobase/observations/?coordsearch=212,48
    coordsearch = filters.CharFilter(field_name='coordsearch', method='search_my_coords')

    def search_my_fields(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value) | Q(field_name__icontains=value) |
            Q(quality__icontains=value)| Q(my_status__icontains=value)|
            Q(taskID__icontains=value) | Q(parent__taskID__icontains=value)
        )

    def search_my_coords(self, queryset, name, value):
        # value is a comma separated decimal RA,dec coordinate
        # chain the filters to create a query to find the coordinate in the bounding box of observations
        try:
            ra,dec = value.split(',')
        except:
            ra, dec = value.split(' ')

        search_ra = float(ra.strip())
        search_dec = float(dec.strip())
        q = queryset.filter(ra_min__lte=search_ra)\
            .filter(ra_max__gte=search_ra)\
            .filter(dec_min__lte=search_dec)\
            .filter(dec_max__gte=search_dec)
        return q

    class Meta:
        model = Observation2

        fields = {
            'id': ['exact', 'in'],
            'instrument': ['exact', 'in', 'icontains'],
            'filter': ['exact', 'in', 'icontains'],
            'task_type': ['exact', 'in', 'icontains'],  #
            'field_name': ['gt', 'lt', 'gte', 'lte', 'icontains', 'exact','in'],
            'field_ra': ['gt', 'lt', 'gte', 'lte', 'contains', 'exact'],
            'field_dec': ['gt', 'lt', 'gte', 'lte', 'contains', 'exact'],
            'field_fov': ['gt', 'lt', 'gte', 'lte', 'contains', 'exact'],
            'ra_min': ['gt', 'lt', 'gte', 'lte'],
            'ra_max': ['gt', 'lt', 'gte', 'lte'],
            'dec_min': ['gt', 'lt', 'gte', 'lte'],
            'dec_max': ['gt', 'lt', 'gte', 'lte'],
            'name': ['exact', 'icontains','in'],
            'description': ['exact', 'icontains', 'in'],
            'my_status': ['exact', 'icontains', 'in', 'startswith'],          #/my_astrobase/observations?&my_status__in=archived,removing
            'taskID': ['gt', 'lt', 'gte', 'lte','exact', 'icontains', 'startswith','in'],
            'creationTime' : ['gt', 'lt', 'gte', 'lte', 'contains', 'exact'],
            'date' : ['gt', 'lt', 'gte', 'lte', 'contains', 'exact'],
            'data_location': ['exact', 'icontains'],
            'quality': ['exact', 'icontains','in'],
            'exposure_in_seconds' : ['gt', 'lt', 'gte', 'lte', 'contains', 'exact'],
            'iso': ['gt', 'lt', 'gte', 'lte', 'contains', 'exact'],
            'focal_length': ['gt', 'lt', 'gte', 'lte', 'contains', 'exact'],
            'stacked_images' : ['gt', 'lt', 'gte', 'lte', 'contains', 'exact'],
            'magnitude' : ['gt', 'lt', 'gte', 'lte', 'contains', 'exact'],
            'image_type': ['icontains', 'exact'],
            'used_in_hips': ['exact'],
            #'fieldsearch': ['exact', 'icontains', 'in'],
            #'coordsearch': ['exact'],

        }


class Collection2Filter(filters.FilterSet):

    # example of an OR filter.
    # this filters a range of fields for the given value of 'fieldsearch='.
    # example: http://localhost:8000/my_astrobase/observations/?fieldsearch=aurora
    fieldsearch = filters.CharFilter(field_name='fieldsearch', method='search_my_fields')

    def search_my_fields(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value) | Q(description__icontains=value)
        )

    class Meta:
        model = Collection2

        fields = {
            'description': ['exact', 'icontains'],
            'name': ['exact', 'icontains'],
            'collection_type': ['icontains', 'exact'],
            # 'fieldsearch': ['exact', 'icontains', 'in']
        }


# example: /my_astrobase/dataproducts?status__in=created,archived
class JobFilter(filters.FilterSet):

    class Meta:
        model = Job

        fields = {
            'status': ['exact', 'icontains', 'in'],
        }

# example: /my_astrobase/cutouts?status__in=created,archived
class CutoutFilter(filters.FilterSet):

    class Meta:
        model = Cutout

        fields = {
            'field_name': ['exact', 'icontains', 'in'],
            'directory' : ['exact', 'icontains'],
            'visible': ['exact'],
            'delete': ['exact'],
            'status': ['exact', 'icontains', 'in'],
            'observation_quality': ['exact', 'icontains', 'in'],
            'cutout_quality': ['exact', 'icontains', 'in'],
        }


# this uses a form
def do_filter(request):

    if request.method == 'GET':
        # create a form instance and populate it with data from the request:
        form = FilterForm(request.POST)
        if form.is_valid():
            status = form.cleaned_data.get('status')
            #observations = get_filtered_observations()
            return HttpResponseRedirect('/my_astrobase/')
    else:
        form = FilterForm

    return render(request, 'backend_app/index.html', {'my_form': form})

# ---------- GUI Views -----------

class IndexView(ListView):
    """
    This is the main view of astrobase. It shows a pagination list of observations, sorted by creationTime.
    """
    template_name = 'backend_app/index.html'

    # by default this returns the list in an object called object_list, so use 'object_list' in the html page.
    # but if 'context_object_name' is defined, then this returned list is named and can be accessed that way in html.
    context_object_name = 'my_observations'

    def get_queryset(self):

        my_status = self.request.GET.get('my_status')
        not_my_status = self.request.GET.get('not_my_status')
        search_box = self.request.GET.get('search_box', None)

        if (search_box is not None):
            observations = get_searched_observations(search_box)
        else:
            #observations = Observation.objects.order_by('-taskID')
            observations = Observation2.objects.order_by('-date')
        if (my_status is not None):
            observations = get_filtered_observations(my_status)
        if (not_my_status is not None):
            observations = get_unfiltered_observations(not_my_status)

        paginator = Paginator(observations, config.OBSERVATIONS_PER_PAGE)  # Show 50 observations per page

        page = self.request.GET.get('page')

        try:
            observations = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            observations = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            observations = paginator.page(paginator.num_pages)

        return observations

# an attempt to get a filtering mechanism in the GUI
# filter on a single status
# http://localhost:8000/my_astrobase/query?my_status=scheduled
def get_filtered_observations(my_status):
    q = Observation2.objects.order_by('-date')
    q = q.filter(my_status=my_status)
    #q = q.exclude(my_status__icontains='removed')
    return q

# http://localhost:8000/my_astrobase/query?not_my_status=removed
def get_unfiltered_observations(my_status):
    q = Observation2.objects.order_by('-date')
    q = q.exclude(my_status=my_status)
    return q

def get_searched_observations(search):
    observations = Observation2.objects.filter(
        Q(taskID__contains=search) |
        Q(parent__taskID__contains=search) |
        Q(my_status__icontains=search) |
        Q(field_name__icontains=search)).order_by('-date')
    return observations


# a custom pagination class to return more than the default 100 dataproducts
class NoPagination(pagination.PageNumberPagination):
    page_size = 10000

# ---------- REST API views -----------

class Observation2ListViewAPI(generics.ListCreateAPIView):
    """
    A pagination list of observations, sorted by date.
    """
    model = Observation2
    queryset = Observation2.objects.all().order_by('-date')
    serializer_class = Observation2Serializer

    # using the Django Filter Backend - https://django-filter.readthedocs.io/en/latest/index.html
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = Observation2Filter


class Observation2DetailsViewAPI(generics.RetrieveUpdateDestroyAPIView):
    """
    Detailed view of an observation.
    """
    model = Observation2
    queryset = Observation2.objects.all()
    serializer_class = Observation2Serializer

class CollectionPagination(pagination.PageNumberPagination):
    page_size = 10


class Collection2ListViewAPI(generics.ListCreateAPIView):
    """
    A pagination list of Collections, sorted by date.
    """
    model = Collection2
    queryset = Collection2.objects.all().order_by('-date')
    serializer_class = Collection2Serializer
    pagination_class = CollectionPagination

    # using the Django Filter Backend - https://django-filter.readthedocs.io/en/latest/index.html
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = Collection2Filter


# example: /my_astrobase/Collections/5/
# calling this view serializes an Collection in the REST API
class Collection2DetailsViewAPI(generics.RetrieveUpdateDestroyAPIView):
    """
    Detailed view of an Collection2.
    """
    model = Collection2
    queryset = Collection2.objects.all()
    serializer_class = Collection2Serializer


# example: /my_astrobase/projects/
# calling this view serializes the projects list in a REST API
class ProjectListViewAPI(generics.ListCreateAPIView):
    """
    A pagination list of projects, sorted by date
    """

    # a projects is a observation
    model = Observation2
    queryset = Observation2.objects.filter(task_type='master').order_by('-date')
    serializer_class = Observation2Serializer

    # using the Django Filter Backend - https://django-filter.readthedocs.io/en/latest/index.html
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = Observation2Filter


# example: /my_astrobase/Jobs/
# calling this view serializes the Jobs list in a REST API
class JobListViewAPI(generics.ListCreateAPIView):
    """
    A pagination list of Jobs, sorted by date.
    """
    model = Job
    queryset = Job.objects.all()
    serializer_class = JobSerializer

    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = JobFilter


# example: /my_astrobase/Jobs/5/
# calling this view serializes an Job in the REST API
class JobDetailsViewAPI(generics.RetrieveUpdateDestroyAPIView):
    """
    Detailed view of an Job.
    """
    model = Job
    queryset = Job.objects.all()
    serializer_class = JobSerializer

# --- Command views, triggered by a button in the GUI or directoy with a URL ---
# set observation status to 'new_status' - called from the GUI
# example: 'Schedule', 'Unschedule', 'Ready to Ingest', 'Remove Data'


def ObservationSetStatus(request,pk,new_status,page):
    model = Observation2
    observation = Observation2.objects.get(pk=pk)
    observation.new_status = new_status
    observation.save()
    return redirect('/my_astrobase/?page='+page)


def ObservationSetQuality(request,pk,quality,page):
    model = Observation2
    observation = Observation2.objects.get(pk=pk)
    observation.quality = quality
    observation.save()
    return redirect('/my_astrobase/?page='+page)


def ObservationSetHips(request,pk,hips,page):
    model = Observation2
    observation = Observation2.objects.get(pk=pk)
    observation.used_in_hips = hips
    observation.save()
    return redirect('/my_astrobase/?page='+page)

def ObservationSetTaskType(request,pk,type,page):
    model = Observation2
    observation = Observation2.objects.get(pk=pk)
    observation.task_type = type
    observation.save()
    return redirect('/my_astrobase/?page='+page)


# get the next taskid based on starttime and what is currently in the database
#/my_astrobase/get_next_taskid?timestamp=2019-04-05
class GetNextTaskIDView(generics.ListAPIView):
    queryset = Observation2.objects.all()

    # override list and generate a custom response
    def list(self, request, *args, **kwargs):

        # read the arguments from the request
        try:
            timestamp = self.request.query_params['timestamp']
        except:
            timestamp = None

        # read the arguments from the request
        try:
            taskid_postfix = self.request.query_params['taskid_postfix']
        except:
            taskid_postfix = None

        # call the business logic
        taskID = algorithms.get_next_taskid(timestamp, taskid_postfix)

        # return a response
        return Response({
            'taskID': taskID,
        })


# add dataproducts as a batch
# /my_astrobase/post_dataproducts&taskid=190405034
class PostDataproductsView(generics.CreateAPIView):
    queryset = Observation2.objects.all()
    pagination_class = NoPagination

    def post(self, request, *args, **kwargs):
        # read the arguments from the request
        try:
            taskID = self.request.query_params['taskID']
        except:
            taskID = None

        try:
            body_unicode = request.body.decode('utf-8')
            dataproducts = json.loads(body_unicode)
        except:
            dataproducts = None

        taskID = algorithms.add_dataproducts(taskID, dataproducts)

        # return a response
        return Response({
            'taskID': taskID,
        })


# overview of the uploads
class UploadsView(generics.ListCreateAPIView):
    serializer_class = AstroFileSerializer
    queryset = AstroFile.objects.all()


# overview of the uploads
class UploadsDetailsView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AstroFileSerializer
    queryset = AstroFile.objects.all()


# view for uploading images to the 'landing_pad website
class UploadFileView(APIView):
    # https://stackoverflow.com/questions/4894976/django-custom-file-storage-system
    parser_classes = (MultiPartParser, FormParser, FileUploadParser)
    serializer_class = AstroFileSerializer
    queryset = AstroFile.objects.all()

    def post(self, request, *args, **kwargs):
        # http://www.django-rest-framework.org/api-guide/parsers/
        logger.info('UploadFileView.post()')

        file_serializer = AstroFileSerializer(data=request.data)

        if file_serializer.is_valid():
            file_serializer.save()
            return Response(file_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def get_queryset_auth(object, my_model_class, process_type=None):
    """
    This is a global function that can be used to override the get_queryset for a model
    It is specifically used to return a different queryset for anonymous or authenticated users based

    :param object:
    :param my_model_class:
    :return:
    """
    user = str(object.request.user)
    auth = str(object.request.auth)
    logger.info("user (auth) : " + user + ' (' + auth + ')')

    # Authorisation: Anonymous users only see 'public' dataproducts
    if (object.request.user.is_superuser):
        # superusers can use all commands
        queryset = my_model_class.objects.all()
    else:
        queryset = my_model_class.objects.filter(rights='anonymous')

    return queryset


# run an external command
# /my_astrobase/run-command/?command=foo&observation_id=1
class RunCommandView(generics.ListAPIView):
    serializer_class = JobSerializer
    queryset = Job.objects.all()
    # commands can only be run by authenticated users (me)
    # permission_classes = (IsAuthenticated,)

    def list(self, request, *args, **kwargs):
        # read the arguments from the request
        try:
            command = self.request.query_params['command']
        except:
            command = None

        try:
            observation_id = self.request.query_params['observation_id']
        except:
            observation_id = None

        try:
            params = self.request.query_params['params']
        except:
            params = None

        # result = "jobs can only be executed by authenticated users"
        # if self.request.user.is_superuser:
        result = jobs.dispatch_job(command, observation_id, params)

        # return a response

        return Response({
            'command': command,
            'observation_id' : observation_id,
            'params': params,
            'result' : result
        })

# Observation Coordinates for Aladin
class Observation2BoxesListView(generics.ListCreateAPIView):
    queryset = Observation2Box.objects.all()
    serializer_class = Observation2BoxSerializer
    pagination_class = NoPagination
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = Observation2Filter


class CutoutDirectoryListView(generics.ListCreateAPIView):
    """
    A pagination list of cutoutDirectory.
    """
    model = CutoutDirectory
    queryset = CutoutDirectory.objects.all()
    serializer_class = CutoutDirectorySerializer

    # using the Django Filter Backend - https://django-filter.readthedocs.io/en/latest/index.html
    filter_backends = (filters.DjangoFilterBackend,)
    # filter_class = CutoutDirectoryFilter


class CutoutDirectoryDetailsView(generics.RetrieveUpdateDestroyAPIView):
    """
    Detailed view of a cutout
    """

    # the primary key of cutout is not 'id', but a unique filename
    lookup_field = 'directory'

    model = CutoutDirectory
    queryset = CutoutDirectory.objects.all()
    serializer_class = CutoutDirectorySerializer


class CutoutListView(generics.ListCreateAPIView):
    """
    A pagination list of cutouts, sorted by date.
    """
    model = Cutout
    queryset = Cutout.objects.all().order_by('-field_name')
    serializer_class = CutoutSerializer

    # using the Django Filter Backend - https://django-filter.readthedocs.io/en/latest/index.html
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = CutoutFilter


class CutoutDetailsView(generics.RetrieveUpdateDestroyAPIView):
    """
    Detailed view of a cutout
    """

    # the primary key of cutout is not 'id', but a unique filename
    lookup_field = 'filename'

    model = Cutout
    queryset = Cutout.objects.all()
    serializer_class = CutoutSerializer


def CutoutDirectorySetThumbnail(request,directory,filename):
    logger.info('CutoutDirectorySetThumbnail()')
    directory = CutoutDirectory.objects.get(directory=directory)
    cutout = Cutout.objects.get(filename=filename)
    directory.thumbnail = cutout.derived_url
    directory.save()


def RemoveCutoutDirectory(request,directory):
    logger.info('RemoveCutoutDirectory()')
    CutoutDirectory.objects.filter(directory=directory).delete()

    # also remove all the images associated with this directory
    Cutout.objects.filter(directory=directory).delete()


def RemoveCutoutImage(request,filename):
    logger.info('RemoveCutoutImage()')
    Cutout.objects.filter(filename=filename).delete()