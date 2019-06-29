import math

from flask import g
import googlemaps

import functions


# Handle Flask App Initialisation
def init_app(app):
    g.gmaps = googlemaps.Client(key=app.config['GOOGLE_MAPS_API_KEY'])

    return


# Helper functions
# Get table SRID value
def get_srid():
    srid = 4326
    return srid


# Get the elevation of a single point
def get_elevation(lat, lng, srid=get_srid()):
    elevation = None

    result = g.gmaps.elevation((lat, lng))
    if result:
        elevation = result[0]['elevation']

    return elevation


# Get an elevation profile
def get_elevation_profile(coords, srid=get_srid()):
    elevations = None
    max_samples = 512

    # Get first and last coordinate
    coord_a = coords[0]
    coord_b = coords[-1]

    # Make API request
    result = g.gmaps.elevation_along_path([coord_a, coord_b], max_samples)
    if result:
        elevations = []
        for r in result:
            elevation = {
                'lat': r['location']['lat'],
                'lng': r['location']['lng'],
                'elevation': r['elevation'],
                'distance': functions.get_distance(coord_a, (r['location']['lat'], r['location']['lng'])),
            }
            elevations.append(functions.dotdict(elevation))

    return elevations


# Get a distance sampled elevation profile
def get_elevation_profile_sampled(coords, srid=get_srid(), sample_dist=5):
    elevations = None
    max_samples = 512

    # Get first and last coordinate
    coord_a = coords[0]
    coord_b = coords[-1]

    # Work out how many samples to request along the path
    distance = functions.get_distance(coord_a, coord_b)
    samples = math.ceil(distance / sample_dist)

    if samples > max_samples:
        samples = max_samples

    # Make API request
    result = g.gmaps.elevation_along_path([coord_a, coord_b], samples)
    if result:
        elevations = []
        for r in result:
            elevation = {
                'lat': r['location']['lat'],
                'lng': r['location']['lng'],
                'elevation': r['elevation'],
                'distance': functions.get_distance(coord_a, (r['location']['lat'], r['location']['lng'])),
            }
            elevations.append(functions.dotdict(elevation))

    return elevations


# Get distance between two points
def get_distance(coord_a, coord_b, srid=get_srid()):
    distance = functions.get_distance(coord_a, coord_b)
    return distance


# Get bearing between two points
def get_bearing(coord_a, coord_b, srid=get_srid()):
    bearing = functions.get_bearing(coord_a, coord_b)
    return bearing
