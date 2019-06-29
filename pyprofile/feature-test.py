import argparse
import importlib
from pyprofile import create_app, functions

import test_values


def parse_args():
    parser = argparse.ArgumentParser(description="PyProfile Feature Test")
    parser.add_argument(
        'backend', help="Name of elevation backend; defaults to 'postgis'", nargs='?', default='postgis')
    parser.add_argument('-t', '--test-full-resolution',
                        help='Include full resolution test', action='store_true')

    args = parser.parse_args()

    return args


def main():
    # Parse CLI arguments
    args = parse_args()

    # Import chosen backend
    backend = importlib.import_module(f'backends.{args.backend}')

    # Create app
    app = create_app()

    # In app context, test!
    with app.app_context():
        # Initialise any flask extensions exposed by the backend
        backend.init_app(app)

        # Single point test
        coord_lat = test_values.coord_lat
        coord_lng = test_values.coord_lng
        coord_srid = test_values.coord_srid

        dem_srid = backend.get_srid()
        elevation = backend.get_elevation(coord_lat, coord_lng, coord_srid)

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
        dem_distance = backend.get_distance(*coords, coord_srid)
        computed_bearing = functions.get_bearing(*coords)
        dem_bearing = backend.get_bearing(*coords, coord_srid)
        elevation_profile_sampled = backend.get_elevation_profile_sampled(coords, coord_srid, sample_dist)

        if elevation_profile_sampled:
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
        if args.test_full_resolution:
            elevation_profile = backend.get_elevation_profile(coords, coord_srid)

            if elevation_profile:
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


# Entrypoint
if __name__ == "__main__":
    main()
