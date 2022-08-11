
from .svg import Svg
import codecs
import json

MARGIN_X=0
MARGIN_Y=0

LABEL_OFFSET_X = 4
LABEL_OFFSET_Y = 3


class Diagram:
    def __init__(self, starchart, area, star_data_list, star_label_list, plot_data_list):
        self.starchart = starchart
        self.title = starchart.name
        self.area = area
        self.star_data_list = star_data_list
        self.star_label_list = star_label_list
        self.plot_data_list = plot_data_list
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
        for label_data in self.star_label_list.data:
            if label_data.label:
                x, y = self._invert_and_offset(label_data.x, label_data.y)
                d = self._mag_to_d(label_data.mag)
                svg.text(x + LABEL_OFFSET_X + d / 2, y + LABEL_OFFSET_Y, label_data.label, self.starchart.font_color,
                         self.starchart.font_size)

        # add additional elements from the 'extra' field
        for plot_data in self.plot_data_list.data:
            x, y = self._invert_and_offset(plot_data.x, plot_data.y)
            d = self._mag_to_d(plot_data.size)

            if plot_data.shape == "circle":
                svg.circle(x, y, d, plot_data.color)

            if plot_data.shape == "circle_outline":
                svg.circle_outline(x, y, d, plot_data.color)

            if plot_data.shape == "cross":
                svg.circle(x, y, d, plot_data.color)
                
            if plot_data.label:
                x, y = self._invert_and_offset(plot_data.x, plot_data.y)
                svg.text(x + LABEL_OFFSET_X, y + LABEL_OFFSET_Y, plot_data.label, plot_data.color, self.starchart.font_size)

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
