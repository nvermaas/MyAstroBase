import sqlite3
from sqlite3 import Error

import codecs
from .star_data import StarData, StarDataList

class StarDatabase:
    def __init__(self, db_file):

        self.conn = None
        try:
            self.conn = sqlite3.connect(db_file)
        except Error as e:
            print(e)


    def get_stars(self, sky_area):

            """
            Query all rows in the tasks table
            :param conn: the Connection object
            :return:
            """
            cur = self.conn.cursor()
            cur.execute("SELECT RightAscension,Declination,Magnitude,BayerFlamsteed FROM hygdata")

            rows = cur.fetchall()

            matches = []

            for row in rows:
                #print(row)
                ra = row[0]/15
                dec = row[1]
                mag = row[2]
                label = row[3]

                # add magnitude as label
                #label = row[2]

                # add colors:
                # https://stackoverflow.com/questions/21977786/star-b-v-color-index-to-apparent-rgb-color

                if mag > sky_area.mag_min:  # because smaller mag values mean brighter stars
                    continue
                if not (sky_area.ra_min <= ra <= sky_area.ra_max):
                    continue
                if not (sky_area.dec_min <= dec <= sky_area.dec_max):
                    continue

                matches.append(StarData(ra, dec, mag, label))

            return StarDataList(matches)