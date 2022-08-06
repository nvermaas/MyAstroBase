import psycopg2
from psycopg2 import Error
from ..utils import timeit
import math

from .star_data import StarData, StarDataList

class UCAC4StarDatabase:
    def __init__(self,host,port,database,user,password):

        self.conn = None
        try:
            self.conn = psycopg2.connect(
                database=database,
                user=user,
                password=password,
                host=host,
                port=port
            )
        except Error as e:
            print(e)

    @timeit
    def get_stars(self, sky_area, limit):

            """
            Query all rows in the tasks table
            :param conn: the Connection object
            :return:
            """
            cur = self.conn.cursor()
            where = "ra > " + str(sky_area.ra_min) + " and "
            where+= "ra < " + str(sky_area.ra_max) + " and "
            where+= "dec > " + str(sky_area.dec_min) + " and "
            where+= "dec < " + str(sky_area.dec_max) + " and "
            where+= "j_mag < " + str(sky_area.mag_min * 1000)
            where+= " LIMIT " + str(limit)

            cur.execute("SELECT ra,dec,j_mag FROM public.stars where "+where)
            #cur.execute("SELECT ra,dec,j_mag FROM public.z570 where " + where)

            rows = cur.fetchall()

            results = []

            for row in rows:
                #print(row)
                ra = row[0]
                dec = row[1]
                mag = row[2]/1000
                label = ""

                # add magnitude as label
                #label = row[2]

                # add colors:
                # https://stackoverflow.com/questions/21977786/star-b-v-color-index-to-apparent-rgb-color

                results.append(StarData(ra, dec, mag, label))

            return StarDataList(results)


    def cone_search(self, sky_area, limit):
        pass