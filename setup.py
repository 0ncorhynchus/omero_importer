#! /usr/bin/python

from setuptools import setup

setup(
    name = 'omero importer',
    version = '0.0.1',
    author = 'Suguru Kato',
    package_dir = {'omero_import': 'src'},
    packages = ['omero_import'],
    test_suite = 'test'
)
