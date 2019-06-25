from flask import current_app as app


# Quick log function
def log(var):
    app.logger.info(var)
