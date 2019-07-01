import math
import os
import re
import importlib
from flask import current_app
from geographiclib.geodesic import Geodesic


# Quick log function
def log(var):
    current_app.logger.info(var)


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


# Import and initialise pyprofile backends
def get_backends():
    backends = {}
    script_root = os.path.dirname(os.path.realpath(__file__))
    with os.scandir(f'{script_root}{os.sep}backends') as backend_dirs:
        for backend_dir in backend_dirs:
            if not re.match(r'\.|_', backend_dir.name) and backend_dir.is_dir():
                backend = importlib.import_module(f'pyprofile.backends.{backend_dir.name}')
                backends[backend_dir.name] = backend

    return backends


# Enable 'dot' access to dict keys
class dotdict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__
