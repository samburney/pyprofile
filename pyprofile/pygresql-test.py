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
    coords = test_values.profile_coords

    # Get DEM SRID value
    sql = f'SELECT ST_SRID(rast) FROM dem LIMIT 1'
    cursor = conn.cursor()
    with cursor:
        cursor.execute(sql)
        dem_srid = cursor.fetchone().st_srid

    # Get elevation of a point
    sql = (
        f'SELECT ST_Value(rast, ST_Transform(ST_SetSRID(ST_MakePoint({coord_lng}, {coord_lat}), {coord_srid}), {dem_srid}))'
        f'  AS elevation'
        f'  FROM dem'
        f'  WHERE ST_Intersects(rast, ST_Transform(ST_SetSRID(ST_MakePoint({coord_lng}, {coord_lat}), {coord_srid}), {dem_srid}))'
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

    # Get elevation of all intersections along a line
    coords_a = coords[0]
    coords_b = coords[-1]

    sql = (
        f'WITH\n'
        f'  line AS\n'
        f'      (SELECT ST_MakeLine(\n'
        f'          ST_Transform(ST_SetSRID(ST_MakePoint({coords_a[1]}, {coords_a[0]}), {coord_srid}), {dem_srid}),\n'
        f'          ST_Transform(ST_SetSRID(ST_MakePoint({coords_b[1]}, {coords_b[0]}), {coord_srid}), {dem_srid})\n'
        f'      ) AS geom\n'
        f'  ),\n'
        f'  cells AS\n'
        f'      (SELECT ST_Centroid((ST_Intersection(dem.rast, line.geom)).geom) AS geom,\n'
        f'      (ST_Intersection(dem.rast, line.geom)).val as val\n'
        f'      FROM dem, line\n'
        f'      WHERE ST_Intersects(dem.rast, line.geom)),\n'
        f'  points3d AS\n'
        f'      (\n'
        f'          SELECT ST_SetSRID(ST_MakePoint(ST_X(cells.geom), ST_Y(cells.geom), val), {dem_srid}) AS geom,\n'
        f'              ST_Distance(ST_StartPoint(line.geom), cells.geom) as distance\n'
        f'          FROM cells, line\n'
        f'          ORDER BY distance\n'
        f'      )\n'
        f'  SELECT distance, ST_Z(geom) as y FROM points3d\n'
    )
    print(sql)
    cursor = conn.cursor()
    with cursor:
        cursor.execute(sql)
        profile_points = cursor.fetchall()

        print(profile_points)

    # Get elevation of a regular sample of intersections along a line
    coords_a = coords[0]
    coords_b = coords[-1]
    samples = 25

    sql = (
        f'WITH\n'
        f'  line AS\n'
        f'      (SELECT ST_MakeLine(\n'
        f'          ST_Transform(ST_SetSRID(ST_MakePoint({coords_a[1]}, {coords_a[0]}), {coord_srid}), {dem_srid}),\n'
        f'          ST_Transform(ST_SetSRID(ST_MakePoint({coords_b[1]}, {coords_b[0]}), {coord_srid}), {dem_srid})\n'
        f'      ) AS geom\n'
        f'  ),\n'
        f'  linemeasure AS\n'
        f'     (SELECT ST_AddMeasure(line.geom, 0, ST_Length(line.geom)) AS linem,\n'
        f'             generate_series(0, ST_Length(line.geom)::int, {samples}) AS sample\n'
        f'      FROM line),\n'
        f'  points2d AS\n'
        f'    (SELECT ST_GeometryN(ST_LocateAlong(linem, sample), 1) AS geom FROM linemeasure),\n'
        f'  cells AS\n'
        f'    (SELECT p.geom AS geom, ST_Value(dem.rast, 1, p.geom) AS val\n'
        f'     FROM dem, points2d p\n'
        f'     WHERE ST_Intersects(dem.rast, p.geom)),\n'
        f'  points3d AS\n'
        f'      (\n'
        f'          SELECT ST_SetSRID(ST_MakePoint(ST_X(cells.geom), ST_Y(cells.geom), val), {dem_srid}) AS geom,\n'
        f'              ST_Distance(ST_StartPoint(line.geom), cells.geom) as distance\n'
        f'          FROM cells, line\n'
        f'          ORDER BY distance\n'
        f'      )\n'
        f'  SELECT distance, ST_Z(geom) as y FROM points3d\n'
    )
    print(sql)
    cursor = conn.cursor()
    with cursor:
        cursor.execute(sql)
        profile_points = cursor.fetchall()

        print(profile_points)
