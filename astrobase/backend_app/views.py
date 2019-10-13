import time
import logging
import json
import datetime

from . import config
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import ListView
from rest_framework import generics, pagination
from rest_framework.response import Response
from django_filters import rest_framework as filters
from django.template import loader
from django.shortcuts import render, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .models import DataProduct, Observation, Status
from django.db.models import Q
from .serializers import DataProductSerializer, ObservationSerializer, StatusSerializer
from .forms import FilterForm

from .services import algorithms

logger = logging.getLogger(__name__)


# ---------- filters (in the REST API) ---------
# example: /astrobase/observations/?observing_mode__icontains=powershot_g2
class ObservationFilter(filters.FilterSet):
    # A direct filter on a @property field is not possible, this simulates that behaviour
    class Meta:
        model = Observation

        fields = {
            'observing_mode': ['exact', 'in', 'icontains'],  # /astrobase/observations?&observing_mode=g2
            'process_type': ['exact', 'in', 'icontains'], #/astrobase/observations?&process_type=observation
            'field_name': ['gt', 'lt', 'gte', 'lte', 'contains', 'exact'],
            'field_ra': ['gt', 'lt', 'gte', 'lte', 'contains', 'exact'],
            'field_dec': ['gt', 'lt', 'gte', 'lte', 'contains', 'exact'],
            'field_fov': ['gt', 'lt', 'gte', 'lte', 'contains', 'exact'],
            'name': ['exact', 'icontains'],
            'my_status': ['exact', 'icontains', 'in', 'startswith'],          #/astrobase/observations?&my_status__in=archived,removing
            'taskID': ['gt', 'lt', 'gte', 'lte','exact', 'icontains', 'startswith','in'],
            'creationTime' : ['gt', 'lt', 'gte', 'lte', 'contains', 'exact'],
            'date' : ['gt', 'lt', 'gte', 'lte', 'contains', 'exact'],
            'data_location': ['exact', 'icontains'],
            'quality': ['exact', 'icontains'],
        }

# example: /astrobase/dataproducts?status__in=created,archived
class DataProductFilter(filters.FilterSet):

    class Meta:
        model = DataProduct

        fields = {
            'dataproduct_type': ['exact', 'in'],  # ../dataproducts?dataProductType=IMAGE,VISIBILITY
            'description': ['exact', 'icontains'],
            'name': ['exact', 'icontains'],
            'filename': ['exact', 'icontains'],
            'taskID': ['exact', 'icontains'],
            'creationTime': ['gt', 'lt', 'gte', 'lte', 'contains', 'exact'],
            'parent__taskID': ['exact', 'in', 'icontains'],
            'my_status': ['exact', 'icontains', 'in'],
            'data_location': ['exact', 'icontains'],
        }

# example: has 1811130001 been 'processed?'
# http://localhost:8000/astrobase/status/?&taskID=181130001&name=processed
class StatusFilter(filters.FilterSet):

    # A direct filter on a @property field is not possible, this simulates that behaviour
    taskID = filters.Filter(field_name="taskObject__taskID",lookup_expr='exact')

    class Meta:
        model = Status

        # https://django-filter.readthedocs.io/en/master/ref/filters.html?highlight=exclude
        fields = {
            #'taskid': ['exact', 'in'],
            'name': ['exact', 'in'],
            'timestamp': ['gt', 'lt', 'gte', 'lte', 'contains', 'exact'],
            'taskObject__taskID': ['exact', 'in'],
            'taskID': ['exact', 'in'],

            #'derived_taskid' : ['exact', 'in']
        }

# this uses a form
def do_filter(request):

    if request.method == 'GET':
        # create a form instance and populate it with data from the request:
        form = FilterForm(request.POST)
        if form.is_valid():
            status = form.cleaned_data.get('status')
            #observations = get_filtered_observations()
            return HttpResponseRedirect('/astrobase/')
    else:
        form = FilterForm

    return render(request, 'backend_app/index.html', {'my_form': form})

# ---------- GUI Views -----------
# http://localhost:8000/astrobase/
# calling this view renders the index.html template in the GUI (the observation list)
# http://localhost:8000/astrobase/query?my_status=removed
# http://localhost:8000/astrobase/query?not_my_status=removed

class IndexView(ListView):
    """
    This is the main view of astrobase. It shows a pagination list of observations, sorted by creationTime.
    """
    template_name = 'backend_app/index.html'

    # by default this returns the list in an object called object_list, so use 'object_list' in the html page.
    # but if 'context_object_name' is defined, then this returned list is named and can be accessed that way in html.
    context_object_name = 'my_observations'

    def get_queryset(self):
        #observations = Observation.objects.order_by('-creationTime')
        #observations = get_filtered_observations()
        my_status = self.request.GET.get('my_status')
        not_my_status = self.request.GET.get('not_my_status')
        search_box = self.request.GET.get('search_box', None)

        if (search_box is not None):
            observations = get_searched_observations(search_box)
        else:
            #observations = Observation.objects.order_by('-taskID')
            observations = Observation.objects.order_by('-date')
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
# http://localhost:8000/astrobase/query?my_status=scheduled
def get_filtered_observations(my_status):
    q = Observation.objects.order_by('-creationTime')
    q = q.filter(my_status=my_status)
    #q = q.exclude(my_status__icontains='removed')
    return q

