import os
from django.shortcuts import render, redirect
from pathlib import Path
from django.core.files import File

from .starchart import sky_area, star_database, coord_calc, diagram
from .models import StarChart

from django.conf import settings

def StarChartView(request):
    # https://stackoverflow.com/questions/35288793/django-media-url-tag
    filename = 'starchart.svg'
    
    starchart_url_media = settings.MEDIA_URL + 'my_starmaps/' + filename
    #if settings.DEBUG:
    #    starchart_url_media = "http://localhost:8000/my_astrobase" + starchart_url_media

    title = 'my_starchart'
    starchart = StarChart.objects.get(title=title)

    return render(request, "starcharts_app/index.html", {'starchart':starchart,'starchart_url_media': starchart_url_media})


#create-starchart?ra_min=44&ra_max=56&dec_min=10.75&dec_max=19.15&mag=10
#http://localhost:8000/my_astrobase/create-starchart?ra_min=44&ra_max=56&dec_min=10.75&dec_max=19.15&mag=10
def CreateStarChart(request):
    ra_min = float(request.GET.get('ra_min','44'))/15
    ra_max = float(request.GET.get('ra_max','56'))/15
    dec_min = float(request.GET.get('dec_min','10.75'))
    dec_max = float(request.GET.get('dec_max','19.25'))
    mag = float(request.GET.get('mag','10'))
    title = 'my_starchart'

    try:
        starchart = StarChart.objects.get(title=title)
    except:
        starchart = StarChart(title=title, ra_min=ra_min,ra_max=ra_max, dec_min=dec_min, dec_max=dec_max, magnitude_limit=mag)

    area = sky_area.SkyArea(ra_min,ra_max,dec_min,dec_max,mag)

    db = star_database.StarDatabase(settings.MY_HYG_ROOT)
    star_data_list = db.get_stars(area)

    cc = coord_calc.CoordCalc(star_data_list, area, 800)
    cc.process()

    d = diagram.Diagram(title, area, star_data_list)
    list(map(d.add_curve, cc.calc_curves()))

    filename = 'starchart.svg'
    starchart_path = os.path.join(settings.MEDIA_ROOT, filename)
    d.render_svg(starchart_path)

    starchart_url_media = settings.MEDIA_URL + 'my_starmaps/' + filename
    #if settings.DEBUG:
    #    starchart_url_media = "http://localhost:8000/my_astrobase" + starchart_url_media

    path = Path(starchart_path)
    with path.open(mode='rb') as f:
        #starchart.file = File(f, name=path.name)
        starchart.image = File(f, name=path.name)
        starchart.save()

    return render(request, "starcharts_app/index.html", {'starchart':starchart,'starchart_url_media': starchart_url_media})
