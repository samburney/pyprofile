from flask import current_app, Blueprint, request, jsonify
import geojson

from . import functions

bp = Blueprint('api', __name__, url_prefix='/api')


# Get elevation of a single point
@bp.route('elevation', methods=('GET', 'POST'))
def get_elevation():
    lat = float(request.args.get('lat') or request.form.get('lat')) or None
    lng = float(request.args.get('lng') or request.form.get('lng')) or None
    backend = request.args.get('backend') or request.form.get(
        'backend') or current_app.config['PYPROFILE_DEFAULT_BACKEND']
    srid = request.args.get('srid') or request.form.get('srid') or 4326

    status = 'Error'
    errors = []
    data = None

    # Get elevation from backend
    backends = functions.get_backends()
    result = backends[backend].get_elevation(lat, lng, srid)

    if result is not None:
        status = 'OK'
        coordinates = (
            result.lng,
            result.lat,
            result.elevation,
        )
        data = geojson.Point(coordinates)

    json_data = {'status': status, 'errors': errors, 'data': data}

    return jsonify(json_data)
