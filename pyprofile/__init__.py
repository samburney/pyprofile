from flask import Flask
import sqlalchemy

# Import local modules
from . import dem
from . functions import log


# Create Flask app
def create_app():
    app = Flask(__name__)

    # Default config
    app.config.from_mapping(
        DEBUG=True,
        SECRET_KEY=None,
        SQLALCHEMY_TRACK_MODIFICATIONS=True,
        SQLALCHEMY_DATABASE_URI=None,
        POSTGIS_DRIVER='postgresql',
        POSTGIS_HOST=None,
        POSTGIS_PORT=None,
        POSTGIS_USERNAME=None,
        POSTGIS_PASSWORD=None,
        POSTGIS_DATABASE=None,
    )

    # Load config file, if it exists
    app.config.from_pyfile('config.py', silent=True)

    # Initialise POSTGIS DEM DB
    if not app.config['SQLALCHEMY_DATABASE_URI']:
        app.config['SQLALCHEMY_DATABASE_URI'] = sqlalchemy.engine.url.URL(
            app.config['POSTGIS_DRIVER'],
            host=app.config['POSTGIS_HOST'],
            port=app.config['POSTGIS_PORT'],
            database=app.config['POSTGIS_DATABASE'],
            username=app.config['POSTGIS_USERNAME'],
            password=app.config['POSTGIS_PASSWORD'],
        )

    with app.app_context():
        dem.db.init_app(app)

    @app.route('/')
    def home():
        return 'Welcome!'

    # Return app factory
    return app
