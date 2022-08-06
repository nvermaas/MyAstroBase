from django.shortcuts import render, redirect
from django_filters import rest_framework as filters
from rest_framework import generics, pagination
from django.conf import settings
from .models import StarChart, Scheme, Stars
from .serializers import StarChartSerializer, StarsSerializer
from .forms import StarChartForm
from .starchart.main import create_starchart, construct_starcharts_list, create_scheme_from_chart
from .starchart.hyg_star_database import HygStarDatabase

class StarsFilter(filters.FilterSet):

    class Meta:
        model = Stars

        fields = {
            'BayerFlamsteed': ['exact', 'icontains', 'in'],
            'HipparcosID': ['exact', 'icontains', 'in'],
            'HenryDraperID': ['exact', 'icontains', 'in'],
            'GlieseID': ['exact', 'icontains', 'in'],
            'Constellation': ['exact', 'icontains', 'in'],
            'SpectralType': ['exact', 'icontains', 'in'],
            'RightAscension': ['exact', 'icontains', 'lte','gte'],
            'Declination': ['exact', 'icontains', 'lte', 'gte'],
            'DistanceInParsecs': ['exact', 'icontains', 'lte', 'gte'],
            'ProperMotionRA': ['exact', 'icontains', 'lte', 'gte'],
            'ProperMotionDec': ['exact', 'icontains', 'lte', 'gte'],
            'RadialVelocity': ['exact', 'icontains', 'lte', 'gte'],
            'Magnitude': ['exact', 'icontains', 'lte', 'gte'],
            'AbsoluteMagnitude': ['exact', 'icontains', 'lte', 'gte'],
            'Luminosity': ['exact', 'icontains', 'lte', 'gte'],
            'ColorIndex': ['exact', 'icontains', 'lte', 'gte'],
            'VariableMinimum': ['exact', 'icontains', 'lte', 'gte'],
            'VariableMaximum': ['exact', 'icontains', 'lte', 'gte'],
        }


class StarsAPIView(generics.ListAPIView):
    model = Stars
    queryset = Stars.objects.using('stars').all()
    serializer_class = StarsSerializer
    filter_class = StarsFilter


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
    source = scheme_name = request.GET.get('source','ucac4_postgres')

    try:
        ra = float(request.GET.get('ra'))
        dec = float(request.GET.get('dec'))
    except:
        # no cone is given, try box
        ra = None
        dec = None

    try:
        ra_min = float(request.GET.get('ra_min'))
        ra_max = float(request.GET.get('ra_max'))
        dec_min = float(request.GET.get('dec_min'))
        dec_max = float(request.GET.get('dec_max'))
    except:
        # no box is given, hope for cone
        ra_min = None
        ra_max = None
        dec_min = None
        dec_max = None

    try:
        # try single radius
        radius_ra = float(request.GET.get('radius'))
        radius_dec = float(request.GET.get('radius'))
    except:
        # try split radius
        try:
            radius_ra = float(request.GET.get('radius_ra'))
            radius_dec = float(request.GET.get('radius_dec'))
        except:
            radius_ra = None
            radius_dec = None

    rotation = int(request.GET.get('rotation', '0'))
    magnitude = float(request.GET.get('magnitude','10'))

    try:
        scheme = Scheme.objects.get(name=scheme_name)
    except:
        scheme = None


    input_starchart = StarChart(name=name,
                                scheme = scheme,
                                source = source,
                                ra = ra,
                                dec = dec,
                                radius_ra = radius_ra,
                                radius_dec = radius_dec,
                                rotation = rotation,
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
            object_to_save = request.POST['save']

            if object_to_save == 'scheme':
                # save as scheme button was pushed
                create_scheme_from_chart(starchart)

            else:
                # save chart button was pushed
                # update the name and save to apply a potential change of scheme before creating the svg
                starchart.name = starchart.name.replace(" ", "")

                # first delete the existing starchart with this name
                try:
                    old_starchart = StarChart.objects.get(name=starchart.name)
                    old_starchart.delete()
                except Exception as e:
                    print(e)
                    pass

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
                'starcharts_list': starcharts_list})

    # a GET presents the form to the user to fill in and submit as a POST
    else:
        form = StarChartForm(instance=starchart)

        return render(request, "starcharts_app/starchart.html", {
            'form': form,
            'starchart': starchart,
            'starchart_url_media': starchart_url_media,
            'starcharts_list' : starcharts_list})


#create-starchart?ra_min=44&ra_max=56&dec_min=10.75&dec_max=19.15&mag=10
#http://localhost:8000/my_astrobase/create-starchart?ra_min=44&ra_max=56&dec_min=10.75&dec_max=19.15&mag=10
# fill the Django controlled stars.sqlite3 database with the data from hygdata.sqlite3
def ImportStars(request):
    print('importstars')
    db = HygStarDatabase(settings.MY_HYG_ROOT)
    db.import_stars()

    return redirect("/my_astrobase/starchart/")