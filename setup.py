#!/usr/bin/env python

from setuptools import setup
from sys import version_info

if version_info < (2,6):
    dependencies = ['simplejson']
else:
    dependencies = []

setup(
    name='webuntis',
    version='0.1.0',
    author='Markus Unterwaditzer',
    author_email='markus@unterwaditzer.net',
    packages=['webuntis', 'webuntis.utils', 'webuntis.tests'],
    include_package_data=True,
    url='http://dev.unterwaditzer.net/python-webuntis/',
    license='LICENSE',
    description='Bindings for WebUntis API',
    long_description=open('README.rst').read(),
    install_requires=dependencies
)
