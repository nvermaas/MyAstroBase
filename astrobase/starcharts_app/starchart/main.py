import os
from pathlib import Path
from django.core.files import File
from django.conf import settings
from ..models import StarChart
from .sky_area import SkyArea
from .diagram import Diagram
from .star_database import StarDatabase
from .coord_calc import CoordCalc


def create_starchart(name, ra_min, ra_max, dec_min, dec_max, mag):
    try:
        starchart = StarChart.objects.get(name=name)
        starchart.delete()
    except:
        pass

    starchart = StarChart(name=name, ra_min=ra_min, ra_max=ra_max, dec_min=dec_min, dec_max=dec_max,
                          magnitude_limit=mag)

    area = SkyArea(ra_min, ra_max, dec_min, dec_max, mag)

    db = StarDatabase(settings.MY_HYG_ROOT)
    star_data_list = db.get_stars(area)

    cc = CoordCalc(star_data_list, area, 800)
    cc.process()

    # create the diagram
    d = Diagram(name, area, star_data_list)
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

    return starchart,starchart_url_media