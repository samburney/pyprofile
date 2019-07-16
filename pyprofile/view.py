from flask import current_app, Blueprint, request, render_template

from . import functions

bp = Blueprint('view', __name__, url_prefix='/view')


@bp.route('/profile', methods=('GET',))
def get_profile():
    api_base = current_app.config['PYPROFILE_API_BASE']
    api_backend = request.args.get(
        'backend') or current_app.config['PYPROFILE_DEFAULT_BACKEND']

    request_data = {
        'api_base': api_base,
        'backend': api_backend,
        'srid': int(request.args.get('srid') or 4326),
        'lat1': float(request.args.get('lat1')) or None,
        'lng1': float(request.args.get('lng1')) or None,
        'lat2': float(request.args.get('lat2')) or None,
        'lng2': float(request.args.get('lng2')) or None,
        'sample_dist': float(request.args.get('sample_dist') or 5),
    }

    return render_template('view/profile.html', request_data=request_data)
