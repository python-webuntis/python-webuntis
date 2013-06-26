'''
    This file is part of python-webuntis

    :copyright: (c) 2013 by Markus Unterwaditzer.
    :license: BSD, see LICENSE for more details.
'''

import datetime


forms = {
    'date': ('%Y%m%d', 6),
    'time': ('%H%M', 4),
}


def parse_date(string):
    return _parse(string, 'date')


def parse_time(string):
    return _parse(string, 'time')


def parse_datetime(date, time):
    return datetime.datetime.combine(
        parse_date(date).date(),
        parse_time(time).time()
    )


def _parse(string, form):
    form_string, formlen = forms[form]
    return datetime.datetime.strptime(_satinize(string, form), form_string)


def format_date(obj):
    return _format(obj, 'date')


def format_time(obj):
    return _format(obj, 'time')


def _format(obj, form):
    form_string, formlen = forms[form]
    try:
        int(obj)  # is this already formatted?
    except TypeError:
        return int(datetime.datetime.strftime(obj, form_string))
    else:
        return int(obj)

def _satinize(raw_date, form):
    '''Convert a raw date/time integer or string to a string with fixed length.'''
    form_string, formlen = forms[form]
    raw_date = str(raw_date)

    while len(raw_date) < formlen:
        raw_date = '0' + raw_date

    return raw_date
