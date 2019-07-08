import requests
from flask import current_app

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
    api_base = current_app.config['PYPROFILE_API_BASE']
    api_backend = current_app.config['PYPROFILE_API_BACKEND'] or 'postgis'

    elevation = None

    request_url = f'{api_base}/elevation'
    request_data = {
        'srid': srid,
        'lat': lat,
        'lng': lng,
        'backend': api_backend,
    }

    request = requests.post(request_url, request_data)
    if request.status_code == 200:
        result = request.json()

        if result['status'] == 'OK':
            elevation = {
                'lat': result['data']['geojson']['coordinates'][1],
                'lng': result['data']['geojson']['coordinates'][0],
                'elevation': result['data']['geojson']['coordinates'][2],
            }
            elevation = functions.dotdict(elevation)

    return elevation


# Get an elevation profile
def get_elevation_profile(coords, srid=get_srid()):
    return get_elevation_profile_sampled(coords, srid=get_srid(), sample_dist=None, unsampled=True)


# Get a distance sampled elevation profile
def get_elevation_profile_sampled(coords, srid=get_srid(), sample_dist=5, unsampled=False):
    api_base = current_app.config['PYPROFILE_API_BASE']
    api_backend = current_app.config['PYPROFILE_API_BACKEND'] or 'postgis'

    elevations = None

    # Get first and last coordinate
    coord_a = coords[0]
    coord_b = coords[-1]

    if unsampled is False:
        request_url = f'{api_base}/profile/sampled'
    elif unsampled is True:
        request_url = f'{api_base}/profile'

    request_data = {
        'srid': srid,
        'lat1': coord_a[0],
        'lng1': coord_a[1],
        'lat2': coord_b[0],
        'lng2': coord_b[1],
        'backend': api_backend,
    }

    request = requests.post(request_url, request_data)
    if request.status_code == 200:
        result = request.json()

        if result['status'] == 'OK':
            elevations = []
            for index, coordinate in enumerate(result['data']['geojson']['coordinates']):
                elevation = {
                    'lng': float(coordinate[1]),
                    'lat': float(coordinate[0]),
                    'elevation': float(coordinate[2]),
                    'distance': float(result['data']['coordinate_distances'][index]),
                }
                elevations.append(functions.dotdict(elevation))

    return elevations


# Get distance between two points
def get_distance(coord_a, coord_b, srid=get_srid()):
    api_base = current_app.config['PYPROFILE_API_BASE']
    api_backend = current_app.config['PYPROFILE_API_BACKEND'] or 'postgis'

    distance = None

    request_url = f'{api_base}/distance'
    request_data = {
        'srid': srid,
        'lat1': coord_a[0],
        'lng1': coord_a[1],
        'lat2': coord_b[0],
        'lng2': coord_b[1],
        'backend': api_backend,
    }

    request = requests.post(request_url, request_data)
    if request.status_code == 200:
        result = request.json()

        if result['status'] == 'OK':
            distance = result['data']['distance']

    return distance


# Get bearing between two points
def get_bearing(coord_a, coord_b, srid=get_srid()):
    api_base = current_app.config['PYPROFILE_API_BASE']
    api_backend = current_app.config['PYPROFILE_API_BACKEND'] or 'postgis'

    bearing = None

    request_data = {
        'srid': srid,
        'lat1': coord_a[0],
        'lng1': coord_a[1],
        'lat2': coord_b[0],
        'lng2': coord_b[1],
        'backend': api_backend,
    }

    request_url = f'{api_base}/bearing'
    request = requests.post(request_url, request_data)
    if request.status_code == 200:
        result = request.json()

        if result['status'] == 'OK':
            bearing = result['data']['bearing']

    return bearing
