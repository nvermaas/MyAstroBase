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
        # examples
        # https://github.com/behrouzz/skychart/blob/main/skychart/plotting.py
        # https://matplotlib.org/stable/tutorials/introductory/pyplot.html
        # https://www.geeksforgeeks.org/how-to-reverse-axes-in-matplotlib/#:~:text=In%20Matplotlib%20we%20can%20reverse,methods%20for%20the%20pyplot%20object.
        # https://matplotlib.org/basemap/users/pstere.html
        # https://astroplan.readthedocs.io/en/latest/tutorials/plots.html#plots-sky-charts

        print(self.title)
        ra_list = []
        dec_list = []
        mag_list = []
        size_list = []

        mag_limit = 15
        dimmest = 10
        mag_limit = self.starchart.magnitude_limit
        dimmest = self.starchart.dimmest_mag
        for star in self.star_data_list.data:
            ra_list.append(star.ra)
            dec_list.append(star.dec)
            mag_list.append((dimmest - star.mag) ** 2)
            #size_list.append((0.5 + mag_limit - star.mag) * 3)
            size_list.append((0.5 + mag_limit - star.mag) * 1)

        #fig, ax = plt.subplots()
        #colormap = 'gray'

        plt.scatter(ra_list, dec_list, s=mag_list, color=self.starchart.star_color, alpha=1.0)
        #plt.invert_xaxis()
        plt.xlim(max(ra_list), min(ra_list))
        plt.ylim(min(dec_list), max(dec_list))


        plt.title(self.title)
        #plt.subplot(projection="hammer")
        plt.suptitle("Astrobase Starcharts")
        plt.xlabel('Right Ascension (degrees)')
        plt.ylabel('Declination')
        plt.grid(True, alpha=0.3)

        for label in self.star_label_list.data:
            plt.text(label.ra,label.dec, label.label,fontsize=self.starchart.font_size, color=self.starchart.font_color)

        ax = plt.gca()
        ax.set_facecolor(self.starchart.background)

        fig = plt.gcf()
        fig.set_size_inches(20, 15)
        fig.savefig("d:\\temp\plot.png", dpi=200)

        #plt.savefig("d:\\temp\plot.png")
        #plt.show()
