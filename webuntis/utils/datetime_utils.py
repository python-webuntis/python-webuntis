'''
    This file is part of python-webuntis

    :copyright: (c) 2012 by Markus Unterwaditzer.
    :license: BSD, see LICENSE for more details.
'''

from __future__ import unicode_literals
from datetime import datetime


forms = {
    'date': ('%Y%m%d', 6),
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
    form_string, formlen = forms[form]
    return datetime.strptime(_satinize(string, form), form_string)


def format_date(obj):
    return _format(obj, 'date')


def format_time(obj):
    return _format(obj, 'time')


def _format(obj, form):
    form_string, formlen = forms[form]
    try:
        int(obj)  # is this already formatted?
    except TypeError:
        return int(datetime.strftime(obj, form_string))
    else:
        return int(obj)

def _satinize(raw_date, form):
    '''Convert a raw date/time integer or string to a string with fixed length.'''
    form_string, formlen = forms[form]
    raw_date = str(raw_date)

    while len(raw_date) < formlen:
        raw_date = '0' + raw_date

    return raw_date
