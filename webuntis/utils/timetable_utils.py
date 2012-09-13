'''
    This file is part of python-webuntis

    :copyright: (c) 2012 by Markus Unterwaditzer.
    :license: BSD, see LICENSE for more details.
'''

from __future__ import unicode_literals
import itertools


def table(timetable):
    '''
    Creates a table-like nested list out of an instance of
    :py:class:`webuntis.objects.PeriodList`.

    Returns a list containing tuples of "rows" and a datetime object, which in
    turn contain tuples of "hours" and their weekday number, which
    contain :py:class:`webuntis.objects.PeriodObject` instances which
    are happening at the same time.

    >>> from webuntis.utils.timetable_utils import table
    >>> table(s.timetable(klasse=109))
    '''

    if not len(timetable):
        return []

    time = lambda x: int(x.start.strftime('%H%M%S'))
    date = lambda x: int(x.start.strftime('%Y%m%d'))

    grouped = []
    times = []
    for i, row in itertools.groupby(sorted(timetable, key=time), time):
        new_row = []

        starttime = None

        # group lessons by date -- now all lessons occuring at the same time
        # are grouped
        for i2, hour in itertools.groupby(sorted(row, key=date), date):
            if hour:
                # itertools._grouper objects can't be accessed like lists
                hour = list(hour)
                weekday = hour[0].start.weekday()

                while (len(new_row) - 1) < weekday:
                    new_row.append(list())  # expand row as much as needed
                new_row[weekday] = hour

                if not starttime:
                    starttime = hour[0].start

        grouped.append(new_row)
        times.append(starttime)

    # expand each row to the maximal length
    longest_row = len(max(grouped, key=len))
    for row in grouped:
        while len(row) < longest_row:
            row.append(list())

    # at last add a weekday indicator
    return zip(times, [enumerate(row) for row in grouped])
