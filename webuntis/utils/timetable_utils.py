'''
    This file is part of python-webuntis

    :copyright: (c) 2012 by Markus Unterwaditzer.
    :license: BSD, see LICENSE for more details.
'''

from __future__ import unicode_literals
from . import log
from datetime import timedelta


def table(periods, width=None):
    '''The backend of :py:meth:`webuntis.objects.PeriodList.to_table`.'''

    if not len(periods):
        return []

    times = set()
    dates = set()
    table = {}

    for period in periods:
        time = period.start.time()
        date = period.start.date()

        if time not in table:
            table[time] = {}
        row = table[time]

        if date not in row:
            row[date] = set()
        hour = row[date]

        hour.add(period)
        times.add(time)
        dates.add(date)

    # len(dates) = width
    # Add additional dates so the next step will create stub cells for them.
    if width is not None:
        if len(dates) > width:
            raise ValueError(
                'Fixed width too small. Need at least %i' % len(dates))
        else:
            while len(dates) < width:
                dates.add(max(dates) + timedelta(days=1))

    # Add stub cells for missing combinations of date and time.
    for time in times:
        for date in dates:
            if date not in table[time]:
                table[time][date] = set()

    # Convert the hashtable to the output format by sorting each dictionary's
    # .items() by key.
    table = sorted((time, sorted(row.items())) for time, row in table.items())

    return table
