import sqlite3
from sqlite3 import Error

from ..models import Stars
from .star_data import StarData, StarDataList

class StarLabelsDatabase:
    def __init__(self, db_file):

        self.conn = None
        try:
            self.conn = sqlite3.connect(db_file)
        except Error as e:
            print(e)


    def get_labels(self, sky_area):

            cur = self.conn.cursor()
            cur.execute("SELECT RightAscension,Declination,Magnitude,BayerFlamsteed FROM hygdata")

            rows = cur.fetchall()

            results = []

            for row in rows:
                ra = row[0]
                dec = row[1]
                mag = row[2]
                label = row[3]

                if not label:
                    continue
                if mag > sky_area.mag_min:  # because smaller mag values mean brighter stars
                    continue
                if not (sky_area.ra_min <= ra <= sky_area.ra_max):
                    continue
                if not (sky_area.dec_min <= dec <= sky_area.dec_max):
                    continue

                results.append(StarData(ra, dec, mag, label))

            return StarDataList(results)
