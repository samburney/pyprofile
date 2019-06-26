from flask_sqlalchemy import SQLAlchemy
from geoalchemy2 import Raster


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
        query = db.session.query(self.rast.ST_SRID().label('srid'))
        result = query.first()
        if result:
            dem_srid = result.srid

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


# Get elevation profile
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
