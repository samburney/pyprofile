from pyprofile import create_app, dem

import test_values

# Create app
app = create_app()

# In app context, test!
with app.app_context():
    coord_lat = test_values.coord_lat
    coord_lng = test_values.coord_lng
    coord_srid = test_values.coord_srid

    dem_srid = dem.get_srid()
    elevation = dem.get_elevation(coord_lat, coord_lng, coord_srid)

    print(
        f'SRID: {dem_srid}\n'
        f'Lat: {coord_lat}\n'
        f'Lng: {coord_lng}\n'
        f'Elevation: {elevation} m\n'
    )
