import os
from django.shortcuts import render, redirect

from .my_starcharts import sky_area, star_database, coord_calc, diagram
from .models import StarChart

from django.conf import settings

def StarChartView(request):
    # https://stackoverflow.com/questions/35288793/django-media-url-tag
    filename = 'starchart.svg'
    starchart_url_media = os.path.join(settings.MEDIA_URL,filename)
    starchart_url_static = os.path.join(settings.STATIC_URL, filename)
    return render(request, "starcharts_app/index.html", {'starchart_url_media': starchart_url_media, 'starchart_url_static': starchart_url_static})


#create-starchart?ra_min=44&ra_max=56&dec_min=10.75&dec_max=19.15&mag=10
#http://localhost:8000/my_astrobase/create-starchart?ra_min=44&ra_max=56&dec_min=10.75&dec_max=19.15&mag=10
def CreateStarChart(request):
    ra_min = float(request.GET.get('ra_min','44'))/15
    ra_max = float(request.GET.get('ra_max','56'))/15
    dec_min = float(request.GET.get('dec_min','10.75'))
    dec_max = float(request.GET.get('dec_max','19.25'))
    mag = float(request.GET.get('mag','10'))
    title = 'my_starchart'

    starchart = StarChart(title=title, ra_min=ra_min,ra_max=ra_max, dec_min=dec_min, dec_max=dec_max, magnitude_limit=mag)

    area = sky_area.SkyArea(ra_min,ra_max,dec_min,dec_max,mag)

    db = star_database.StarDatabase(settings.MY_HYG_ROOT)
    star_data_list = db.get_stars(area)

    cc = coord_calc.CoordCalc(star_data_list, area, 800)
    cc.process()

    d = diagram.Diagram(title, area, star_data_list)
    list(map(d.add_curve, cc.calc_curves()))

    filename = 'starchart.svg'
    path = os.path.join(settings.MEDIA_ROOT, filename)
    d.render_svg(path)

    starchart.image='starchart_image.svg'
    starchart.file='starchart_file.svg'
    starchart.save()

    return redirect('/my_astrobase/starchart/')
