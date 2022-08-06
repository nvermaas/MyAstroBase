
from .svg import Svg
import codecs

MARGIN_X=0
MARGIN_Y=0
#MAGNIFICATION = 500

#MIN_D = 1
#MAX_D = 4

#DIMMEST_MAG = 6
#DIMMEST_MAG = 8
#BRIGHTEST_MAG = -1.5

LABEL_OFFSET_X = 4
LABEL_OFFSET_Y = 3
#FONT_SIZE=8
#FONT_COLOUR='#167ac6'

#TITLE_SIZE=16
#TITLE_COLOUR='#FFF'
#COORDS_SIZE=12
#COORDS_COLOUR='#FFF'

#STAR_COLOUR='#FFF'

#CURVE_WIDTH = 0.1
#CURVE_COLOUR = '#FFF'

class Diagram:
    def __init__(self, starchart, area, star_data_list, star_label_list):
        self.starchart = starchart
        self.title = starchart.name
        self.area = area
        self.star_data_list = star_data_list
        self.star_label_list = star_label_list
        self.curves = []
        self.border_min_x = self.border_min_y = self.border_max_x = self.border_max_y = None

    def add_curve(self, curve_points):
        self.curves.append(curve_points)

    def _mag_to_d(self, m):
        mag_range = self.starchart.dimmest_mag - self.starchart.brightest_mag
        m_score = (self.starchart.dimmest_mag - m) / mag_range
        r_range = self.starchart.max_d - self.starchart.min_d
        return self.starchart.min_d + m_score * r_range

    def _invert_and_offset(self, x, y):
        return x + MARGIN_X, (self.star_data_list.max_y - y) + MARGIN_Y

    def render_svg(self, outfile):
        svg = Svg(self.starchart.background)

        # add stars first
        for star_data in self.star_data_list.data:
            x, y = self._invert_and_offset(star_data.x, star_data.y)
            svg.circle(x, y, self._mag_to_d(star_data.mag), self.starchart.star_color)

        # next add labels
        for star_data in self.star_label_list.data:
            if star_data.label:
                x, y = self._invert_and_offset(star_data.x, star_data.y)
                d = self._mag_to_d(star_data.mag)
                svg.text(x + LABEL_OFFSET_X + d / 2, y + LABEL_OFFSET_Y, star_data.label, self.starchart.font_color,
                         self.starchart.font_size)

        # next add curves
        for curve_points in self.curves:
            svg.curve([self._invert_and_offset(cp[0], cp[1]) for cp in curve_points], self.starchart.curve_width, self.starchart.curve_color)

        # title
        #center_x = self.star_data_list.max_x/2 + MARGIN_X
        #svg.text(center_x, MARGIN_Y/2, self.title, TITLE_COLOUR, TITLE_SIZE, 'middle', 'underline')

        # coords
        #chart_bottom_y = self.star_data_list.max_y + MARGIN_Y
        #svg.text(center_x, chart_bottom_y + MARGIN_Y/2, "RA: {}-{}".format(self.area.ra_min, self.area.ra_max), COORDS_COLOUR, COORDS_SIZE, 'middle')
        #svg.text(center_x, chart_bottom_y + MARGIN_Y/2 + COORDS_SIZE, "Dec: {}-{}".format(self.area.dec_min, self.area.dec_max), COORDS_COLOUR, COORDS_SIZE, 'middle')

        codecs.open(outfile, 'w', 'utf-8').writelines(svg.to_list())
