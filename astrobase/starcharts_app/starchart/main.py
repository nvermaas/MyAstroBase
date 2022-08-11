import os
from pathlib import Path
from django.core.files import File
from django.conf import settings
from ..models import StarChart, Scheme
from .sky_area import SkyArea, ConeToSkyArea
from .diagram import Diagram
from .hyg_star_database import HygStarDatabase
from .ucac4_star_database import UCAC4StarDatabase
from .starlabels_database import StarLabelsDatabase
from .coord_calc import CoordCalc
from .plot_data import PlotData, PlotDataList

def create_starchart(input_starchart):
    try:
        starchart = StarChart.objects.get(name=input_starchart.name)
        starchart.delete()
    except Exception as e:
        pass

    starchart = input_starchart

    if starchart.ra:
        area = ConeToSkyArea(starchart.ra,starchart.dec,starchart.radius_ra,starchart.radius_dec,starchart.magnitude_limit)
        starchart.ra_min = area.ra_min
        starchart.ra_max = area.ra_max
        starchart.dec_min = area.dec_min
        starchart.dec_max = area.dec_max
    else:
        area = SkyArea(starchart.ra_min, starchart.ra_max, starchart.dec_min, starchart.dec_max, starchart.magnitude_limit)
        starchart.ra = (area.ra_min + area.ra_max) / 2
        starchart.dec = (area.dec_min + area.dec_max) / 2

    if starchart.source == "hyg_sqlite":
        hyg_db = HygStarDatabase(settings.MY_HYG_ROOT)
        star_data_list = hyg_db.get_stars(area)

    elif starchart.source == "ucac4_postgres":
        ucac4_db = UCAC4StarDatabase(settings.UCAC4_HOST,
                                     settings.UCAC4_PORT,
                                     settings.UCAC4_DATABASE,
                                     settings.UCAC4_USER,
                                     settings.UCAC4_PASSWORD)
        star_data_list = ucac4_db.get_stars(area,starchart.query_limit)

    starchart.nr_of_stars = len(star_data_list.data)

    # get star labels from the HYG database
    starlabels_db = StarLabelsDatabase(settings.MY_STARLABELS_ROOT)
    star_label_list = starlabels_db.get_labels(area,starchart.label_field)

    # extra objects to draw on the starchart
    plot_data_list = PlotDataList(starchart.extra)

    cc = CoordCalc(star_data_list,
                   star_label_list,
                   plot_data_list,
                   area, starchart.diagram_size)

    try:
        cc.process()

        # create the diagram
        d = Diagram(starchart, area, star_data_list, star_label_list, plot_data_list)
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
    except Exception as e:
        print(e)
        return starchart, 'not enough stars to create a starchart of this area'


def construct_starcharts_list():
    results = ''

    left = '<li><a class="dropdown-item" href="'
    base_url = "/my_astrobase/starchart/"
    if settings.DEBUG:
        base_url = "http://localhost:8000/my_astrobase/starchart/"

    right = '</a></li>'

    for starchart in StarChart.objects.all():
        line = left + base_url + starchart.name + '">' + starchart.name + right
        results += line

    return results


def create_scheme_from_chart(input_starchart):
    scheme = Scheme(
        name=input_starchart.name,
        magnitude_limit=input_starchart.magnitude_limit,
        dimmest_mag=input_starchart.dimmest_mag,
        brightest_mag=input_starchart.brightest_mag,
        min_d=input_starchart.min_d,
        max_d=input_starchart.max_d,
        font_size=input_starchart.font_size,
        font_color=input_starchart.font_color,
        curve_width=input_starchart.curve_width,
        curve_color=input_starchart.curve_color,
        star_color=input_starchart.star_color,
        background=input_starchart.background)
    scheme.save()

