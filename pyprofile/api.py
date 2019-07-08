from flask import current_app, Blueprint, request, jsonify
import geojson

from . import functions

bp = Blueprint('api', __name__, url_prefix='/api')


# Get elevation of a single point
@bp.route('/elevation', methods=('GET', 'POST'))
def get_elevation():
    srid = request.args.get('srid') or request.form.get('srid') or 4326
    lat = float(request.args.get('lat') or request.form.get('lat')) or None
    lng = float(request.args.get('lng') or request.form.get('lng')) or None

    backend_name = request.args.get('backend') or request.form.get(
        'backend') or current_app.config['PYPROFILE_DEFAULT_BACKEND']

    status = 'Error'
    errors = []
    data = None

    # Get DEM backend
    backends = functions.get_backends()
    backend = backends[backend_name]

    # Get elevation from backend
    result = backend.get_elevation(lat, lng, srid)

    if result is not None:
        status = 'OK'
        coordinates = (
            result.lng,
            result.lat,
            result.elevation,
        )
        data = {
            'geojson': geojson.Point(coordinates),
        }

    json_data = {'status': status, 'errors': errors, 'data': data}

    return jsonify(json_data)


# Get A to B elevation profile
@bp.route('/profile/sampled', methods=('GET', 'POST'))
@bp.route('/profile', methods=('GET', 'POST'))
def get_profile():
    srid = int(request.args.get('srid') or request.form.get('srid') or 4326)
    lat1 = float(request.args.get('lat1') or request.form.get('lat1')) or None
    lng1 = float(request.args.get('lng1') or request.form.get('lng1')) or None
    lat2 = float(request.args.get('lat2') or request.form.get('lat2')) or None
    lng2 = float(request.args.get('lng2') or request.form.get('lng2')) or None
    sample_dist = float(request.args.get('sample_dist') or request.form.get('sample_dist') or 5)

    backend_name = request.args.get('backend') or request.form.get(
        'backend') or current_app.config['PYPROFILE_DEFAULT_BACKEND']

    status = 'Error'
    errors = []
    data = None

    # Get DEM backend
    backends = functions.get_backends()
    backend = backends[backend_name]

    # Get elevation from backend
    results = None
    if str(request.url_rule) == '/api/profile':
        results = backend.get_elevation_profile(
            ((lat1, lng1), (lat2, lng2)), srid)
    elif str(request.url_rule) == '/api/profile/sampled':
        results = backend.get_elevation_profile_sampled(
            ((lat1, lng1), (lat2, lng2)), srid, sample_dist)

    if results is not None:
        status = 'OK'

        coordinates = []
        coordinate_distances = []
        for result in results:
            coordinates.append((
                result.lng,
                result.lat,
                result.elevation,
            ))
            coordinate_distances.append(f'{result.distance:6f}')
        data = {
            'geojson': geojson.LineString(coordinates),
            'coordinate_distances': coordinate_distances,
            'distance': backend.get_distance((lat1, lng1), (lat2, lng2), srid),
            'bearing': backend.get_bearing((lat1, lng1), (lat2, lng2), srid),
            'samples': len(results),
        }
    json_data = {'status': status, 'errors': errors, 'data': data}

    return jsonify(json_data)


# Get A to B distance
@bp.route('/distance', methods=('GET', 'POST'))
def get_distance():
    srid = int(request.args.get('srid') or request.form.get('srid') or 4326)
    lat1 = float(request.args.get('lat1') or request.form.get('lat1')) or None
    lng1 = float(request.args.get('lng1') or request.form.get('lng1')) or None
    lat2 = float(request.args.get('lat2') or request.form.get('lat2')) or None
    lng2 = float(request.args.get('lng2') or request.form.get('lng2')) or None

    backend_name = request.args.get('backend') or request.form.get(
        'backend') or current_app.config['PYPROFILE_DEFAULT_BACKEND']

    status = 'Error'
    errors = []
    data = None

    # Get DEM backend
    backends = functions.get_backends()
    backend = backends[backend_name]

    # Get distance from backend
    result = backend.get_distance((lat1, lng1), (lat2, lng2), srid)
    if result is not None:
        status = 'OK'

        data = {
            'distance': result,
        }
    json_data = {'status': status, 'errors': errors, 'data': data}

    return jsonify(json_data)


# Get A to B bearing
@bp.route('/bearing', methods=('GET', 'POST'))
def get_bearing():
    srid = int(request.args.get('srid') or request.form.get('srid') or 4326)
    lat1 = float(request.args.get('lat1') or request.form.get('lat1')) or None
    lng1 = float(request.args.get('lng1') or request.form.get('lng1')) or None
    lat2 = float(request.args.get('lat2') or request.form.get('lat2')) or None
    lng2 = float(request.args.get('lng2') or request.form.get('lng2')) or None

    backend_name = request.args.get('backend') or request.form.get(
        'backend') or current_app.config['PYPROFILE_DEFAULT_BACKEND']

    status = 'Error'
    errors = []
    data = None

    # Get DEM backend
    backends = functions.get_backends()
    backend = backends[backend_name]

    # Get bearing from backend
    result = backend.get_bearing((lat1, lng1), (lat2, lng2), srid)
    if result is not None:
        status = 'OK'

        data = {
            'bearing': result,
        }
    json_data = {'status': status, 'errors': errors, 'data': data}

    return jsonify(json_data)
