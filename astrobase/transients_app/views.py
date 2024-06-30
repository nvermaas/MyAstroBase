
from rest_framework.response import Response
from rest_framework import generics, pagination
from django_filters import rest_framework as filters

from .serializers import TransientSerializer, MinorPlanetSerializer, AsteroidSerializer
import datetime

from .models import Transient,Asteroid
from .services import algorithms, starmaps

# example: /my_astrobase/dataproducts?status__in=created,archived
class AsteroidFilter(filters.FilterSet):

    class Meta:
        model = Asteroid

        fields = {
            'designation': ['exact', 'icontains', 'in'],
            'ra': ['gt', 'lt', 'gte', 'lte', 'contains', 'exact'],
            'dec': ['gt', 'lt', 'gte', 'lte', 'contains', 'exact'],
            'absolute_magnitude': ['gt', 'lt', 'gte', 'lte'],
            'visual_magnitude': ['gt', 'lt', 'gte', 'lte'],
        }

# a custom pagination class to return more than the default 100 dataproducts
class NoPagination(pagination.PageNumberPagination):
    page_size = 10000

class AsteroidsView(generics.ListAPIView):
    model = Asteroid
    queryset = Asteroid.objects.all()
    serializer_class = AsteroidSerializer
    filterset_class = AsteroidFilter


class AsteroidsAllView(generics.ListAPIView):
    model = Asteroid
    queryset = Asteroid.objects.all()
    serializer_class = AsteroidSerializer
    filterset_class = AsteroidFilter
    pagination_class = NoPagination


class TransientView(generics.ListAPIView):
    model = Transient
    queryset = Transient.objects.all()
    serializer_class = TransientSerializer

    # override the list method to be able to plug in my transient business logic
    def list(self, request):

        try:
            name = self.request.query_params['name']
        except:
            name = "eros"

        # uses astropy to also calc emphemeris
        my_transients = algorithms.get_transients(name)
        return Response(my_transients)



class MinorPlanetsView(generics.ListAPIView):
    model = Transient
    queryset = Transient.objects.all()
    serializer_class = MinorPlanetSerializer

    # override the list method to be able to plug in my transient business logic
    def list(self, request):

        try:
            name = self.request.query_params['name']
        except:
            name = "ceres"

        try:
            s = self.request.query_params['timestamp']
            timestamp = datetime.datetime.strptime(s,algorithms.DJANGO_TIME_FORMAT)
        except:
            timestamp = datetime.datetime.now()

        # call to the business logic that returns a list of moonphase
        my_transients = algorithms.get_minor_planets_webservice(name, timestamp)

        # serializer = MinorPlanetSerializer(instance=my_transients, many=True)
        # data = {'minor_planets' : serializer.data}
        # return Response(serializer.data)
        return Response(my_transients)


# http://localhost:8000/my_astrobase/comet/?name=C/2020%20F3%20(NEOWISE)&timestamp=2020-07-12T08:55:59Z
class CometView(generics.ListAPIView):
    model = Transient
    queryset = Transient.objects.all()
    serializer_class = TransientSerializer

    # override the list method to be able to plug in my transient business logic
    def list(self, request):

        try:
            name = self.request.query_params['name']
        except:
            name = "C/2020 F3 (NEOWISE)"

        try:
            s = self.request.query_params['timestamp']
            timestamp = datetime.datetime.strptime(s,algorithms.DJANGO_TIME_FORMAT)
        except:
            timestamp = datetime.datetime.now()

        print(timestamp)
        # call to the business logic that returns a list of moonphase
        my_comet,_ = algorithms.get_comet(name,timestamp)

        # serializer = MinorPlanetSerializer(instance=my_transients, many=True)
        # data = {'minor_planets' : serializer.data}
        # return Response(serializer.data)
        return Response(my_comet)

# http://localhost:8000/my_astrobase/asteroid/?name=psyche&timestamp=2021-01-12T20:55:59Z
class AsteroidView(generics.ListAPIView):
    model = Transient
    queryset = Transient.objects.all()
    serializer_class = TransientSerializer

    # override the list method to be able to plug in my transient business logic
    def list(self, request):

        try:
            name = self.request.query_params['name']
        except:
            name = "Psyche"

        try:
            s = self.request.query_params['timestamp']
            timestamp = datetime.datetime.strptime(s,algorithms.DJANGO_TIME_FORMAT)
        except:
            timestamp = datetime.datetime.now()

         # call to the business logic that returns a list of moonphase
        my_asteroid,_ = algorithms.get_asteroid(name,timestamp)

        return Response(my_asteroid)


class PlanetView(generics.ListAPIView):
    model = Transient
    queryset = Transient.objects.all()
    serializer_class = TransientSerializer

    # override the list method to be able to plug in my transient business logic
    def list(self, request):

        try:
            name = self.request.query_params['name']
        except:
            name = "Neptune"

        try:
            s = self.request.query_params['timestamp']
            timestamp = datetime.datetime.strptime(s,algorithms.DJANGO_TIME_FORMAT)
        except:
            timestamp = datetime.datetime.now()

         # call to the business logic that returns a list of moonphase
        my_planet,_ = algorithms.get_planet(name,timestamp)

        return Response(my_planet)


class UpdateAsteroids(generics.ListAPIView):
    model = Asteroid
    queryset = Asteroid.objects.all()

    # override the list method to be able to plug in my transient business logic
    def list(self, request):

         # call to the business logic that returns a list of moonphase
        algorithms.update_asteroid_table()
        count = Asteroid.objects.all().count()
        return Response({str(count)+" asteroids updated"})


class UpdateAsteroidsEphemeris(generics.ListAPIView):
    model = Asteroid
    queryset = Asteroid.objects.all()

    # override the list method to be able to plug in my transient business logic
    def list(self, request):
        try:
            s = self.request.query_params['timestamp']
            timestamp = datetime.datetime.strptime(s, algorithms.DJANGO_TIME_FORMAT)
        except:
            timestamp = datetime.datetime.now()

         # call to the business logic that returns a list of moonphase
        algorithms.update_asteroid_table_ephemeris(timestamp)

        count = Asteroid.objects.all().count()
        return Response({str(count)+" asteroids updated"})


# http://localhost:8000/my_astrobase/starmap/?name=Psyche&timestamp=2021-02-23T22:55:59Z

class StarMap(generics.ListAPIView):

    queryset = Asteroid.objects.all()

    def list(self, request, *args, **kwargs):
        # read the arguments from the request
        try:
            name = self.request.query_params['name']
        except:
            name = "C/2020 F3 (NEOWISE)"

        try:
            s = self.request.query_params['timestamp']
            timestamp = datetime.datetime.strptime(s,algorithms.DJANGO_TIME_FORMAT)
        except:
            timestamp = datetime.datetime.now()

        try:
            fov = int(self.request.query_params['fov'])
        except:
            fov = 45

        try:
            days_past = int(self.request.query_params['days_past'])
        except:
            days_past = 5

        try:
            days_future = int(self.request.query_params['days_future'])
        except:
            days_future = 10

        try:
            magnitude = int(self.request.query_params['magnitude'])
        except:
            magnitude = 8

        # result = "jobs can only be executed by authenticated users"
        # if self.request.user.is_superuser:
        url = starmaps.create_starmap(name, timestamp, days_past, days_future, fov, magnitude)

        # return a response

        return Response({
            'name': name,
            'timestamp' : timestamp,
            'days_past': days_past,
            'days_future': days_future,
            'fov': fov,
            'magnitude': magnitude,
            'url' : url
        })