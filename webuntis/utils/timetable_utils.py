"""
    This file is part of python-webuntis

    :copyright: (c) 2013 by Markus Unterwaditzer.
    :license: BSD, see LICENSE for more details.
"""

from __future__ import unicode_literals
from datetime import datetime


def table(periods, dates=None, times=None):
    """The backend of :py:meth:`webuntis.objects.PeriodList.to_table`."""

    if not len(periods):
        return []

    # generate some useful sets
    times = set(times or []).union(period.start.time() for period in periods)
    dates = set(dates or []).union(period.start.date() for period in periods)
    datetimes = set(datetime.combine(d, t) for d in dates for t in times)

    # create an empty table from all possible combinations of dates and times
    table = dict((t, dict((d, set()) for d in dates)) for t in times)

    # add the periods to the table
    # periods may be added twice if they are longer than one hour
    for period in periods:
        for dt in datetimes:
            if period.start <= dt and period.end > dt:
                table[dt.time()][dt.date()].add(period)

    # Convert the hashtable to the output format by sorting each dictionary's
    # .items() by key.
    return sorted((time, sorted(row.items())) for time, row in table.items())
