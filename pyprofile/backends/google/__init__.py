import math

from flask import current_app
import googlemaps

import pyprofile.functions as functions


# Handle Flask App Initialisation
def init_app(app):
    return


# Helper functions
# Get table SRID value
def get_srid():
    srid = 4326
    return srid


# Get the elevation of a single point
def get_elevation(lat, lng, srid=get_srid()):
    gmaps = googlemaps.Client(key=current_app.config['GOOGLE_MAPS_API_KEY'])
    elevation = None

    result = gmaps.elevation((lat, lng))
    if result:
        elevation = {
            'lat': result[0]['location']['lat'],
            'lng': result[0]['location']['lng'],
            'elevation': result[0]['elevation'],
        }
        elevation = functions.dotdict(elevation)

    return elevation


# Get an elevation profile
def get_elevation_profile(coords, srid=get_srid()):
    gmaps = googlemaps.Client(key=current_app.config['GOOGLE_MAPS_API_KEY'])
    elevations = None
    max_samples = 512

    # Get first and last coordinate
    coord_a = coords[0]
    coord_b = coords[-1]

    # Make API request
    result = gmaps.elevation_along_path([coord_a, coord_b], max_samples)
    if result:
        elevations = []
        for r in result:
            elevation = {
                'lng': r['location']['lng'],
                'lat': r['location']['lat'],
                'elevation': r['elevation'],
                'distance': functions.get_distance(coord_a, (r['location']['lat'], r['location']['lng'])),
            }
            elevations.append(functions.dotdict(elevation))

    return elevations


# Get a distance sampled elevation profile
def get_elevation_profile_sampled(coords, srid=get_srid(), sample_dist=5):
    gmaps = googlemaps.Client(key=current_app.config['GOOGLE_MAPS_API_KEY'])
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
    result = gmaps.elevation_along_path([coord_a, coord_b], samples)
    if result:
        elevations = []
        for r in result:
            elevation = {
                'lng': r['location']['lng'],
                'lat': r['location']['lat'],
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
