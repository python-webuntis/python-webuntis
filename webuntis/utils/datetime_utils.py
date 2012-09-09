'''
    This file is part of python-webuntis

    :copyright: (c) 2012 by Markus Unterwaditzer.
    :license: BSD, see LICENSE for more details.
'''

from __future__ import unicode_literals
from datetime import datetime as datetime


def parse_date(string):
    return _parse(string, '%Y%m%d')


def parse_time(string):
    return _parse(string, '%H%M')


def parse_datetime(date, time):
    return _parse(str(date) + '///' + str(time), '%Y%m%d///%H%M')


def _parse(string, formatting):
    if type(string) == int:
        string = str(string)

    return datetime.strptime(string, formatting)


def format_date(obj):
    return _format(obj, '%Y%m%d')


def format_time(obj):
    return _format(obj, '%H%M')


def _format(obj, formatting):
    return int(datetime.strftime(obj, formatting))
