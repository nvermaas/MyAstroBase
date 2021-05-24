# create starmaps using skyfield and matplotlib

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.collections import LineCollection

from skyfield.api import Star, load
from skyfield.constants import GM_SUN_Pitjeva_2005_km3_s2 as GM_SUN
from skyfield.data import hipparcos, mpc, stellarium
from skyfield.projections import build_stereographic_projection

import os
from django.conf import settings

from . import algorithms

# /astrobase/starmap?name=C/2020%20F3%20(NEOWISE)&timestamp=2020-07-12T08:55:59Z
def create_starmap(name, timestamp, days_past, days_future, fov, magnitude):

    # The comet is plotted on several dates `t_transient`.  But the stars only
    # need to be drawn once, so we take the middle comet date as the single
    # time `t` we use for everything else.

    try:
        # first try comets
        d, transient = algorithms.get_comet(name, timestamp)
    except:
        # then try asteroids
        d, transient = algorithms.get_asteroid(name, timestamp)

    ts = load.timescale()
    t_timestamp = ts.utc(timestamp.year, timestamp.month, timestamp.day, timestamp.hour, timestamp.minute)

    t_transient = ts.utc(timestamp.year, timestamp.month, range(timestamp.day-days_past, timestamp.day+days_future))
    t = t_transient[len(t_transient) // 2]  # middle date

    # An ephemeris from the JPL provides Sun and Earth positions.

    eph = load('de421.bsp')
    earth = eph['earth']

    # The Hipparcos mission provides our star catalog.

    # with load.open(hipparcos.URL) as f:
    with load.open(settings.MY_HIPPARCOS_URL) as f:
        stars = hipparcos.load_dataframe(f)

    # And the constellation outlines come from Stellarium.  We make a list
    # of the stars at which each edge stars, and the star at which each edge
    # ends.

    url = ('https://raw.githubusercontent.com/Stellarium/stellarium/master'
           '/skycultures/western_SnT/constellationship.fab')

    with load.open(url) as f:
        constellations = stellarium.parse_constellations(f)

    edges = [edge for name, edges in constellations for edge in edges]
    edges_star1 = [star1 for star1, star2 in edges]
    edges_star2 = [star2 for star1, star2 in edges]

    # We will center the chart on the comet's middle position.

    center = earth.at(t).observe(transient)
    projection = build_stereographic_projection(center)
    field_of_view_degrees = float(fov)
    limiting_magnitude = magnitude

    # Now that we have constructed our projection, compute the x and y
    # coordinates that each star and the comet will have on the plot.

    star_positions = earth.at(t).observe(Star.from_dataframe(stars))
    stars['x'], stars['y'] = projection(star_positions)

    transient_x, transient_y = projection(earth.at(t_transient).observe(transient))

    # Create a True/False mask marking the stars bright enough to be
    # included in our plot.  And go ahead and compute how large their
    # markers will be on the plot.

    bright_stars = (stars.magnitude <= limiting_magnitude)
    magnitude = stars['magnitude'][bright_stars]
    marker_size = (0.5 + limiting_magnitude - magnitude) ** 2.0

    # The constellation lines will each begin at the x,y of one star and end
    # at the x,y of another.  We have to "rollaxis" the resulting coordinate
    # array into the shape that matplotlib expects.

    xy1 = stars[['x', 'y']].loc[edges_star1].values
    xy2 = stars[['x', 'y']].loc[edges_star2].values
    lines_xy = np.rollaxis(np.array([xy1, xy2]), 1)

    # Time to build the figure!

    fig, ax = plt.subplots(figsize=[9, 12])

    # Draw the constellation lines.

    ax.add_collection(LineCollection(lines_xy, colors='#00f2'))

    # Draw the stars.

    ax.scatter(stars['x'][bright_stars], stars['y'][bright_stars],
               s=marker_size, color='k')

    # Draw the comet positions, and label them with dates.

    transient_color = '#f00'
    offset = 0.001

    ax.plot(transient_x, transient_y, '+', c=transient_color, zorder=3)

    for xi, yi, tstr in zip(transient_x, transient_y, t_transient.utc_strftime('%m/%d')):
        tstr = tstr.lstrip('0')
        text = ax.text(xi + offset, yi - offset, tstr, color=transient_color,
                       ha='left', va='top', fontsize=9, weight='bold', zorder=-1)
        text.set_alpha(0.5)

    # Finally, title the plot and set some final parameters.

    angle = np.pi - field_of_view_degrees / 360.0 * np.pi
    limit = np.sin(angle) / (1.0 - np.cos(angle))

    ax.set_xlim(-limit, limit)
    ax.set_ylim(-limit, limit)
    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)
    ax.set_aspect(1.0)
    ax.set_title('{} {} through {}'.format(
        name,
        t_transient[0].utc_strftime('%d %B %Y'),
        t_transient[-1].utc_strftime('%d %B %Y'),
    ))

    # Save.
    filename = 'starmap.png'
    path = os.path.join(settings.MEDIA_ROOT, filename)

    fig.savefig(path, bbox_inches='tight')

    image_url = os.path.join(settings.MEDIA_URL, filename)
    return image_url