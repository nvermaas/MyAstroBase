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
        print(self.title)
        ra_list = []
        dec_list = []
        mag_list = []
        size_list = []

        mag_limit = 15
        for star in self.star_data_list.data:
            ra_list.append(star.ra)
            dec_list.append(star.dec)
            mag_list.append((10 - star.mag) ** 2)
            size_list.append((0.5 + mag_limit - star.mag) * 3)
            print(ra_list)
            print(dec_list)

        fig, ax = plt.subplots()
        colormap = 'gray'
        # size = (0.5 + mag_lim - qtab['Gmag']) * 3
        plt.scatter(ra_list, dec_list, s=mag_list, color='black', alpha=1.0)
        #plt.invert_xaxis()
        plt.xlim(max(ra_list), min(ra_list))
        plt.ylim(min(dec_list), max(dec_list))

        #plt.style.use('dark_background')
        #plt.figure(figsize=(12,6))
        #plt.subplot(projection="hammer")
        plt.title(self.title)
        plt.suptitle("Astrobase Starcharts")
        plt.xlabel('Right Ascension (degrees)')
        plt.ylabel('Declination')
        plt.grid(True, alpha=0.3)
        plt.savefig("d:\\temp\plot.png")
        #plt.show()
