import os
import sky_area
from input_file import InputFile
from diagram import Diagram
from star_database import StarDatabase
from coord_calc import CoordCalc


#area = sky_area.SKY_AREA_TAURUS
#area = sky_area.HD84406
title = 'Cetus'
area = sky_area.SkyArea(50/15, 60/15, 20, 30, 15)

area = sky_area.SkyArea(44/15, 56/15, 10.75, 19.25, 10)

db_file = "hygdata.sqlite3"
db = StarDatabase(db_file)
star_data_list = db.get_stars(area)

cc = CoordCalc(star_data_list, area, 800)
cc.process()

d = Diagram(title, area, star_data_list)
list(map(d.add_curve, cc.calc_curves()))
#d.render_svg('taurus-hyg.svg')
d.render_svg(os.path.join('output',title+'.svg'))