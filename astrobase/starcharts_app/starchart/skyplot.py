from matplotlib import pyplot as plt

# https://matplotlib.org/stable/tutorials/introductory/pyplot.html
class SkyPlot:
    def __init__(self, starchart, area, star_data_list, star_label_list, plot_data_list):
        self.starchart = starchart
        self.title = starchart.name
        self.area = area
        self.star_data_list = star_data_list
        self.star_label_list = star_label_list
        self.plot_data_list = plot_data_list
        self.curves = []
        self.border_min_x = self.border_min_y = self.border_max_x = self.border_max_y = None

    def render_plot(self, outfile):
        pass