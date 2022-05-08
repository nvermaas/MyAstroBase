import os
from pathlib import Path
from django.core.files import File
from django.conf import settings
from ..models import StarChart
from .sky_area import SkyArea
from .diagram import Diagram
from .star_database import StarDatabase
from .coord_calc import CoordCalc


def create_starchart(input_starchart):
    try:
        starchart = StarChart.objects.get(name=input_starchart.name)
        starchart.delete()
    except:
        pass

    starchart = input_starchart

    area = SkyArea(starchart.ra_min/15, starchart.ra_max/15, starchart.dec_min, starchart.dec_max, starchart.magnitude_limit)

    db = StarDatabase(settings.MY_HYG_ROOT)
    star_data_list = db.get_stars(area)

    cc = CoordCalc(star_data_list, area, starchart.diagram_size)
    cc.process()

    # create the diagram
    d = Diagram(starchart, area, star_data_list)
    list(map(d.add_curve, cc.calc_curves()))

    # generate the temporary image file
    temp_filename = 'starchart.svg'
    temp_path = os.path.join(settings.MEDIA_ROOT, temp_filename)
    d.render_svg(temp_path)

    # delete existing file before uploading
    my_filename = starchart.name + '.svg'
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

    return starchart,starchart_url_media


def construct_starcharts_list():
#  <li><a class="dropdown-item" href="http://localhost:8000/my_astrobase/starchart/my_starchart">my_starchart</a></li>
#  <li><a class="dropdown-item" href="http://localhost:8000/my_astrobase/starchart/MyOrion">MyOrion</a></li>
    results = ''

    left = '<li><a class="dropdown-item" href="'
    base_url = settings.MEDIA_URL + "/starchart/"
    if settings.DEBUG:
        base_url = "http://localhost:8000/my_astrobase/starchart/"

    right = '</a></li>'

    for starchart in StarChart.objects.all():
        line = left + base_url + starchart.name + '">' + starchart.name + right
        results += line

    return results