from setuptools import setup, find_packages

requires = [
    'flask',
    'flask_sqlalchemy',
    'GeoAlchemy2',
    'geographiclib',
]

setup(
    name='pyprofile',
    version='0.0.1',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=requires,
)
