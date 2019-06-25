from pyprofile import create_app, functions, dem

import test_values

# Create app
app = create_app()

# In app context, test!
with app.app_context():
    # Single point test
    coord_lat = test_values.coord_lat
    coord_lng = test_values.coord_lng
    coord_srid = test_values.coord_srid

#    dem_srid = dem.get_srid()
#    elevation = dem.get_elevation(coord_lat, coord_lng, coord_srid)
#
#    print(
#        f'SRID: {dem_srid}\n'
#        f'Lat: {coord_lat}\n'
#        f'Lng: {coord_lng}\n'
#        f'Elevation: {elevation} m\n'
#    )

    # A to B profile test
    coords = (test_values.profile_coords[0], test_values.profile_coords[-1])
    distance = functions.get_distance(*coords)
    bearing = functions.get_bearing(*coords)
    elevation_profile = dem.get_elevation_profile(coords, coord_srid)

    print(
        f'A: {coords[0]}\n'
        f'B: {coords[1]}\n'
        f'Distance: {distance} m\n'
        f'Bearing: {bearing} degrees\n'
    )
