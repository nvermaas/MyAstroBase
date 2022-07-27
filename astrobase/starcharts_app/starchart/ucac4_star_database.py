import psycopg2
from psycopg2 import Error
from ..utils import timeit

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
            where = "ra > " + str(sky_area.ra_min * 15) + " and "
            where+= "ra < " + str(sky_area.ra_max * 15) + " and "
            where+= "dec > " + str(sky_area.dec_min) + " and "
            where+= "dec < " + str(sky_area.dec_max) + " and "
            where+= "j_mag < " + str(sky_area.mag_min * 1000)
            where+= " LIMIT " + str(limit)

            cur.execute("SELECT ra,dec,j_mag FROM public.stars where "+where)

            rows = cur.fetchall()

            matches = []

            for row in rows:
                #print(row)
                ra = row[0]/15
                dec = row[1]
                mag = row[2]/1000
                label = ""

                # add magnitude as label
                #label = row[2]

                # add colors:
                # https://stackoverflow.com/questions/21977786/star-b-v-color-index-to-apparent-rgb-color

                matches.append(StarData(ra, dec, mag, label))

            return StarDataList(matches)


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