# http://localhost:8000/astrobase/query?not_my_status=removed
def get_unfiltered_observations(my_status):
    q = Observation.objects.order_by('-creationTime')
    q = q.exclude(my_status=my_status)
    return q

def get_searched_observations(search):
    observations = Observation.objects.filter(
        Q(taskID__contains=search) |
        Q(observing_mode__icontains=search) |
        Q(my_status__icontains=search) |
        Q(field_name__icontains=search)).order_by('-creationTime')
    return observations


# example: /astrobase/task/180323003/
# https://docs.djangoproject.com/en/2.1/topics/class-based-views/generic-display/
# calling this view renders the dataproducts.html template in the GUI
# a custom pagination class to return more than the default 100 dataproducts
class DataProductsPagination(pagination.PageNumberPagination):
    page_size = 10000

class DataProductsListView(ListView):
    model = DataProduct
    context_object_name = 'my_dataproducts_list'
    template_name = 'backend_app/dataproducts.html'
    pagination_class = DataProductsPagination

    # override get_queryset to make a custom query on taskid
    def get_queryset(self):
        logger.info("DataProductsListView.get_queryset()")
        taskid = self.kwargs['taskID']
        my_queryset = DataProduct.objects.filter(taskID=taskid)
        logger.info("my_queryset retrieved")
        return my_queryset



# ---------- REST API views -----------
# example: /astrobase/status

class StatusListViewAPI(generics.ListCreateAPIView):
    model = Status
    queryset = Status.objects.all()
    serializer_class = StatusSerializer
    pagination_class = DataProductsPagination

    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = StatusFilter


# example: /astrobase/dataproducts/
# calling this view serializes the dataproduct list in a REST API
class DataProductListViewAPI(generics.ListCreateAPIView):
    model = DataProduct
    queryset = DataProduct.objects.all()
    serializer_class = DataProductSerializer
    pagination_class = DataProductsPagination

    # using the Django Filter Backend - https://django-filter.readthedocs.io/en/latest/index.html
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = DataProductFilter


# example: /astrobase/dataproducts/5/
# calling this view serializes a dataproduct in the REST API
class DataProductDetailsViewAPI(generics.RetrieveUpdateDestroyAPIView):
    model = DataProduct
    queryset = DataProduct.objects.all()
    serializer_class = DataProductSerializer


# example: /astrobase/observations/
# calling this view serializes the observations list in a REST API
class ObservationListViewAPI(generics.ListCreateAPIView):
    """
    A pagination list of observations, unsorted.
    """
    model = Observation
    queryset = Observation.objects.all()
    serializer_class = ObservationSerializer

    # using the Django Filter Backend - https://django-filter.readthedocs.io/en/latest/index.html
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = ObservationFilter


# example: /astrobase/observations/5/
# calling this view serializes an observation in the REST API
class ObservationDetailsViewAPI(generics.RetrieveUpdateDestroyAPIView):
    """
    Detailed view of an observation.
    """
    model = Observation
    queryset = Observation.objects.all()
    serializer_class = ObservationSerializer


# --- Command views, triggered by a button in the GUI or directoy with a URL ---
# set observation status to 'new_status' - called from the GUI
# example: 'Schedule', 'Unschedule', 'Ready to Ingest', 'Remove Data'

def ObservationSetStatus(request,pk,new_status,page):
    model = Observation
    observation = Observation.objects.get(pk=pk)
    observation.new_status = new_status
    observation.save()
    return redirect('/astrobase/?page='+page)


# set the status of an observation and all its dataproducts to 'new_dps_status'
# example: 'Validate DPS' button
# /astrobase/observations/<int:pk>/setstatus_dps/<new_dps_status>/<new_obs_status>/<page>
def ObservationSetStatusDataProducts(request,pk,new_dps_status,new_obs_status,page):
    model = Observation
    observation = Observation.objects.get(pk=pk)
    observation.new_status = new_obs_status
    observation.save()
    taskid = observation.taskID

    dataproducts = DataProduct.objects.filter(taskID=taskid)
    for dataproduct in dataproducts:
        dataproduct.new_status = new_dps_status
        dataproduct.save()

    return redirect('/astrobase/?page='+page)

# set the status of a dataproduct to 'new_status'
# example: 'Validate', 'Skip' and 'Remove' buttons
def DataProductSetStatusView(request,pk,new_status):
    model = DataProduct
    dataproduct = DataProduct.objects.get(pk=pk)
    dataproduct.new_status = new_status
    dataproduct.save()

    taskid = dataproduct.taskID

    return redirect('/astrobase/task/'+taskid)


# get the next taskid based on starttime and what is currently in the database
#/astrobase/get_next_taskid?timestamp=2019-04-05
class GetNextTaskIDView(generics.ListAPIView):
    queryset = Observation.objects.all()

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
# /astrobase/post_dataproducts&taskid=190405034
class PostDataproductsView(generics.CreateAPIView):
    queryset = DataProduct.objects.all()
    serializer_class = DataProductSerializer
    pagination_class = DataProductsPagination

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
