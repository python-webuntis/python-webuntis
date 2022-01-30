#!/usr/bin/env python
"""
    This file is part of python-webuntis

    :copyright: (c) 2012 by Markus Unterwaditzer.
    :license: BSD, see LICENSE for more details.
"""

from setuptools import setup, find_packages
from sys import version_info

dependencies = ['requests']

setup(
    name='webuntis',
    version='0.1.12',
    author=u'Markus Unterwaditzer, August Hörandl',
    author_email='markus@unterwaditzer.net, august.hoerandl@gmx.at',
    packages=find_packages(),
    include_package_data=True,
    url='https://github.com/python-webuntis/python-webuntis',
    license='new-style BSD',
    description='Bindings for WebUntis API',
    long_description=open('README.rst').read(),
    install_requires=dependencies,
    classifiers=[
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: Implementation :: PyPy'
    ]
)
