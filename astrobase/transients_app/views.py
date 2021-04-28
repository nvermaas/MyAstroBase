
from rest_framework.response import Response
from rest_framework import generics
from django_filters import rest_framework as filters

from .serializers import TransientSerializer, MinorPlanetSerializer, AsteroidSerializer
import datetime

from .models import Transient,Asteroid
from .services import algorithms

# example: /my_astrobase/dataproducts?status__in=created,archived
class AsteroidFilter(filters.FilterSet):

    class Meta:
        model = Asteroid

        fields = {
            'designation': ['exact', 'icontains', 'in'],
            'ra': ['gt', 'lt', 'gte', 'lte', 'contains', 'exact'],
            'dec': ['gt', 'lt', 'gte', 'lte', 'contains', 'exact'],
            'absolute_magnitude': ['gt', 'lt', 'gte', 'lte'],
            'apparent_magnitude': ['gt', 'lt', 'gte', 'lte'],
        }

class AsteroidsView(generics.ListAPIView):
    model = Asteroid
    queryset = Asteroid.objects.all()
    serializer_class = AsteroidSerializer
    filter_class = AsteroidFilter


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
        my_comet = algorithms.get_comet(name,timestamp)

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
        my_asteroid = algorithms.get_asteroid(name,timestamp)

        return Response(my_asteroid)

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