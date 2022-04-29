import os
from django.shortcuts import render, redirect

from .my_starcharts import sky_area, star_database, coord_calc, diagram

from django.conf import settings

def StarChart(request):
    # https://stackoverflow.com/questions/35288793/django-media-url-tag
    filename = 'starchart.svg'
    starchart_url = os.path.join(settings.MEDIA_URL,filename)
    return render(request, "starcharts_app/index.html", {'starchart_url': starchart_url})


#create-starchart?ra_min=44&ra_max=56&dec_min=10.75&dec_max=19.15&mag=10
#http://localhost:8000/my_astrobase/create-starchart?ra_min=44&ra_max=56&dec_min=10.75&dec_max=19.15&mag=10
def CreateStarChart(request):
    ra_min = float(request.GET.get('ra_min','44'))/15
    ra_max = float(request.GET.get('ra_max','56'))/15
    dec_min = float(request.GET.get('dec_min','10.75'))
    dec_max = float(request.GET.get('dec_max','19.25'))
    mag = float(request.GET.get('mag','10'))
    title = 'my_starchart'

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

    return redirect('/my_astrobase/starchart/')
