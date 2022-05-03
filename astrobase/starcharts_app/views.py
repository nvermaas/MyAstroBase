import os
from django.shortcuts import render, redirect
from pathlib import Path
from django.core.files import File
from django_filters import rest_framework as filters
from rest_framework import generics, pagination

from .starchart import sky_area, star_database, coord_calc, diagram
from .models import StarChart
from .serializers import StarChartSerializer

from django.conf import settings

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

    try:
        starchart = StarChart.objects.get(name=name)
        starchart.delete()
    except:
        pass

    starchart = StarChart(name=name, ra_min=ra_min,ra_max=ra_max, dec_min=dec_min, dec_max=dec_max, magnitude_limit=mag)

    area = sky_area.SkyArea(ra_min,ra_max,dec_min,dec_max,mag)

    db = star_database.StarDatabase(settings.MY_HYG_ROOT)
    star_data_list = db.get_stars(area)

    cc = coord_calc.CoordCalc(star_data_list, area, 800)
    cc.process()

    # create the diagram
    d = diagram.Diagram(name, area, star_data_list)
    list(map(d.add_curve, cc.calc_curves()))

    # generate the temporary image file
    temp_filename = 'starchart.svg'
    temp_path = os.path.join(settings.MEDIA_ROOT, temp_filename)
    d.render_svg(temp_path)

    # delete existing file before uploading
    my_filename = name + '.svg'
    try:
        existing_file = os.path.join(os.path.join(settings.MEDIA_ROOT, 'my_starmaps'), my_filename)
        os.remove(existing_file)
    except:
        pass

    # add the image to the StarChart object and database
    path = Path(temp_path)
    with path.open(mode='rb') as f:
        starchart.image = File(f, name=my_filename)
        starchart.save()

    starchart_url_media = settings.MEDIA_URL + 'my_starmaps/' + my_filename
    if settings.DEBUG:
        starchart_url_media = "http://localhost:8000/my_astrobase" + starchart_url_media


    return render(request, "starcharts_app/index.html", {'starchart':starchart,'starchart_url_media': starchart_url_media})

