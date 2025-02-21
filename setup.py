#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
    version='0.1.24',
    author=u'Markus Unterwaditzer, August Hörandl',
    author_email='markus@unterwaditzer.net, august.hoerandl@gmx.at',
    packages=find_packages(),
    include_package_data=True,
    url='https://github.com/python-webuntis/python-webuntis',
    license='new-style BSD',
    description='Bindings for WebUntis API',
    long_description=open('README.rst').read(),
    long_description_content_type = 'text/x-rst',
    install_requires=dependencies,
    classifiers=[
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: Implementation :: PyPy'
    ]
)
