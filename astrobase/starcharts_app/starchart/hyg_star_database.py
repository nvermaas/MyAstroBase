import sqlite3
from sqlite3 import Error

from ..models import Stars
from .star_data import StarData, StarDataList

class HygStarDatabase:
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

            results = []

            for row in rows:
                #print(row)
                ra = row[0]
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

                results.append(StarData(ra, dec, mag, label))

            return StarDataList(results)


    def import_stars(self):

        """
        Import all stars from hygdata table into the stars database
        """


        cur = self.conn.cursor()
        cur.execute("SELECT RightAscension,Declination,Magnitude,HipparcosID,GlieseID,BayerFlamsteed,DistanceInParsecs,"
                    "ProperMotionRA,ProperMotionDec,RadialVelocity,AbsoluteMagnitude,Luminosity,SpectralType,"
                    "ColorIndex,Constellation,VariableMinimum,VariableMaximum FROM hygdata")

        rows = cur.fetchall()

        # clear the current Stars database
        Stars.objects.all().delete()

        for row in rows:
            # get rid of the '' in the fields that are supposed to be a float
            _row13 = None if row[13]=='' else row[13]
            _row15 = None if row[15]=='' else row[15]
            _row16 = None if row[16]=='' else row[16]

            try:
                star = Stars(
                    RightAscension=row[0],
                    Declination=row[1],
                    Magnitude=row[2],
                    HipparcosID=row[3],
                    GlieseID=row[4],
                    BayerFlamsteed=row[5],
                    DistanceInParsecs=row[6],
                    ProperMotionRA=row[7],
                    ProperMotionDec=row[8],
                    RadialVelocity=row[9],
                    AbsoluteMagnitude=row[10],
                    Luminosity=row[11],
                    SpectralType=row[12],
                    ColorIndex=_row13,
                    Constellation=row[14],
                    VariableMinimum=_row15,
                    VariableMaximum=_row16,
                )
                star.save()
            except Exception as e:
                print('error reading star: '+str(e))

            print(star)


        return