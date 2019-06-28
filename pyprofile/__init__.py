from flask import Flask


# Create Flask app
def create_app():
    app = Flask(__name__)

    # Default config
    app.config.from_mapping(
        DEBUG=True,
        SECRET_KEY=None,
    )

    # Load config file, if it exists
    app.config.from_pyfile('config.py', silent=True)

    @app.route('/')
    def home():
        return 'Welcome!'

    # Return app factory
    return app
