from sqlalchemy import engine, func, create_engine, Column, Integer, String
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from geoalchemy2 import Raster

import test_values
import config


# Set up SQLAlchemy
Base = declarative_base()


# Define table(s)
class Elevation(Base):
    __tablename__ = 'dem'
    rid = Column(Integer, primary_key=True)
    rast = Column(Raster)
    filename = Column(String(255))


# Initialise DB Connection
pg_uri = engine.url.URL(
    'postgresql',
    host=config.POSTGIS_HOST,
    port=config.POSTGIS_PORT,
    database=config.POSTGIS_DATABASE,
    username=config.POSTGIS_USERNAME,
    password=config.POSTGIS_PASSWORD,
)
engine = create_engine(pg_uri)
db = scoped_session(sessionmaker(bind=engine))


# Define test values
coord_lat = test_values.coord_lat
coord_lng = test_values.coord_lng
coord_srid = test_values.coord_srid


# Get DEM SRID value
dem_srid = 4326
query = db.query(Elevation.rast.ST_SRID())
result = query.first()
if result:
    dem_srid = result[0]

# Make the coord object
query = db.query(
    func.ST_SetSRID(func.ST_MakePoint(coord_lng, coord_lat), coord_srid)
)
result = query.first()
if result:
    coord = result[0]

# Reproject coord if necessary
if dem_srid != coord_srid:
    query = db.query(func.ST_Transform(coord, dem_srid))
    result = query.first()
    if result:
        coord = result[0]

# Get elevation of a point
query = db.query(
    Elevation.rast.ST_Value(coord)
).filter(
    Elevation.rast.ST_Intersects(coord)
)
result = query.first()
elevation = result[0]


print(
    f'SRID: {dem_srid}\n'
    f'Lat: {coord_lat}\n'
    f'Lng: {coord_lng}\n'
    f'Elevation: {elevation} m\n'
)
