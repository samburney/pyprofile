from flask_sqlalchemy import SQLAlchemy
import sqlalchemy
from geoalchemy2 import Raster, Geometry
import geoalchemy2.types


# Initialise database object
db = SQLAlchemy()


# Handle Flask App Initialisation
def init_app(app):
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialise POSTGIS DEM DB
    if not app.config.get('SQLALCHEMY_DATABASE_URI', None):
        app.config['SQLALCHEMY_DATABASE_URI'] = sqlalchemy.engine.url.URL(
            app.config['POSTGIS_DRIVER'],
            host=app.config['POSTGIS_HOST'],
            port=app.config['POSTGIS_PORT'],
            database=app.config['POSTGIS_DATABASE'],
            username=app.config['POSTGIS_USERNAME'],
            password=app.config['POSTGIS_PASSWORD'],
        )

    db.init_app(app)


# Define table(s)
class Elevation(db.Model):
    __tablename__ = 'dem'

    rid = db.Column(db.Integer, primary_key=True)
    rast = db.Column(Raster)
    filename = db.Column(db.String(255))

    @property
    def srid(self):
        dem_srid = 4326
        query = db.session.query(self.rast.ST_SRID().label('srid'))
        result = query.first()
        if result:
            dem_srid = result.srid

        return dem_srid


# Custom SQLAlchemy Data Types
class GeomvalType(geoalchemy2.types.CompositeType):
    typemap = {'geom': Geometry('MULTIPOLYGON'), 'val': db.Float}


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
        db.func.ST_SetSRID(
            db.func.ST_MakePoint(coord_lng, coord_lat), coord_srid
        ).label('point')
    )
    result = query.first()
    if result:
        point = result.point

    # Reproject if necessary
    if coord_srid != dem_srid:
        query = db.session.query(db.func.ST_Transform(point, dem_srid).label('point'))
        result = query.first()
        if result:
            point = result.point

    return point


# Get the elevation of a single point
def get_elevation(lat, lng, srid):
    point = get_point(lat, lng, srid)
    elevation = None

    query = db.session.query(
        Elevation.rast.ST_Value(point).label('elevation')
    ).filter(Elevation.rast.ST_Intersects(point))
    result = query.first()
    if result:
        elevation = result.elevation

    return elevation


# Get an elevation profile
def get_elevation_profile(coords, srid):
    elevations = None
    dem_srid = get_srid()

    # Get first and last coordinate and make a PostGIS point for each
    coords_a = coords[0]
    coords_b = coords[-1]
    point_a = get_point(*coords_a, srid)
    point_b = get_point(*coords_b, srid)

    # Build a series of subqueries which will combine together to return a path profile
    # Make a line from point_a to point_b
    line = db.select([db.func.ST_MakeLine(point_a, point_b).label('geom')]).cte('line')

    # Find the coordinates of each DEM cell line intersects with
    intersection_geomvals = db.select([
        db.type_coerce(Elevation.rast.ST_Intersection(line.c.geom), GeomvalType()).label('geomval')
    ]).where(Elevation.rast.ST_Intersects(line.c.geom)).cte('intersection_geomvals')
    intersection_geomvals_q = db.session.query(intersection_geomvals)

    # Get values for each coordinate
    intersections = db.select([
        db.func.ST_Centroid(
            intersection_geomvals_q.subquery().c.geomval.geom
        ).label('geom'),
        intersection_geomvals_q.subquery().c.geomval.val.label('val')
    ]).cte('intersections')

    # Create a 3D point with the elevation on the Z axis
    profile_points = db.select([
        db.func.ST_SetSRID(
            db.func.ST_MakePoint(
                db.func.ST_X(intersections.c.geom),
                db.func.ST_Y(intersections.c.geom),
                intersections.c.val
            ),
            dem_srid
        ).label('geom'),
        db.func.ST_Distance(
            db.func.ST_StartPoint(line.c.geom), intersections.c.geom
        ).label('distance')
    ]).order_by('distance').cte('profile_points')

    # Build query and get elevation data
    query = db.session.query(
        db.func.ST_Y(db.func.ST_Transform(profile_points.c.geom, srid)).label('lat'),
        db.func.ST_X(db.func.ST_Transform(profile_points.c.geom, srid)).label('lng'),
        profile_points.c.distance.label('distance'),
        db.func.ST_Z(profile_points.c.geom).label('elevation'),
    )
    result = query.all()
    if result:
        elevations = result

    return elevations


# Get a distance sampled elevation profile
def get_elevation_profile_sampled(coords, srid, sample_dist):
    elevations = None
    dem_srid = get_srid()

    # Get first and last coordinate and make a PostGIS point for each
    coords_a = coords[0]
    coords_b = coords[-1]
    point_a = get_point(*coords_a, srid)
    point_b = get_point(*coords_b, srid)

    # Build a series of subqueries which will combine together to return a path profile
    # Make a line from point_a to point_b
    line = db.select([db.func.ST_MakeLine(point_a, point_b).label('geom')]).cte('line')

    # Chop line into segments matching the sample_dist in metres
    line_segments = db.select([
        db.func.ST_AddMeasure(
            line.c.geom, 0, db.func.ST_Length(line.c.geom)
        ).label('linem'),
        db.func.Generate_Series(
            0, db.cast(db.func.ST_Length(line.c.geom), db.Integer), sample_dist
        ).label('sample'),
    ]).cte('line_segments')

    # Get the coordinates of each segment along the line
    line_points = db.select([
        db.func.ST_GeometryN(
            db.func.ST_LocateAlong(line_segments.c.linem, line_segments.c.sample), 1
        ).label('geom')
    ]).cte('line_points')

    # Find the coordinates of the DEM cell each line_point intersects with
    intersections = db.select([
        line_points.c.geom.label('geom'),
        db.func.ST_Value(Elevation.rast, 1, line_points.c.geom).label('val')
    ]).where(Elevation.rast.ST_Intersects(line_points.c.geom)).cte('intersections')

    # Create a 3D point with the elevation on the Z axis
    profile_points = db.select([
        db.func.ST_SetSRID(
            db.func.ST_MakePoint(
                db.func.ST_X(intersections.c.geom),
                db.func.ST_Y(intersections.c.geom),
                intersections.c.val
            ),
            dem_srid
        ).label('geom'),
        db.func.ST_Distance(
            db.func.ST_StartPoint(line.c.geom), intersections.c.geom
        ).label('distance')
    ]).order_by('distance').cte('profile_points')

    # Build query and get elevation data
    query = db.session.query(
        db.func.ST_Y(db.func.ST_Transform(profile_points.c.geom, srid)).label('lat'),
        db.func.ST_X(db.func.ST_Transform(profile_points.c.geom, srid)).label('lng'),
        profile_points.c.distance.label('distance'),
        db.func.ST_Z(profile_points.c.geom).label('elevation'),
    )
    result = query.all()
    if result:
        elevations = result

    return elevations


# Get distance between two points
def get_distance(coord_a, coord_b, srid):
    distance = None

    point_a = get_point(*coord_a, srid)
    point_b = get_point(*coord_b, srid)

    query = db.session.query(
        db.func.ST_Distance(point_a, point_b).label('distance')
    )
    result = query.one()
    if result:
        distance = result.distance

    return distance


# Get bearing between two points
def get_bearing(coord_a, coord_b, srid):
    bearing = None

    point_a = get_point(*coord_a, srid)
    point_b = get_point(*coord_b, srid)

    query = db.session.query(
        db.func.degrees(db.func.ST_Azimuth(point_a, point_b)).label('bearing')
    )
    result = query.one()
    if result:
        bearing = result.bearing

    return bearing
