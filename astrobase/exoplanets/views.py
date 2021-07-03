from rest_framework.response import Response
from rest_framework import generics, pagination
from django_filters import rest_framework as filters

from .serializers import ExoplanetSerializer
import datetime

from .models import Exoplanet
from .services import algorithms

# example: /my_astrobase/dataproducts?status__in=created,archived
class ExoplanetFilter(filters.FilterSet):

    class Meta:
        model = Exoplanet

        fields = {
            'pl_name': ['exact', 'icontains', 'in'],
            'hostname': ['exact', 'icontains', 'in'],
            'soltype': ['exact', 'icontains', 'in'],
            'ra': ['gt', 'lt', 'gte', 'lte', 'contains', 'exact'],
            'dec': ['gt', 'lt', 'gte', 'lte', 'contains', 'exact'],
        }

# a custom pagination class to return more than the default 100 dataproducts
class NoPagination(pagination.PageNumberPagination):
    page_size = 10000

class ExoplanetsView(generics.ListAPIView):
    model = Exoplanet
    queryset = Exoplanet.objects.all()
    serializer_class = ExoplanetSerializer
    filter_class = ExoplanetFilter


class ExoplanetsAllView(generics.ListAPIView):
    model = Exoplanet
    queryset = Exoplanet.objects.all()
    serializer_class = ExoplanetSerializer
    filter_class = ExoplanetFilter
    pagination_class = NoPagination


class UpdateExoplanets(generics.ListAPIView):
    model = Exoplanet
    queryset = Exoplanet.objects.all()

    # override the list method to be able to plug in my transient business logic
    def list(self, request):

         # call to the business logic that returns a list of moonphase
        algorithms.update_exoplanet_table()
        count = Exoplanet.objects.all().count()
        return Response({str(count)+" exoplanets updated"})