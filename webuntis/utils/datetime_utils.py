'''
    This file is part of python-webuntis

    :copyright: (c) 2012 by Markus Unterwaditzer.
    :license: BSD, see LICENSE for more details.
'''

from __future__ import unicode_literals
from datetime import datetime as datetime


forms = {
    'date' : ('%Y%m%d', 6),
    'time': ('%H%M', 4),
}


def parse_date(string):
    return _parse(string, 'date')


def parse_time(string):
    return _parse(string, 'time')


def parse_datetime(date, time):
    pdate = parse_date(date)
    ptime = parse_time(time)

    newdate = datetime(
        year=pdate.year,
        month=pdate.month,
        day=pdate.day,
        hour=ptime.hour,
        minute=ptime.minute
    )

    return newdate


def _parse(string, form):
    if type(string) == int:
        string = str(string)

    formlen = forms[form][1]
    while len(string) < formlen:
        string = '0' + string

    return datetime.strptime(string, forms[form][0]) 


def format_date(obj):
    return _format(obj, 'date')


def format_time(obj):
    return _format(obj, 'time')


def _format(obj, form):
    return int(datetime.strftime(obj, forms[form][0]))
