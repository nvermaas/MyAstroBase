
from rest_framework import viewsets
from rest_framework.response import Response

from django.views.generic import ListView
from rest_framework import generics

from .serializers import MoonPhasesSerializer
import datetime
from .my_moon.moon import get_new_moons
from .models import MoonPhases

class MoonPhasesView(generics.ListAPIView):
#class MoonPhasesView(viewsets.ViewSet):
    model = MoonPhases
    queryset = MoonPhases.objects.all()
    serializer_class = MoonPhasesSerializer

    # override the list method to be able to plug in my moonphase business logic
    def list(self, request):
        # read the year from the request: .../moonphases/?year=2018
        try:
            year = self.request.query_params['year']
        except:
            year = datetime.datetime.now().year

        # call to the business logic that returns a list of moonphase
        my_moonphases = get_new_moons(int(year))
        serializer = MoonPhasesSerializer(instance=my_moonphases, many=True)

        # add some extra structure to the json response
        numphases = len(my_moonphases)
        data = {'numphases' : numphases, 'phasedata' : serializer.data}

        # manually add a CORS header to the response
        #response["Access-Control-Allow-Origin"] = "*"
        return Response(data)