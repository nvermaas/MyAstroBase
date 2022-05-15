from django.shortcuts import render, redirect
from django_filters import rest_framework as filters
from rest_framework import generics, pagination
from django.conf import settings
from .models import StarChart, Scheme
from .serializers import StarChartSerializer
from .forms import StarChartForm
from .starchart.main import create_starchart, construct_starcharts_list


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


def ShowStarChartView(request, name='my_starchart'):

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
    name = request.GET.get('name', 'my_starchart')
    scheme_name = request.GET.get('scheme','default')
    ra_min = float(request.GET.get('ra_min','44'))
    ra_max = float(request.GET.get('ra_max','56'))
    dec_min = float(request.GET.get('dec_min','10.75'))
    dec_max = float(request.GET.get('dec_max','19.25'))
    magnitude = float(request.GET.get('magnitude','10'))

    try:
        scheme = Scheme.objects.get(name=scheme_name)
    except:
        scheme = None


    input_starchart = StarChart(name=name,
                                scheme = scheme,
                                ra_min=ra_min,
                                ra_max=ra_max,
                                dec_min=dec_min,
                                dec_max=dec_max,
                                magnitude_limit=magnitude)

    starchart, starchart_url_media = create_starchart(input_starchart)
    starcharts_list = construct_starcharts_list()
    form = StarChartForm(instance=starchart)

    return render(request, "starcharts_app/starchart.html",
                  {'form': form,
                   'starchart': starchart,
                   'starchart_url_media': starchart_url_media,
                   'starcharts_list': starcharts_list})

def StarChartView(request, name=None):

    try:
        starchart = StarChart.objects.get(name=name)
        filename = name + '.svg'

        starchart_url_media = settings.MEDIA_URL + 'my_starmaps/' + filename
        if settings.DEBUG:
            starchart_url_media = "http://localhost:8000/my_astrobase" + starchart_url_media

    except:
        starchart = StarChart()
        starchart_url_media=""

    starcharts_list = construct_starcharts_list()

    # a POST means that the form is filled in and should be stored in the database
    if request.method == "POST":

        form = StarChartForm(request.POST, instance=starchart)
        if form.is_valid():
            # update the name and save to apply a potential change of scheme before creating the svg
            starchart.name = starchart.name.replace(" ", "_")
            starchart.save()

            # reload the form with the above changes so they show up in the template
            form = StarChartForm(instance=starchart)

            starchart, starchart_url_media = create_starchart(starchart)
            return render(request, "starcharts_app/starchart.html",
                          {'form': form,
                           'starchart': starchart,
                           'starchart_url_media': starchart_url_media,
                           'starcharts_list' : starcharts_list})
        else:
            # form is invalid
            return render(request, "starcharts_app/starchart.html", {
                'form': form,
                'starchart': starchart,
                'starchart_url_media': starchart_url_media,
                'starcharts_list': starcharts_list,
                'schemes_list' :schemes_list})

    # a GET presents the form to the user to fill in and submit as a POST
    else:
        form = StarChartForm(instance=starchart)

        return render(request, "starcharts_app/starchart.html", {
            'form': form,
            'starchart': starchart,
            'starchart_url_media': starchart_url_media,
            'starcharts_list' : starcharts_list})


