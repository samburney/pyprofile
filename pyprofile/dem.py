from flask_sqlalchemy import SQLAlchemy
from geoalchemy2 import Raster

# Import local modules
from . functions import log

# Initialise database object
db = SQLAlchemy()


# Define table(s)
class Elevation(db.Model):
    __tablename__ = 'dem'

    rid = db.Column(db.Integer, primary_key=True)
    rast = db.Column(Raster)
    filename = db.Column(db.String(255))

    @property
    def srid(self):
        dem_srid = 4326
        query = db.session.query(self.rast.ST_SRID())
        result = query.first()
        if result:
            dem_srid = result[0]

        return dem_srid


# Helper functions
# Get table SRID value
def get_srid():
    elev = Elevation.query.first()
    srid = elev.srid

    return srid


# Make a PostGIS point object
def get_point(coord_lat, coord_lng, coord_srid):
    dem_srid = get_srid()

    # Make object
    point = None
    query = db.session.query(
        db.func.ST_SetSRID(db.func.ST_MakePoint(coord_lng, coord_lat), coord_srid)
    )
    result = query.first()
    if result:
        point = result[0]

    # Reproject if necessary
    if coord_srid != dem_srid:
        query = db.session.query(db.func.ST_Transform(point, dem_srid))
        result = query.first()
        if result:
            point = result[0]

    return point


# Get the elevation of a single point
def get_elevation(lat, lng, srid):
    point = get_point(lat, lng, srid)

    query = db.session.query(Elevation.rast.ST_Value(point)
                             ).filter(Elevation.rast.ST_Intersects(point))
    result = query.first()
    elevation = result[0]

    return elevation


# Get elevation profile
def get_elevation_profile(coords, srid):
    coords_a = coords[0]
    coords_b = coords[-1]

    point_a = get_point(*coords_a, srid)
    point_b = get_point(*coords_b, srid)

    dem_srid = get_srid()

    # Make a line
    query = db.session.query(db.func.ST_Makeline(point_a, point_b))
    result = query.first()
    if result:
        line = result[0]

    print(line)

    # Get the elevation for every intersected cell on the line
    query = db.session.query(
        db.func.ST_Centroid(
            db.func.ST_Intersection(Elevation.rast, line),
            
        )
    )

    return
