from flask import Flask

from . import functions


# Create Flask app
def create_app():
    app = Flask(__name__)

    # Default config
    app.config.from_mapping(
        DEBUG=True,
        SECRET_KEY=None,
        PYPROFILE_DEFAULT_BACKEND='postgis',
    )

    # Load config file, if it exists
    app.config.from_pyfile('config.py', silent=True)

    # Import and initialise pyprofile backends
    with app.app_context():
        backends = functions.get_backends()
        for name, backend in backends.items():
            backend.init_app(app)

    # Register blueprints
    from . import api
    app.register_blueprint(api.bp)

    # Return app factory
    return app
