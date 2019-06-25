import pgdb

import test_values
import config


# Connect to DB
conn = pgdb.connect(
    host=f'{config.POSTGIS_HOST}:{config.POSTGIS_PORT}',
    user=config.POSTGIS_USERNAME,
    password=config.POSTGIS_PASSWORD,
    database=config.POSTGIS_DATABASE,
)
with conn:
    # Define test values
    coord_lat = test_values.coord_lat
    coord_lng = test_values.coord_lng
    coord_srid = test_values.coord_srid

    # Get DEM SRID value
    sql = f'SELECT ST_SRID(rast) FROM dem LIMIT 1'
    cursor = conn.cursor()
    with cursor:
        cursor.execute(sql)
        dem_srid = cursor.fetchone().st_srid

    # Get elevation of a point
    sql = (
        f'SELECT ST_Value(rast, ST_Transform(ST_SetSRID(ST_MakePoint({coord_lng}, {coord_lat}), 4326), {dem_srid}))'
        f'  AS elevation'
        f'  FROM dem'
        f'  WHERE ST_Intersects(rast, ST_Transform(ST_SetSRID(ST_MakePoint({coord_lng}, {coord_lat}), 4326), {dem_srid}))'
    )
    cursor = conn.cursor()
    with cursor:
        cursor.execute(sql)
        elevation = cursor.fetchone().elevation

    print(
        f'SRID: {dem_srid}\n'
        f'Lat: {coord_lat}\n'
        f'Lng: {coord_lng}\n'
        f'Elevation: {elevation} m\n'
    )
