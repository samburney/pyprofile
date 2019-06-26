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

    dem_srid = dem.get_srid()
    elevation = dem.get_elevation(coord_lat, coord_lng, coord_srid)

    print(
        f'Single Point Test\n'
        f'-----------------\n'
        f'SRID: {dem_srid}\n'
        f'Lat: {coord_lat}\n'
        f'Lng: {coord_lng}\n'
        f'Elevation: {elevation} m\n'
    )

    # A to B profile test (Sampled)
    coords = (test_values.profile_coords[0], test_values.profile_coords[-1])
    sample_dist = test_values.sample_dist
    computed_distance = functions.get_distance(*coords)
    dem_distance = dem.get_distance(*coords, coord_srid)
    computed_bearing = functions.get_bearing(*coords)
    dem_bearing = dem.get_bearing(*coords, coord_srid)
    elevation_profile_sampled = dem.get_elevation_profile_sampled(coords, coord_srid, sample_dist)

    print(
        f'A to B profile test (Sampled)\n'
        f'-----------------------------\n'
        f'A: {coords[0]}\n'
        f'B: {coords[1]}\n'
        f'Points sampled: {len(elevation_profile_sampled)}\n'
        f'Computed Distance: {computed_distance} m\n'
        f'DEM Distance: {dem_distance} m\n'
        f'Computed Bearing: {computed_bearing} degrees\n'
        f'DEM Bearing: {dem_bearing} degrees\n'
        f'Start elevation: {elevation_profile_sampled[0].lat}, {elevation_profile_sampled[0].lng}, {elevation_profile_sampled[0].distance:.2f}, {elevation_profile_sampled[0].elevation:.2f}\n'
        f'End elevation: {elevation_profile_sampled[-1].lat}, {elevation_profile_sampled[-1].lng}, {elevation_profile_sampled[-1].distance:.2f}, {elevation_profile_sampled[-1].elevation:.2f}\n'
    )

    # A to B profile test (Full resolution)
    elevation_profile = dem.get_elevation_profile(coords, coord_srid)

    print(
        f'A to B profile test (Full Resolution)\n'
        f'-------------------------------------\n'
        f'A: {coords[0]}\n'
        f'B: {coords[1]}\n'
        f'Points sampled: {len(elevation_profile)}\n'
        f'Computed Distance: {computed_distance} m\n'
        f'DEM Distance: {dem_distance} m\n'
        f'Computed Bearing: {computed_bearing} degrees\n'
        f'DEM Bearing: {dem_bearing} degrees\n'
        f'Start elevation: {elevation_profile[0].lat}, {elevation_profile[0].lng}, {elevation_profile[0].distance:.2f}, {elevation_profile[0].elevation:.2f}\n'
        f'End elevation: {elevation_profile[-1].lat}, {elevation_profile[-1].lng}, {elevation_profile[-1].distance:.2f}, {elevation_profile[-1].elevation:.2f}\n'
    )
