import math
from flask import current_app as app
from geographiclib.geodesic import Geodesic


# Quick log function
def log(var):
    app.logger.info(var)


# Determine bearing between two coordinates
def get_bearing(coord_a, coord_b):
    geodesic = Geodesic.WGS84.Inverse(*coord_a, *coord_b)
    bearing = geodesic['azi1']

    return bearing


# Determine distance between two coordinates
def get_distance(coord_a, coord_b):
    geodesic = Geodesic.WGS84.Inverse(*coord_a, *coord_b)
    distance = geodesic['s12']

    return distance


# Convert Radians to Degrees
def rad2deg(rad):
    deg = rad * 180 / math.pi

    return deg
