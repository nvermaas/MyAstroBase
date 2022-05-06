from django.shortcuts import render, redirect
from django_filters import rest_framework as filters
from rest_framework import generics, pagination
from django.conf import settings
from .models import StarChart
from .serializers import StarChartSerializer
from .forms import StarChartForm
from .starchart.main import create_starchart


class StarChartFilter(filters.FilterSet):

    class Meta:
        model = StarChart

        fields = {
            'name': ['exact', 'icontains', 'in'],
        }


class StarChartAPIView(generics.ListAPIView):
    model = StarChart
    queryset = StarChart.objects.all()
    serializer_class = StarChartSerializer
    filter_class = StarChartFilter


def StarChartView(request, name='my_starchart'):

    try:
        starchart = StarChart.objects.get(name=name)
        filename = name + '.svg'

        starchart_url_media = settings.MEDIA_URL + 'my_starmaps/' + filename
        if settings.DEBUG:
            starchart_url_media = "http://localhost:8000/my_astrobase" + starchart_url_media
    except:
        starchart = None
        starchart_url_media = None

    return render(request, "starcharts_app/index.html", {'starchart' : starchart, 'starchart_url_media' : starchart_url_media})


#create-starchart?ra_min=44&ra_max=56&dec_min=10.75&dec_max=19.15&mag=10
#http://localhost:8000/my_astrobase/create-starchart?ra_min=44&ra_max=56&dec_min=10.75&dec_max=19.15&mag=10
def CreateStarChart(request):
    ra_min = float(request.GET.get('ra_min','44'))/15
    ra_max = float(request.GET.get('ra_max','56'))/15
    dec_min = float(request.GET.get('dec_min','10.75'))
    dec_max = float(request.GET.get('dec_max','19.25'))
    mag = float(request.GET.get('mag','10'))
    name = request.GET.get('name','my_starchart')

    starchart, starchart_url_media = create_starchart(name, ra_min, ra_max, dec_min, dec_max, mag)

    return render(request, "starcharts_app/index.html", {'starchart':starchart,'starchart_url_media': starchart_url_media})



#create-starchart?ra_min=44&ra_max=56&dec_min=10.75&dec_max=19.15&mag=10
#http://localhost:8000/my_astrobase/create-starchart?ra_min=44&ra_max=56&dec_min=10.75&dec_max=19.15&mag=10
def FormStarChart(request, name=None):

    starchart = StarChart.objects.get(name=name)

    # a POST means that the form is filled in and should be stored in the database
    if request.method == "POST":

        form = StarChartForm(request.POST, instance=starchart)

        name = starchart.name
        mag = starchart.magnitude_limit
        ra_min = float(request.GET.get('ra_min','44'))/15
        ra_max = float(request.GET.get('ra_max','56'))/15
        dec_min = float(request.GET.get('dec_min','10.75'))
        dec_max = float(request.GET.get('dec_max','19.25'))
        mag = float(request.GET.get('mag','10'))

        # todo: just give the (alterned) starchart als parameter instead of this whole list?
        starchart, starchart_url_media = create_starchart(name,ra_min,ra_max,dec_min,dec_max,mag)

        return render(request, "starcharts_app/do-starchart.html", {'starchart':starchart,'starchart_url_media': starchart_url_media})

    else:
        try:
            if not name:
                name = 'my_starchart'
            starchart = StarChart.objects.get(name=name)
        except:
            starchart = StarChart()

        #form = StarChartForm(initial={'name': name})
        form = StarChartForm(instance=starchart)
        return render(request, "starcharts_app/do_starchart.html",{'form':form, 'starchart': starchart})

