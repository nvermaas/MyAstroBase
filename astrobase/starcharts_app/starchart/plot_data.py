import json

class PlotData:

    def __init__(self, ra, dec, shape, size, color, label=None):
        self.ra    = ra
        self.dec   = dec
        self.shape = shape
        self.size   = size
        self.color = color
        self.label = label

        self.ra_angle  = None
        self.dec_angle = None

        self.x = None
        self.y = None


class PlotDataList:

    def __init__(self, input_data):
        list = json.loads(input_data)
        self.data = []
        self.min_x = self.max_x = self.min_y = self.max_y = None

        for element in list:
            ra = element['ra']
            dec = element['dec']
            size = element['size']
            shape = element['shape']
            color = element['color']
            label = element['label']

            self.data.append(PlotData(ra, dec, shape, size, color, label))


