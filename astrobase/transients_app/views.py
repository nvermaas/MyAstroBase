
from rest_framework.response import Response
from rest_framework import generics

from .serializers import TransientSerializer, MinorPlanetSerializer
import datetime

from .models import Transient
from .services import algorithms


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

        # call to the business logic that returns a list of moonphase
        my_transients = algorithms.get_minor_planets_webservice(name)

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
